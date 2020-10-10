#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import socket
import select
import struct
import json
import base64
import hashlib
import ipaddress
import asyncio
from collections import OrderedDict
from typing import Any, List, Tuple, Dict, Coroutine, Union, Optional

try:
    import numpy as np
    import crcmod
    from Crypto.Cipher import AES
    import netifaces
except ImportError:
    print('*** Required modules are missing.')
    print('Please run as administrator:')
    print('    pip install numpy crcmod pycryptodome netifaces')
    sys.exit(-1)

# Packet type
SG_PKT_TYPE_REQ = 1
SG_PKT_TYPE_RSP = 2
SG_PKT_TYPE_AUDIO = 3
SG_PKT_TYPE_AUDIO_ACK = 4
SG_PKT_TYPE_LANSRCH = 5
SG_PKT_TYPE_LANSRCH_RSP = 6

SG_PKT_HEADSZ = 8  # size of the packet header
SG_PKT_BUFSZ = 2048  # size of the packet buffer

SG_NET_SERVER_PORT = 2228
SG_LAN_SEARCH_PORT = 2229

SG_AUDIO_PCMS8 = 1
SG_AUDIO_PCMS16LE = 2
SG_AUDIO_PCMS24LE = 3
SG_AUDIO_PCMS32LE = 4
SG_AUDIO_OPUS = 10

SG_DEF_PASSWORD = "12345678"
SG_DEF_SECURITY_KEY = b'\x8E\x75\x9C\x0A\x29\xEB\xA7\xE3\x48\x42\x8D\x86\xF5\x87\xE5\x8C'


class SgDevice:
    def __init__(self):
        self.product_id = ""
        self.device_id = ""
        self.fw_version = ""
        self.device_name = ""
        self.mac_addr = ""
        self.ip_addr = ""


class SgAudioPacket:
    def __init__(self):
        self.session_id = 0
        self.sn = 0
        self.timestamp = 0
        self.output_channel = 0
        self.audio_encoder = 0
        self.audio_channels = 0
        self.audio_sample_rate = 0
        self.audio_frame_size = 0
        self.audio_sample_bits = 0
        self.payload_size = 0
        self.payload: Optional[bytes] = None


