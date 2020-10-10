#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
import json
import hashlib

import numpy as np              # pip install numpy
import crcmod                   # pip install crcmod
from Crypto.Cipher import AES   # pip install pycryptodome

# Packet type
SG_PKT_TYPE_REQ	= 1
SG_PKT_TYPE_RSP	= 2
SG_PKT_TYPE_AUDIO = 3
SG_PKT_TYPE_AUDIO_ACK = 4
SG_PKT_TYPE_LANSRCH = 5
SG_PKT_TYPE_LANSRCH_RSP = 6

SG_PKT_HEADSZ = 8   # size of the packet header
SG_PKT_BUFSZ = 2048 # size of the packet buffer

SG_NET_SERVER_PORT = 2228
SG_LAN_SEARCH_PORT = 2229

SG_DEF_SECURITY_KEY = b'\x8E\x75\x9C\x0A\x29\xEB\xA7\xE3\x48\x42\x8D\x86\xF5\x87\xE5\x8C'


class sg_pickup_dev:
    def __init__(self):
        self.product_id = ""
        self.device_id = ""
        self.fw_version = ""
        self.device_name = ""
        self.mac_addr = ""
        self.ip_addr = ""


class sg_audio_packet:
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
        self.payload = None


def sg_gen_security_key(password):
    m = hashlib.md5()
    m.update(password.encode())
    m.update(b'\xFD\x50\xF7\x22\x8C\x8F\x10\x1B\x2C\x89\x89\x40\x2B\x0F\x15\x8F')
    return m.digest()


def sg_net_build_packet(buf: memoryview,
                        cryptor: object,
                        req: object,
                        packet_type=SG_PKT_TYPE_REQ) -> memoryview:
    if isinstance(req, dict):
        payload = json.dumps(req).encode()
    else:
        payload = req

    # Copy payload
    size = SG_PKT_HEADSZ + len(payload)
    # Do not copy if payload is store in the same buffer
    if not isinstance(req, memoryview) or req.obj is not buf.obj:
        buf[SG_PKT_HEADSZ:size] = payload

    # Appand padding zero: len(payload) == 0 (mod 16)
    padding = (-(size - SG_PKT_HEADSZ) & 15)
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
    crc = crcmod.predefined.Crc('modbus')
    crc.update(buf[6:size])
    struct.pack_into('<H', buf, 4, crc.crcValue)
    
    buf[SG_PKT_HEADSZ:size] = cryptor.encrypt(buf[SG_PKT_HEADSZ:size])
    return buf[:size]


def sg_net_parse_packet(cryptor: object,
                        packet: object) -> object:
    magic, size, chksum, packet_type = struct.unpack_from('<HHHB', packet, 0)
    if magic != 0x7E7E or size > len(packet):
        raise ValueError('Packet error.')

    payload_size = size - SG_PKT_HEADSZ
    payload = packet[SG_PKT_HEADSZ:size]

    if packet_type in (SG_PKT_TYPE_RSP, SG_PKT_TYPE_LANSRCH_RSP):
        # Non-audio
        if payload_size % 16 != 0:
            raise ValueError('Payload length error.')
        # AES decrypt
        payload = cryptor.decrypt(payload)
    elif packet_type == SG_PKT_TYPE_AUDIO:
        # Audio
        if payload_size < 36:
            raise ValueError('Payload length error.')
        # AES decrypt
        payload[4:36] = cryptor.decrypt(payload[4:36])
    else:
        raise ValueError('Packet type error.')

    crc = crcmod.predefined.Crc('modbus')
    crc.update(packet[6:SG_PKT_HEADSZ])
    crc.update(payload)
    if crc.crcValue != chksum:
        raise ValueError('CRC error.')

    if packet_type in (SG_PKT_TYPE_RSP, SG_PKT_TYPE_LANSRCH_RSP):
        # Non-audio, parse JSON
        end = payload.rfind(b'}') + 1
        return json.loads(payload[:end]) if end > 0 else {}

    # Parse audio packet
    apk = sg_audio_packet()
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
    apk.payload = (np.frombuffer(payload[30 : 30 + apk.payload_size], dtype=np.uint8) ^ xor_key).tobytes()
    return apk


def sg_net_audio_ack(buf: memoryview, session_id: int, sn_list: list) -> memoryview:
    n = len(sn_list)
    struct.pack_into('<IHH{}I'.format(len(sn_list)), buf, 0,
        session_id, n, 0, *sn_list)
    n = 8 + n * 4
    return buf[:n]


def sg_net_tcp_recv(sock: socket.socket, buf: memoryview) -> memoryview:
    sock.recv_into(buf, SG_PKT_HEADSZ, socket.MSG_WAITALL)
    magic, size = struct.unpack_from('<HH', buf, 0)
    if magic != 0x7E7E or size > len(buf):
        raise ValueError('Packet error.')
    sock.recv_into(buf[SG_PKT_HEADSZ:], size - SG_PKT_HEADSZ, socket.MSG_WAITALL)
    return buf[:size]


def sg_net_udp_recv(sock: socket.socket, buf: memoryview) -> (memoryview, tuple):
    size, addr = sock.recvfrom_into(buf)
    if size < 12:
        raise ValueError('UDP packet error.')
    return buf[:size], addr
