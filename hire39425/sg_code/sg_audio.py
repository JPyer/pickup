#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DURATION = 5.0  # in seconds
DEVICE_IP = "127.0.0.1"
DEVICE_IP = "192.168.2.218"
DEVICE_PASSWORD = "12345678"
LOCAL_IP = "127.0.0.1"
LOCAL_IP = "192.168.2.10"
LOCAL_PORT = 2228

################################################################################

import os
import time
import random
import base64

if '.' in __name__:
    from .sg_net import *
else:
    from sg_net import *


################################################################################


def sg_net_request(sock, buf, cryptor, req, packet_type=SG_PKT_TYPE_REQ):
    pkt = sg_net_build_packet(buf, cryptor, req, packet_type)
    sock.sendall(pkt)

    if packet_type == SG_PKT_TYPE_REQ:
        rsp = sg_net_parse_packet(cryptor, sg_net_tcp_recv(sock, buf))
        return rsp
    return None


def sg_audio_main():
    # Create a buffer for socket IO.
    buf = memoryview(bytearray(SG_PKT_BUFSZ))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s, \
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:

        try:
            s.connect((DEVICE_IP, SG_NET_SERVER_PORT))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            print('  Can not connect to the device {}.'.format(DEVICE_IP))
            return -1

        # Create AES cryptor by device security key.
        dev_cryptor = AES.new(sg_gen_security_key(DEVICE_PASSWORD), AES.MODE_ECB)

        #######################################################################

        # This dict is used to find the AES decryptor by a session ID.
        session_key_dct = {}

        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind((LOCAL_IP, LOCAL_PORT))

        # Create a new session ID and session key
        session_id = random.randint(1, 0xFFFFFFFF)
        session_key = os.urandom(16)

        # Register the session ID, connect it to the AES cryptor.
        session_key_dct[session_id] = AES.new(session_key, AES.MODE_ECB)

        # Start audio transmission.
        sg_net_request(s, buf, dev_cryptor, dict(
            cmd='open_audio',
            session_id=session_id,
            session_key=base64.b64encode(session_key).decode(),
            server_addr='{}:{}'.format(LOCAL_IP, LOCAL_PORT),
            output_channel=1,
            audio_encoder=3,  # SG_AUDIO_PCMS24LE
            audio_channels=1,  # mono
            audio_frame_size=320,  # samples per frame
            audio_sample_rate=16000,
            audio_sample_bits=24,
            audio_bitrate=0,  # no use for PCM
            retrans_timeout=1000,  # threshold of retransmission timeout, in milliseconds
        ))

        # Start receiving audio frames
        packets = {}
        with open("pickup.pcm", "wb") as f:
            current_sn = None
            start = time.time()
            n = 0
            while start + DURATION >= time.time():
                try:
                    data, addr = sg_net_udp_recv(udp_sock, buf)
                    # The session ID is not encrypted.
                    sid, = struct.unpack_from('<I', data, SG_PKT_HEADSZ)
                    # Get the AES cryptor of the session
                    session_cryptor = session_key_dct[sid]
                    # Parse the packet
                    pkt = sg_net_parse_packet(session_cryptor, data)

                    n += 1
                    if n % 100 == 0 and current_sn is not None:
                        # Test audio ACK
                        ack = sg_net_audio_ack(buf[SG_PKT_HEADSZ:],
                                               session_id, [current_sn, current_sn - 1, current_sn - 2])
                        udp_sock.sendto(sg_net_build_packet(
                            buf, session_cryptor, ack, packet_type=SG_PKT_TYPE_AUDIO_ACK), addr)
                        print("****************** ACK", current_sn)

                    # Packets lost ?
                    if current_sn is None:
                        # The first frame.
                        current_sn = pkt.sn
                    else:
                        delta = (pkt.sn - current_sn) & 0xFFFFFFFF
                        if delta & 0x80000000:
                            delta -= 0x100000000
                        if delta == 1:
                            # Sn is continuous.
                            current_sn += 1
                        elif delta < 0:
                            print("****************** delta", delta, pkt.sn)
                            continue
                        elif delta > 0:
                            print("****************** delta", delta, pkt.sn)
                            continue

                    print(
                        pkt.session_id,
                        pkt.sn,
                        pkt.timestamp / 1000,
                        pkt.output_channel,
                        pkt.audio_encoder,
                        pkt.audio_channels,
                        pkt.audio_sample_rate,
                        pkt.audio_frame_size,
                        pkt.audio_sample_bits,
                        len(pkt.payload)
                    )

                    # Save PCM data to file.
                    if pkt.session_id == session_id:
                        f.write(pkt.payload)

                except (ValueError, IndexError) as e:
                    print(e)

        # Close the session
        del session_key_dct[session_id]
        sg_net_request(s, buf, dev_cryptor, dict(cmd='close_audio', session_id=session_id))


if __name__ == "__main__":
    sg_audio_main()