class SgParser:
    def __init__(self, *, buffer: Optional[memoryview] = None):
        self.m_buffer = buffer or memoryview(bytearray(SG_PKT_BUFSZ))
        self.m_crypter: object = None
        self.m_reader: Optional[asyncio.StreamReader] = None
        self.m_writer: Optional[asyncio.StreamWriter] = None
        self.m_sock: Optional[socket.socket] = None
        self.m_crc = crcmod.predefined.Crc('modbus')

    def buffer(self) -> memoryview:
        return self.m_buffer

    def crypter(self, crypter: object) -> object:
        return self.m_crypter

    def set_crypter(self, crypter: object):
        self.m_crypter = crypter

    def set_password(self, password: str):
        self.m_crypter = AES.new(SgParser.generate_key(password), AES.MODE_ECB)

    def set_key(self, security_key: bytes):
        self.m_crypter = AES.new(security_key, AES.MODE_ECB)

    def reader(self) -> asyncio.StreamReader:
        return self.m_reader

    def writer(self) -> asyncio.StreamWriter:
        return self.m_writer

    def set_streams(self,
                    reader: asyncio.StreamReader,
                    writer: asyncio.StreamWriter):
        self.m_reader = reader
        self.m_writer = writer

    def close_streams(self):
        self.m_reader = None
        if self.m_writer is not None:
            self.m_writer.close()
            self.m_writer = None

    # Build a packet
    def build_packet(self,
                     req: Union[dict, bytes, bytearray, memoryview],
                     packet_type: int = SG_PKT_TYPE_REQ,
                     *,
                     crc_off: Optional[bool] = None) -> memoryview:
        assert self.m_crypter
        buf = self.m_buffer

        if isinstance(req, dict):
            payload = json.dumps(req).encode()
        else:
            payload = req

        # Copy payload
        size = SG_PKT_HEADSZ + len(payload)
        # Do not copy if payload is store in the same buffer
        if not (isinstance(req, memoryview) and req.obj is buf):
            buf[SG_PKT_HEADSZ:size] = payload

        # Appand padding zero: len(payload) == 0 (mod 16)
        padding = -(size - SG_PKT_HEADSZ) & 15
        if padding:
            end = size + padding
            buf[size:end] = b'\0' * padding
            size = end

        # Fill header
        struct.pack_into('<HHHB', buf, 0,
                         0x7E7E,
                         size,
                         0,
                         packet_type
                         )

        # Calculate CRC
        self.m_crc.crcValue = 0xFFFF
        if not crc_off:
            self.m_crc.update(buf[6:size])
        struct.pack_into('<H', buf, 4, self.m_crc.crcValue)

        buf[SG_PKT_HEADSZ:size] = self.m_crypter.encrypt(buf[SG_PKT_HEADSZ:size])
        return buf[:size]

    def build_audio_ack(self,
                        session_id: int,
                        sn_list: List[int],
                        *,
                        crc_off: Optional[bool] = None) -> memoryview:
        n = len(sn_list)
        struct.pack_into(
            '<IHH{}I'.format(n),
            self.m_buffer,
            SG_PKT_HEADSZ,
            session_id,
            n,
            0,
            *sn_list)
        n = SG_PKT_HEADSZ + 8 + 4 * n
        return self.build_packet(self.m_buffer[SG_PKT_HEADSZ:n], SG_PKT_TYPE_AUDIO_ACK, crc_off=crc_off)

    def parse_packet(self,
                     packet: Union[bytes, bytearray, memoryview],
                     *,
                     crc_off: Optional[bool] = None
                     ) -> Union[dict, SgAudioPacket]:
        if isinstance(packet, bytes):
            n = len(packet)
            self.m_buffer[:n] = packet
            packet = self.m_buffer[:n]
        elif isinstance(packet, bytearray):
            packet = memoryview(packet)
        return self.parse_packet2(packet[:SG_PKT_HEADSZ], packet[SG_PKT_HEADSZ:], crc_off=crc_off)

    # Parse a packet's header and payload
    def parse_packet2(self,
                      header: Union[bytes, bytearray, memoryview],
                      payload: Union[bytes, bytearray, memoryview],
                      *,
                      crc_off: Optional[bool] = None
                      ) -> Union[dict, SgAudioPacket]:
        assert self.m_crypter

        magic, size, chksum, packet_type = struct.unpack_from('<HHHB', header, 0)
        if magic != 0x7E7E or size != len(payload) + SG_PKT_HEADSZ:
            raise ValueError('Packet error.')

        payload_size = size - SG_PKT_HEADSZ

        if packet_type in (SG_PKT_TYPE_RSP, SG_PKT_TYPE_LANSRCH_RSP):
            # Non-audio
            if payload_size % 16 != 0:
                raise ValueError('Payload length error.')
            # AES decrypt
            payload = self.m_crypter.decrypt(payload)
        elif packet_type == SG_PKT_TYPE_AUDIO:
            # Audio
            if payload_size < 36:
                raise ValueError('Payload length error.')
            # AES decrypt
            payload[4:36] = self.m_crypter.decrypt(payload[4:36])
        else:
            raise ValueError('Packet type error.')

        if not crc_off:
            cm = self.m_crc
            cm.crcValue = 0xFFFF
            cm = crcmod.predefined.Crc('modbus')
            cm.update(header[6:SG_PKT_HEADSZ])
            cm.update(payload)
            if cm.crcValue != chksum:
                raise ValueError('CRC error.')

        if packet_type in (SG_PKT_TYPE_RSP, SG_PKT_TYPE_LANSRCH_RSP):
            # Non-audio, parse JSON
            end = payload.rfind(b'}') + 1
            return json.loads(payload[:end]) if end > 0 else {}

        # Parse audio packet
        apk = SgAudioPacket()
        (apk.session_id, \
         apk.sn,
         apk.timestamp,
         _,
         apk.output_channel,
         apk.audio_encoder,
         apk.audio_channels,
         apk.audio_sample_rate,
         apk.audio_frame_size,
         apk.audio_sample_bits,
         xor_key,
         apk.payload_size) = struct.unpack_from('<IIQBBBBIHBBH', payload, 0)
        if apk.payload_size + 30 > len(payload):
            raise ValueError('Audio packet error.')
        # Decrypt the payload by <xor_key>
        apk.payload = (np.frombuffer(payload[30: 30 + apk.payload_size], dtype=np.uint8) ^ xor_key).tobytes()
        return apk

    async def connect(self,
                      host: str,
                      port: int = SG_NET_SERVER_PORT,
                      *,
                      loop: Optional[asyncio.AbstractEventLoop] = None):
        reader, writer = await asyncio.open_connection(host, port, loop=loop)
        sock = writer.get_extra_info('socket')
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.set_streams(reader, writer)

    async def read(self) -> Tuple[bytes, bytes]:
        assert self.m_reader
        # Read header.
        header = await self.m_reader.readexactly(SG_PKT_HEADSZ)
        magic, size = struct.unpack_from('<HH', header, 0)
        if magic != 0x7E7E or size > SG_PKT_BUFSZ:
            raise ValueError('Packet error.')
        # Read payload.
        payload = await self.m_reader.readexactly(size - SG_PKT_HEADSZ)
        return (header, payload)

    async def request(self,
                      req: Union[dict, bytes, bytearray, memoryview],
                      packet_type: int = SG_PKT_TYPE_REQ,
                      ) -> Union[dict, SgAudioPacket]:
        assert self.m_writer
        # Build the packet.
        pkt = self.build_packet(req, packet_type)
        # Send the packet and wait done.
        self.m_writer.write(pkt)
        # await self.m_writer.drain()
        if packet_type == SG_PKT_TYPE_REQ:
            # Read the response if needed.
            header, payload = await self.read()
            return self.parse_packet2(header, payload)
        return None

    @staticmethod
    def generate_key(password: str) -> bytes:
        m = hashlib.md5()
        m.update(password.encode())
        m.update(b'\xFD\x50\xF7\x22\x8C\x8F\x10\x1B\x2C\x89\x89\x40\x2B\x0F\x15\x8F')
        return m.digest()


