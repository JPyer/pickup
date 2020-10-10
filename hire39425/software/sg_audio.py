#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("..")
import cache
from software import sg_logger

SG_DEF_DURATION = 10.0  # in seconds
LOCAL_PORT = 0

################################################################################

import os
import re
import time
import random
import pathlib
import urllib
from contextlib import suppress, closing

try:
    from .sg_net import *
except ImportError:
    from sg_net import *

SG_CAPTURE_VERSION = "0.1.0"
SG_CAPTURE_VERINFO = "Audio capture tool v{} for SG+ Pickup\n".format(SG_CAPTURE_VERSION) + \
                     "Copyright (C) Focal Acoustics, 2020-2021."


################################################################################


def sg_get_local_ip(device_ip):
    # Get the proper local IP address.
    dev_ipaddr = ipaddress.IPv4Address(device_ip)
    with suppress(OSError):
        for if_name in netifaces.interfaces():
            with suppress(KeyError):
                addr_infos = netifaces.ifaddresses(if_name)[netifaces.AF_INET]
                for addr_info in addr_infos:
                    ip_addr = addr_info['addr']
                    if dev_ipaddr in ipaddress.ip_network(
                            '{}/{}'.format(ip_addr, addr_info['netmask']),
                            strict=False):
                        return ip_addr
    return None
class sg_audio_file_writer:
    # TODO wave音频格式处理函数
    pass

