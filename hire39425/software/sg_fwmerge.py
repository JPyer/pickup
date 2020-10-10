#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
import json
import time
import hashlib
import crcmod
from Crypto.Cipher import AES
from typing import Any, List, Tuple, Dict, Coroutine, Union, Optional

__all__ = ('SgFwParser',)

SG_FWMERGE_VERSION = "1.0.0"
SG_FWMERGE_VERINFO = "Firmware merge tool v{} for SG+ Pickup\n".format(SG_FWMERGE_VERSION) + \
                     "Copyright (C) Focal Acoustics, 2020-2021."

################################################################################
#
# Firmware header:
#   0:  Magic Word (char[4]):           b"FAFW"
#   4:  File Size (int32_t):            multiples of 16
#   8:  Info Size (int32_t):
#  12:  padding (uint32_t):             0
#  16:  SH256 Hash (uint8_t[32]):       file[0:16] + file[48:]
#  48:  File Info (char[<Info Size>]):  Json text
#
# File Info:
#   {
#       "product_id":       "FA100AA800",
#       "product_name":     "Focal Acoustics SG+ Pickup",
#       "fw_version":       "x.x.x.x",
#       "fw_timestamp":     "yyyy-MM-dd hh:mm:ss",
#       "sections": [
#           {
#               "name":             "APP",
#               "offset":           (int32_t) offset in the file,
#               "size":             (int32_t) section size in bytes,
#               "crc32":            (uint32_t) crcmod.mkPredefinedCrcFun('crc-32'), zlib.crc32()
#               "crc16":            (uint16_t) crcmod.mkPredefinedCrcFun('modbus')
#               "storage_type":     "RAM" / "FLASH" / "FILE",
#               "store_addr":       (int32_t) address in the target storage memory,
#               "load_addr":        (int32_t) address in the load memory,
#           }
#       ]
#   }
#
################################################################################


