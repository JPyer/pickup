#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DURATION = 5.0  # in seconds
# BROADCAST_ADDR = "192.168.5.255"
# BROADCAST_ADDR = "192.168.2.255"
# BROADCAST_ADDR = "169.254.12.1"
BROADCAST_ADDR = "192.168.2.255"
# BROADCAST_ADDR = "169.254.255.255"

########################### #####################################################

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


def sg_search_main(product_ids=None, search_ip_addr = None):
    # Create a buffer for socket IO.
    buf = memoryview(bytearray(SG_PKT_BUFSZ))

    ip_dev_dct = {}
    device_list = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ls:
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        ls.bind(('0.0.0.0', 0))

        # Create AES cryptor by device security key.
        def_cryptor = AES.new(SG_DEF_SECURITY_KEY, AES.MODE_ECB)

        print('LAN search is starting...')
        start = time.time()
        while start + DURATION >= time.time():
            pkt = sg_net_build_packet(
                buf,
                def_cryptor,
                dict(cmd='lan_search', timestamp=round(time.time())),
                SG_PKT_TYPE_LANSRCH
            )
            ls.sendto(pkt, (BROADCAST_ADDR, SG_LAN_SEARCH_PORT))

            readable, _, _ = select.select([ls], (), (), 0.5)
            if readable and ls in readable:
                pkt, (ip_addr, _) = sg_net_udp_recv(ls, buf)
                dev_info = sg_net_parse_packet(def_cryptor, pkt)
                dev = ip_dev_dct.get(ip_addr)
                if dev is None:
                    dev = sg_pickup_dev()
                    dev.product_id = dev_info['product_id']
                    dev.device_id = dev_info['device_id']
                    dev.fw_version = dev_info['fw_version']
                    dev.device_name = dev_info['device_name']
                    dev.mac_addr = dev_info['mac_addr']
                    dev.ip_addr = ip_addr
                    ip_dev_dct[ip_addr] = dev
                    dev_info['ip_addr'] = ip_addr
                    dev_info['key'] = dev_info['product_id']
                    dev_info['editable'] = False
                    print('   ', dev.product_id, dev.device_id, dev.fw_version,
                          dev.device_name, dev.mac_addr, dev.ip_addr)
                    # return True, dev_info
                    device_list.append(dev_info)
                    if search_ip_addr and search_ip_addr == ip_addr:
                        return True, device_list

    print('LAN search is finished.')
    if len(device_list) == 0:
        print('')
        print('No device available.')
        return False, None
    if product_ids:
        device_list = filter(lambda d: d['product_id'] in product_ids, device_list)
    return True, device_list


if __name__ == "__main__":
    sg_search_main()