def sg_audio_path_builder(file_path, dev_info, audio_params, no_timestamp=False):
    localtm = time.localtime()
    fn = "[{}]{}-{}k-{}ch-{}bit.pcm".format(
        re.sub(r'[\\/:\*\?"<>|]', '_', dev_info['device_name']),
        '' if no_timestamp else time.strftime("-D%Y%m%dT%H%M%S", localtm),
        audio_params['audio_sample_rate'] // 1000,
        audio_params['audio_channels'] or 1,
        audio_params['audio_sample_bits'],
    )

    if not file_path:
        file_path = fn
    elif file_path.endswith(os.path.pathsep) or file_path.endswith('/'):
        file_path += fn
    dir = os.path.split(file_path)[0]
    if dir and not os.path.isdir(dir):
        try:
            os.makedirs(dir, exist_ok=True)
        except OSError:
            print('  *** Can not make directory "{}".'.format(dir))
            raise

    AUDIO_ENCODER_DCT = {
        SG_AUDIO_PCMS8: 'PCMS8',
        SG_AUDIO_PCMS16LE: 'PCMS16LE',
        SG_AUDIO_PCMS24LE: 'PCMS24LE',
        SG_AUDIO_PCMS32LE: 'PCMS32LE',
        SG_AUDIO_OPUS: 'OPUS',
    }
    print('  Device info:')
    print('    Product ID:         {}'.format(dev_info['product_id']))
    print('    Device ID:          {}'.format(dev_info['device_id']))
    print('    Device Name:        {}'.format(dev_info['device_name']))
    print('    Firmware Version:   {}'.format(dev_info['fw_version']))
    print('')
    print('  Audio Capture:')
    print('    Listen address:     {}'.format(audio_params['server_addr']))
    print('  Audio File:')
    print('    Codec:              {}'.format(AUDIO_ENCODER_DCT[audio_params['audio_encoder']]))
    print('    Sample Rate:        {}kHz'.format(audio_params['audio_sample_rate'] // 1000))
    print('    Channels:           {}'.format(audio_params['audio_channels'] or 1))
    print('    Bits per Sample:    {}'.format(audio_params['audio_sample_bits']))
    print('    Bitrate:            {}kbps'.format(audio_params['audio_bitrate'] // 1000))
    print('    Timestamp:          {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", localtm)))
    print('    Duration:           {} seconds'.format(options.duration))
    print('    File Name:          {}'.format(file_path))
    return file_path


class SgCaptureProtocol(asyncio.DatagramProtocol):
    RECV_BUFSZ = 2 * 1024 * 1024

    def __init__(self):
        self.transport = None
        self.local_addr: Optional[Tuple[str, int]] = None
        self.m_sessions: Dict[int, SgDeviceSession] = {}

    def loop(self) -> asyncio.AbstractEventLoop:
        return self.transport._loop

    def close(self):
        for session in self.m_sessions.values():
            session.close()
        self.m_sessions.clear()
        self.transport.close()

    def connection_made(self, transport):
        sock = transport.get_extra_info('socket')
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.RECV_BUFSZ)
        self.transport = transport
        self.local_addr = transport.get_extra_info('sockname')

    def datagram_received(self, data, addr):
        try:
            # Drop some packets to test audio ACK.
            # if random.randint(0, 100) == 0:
            #    return

            # The session ID is not encrypted.
            sid, = struct.unpack_from('<I', data, SG_PKT_HEADSZ)
            session = self.m_sessions[sid]
            session.recv_audio_packet(self.transport, data, addr)
        except (struct.error, KeyError, ValueError, IndexError):
            pass

    def create_session(self, device_ip: str, password: str) -> SgDeviceSession:
        # Create a new session and register it.
        while True:
            sid = random.randint(1, 0xFFFFFFFE)
            if sid not in self.m_sessions:
                break
        session = SgDeviceSession(sid, device_ip, password, loop=self.loop())
        session.enable_log(True)
        self.m_sessions[session.id] = session
        return session

    def remove_session(self, session_id: int):
        session = self.m_sessions.get(session_id)
        if session is not None:
            session.close()
            del self.m_sessions[session_id]


async def sg_audio_capture(device_ip: str, options):
    parse_result = urllib.parse.urlsplit('//' + options.listen_addr)
    local_host = parse_result.hostname
    local_port = parse_result.port or LOCAL_PORT
    if not local_host:
        local_host = sg_get_local_ip(device_ip)
        if local_host is None:
            print('  *** The device and this PC are not in a same LAN.')
            return -1

    timer = SgTimer(0.2, lambda: None)
    try:
        try:
            _, capture = await asyncio.get_running_loop().create_datagram_endpoint(
                lambda: SgCaptureProtocol(),
                (local_host, local_port),
                family=socket.AF_INET
            )
        except OSError:
            print('  *** Can not bind the local UDP socket to address "{}:{}".'.format(local_host, local_port))
            return -1

        with closing(capture):
            try:
                session = capture.create_session(device_ip, options.password)
                dev_info = await session.request(dict(cmd='get_device_info'))
            except OSError:
                print('  *** Can not connect to the device "{}".'.format(device_ip))
                return -1

            try:
                audio_params = dict(
                    server_addr='udp://{}:{}'.format(capture.local_addr[0], capture.local_addr[1]),
                    output_channel=options.channels,
                    audio_encoder=SG_AUDIO_PCMS24LE,
                    audio_channels=options.channels,  # mono
                    audio_frame_size=320,  # samples per frame
                    audio_sample_rate=16000,
                    audio_sample_bits=24,
                    audio_bitrate=0,  # no use for PCM
                    retrans_timeout=1000,  # threshold of retransmission timeout, in milliseconds
                    audio_checksum='off',
                )

                cache.RECORDING_DEVICES[device_ip] = {"pid": os.getpid()}
                with open("./pid.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open("./pid.txt", 'w') as f:
                    for line in lines:
                        if device_ip in line:
                            line = "{}:{}".format(device_ip, os.getpid())
                        f.write(line)
                sg_logger.info("current recording devices:{}".format(cache.RECORDING_DEVICES))
                await session.start_capture(audio_params,
                                            lambda params: sg_audio_path_builder(
                                                options.file_path, dev_info, params, options.no_timestamp))
                audio_timer = SgTimer(options.duration, lambda: setattr(sys, 'app_terminated', True))
                while not getattr(sys, 'app_terminated', False):
                    await asyncio.sleep(0.1)
            finally:
                print('')
                # Close the session
                capture.remove_session(session.id)
                await session.stop_capture()
                if session.m_recved_bytes == 0 and not win_advfw_add_program_rule(sys.executable, True):
                    print(' *** Can not receive any audio frame.')
                    print(' Use --fw option to add a firewall rule.')
                    win_advfw_add_program_rule(sys.executable)
            return 0

    except (OSError, IOError, EOFError, ValueError) as e:
        if isinstance(e, (EOFError, ValueError)):
            print('  *** Can access the device.')
            print('  Please input the correct password with "-p" option.')
            sg_logger.warn('  *** Can access the device.')
            sg_logger.warn('  Please input the correct password with "-p" option.')
        return -3
    finally:
        timer.cancel()


def sg_capture_main(device_ip: str, options):
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(
        sg_audio_capture(device_ip, options),
    )
    while True:
        try:
            status, = loop.run_until_complete(tasks)
            break
        except KeyboardInterrupt:
            setattr(sys, 'app_terminated', True)
            print('^C')
            sg_logger.warn('^C')
            # os.remove('pid.txt')
            status = -100
    return status


if __name__ == "__main__":
    try:
        from optparse import OptionParser

        parser = OptionParser(usage=('Usage: %prog [options] <Device Address>\n\n' + SG_CAPTURE_VERINFO))
        parser.get_option("-h").help = "Show this help message and exit."
        parser.add_option("--version",
                          action="store_true", default=False, dest="show_version",
                          help="Show version.")
        parser.add_option("-c", "--channels",
                          action="store", type="int", default=0, dest="channels",
                          help='Audio channels, 1/8/9/16/17/...')
        parser.add_option("-d", "--duration",
                          action="store", type="float", default=SG_DEF_DURATION, dest="duration",
                          help='Duration in seconds, default is "{}"s.'.format(SG_DEF_DURATION))
        parser.add_option("--fp", "--file-path",
                          action="store", type="string", default='', dest="file_path",
                          help="Path of the output PCM file.")
        parser.add_option("--fw", "--add-fw-rule",
                          action="store_true", default=False, dest="add_fw_rule",
                          help='Add a firewall rule to the Windows Advanced Firewall.')
        parser.add_option("--la", "--listen-addr",
                          action="store", type="string", default='', dest="listen_addr",
                          help='Capture\'s listen address, format is "<IP address>", ":<port>" or "<IP address>:<port>".')
        parser.add_option("--nt", "--no-timestamp",
                          action="store_true", default=False, dest="no_timestamp",
                          help='Build file name without timestamp.')
        parser.add_option("-p", "--password",
                          action="store", type="string", default=SG_DEF_PASSWORD, dest="password",
                          help='Device password, default is "{}".'.format(SG_DEF_PASSWORD))
        (options, args) = parser.parse_args()

        if options.show_version:
            print(SG_CAPTURE_VERINFO)
            sys.exit(0)

        if options.add_fw_rule:
            win_advfw_add_program_rule(sys.executable)
            sys.exit(0)

        if len(args) != 1:
            parser.print_help()
            sys.exit(1)

        status = sg_capture_main(args[0], options)
        sys.exit(status)
    except KeyboardInterrupt:
        print('^C')
        sys.exit(-100)
