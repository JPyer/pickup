#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DURATION = 5.0 # in seconds
DEVICE_IP = "127.0.0.1"
DEVICE_PASSWORD = "12345678"

################################################################################

import os
import socket
import select
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
    print('request: ', req)
    sock.sendall(pkt)

    if packet_type == SG_PKT_TYPE_REQ:
        rsp = sg_net_parse_packet(cryptor, sg_net_tcp_recv(sock, buf))
        print("    ", rsp)
        return rsp
    return None


def test_main():
    assert sg_gen_security_key('12345678') == SG_DEF_SECURITY_KEY

    # Create a buffer for socket IO.
    buf = memoryview(bytearray(SG_PKT_BUFSZ))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        #######################################################################
        # Send request and get response

        s.connect((DEVICE_IP, SG_NET_SERVER_PORT))
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Create AES cryptor by device security key.
        dev_cryptor = AES.new(sg_gen_security_key(DEVICE_PASSWORD), AES.MODE_ECB)

        sg_net_request(s, buf, dev_cryptor, dict(cmd='set_device_info', device_id='xxxxxx', device_name='我的设备'))
        sg_net_request(s, buf, dev_cryptor, dict(cmd='get_device_info'))
        sg_net_request(s, buf, dev_cryptor, dict(cmd='set_audio', output_gain=35))
        sg_net_request(s, buf, dev_cryptor, dict(cmd='get_audio'))
        print('')


if __name__ == "__main__":
    test_main()