class SgAudioRetran:
    TIMEOUT = 1.0  # seconds
    MIN_INTERVAL = 0.05
    MAX_INTERVAL = 0.10

    def __init__(self, sn: int, packet: SgAudioPacket, start: float):
        self._times = 0
        self.sn = sn
        self.packet = packet
        self.start = start
        self.stop = start + self.TIMEOUT

    def next(self) -> bool:
        interval = self.MIN_INTERVAL * (1 << self._times)
        if interval <= self.MAX_INTERVAL:
            self._times += 1
        else:
            interval = self.MAX_INTERVAL
        self.start += interval
        return self.start <= self.stop


class SgDeviceSession:
    def __init__(self,
                 session_id: int,
                 device_ip: str,
                 password: str,
                 *,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        self.id = session_id  # session ID
        self.device_addr: Optional[Tuple[str, int]] = (device_ip, 0)
        self.parser = SgParser()
        self.parser.set_password(password)
        self.loop = loop or asyncio.get_running_loop()

        self.m_audio_parser: Optional[SgParser] = None
        self.m_session_key = None  # session key
        self.m_retrans = OrderedDict()
        self.m_next_sn: int = None
        self.m_timestamp = 0
        self.m_now = 0.0
        self.m_log_enabled = False
        self.m_audio_crc_off = False
        self.m_file = None
        self.m_recved_bytes = 0

    def enable_log(self, enabled):
        self.m_log_enabled = enabled

    def logi(self, text: str, *, flush: bool = False):
        print(text, end='', flush=flush)

    def get_audio_parser(self):
        if self.m_audio_parser is None:
            self.m_audio_parser = SgParser(buffer=self.parser.buffer())
            self.m_audio_parser.set_key(self.m_session_key)
        return self.m_audio_parser

    def close(self):
        self.m_session_key = None
        self.m_retrans.clear()
        if self.m_file:
            self.m_file.close()
            self.m_file = None
        self.parser.close_streams()

    async def request(self, req: dict) -> dict:
        conntected = False
        while not conntected:
            if self.parser.writer() is None:
                await self.parser.connect(self.device_addr[0], loop=self.loop)
                conntected = True
            try:
                return await self.parser.request(req)
            except (OSError, IOError, EOFError):
                if conntected:
                    raise
                self.parser.close_streams()

    async def start_capture(self,
                            audio_params: dict,
                            path_builder: callable):
        # New a session key.
        session_key = os.urandom(16)
        # Start audio transmission.
        self.m_audio_crc_off = audio_params.get('audio_checksum') == 'off'
        req = dict(
            cmd='open_audio',
            session_id=self.id,
            session_key=base64.b64encode(session_key).decode(),
            **audio_params,
        )
        str = json.dumps(req)
        rsp = await self.request(req)
        if rsp['err_code'] != 0:
            if self.m_log_enabled:
                self.logi('  *** {}\n'.format(rsp['err_msg']))
            raise IOError()

        file_path = path_builder(rsp if 'audio_channels' in rsp else audio_params)
        # Open file
        try:
            # fixme
            dirpath = os.path.join(os.path.abspath(".."), "media")
            file_path = os.path.join(dirpath, file_path)
            print(file_path)
            self.m_file = open(file_path, "wb")
            self.m_recved_bytes = 0
        except OSError:
            if self.m_log_enabled:
                self.logi(' *** Can not open file "{}".\n'.format(file_path))
            raise
        # Set session key to start.
        self.m_session_key = session_key

    async def stop_capture(self):
        self.m_session_key = None
        self.m_next_sn = None
        self.m_timestamp = 0
        self.m_retrans.clear()
        if self.m_file:
            self.m_file.close()
            self.m_file = None
        try:
            await self.request(dict(cmd='close_audio', session_id=self.id))
        except:
            pass

    def recv_audio_packet(self,
                          transport: asyncio.DatagramTransport,
                          data: Union[bytes, bytearray, memoryview],
                          addr: Tuple[str, int]):
        # Do not receive packet if this session has not been started.
        if self.m_session_key is None:
            return

        # Parse packet.
        packet = self.get_audio_parser().parse_packet(data, crc_off=self.m_audio_crc_off)
        self.device_addr = addr

        is_duplicate = False
        self.m_now = self.loop.time()
        while True:
            if self.m_next_sn is None:
                self.m_next_sn = packet.sn
                self.m_timestamp = packet.timestamp

            lost_num = (packet.sn - self.m_next_sn) & 0xFFFFFFFF
            if lost_num & 0x80000000:
                lost_num -= 0x100000000
            if (packet.timestamp >= self.m_timestamp + SgAudioRetran.TIMEOUT * 1000 or
                    lost_num >= 250):
                # Too many lost packges
                self.m_next_sn = packet.sn
                self.m_timestamp = packet.timestamp
                self.m_retrans.clear()
                if self.m_log_enabled:
                    self.logi('*** {}: drop packets before {}\n'.format(self.id, packet.sn))
            elif lost_num > 0:
                # Some packets lost
                for i in range(0, lost_num):
                    sn = (self.m_next_sn + i) & 0xFFFFFFFF
                    if sn not in self.m_retrans:
                        self.m_retrans[sn] = SgAudioRetran(sn, None, self.m_now)
            elif lost_num < 0:
                is_duplicate = True
                break

            rt = self.m_retrans.get(packet.sn)
            if rt is None:
                self.m_retrans[packet.sn] = SgAudioRetran(packet.sn, packet, self.m_now)
            elif rt.packet is None:
                rt.packet = packet
            else:
                is_duplicate = True
            break
        if is_duplicate and self.m_log_enabled:
            self.logi('*** {}: duplicate packet {}\n'.format(self.id, packet.sn))
        # Process received packets and send ACK if there are lost packets.
        self._process_audio(transport)

    def send_audio_ack(self, transport: asyncio.DatagramTransport):
        if not self.m_retrans:
            return
        sn_list = []
        lost_list = []
        for sn, rt in self.m_retrans.items():
            if rt.packet is None:
                send_ack = False
                while rt.start < self.m_now:
                    send_ack = True
                    if not rt.next():
                        lost_list.append(rt.sn)
                        # timed-out
                        if self.m_log_enabled:
                            self.logi('*** {}: packet {} is timed-out\n'.format(self.id, rt.sn))
                        break
                if send_ack:
                    sn_list.append(rt.sn)
        for sn in lost_list:
            del self.m_retrans[sn]
        if sn_list:
            pkt = self.get_audio_parser().build_audio_ack(self.id, sn_list, crc_off=self.m_audio_crc_off)
            transport.sendto(pkt, self.device_addr)
            if self.m_log_enabled:
                self.logi('*** {}: ACK {}\n'.format(self.id, sn_list))

    def _process_audio(self, transport: asyncio.DatagramTransport):
        while True:
            rt = self.m_retrans.get(self.m_next_sn)
            if rt is None or rt.packet is None:
                break
            pkt = rt.packet
            del self.m_retrans[self.m_next_sn]
            self.m_next_sn += 1
            self.m_timestamp = pkt.timestamp
            if self.m_log_enabled:
                self.logi(".", flush=True)
            # Save PCM data to file.
            self.m_file.write(pkt.payload)
            self.m_recved_bytes += len(pkt.payload)
        self.send_audio_ack(transport)


class SgTimer:
    def __init__(self,
                 interval: float,
                 callback: callable,
                 *,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        self.m_loop = loop or asyncio.get_running_loop()
        self.m_interval = interval
        self.m_callback = callback
        self.m_task = asyncio.ensure_future(self._job(), loop=self.m_loop)

    def loop(self) -> asyncio.AbstractEventLoop:
        return self.m_loop

    def cancel(self):
        if self.m_task is not None:
            self.m_task.cancel()
            self.m_task = None

    async def _job(self):
        while True:
            await asyncio.sleep(self.m_interval, loop=self.m_loop)
            cr = self.m_callback()
            if asyncio.iscoroutine(cr):
                await cr


def win_advfw_add_program_rule(program: str, check_only=False) -> bool:
    if sys.platform != 'win32':
        return True

    import subprocess
    import locale
    import re

    rule_name = '#@program [{}]'.format(re.sub('[\\\\/]', '/', re.sub('[\'\"]', '', program.lower())))

    status = subprocess.call('netsh.exe advfirewall firewall show rule name="{}"'.format(rule_name),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    if status == 0:
        return True
    if check_only:
        return False

    bat_script = (
        '::==============================================================================\n'
        '@echo off\n'
        'setlocal\n'
        'set GETADMIN_VBS=getadmin-%~n0.vbs\n'
        '"%SystemRoot%\system32\cacls.exe" "%SystemRoot%\system32\config\system" 1>nul 2>&1\n'
        'if %errorlevel% neq 0 ( goto UACPrompt ) else ( goto gotAdmin )\n'
        ':UACPrompt\n'
        'echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\%GETADMIN_VBS%"\n'
        'echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\%GETADMIN_VBS%"\n'
        'cscript.exe /nologo "%temp%\%GETADMIN_VBS%"\n'
        'exit /b\n'
        ':gotAdmin\n'
        'if exist "%temp%\%GETADMIN_VBS%" ( del "%temp%\%GETADMIN_VBS%" )\n'
        'cd /d "%~dp0"\n'
        '::==============================================================================\n\n'
        'netsh.exe advfirewall firewall add rule name="{}" dir=in action=allow program="{}"\n'
        'del /q "%~0"\n'
    ).format(rule_name, program)
    bat_name = os.path.join(os.path.expandvars('%temp%'),
                            'getadmin-{}.cmd'.format(os.path.split(__file__)[1].replace('.', '_')))
    with open(bat_name, "w", encoding=locale.getpreferredencoding()) as f:
        f.write(bat_script)
    status = subprocess.call('cmd.exe /c "{}"'.format(bat_name),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
    return status == 0
