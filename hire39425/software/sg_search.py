#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################

import os
import sys
import time
import random
import base64
from contextlib import suppress

try:
    from .sg_net import *
except ImportError:
    from sg_net import *

SG_SEARCH_VERSION = "0.1.0"
SG_SEARCH_VERINFO = "LAN search tool v{} for SG+ Pickup\n".format(SG_SEARCH_VERSION) + \
                    "Copyright (C) Focal Acoustics, 2020-2021."

DEFAULT_DURATION = 5.0  # in seconds

################################################################################


class SgSearchProtocol(asyncio.DatagramProtocol):
    def __init__(self,
                 bc_addr: Tuple[str, int],
                 parser: SgParser,
                 on_search: callable):
        self.m_bc_addr = bc_addr
        self.m_parser = parser
        self.m_on_search = on_search
        self.m_transport = None
        self.m_timer: SgTimer = SgTimer(2.0, self._sendto)

    def connection_made(self, transport):
        self.m_transport = transport
        self._sendto()

    def datagram_received(self, data, addr):
        with suppress(ValueError, KeyError):
            dev_info = self.m_parser.parse_packet(data)
            self.m_on_search(dev_info, addr)

    def connection_lost(self, exc):
        self.m_transport = None
        self.m_timer.cancel()

    def _sendto(self):
        if self.m_transport is not None:
            pkt = self.m_parser.build_packet(
                dict(cmd='lan_search', timestamp=round(time.time())),
                SG_PKT_TYPE_LANSRCH
            )
            self.m_transport.sendto(pkt, self.m_bc_addr)


async def sg_create_transports_by_if(parser: SgParser,
                                     on_search: callable) -> List:
    transports = []
    with suppress(OSError):
        for if_name in netifaces.interfaces():
            with suppress(KeyError):
                addr_infos = netifaces.ifaddresses(if_name)[netifaces.AF_INET]
                for addr_info in addr_infos:
                    addr = addr_info['addr']
                    if addr != '127.0.0.1':
                        with suppress(socket.error):
                            transport, _ = await asyncio.get_running_loop().create_datagram_endpoint(
                                lambda: SgSearchProtocol(
                                    (addr_info['broadcast'], SG_LAN_SEARCH_PORT),
                                    parser,
                                    on_search
                                ),
                                (addr, 0),
                                family=socket.AF_INET,
                                allow_broadcast=True
                            )
                            transports.append(transport)
    return transports


async def sg_search_task(duration: float):
    def on_search(dev_info: dict, addr: Tuple[str, int]):
        ip_addr, _ = addr
        dev = ip_dev_dct.get(ip_addr)
        if dev is None:
            dev = SgDevice()
            dev.product_id = dev_info['product_id']
            dev.device_id = dev_info['device_id']
            dev.fw_version = dev_info['fw_version']
            dev.device_name = dev_info['device_name']
            dev.mac_addr = dev_info['mac_addr']
            dev.ip_addr = ip_addr
            ip_dev_dct[ip_addr] = dev
            print('   ', dev.product_id, dev.device_id, dev.fw_version,
                dev.device_name, dev.mac_addr, dev.ip_addr)

    parser = SgParser()
    parser.set_password(SG_DEF_PASSWORD)

    ip_dev_dct = {}
    transports = await sg_create_transports_by_if(parser, on_search)
    timer = SgTimer(0.2, lambda: None)
    await asyncio.sleep(duration)
    timer.cancel()
    for transport in transports:
        transport.close()
    if not ip_dev_dct:
        print('No device available.')


def sg_search_main(duration: float):
    print('LAN search is starting...')
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(
        sg_search_task(duration),
    )
    loop.run_until_complete(tasks)


if __name__ == "__main__":
    try:
        from optparse import OptionParser
        parser = OptionParser(usage=('Usage: %prog [options]\n\n' + SG_SEARCH_VERINFO))
        parser.get_option("-h").help = "Show this help message and exit."
        parser.add_option("--version",
                          action="store_true", default=False, dest="show_version",
                          help="Show version.")
        parser.add_option("-d", "--duration",
                          action="store", type="float", default=DEFAULT_DURATION, dest="duration",
                          help="The duration of the search, in seconds.")
        (options, args) = parser.parse_args()

        if options.show_version:
            print(SG_SEARCH_VERINFO)
            sys.exit(0)

        sg_search_main(options.duration)
        sys.exit(0)
    except KeyboardInterrupt:
        print('^C')
        sys.exit(-100)