class SgFwParser:
    FW_MAGIC = b'FAFW'
    FW_MAGIC1 = b'JUEB6oqvahK0zvtinbep34TU'
    FW_MAGIC2 = b'n39Mz9C3k284XHI7vbgd7tYZ'

    def __init__(self):
        pass

    def merge(self, *,
              input_file: str,
              output_file: str,
              product_id: str,
              product_name: str,
              fw_version: str,
              storage_type: str = "FLASH",
              store_addr: int = 0,
              load_addr: int = 0,
              alignment: int = 16) -> int:

        offset = 2048
        header_size = 48
        info_max_size = offset - header_size

        # Sections.
        section_infos = []
        section_contents = []
        crc32_hasher = crcmod.predefined.Crc('crc-32')
        crc16_hasher = crcmod.predefined.Crc('modbus')

        # App section.
        with open(input_file, "rb") as f:
            section_content = f.read()
        section_size = (len(section_content) + alignment - 1) // alignment * alignment
        section_padding = b'\0' * (section_size - len(section_content))
        m1 = crc32_hasher.new()
        m1.update(section_content)
        m1.update(section_padding)
        m2 = crc16_hasher.new()
        m2.update(section_content)
        m2.update(section_padding)
        section_info = {
            'name': 'APP',
            'offset': offset,
            'size': section_size,
            'crc32': m1.crcValue,
            'crc16': m2.crcValue,
            'storage_type': storage_type,
            'store_addr': store_addr,
            'load_addr': load_addr,
        }
        section_infos.append(section_info)
        section_contents.append(section_content)
        offset += section_size

        # Build info in JSON format.
        info = {
            'product_id': product_id,
            'product_name': product_name,
            'fw_version': fw_version,
            'fw_timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'sections': section_infos,
        }
        info_content = json.dumps(info).encode(encoding='utf-8')
        info_size = len(info_content)
        file_size = offset
        if info_size > info_max_size:
            raise ValueError('The size of the file info "{}" is too large.'.format(info_size))
        # Write file content.
        buf = memoryview(bytearray(offset))
        # header
        struct.pack_into('<4sII', buf, 0, self.FW_MAGIC, file_size, info_size)
        # info
        buf[header_size : header_size + info_size] = info_content
        # sections
        for i, section in enumerate(section_infos):
            content = section_contents[i]
            buf[section['offset'] : section['offset'] + len(content)] = content
        # SHA256 hash
        m = hashlib.sha256()
        m.update(buf[0:16])
        m.update(buf[48:])
        buf[16:48] = m.digest()
        # AES128 Encryptor
        m = hashlib.sha256()
        m.update(m.digest())
        m.update(self.FW_MAGIC1)
        m.update(self.FW_MAGIC)
        m.update(self.FW_MAGIC2)
        aes = AES.new(m.digest(), AES.MODE_CBC, hashlib.sha256(m.digest()).digest()[:16])
        with open(output_file, "wb") as f:
            f.write(buf[:48])
            f.write(aes.encrypt(buf[48:]))
        return 0

    def parse_file(self, file_path: str):
        with open(file_path, 'rb') as f:
            content = f.read()
        return self.parse_binary(content)

    def parse_binary(self, content: Union[bytes, bytearray, memoryview]):
        magic, file_size, info_size = struct.unpack_from('<4sII', content, 0)
        if magic != self.FW_MAGIC or file_size < 48 or file_size != len(content) or info_size > file_size:
            raise ValueError('invalid firmware')
        
        # AES128 Decryptor
        m = hashlib.sha256()
        m.update(m.digest())
        m.update(self.FW_MAGIC1)
        m.update(self.FW_MAGIC)
        m.update(self.FW_MAGIC2)
        aes = AES.new(m.digest(), AES.MODE_CBC, hashlib.sha256(m.digest()).digest()[:16])
        data = aes.decrypt(content[48:])
        
        # Verify SHA256 hash
        m = hashlib.sha256()
        m.update(content[0:16])
        m.update(data)
        if content[16:48] != m.digest():
            raise ValueError('CRC error')

        # File info
        info = json.loads(data[:info_size].decode(encoding='utf-8'))

        # Sections
        for section in info['sections']:
            offset = section['offset'] - 48
            binary = data[offset : offset + section['size']]
            section['binary'] = binary
            if crcmod.predefined.mkPredefinedCrcFun('crc-32')(binary) != section['crc32']:
                raise ValueError('CRC error')
        return info


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage=('Usage: %prog <input file> -o <output file> [options]\n\n' + SG_FWMERGE_VERINFO))
    parser.get_option('-h').help = 'Show this help message and exit.'
    parser.add_option('--version',
                        action='store_true', default=False, dest='show_version',
                        help='Show version.')
    parser.add_option('-o', '--output-file',
                        action='store', type='string', default=None, dest='output_file',
                        help='Product ID.')
    parser.add_option('--pi', '--product-id',
                        action='store', type='string', default=None, dest='product_id',
                        help='Product ID.')
    parser.add_option('--pn', '--product-name',
                        action='store', type='string', default=None, dest='product_name',
                        help='Product name.')
    parser.add_option('--fv', '--fw-version',
                        action='store', type='string', default=None, dest='fw_version',
                        help='Firmware version.')
    parser.add_option('--storage-type',
                        action='store', type='string', default='FLASH', dest='storage_type',
                        help='Storage type, "RAM" / "FLASH" / "FILE".')
    parser.add_option('--store-addr',
                        action='store', type='int', default=0, dest='store_addr',
                        help='Store address.')
    parser.add_option('--load-addr',
                        action='store', type='int', default=0, dest='load_addr',
                        help='Load address in RAM.')
    parser.add_option('--alignment',
                        action='store', type='int', default=16, dest='alignment',
                        help='Binary alignment.')
    (options, args) = parser.parse_args()

    if options.show_version:
        print(SG_FWMERGE_VERINFO)
        sys.exit(0)

    if (not options.product_id or
            not options.product_name or
            not options.fw_version or
            len(args) != 1):
        parser.print_help()
        sys.exit(1)

    input_file = args[0]
    output_file = options.output_file if options.output_file else (os.path.splitext(input_file)[0] + '.fw')
    parser = SgFwParser()
    parser.merge(
        input_file=input_file,
        output_file=output_file,
        product_id=options.product_id,
        product_name=options.product_name,
        fw_version=options.fw_version,
        storage_type=options.storage_type,
        store_addr=options.store_addr,
        load_addr=options.load_addr,
        alignment=options.alignment,
    )
    sys.exit(0)
