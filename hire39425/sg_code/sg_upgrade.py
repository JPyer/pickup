#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DEVICE_IP = "192.168.2.213"
DEVICE_PASSWORD = "12345678"

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


def sg_upgrade_main(dev_ip: str, dev_passwd: str, fw_path: str):
    # Create a buffer for socket IO.
    buf = memoryview(bytearray(SG_PKT_BUFSZ))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((dev_ip, SG_NET_SERVER_PORT))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            print('  Can not connect to the device {}.'.format(dev_ip))
            return -1

        # Create AES cryptor by device security key.
        dev_cryptor = AES.new(sg_gen_security_key(dev_passwd), AES.MODE_ECB)

        try:
            dev_info = sg_net_request(s, buf, dev_cryptor, dict(cmd='get_device_info'))
            if dev_info['err_code'] != 0:
                raise OSError()
        except OSError:
            print('  Can not get device info.')
            return -2

        try:
            print('  Device info:')
            print('    Product ID:   {}'.format(dev_info['product_id']))
            print('    Device ID:    {}'.format(dev_info['device_id']))
            print('    Device Name:  {}'.format(dev_info['device_name']))
            print('    Fw Version:   {}'.format(dev_info['fw_version']))
            print('    Fw Timestamp: {}'.format(dev_info['fw_timestamp']))
            print('')

            with open(fw_path, 'rb') as f:
                fw_data = f.read()
                crc = crcmod.predefined.Crc('modbus')
                crc.update(fw_data)

                # TODO:
                sid = random.randint(1, 0xFFFFFFFF)
                product_id =dev_info['product_id']
                fw_version = '1.0.0'
                fw_addr = 0
                fw_chksum = crc.crcValue

                # Start upgrading.
                rsp = sg_net_request(s, buf, dev_cryptor, dict(
                    cmd='fw_upgrade',
                    session_id=sid,
                    product_id=product_id,
                    fw_version=fw_version,
                    fw_addr=fw_addr,
                    fw_size=len(fw_data),
                    fw_checksum=fw_chksum,
                ))
                if rsp['err_code'] != 0:
                    print('  ***', rsp['err_msg'])
                    raise ValueError()

                # Download firmware.
                print('  Downloading ', end='')
                trunk_size = 1400
                offset = 0
                dots = 0
                while offset < len(fw_data):
                    if dots <= offset / 10000:
                        dots += 1
                        print('.', end='')
                    size = min(trunk_size, len(fw_data) - offset)
                    rsp = sg_net_request(s, buf, dev_cryptor, dict(
                        cmd='fw_data',
                        session_id=sid,
                        offset=offset,
                        data=base64.b64encode(fw_data[offset:offset + size]).decode(),
                    ))
                    if rsp['err_code'] != 0:
                        print('  ***', rsp['err_msg'])
                        raise ValueError()
                    offset += size
                print('')

                # Burn firmware.
                print('  Burning ...')
                rsp = sg_net_request(s, buf, dev_cryptor, dict(
                    cmd='fw_data',
                    session_id=sid,
                    offset=offset,
                    eos=1,
                ))
                if rsp['err_code'] != 0:
                    print('  ***', rsp['err_msg'])
                    raise IOError()
                print('  Done.')
                return 0
        except (OSError, IOError, ValueError):
            return -3


if __name__ == "__main__":
    sg_upgrade_main(DEVICE_IP, DEVICE_PASSWORD, 'sg_pickup.ais')


n = 1
def _global():
    global n
    n = n + 1
_global()
print(n)