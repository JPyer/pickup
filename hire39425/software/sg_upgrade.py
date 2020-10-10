#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import base64

try:
    from .sg_net import *
    from .sg_fwmerge import *
except ImportError:
    from sg_net import *
    from sg_fwmerge import *


SG_UPGRADE_VERSION = "0.1.0"
SG_UPGRADE_VERINFO = "Firmware upgrade tool v{} for SG+ Pickup\n".format(SG_UPGRADE_VERSION) + \
                     "Copyright (C) Focal Acoustics, 2020-2021."

################################################################################

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class SgUpgradeTimer(SgTimer):
    def __init__(self, interval):
        super().__init__(interval, self.on_timer)
        self.m_show_procgress = False
    
    def show_progress(self, visible):
        self.m_show_procgress = visible

    async def on_timer(self):
        if self.m_show_procgress:
            print('.', end='', flush=True)


async def sg_upgrade_task(address: str, options) -> int:
    file_path = options.file or options.ais_file
    allow_ais = file_path is not options.file

    if not os.path.isfile(file_path):
        print('  *** Can not open file "{}".'.format(file_path))
        return -1
    
    timer = SgUpgradeTimer(0.2)
    parser = SgParser()
    try:
        try:
            # Open TCP connection.
            await parser.connect(address)
        except OSError:
            print('  *** Can not connect to the device "{}".'.format(address))
            return -1

        # Create AES crypter.
        parser.set_password(options.password)

        try:
            dev_info = await parser.request(dict(cmd='get_device_info'))
            if dev_info['err_code'] != 0:
                raise OSError()
        except (OSError, EOFError, ValueError) as e:
            print('  *** Can not get device info.')
            if not isinstance(e, OSError):
                print('  Please input a valid password with "-p" option.')
            return -2

        print('  Device info:')
        print('    Product ID:         {}'.format(dev_info['product_id']))
        print('    Device ID:          {}'.format(dev_info['device_id']))
        print('    Device Name:        {}'.format(dev_info['device_name']))
        print('    Firmware Version:   {}'.format(dev_info['fw_version']))
        print('    Firmware Timestamp: {}'.format(dev_info['fw_timestamp']))
        print('')

        with open(file_path, 'rb') as f:
            fw_data = f.read()
        try:
            fw_parser = SgFwParser()
            fw_info = fw_parser.parse_binary(fw_data)
            app = next(filter(lambda x: x['name'] == 'APP', fw_info['sections']))
            product_id = fw_info['product_id']
            fw_version = fw_info['fw_version']
            fw_addr = app['store_addr']
            fw_chksum = app['crc16']
            fw_data = app['binary']

            print('  Firmware info:')
            print('    Product ID:         {}'.format(product_id))
            print('    Product Name:       {}'.format(fw_info['product_name']))
            print('    Firmware Version:   {}'.format(fw_version))
            print('    Firmware Timestamp: {}'.format(fw_info['fw_timestamp']))
            print('')
        except:
            if not allow_ais:
                print('  *** Invalid firmware file.')
                raise
            # For .ais file, no product info.
            product_id = dev_info['product_id']
            fw_version = '1.0.0'
            fw_addr = 0
            fw_chksum = crcmod.predefined.mkPredefinedCrcFun('modbus')(fw_data)

        # Check product ID.
        if product_id != dev_info['product_id']:
            print('  *** Product ID does not match.')
            raise ValueError()

        if options.require_confirm or allow_ais:
            if allow_ais:
                print('Burn .ais file directly is dangerous!')
            if not query_yes_no('Are you sure you want to upgrade?', 'no' if allow_ais else 'yes'):
                return 1

        # Start upgrade.
        sid = random.randint(1, 0xFFFFFFFF)
        rsp = await parser.request(dict(
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
                print('.', end='', flush=True)
            size = min(trunk_size, len(fw_data) - offset)
            rsp = await parser.request(dict(
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
        print('  Burning .', end='', flush=True)
        timer.show_progress(True)
        rsp = await parser.request(dict(
            cmd='fw_data',
            session_id=sid,
            offset=offset,
            eos=1,
        ))
        timer.show_progress(False)
        print('', flush=True)
        if rsp['err_code'] != 0:
            print('  ***', rsp['err_msg'])
            raise IOError()

        # Reboot device.
        rsp = await parser.request(dict(cmd='reboot'))
        if rsp['err_code'] == 0:
            print('  Rebooting ...')
        else:
            print('  Please power off the device.')
        return 0
    except (OSError, IOError, EOFError, ValueError):
        return -3
    finally:
        timer.cancel()
        parser.close_streams()


def sg_upgrade_main(dev_ip: str, options) -> int:
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(
        sg_upgrade_task(dev_ip, options),
    )
    status, = loop.run_until_complete(tasks)
    return status


if __name__ == "__main__":
    try:
        from optparse import OptionParser
        parser = OptionParser(usage=('Usage: %prog -f <FILE> [options] <Device Address>\n\n' + SG_UPGRADE_VERINFO))
        parser.get_option("-h").help = "Show this help message and exit."
        parser.add_option("--version",
                          action="store_true", default=False, dest="show_version",
                          help="Show version.")
        parser.add_option("-f", "--file",
                          action="store", type="string", default=None, dest="file",
                          help="Firmware file (.fw)")
        parser.add_option("-p", "--password",
                          action="store", type="string", default=SG_DEF_PASSWORD, dest="password",
                          help='Device password, default is "{}".'.format(SG_DEF_PASSWORD))
        parser.add_option("-y",
                          action="store_false", default=True, dest="require_confirm",
                          help='Suppresse prompting to confirm upgrade.')
        parser.add_option("--ais-file",
                          action="store", type="string", default=None, dest="ais_file",
                          help="Flash image file (.ais)")
        (options, args) = parser.parse_args()

        if options.show_version:
            print(SG_UPGRADE_VERINFO)
            sys.exit(0)

        if (not options.file and not options.ais_file) or len(args) != 1:
            parser.print_help()
            sys.exit(1)

        status = sg_upgrade_main(args[0], options)
        sys.exit(status)
    except KeyboardInterrupt:
        print('^C')
        sys.exit(-100)
