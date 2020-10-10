#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import crcmod
import struct
import json
import time
import random
import datetime,os


DURATION = 10.0 # in seconds
DEVICE_IP = "192.168.5.32"
LOCAL_IP = "192.168.2.6"
LOCAL_PORT = 2229


def CreateDir():
    print('CreateDir')
    now_date = datetime.datetime.now().strftime('%Y_%m_%d')
    now_time = datetime.datetime.now().strftime('%H_%M_%S')
    pwd = '/Users/alexis/Desktop/pickup-test' + '/' + now_date + '/' + now_time + '/'
    os.makedirs(pwd)

    for i in range(9):
        a[i] = open('%s' % pwd + 'org_channel%d.pcm' % (i + 1), 'wb')

def test_build_packet(req, packet_type=1):
    if isinstance(req, dict):
        payload = json.dumps(req).encode()
    elif isinstance(req, bytes):
        payload = req
    else:
        assert False
    header = struct.pack('<HHB',
        0x7E7E,
        len(payload) + 3,
        packet_type,
    )
    crc = crcmod.predefined.Crc('modbus')
    crc.update(header[4:])
    crc.update(payload)
    chksum = struct.pack('<H', crc.crcValue)
    return header, payload, chksum


def test_net_request(req, packet_type=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((DEVICE_IP, 2228))
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    header, payload, chksum = test_build_packet(req, packet_type)
    print('request: header =', header, ', checksum =', chksum)
    print(req)
    s.sendall(header)
    s.sendall(payload)
    s.sendall(chksum)
    s.close()


def test_main():
    test_net_request(dict(cmd='set_device_info', device_id='xxxxxx'))
    test_net_request(dict(cmd='get_device_info'))
    test_net_request(dict(cmd='set_audio', output_gain=35))
    test_net_request(dict(cmd='get_audio'))
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((LOCAL_IP, LOCAL_PORT))
    
    # Create a new session ID
    session_id = random.randint(1, 0xFFFFFFFF)

    test_net_request(dict(
        cmd='open_audio',
        session_id=session_id,
        server_addr='{}:{}'.format(LOCAL_IP, LOCAL_PORT),
        output_channel=9,
        audio_encoder=3, # SG_AUDIO_PCMS24LE
        audio_channels=1, # mono
        audio_frame_size=320, # samples per frame
        audio_sample_rate=16000,
        audio_bitrate=0, # no use for PCM
        retrans_timeout=1000, # threshold of retransmission timeout, in milliseconds
    ))
    
    packets = {}
    
    # Variables to calculate the actual audio frame size
    samples_per_frame = None
    fragments_per_frame = 0
    frag_size = 0
    frag_sn = -1
    frag_ts = -1

    recv_data = b''

    with open("pickup.pcm", "wb") as f:
        current_sn = None
        now = time.time()
        n = 0
        while now + DURATION >= time.time():
            (rsp, addr) = s.recvfrom(1500)
            n += 1
            
            if n % 100 == 0 and current_sn is not None:
                # Send ACK
                ack = struct.pack('<IHHI', session_id, 1, 0, current_sn)
                #s.sendto(b''.join(test_build_packet(ack, packet_type=4)), addr)

            magic, len_, type_ = struct.unpack('<HHB', rsp[:5])
            assert len_ + 4 == len(rsp)
            crc = crcmod.predefined.Crc('modbus')
            crc.update(rsp[4:])
            assert crc.crcValue == 0
            
            audio_pkt = rsp[5:-2]
            (sid, sn, timestamp, reserved, output_channel, audio_encoder, 
             audio_channels, audio_sample_rate, audio_frame_size, payload_size) = struct.unpack(
                '<IIQBBBBIHH', audio_pkt[:28]
            )
            assert 28 + payload_size == len(audio_pkt)
            
            # Session ID must match.
            if sid != session_id:
                continue
            
            # Here, we calculate the actual frame size.
            # A frame may be splitted into several fragments, and each fragment has the same timestamp.
            if samples_per_frame is None:
                if frag_sn + 1 == sn:
                    if frag_size == 0:
                        if frag_ts != timestamp:
                            frag_size = audio_frame_size
                            fragments_per_frame = 1
                    elif frag_ts == timestamp:
                        frag_size += audio_frame_size
                        fragments_per_frame += 1
                    else:
                        samples_per_frame = frag_size
                        print("Samples per frame:", samples_per_frame, ", fragments:", fragments_per_frame)
                else:
                    frag_size = 0
                frag_sn = sn
                frag_ts = timestamp

            if current_sn is None:
                # The first frame.
                current_sn = sn
            else:
                delta = (sn - current_sn) & 0xFFFFFFFF
                if delta & 0x80000000:
                    delta -= 0x100000000
                if delta == 1:
                    # Sn is continuous.
                    current_sn += 1
                elif delta < 0:
                    print("****************** delta", delta, sn)
                    continue
                elif delta > 0:
                    print("****************** delta", delta, sn)
                    continue

            print(sid, sn, timestamp / 1000, output_channel, audio_encoder,
                audio_channels, audio_sample_rate, audio_frame_size, payload_size)

            recv_data = audio_pkt[-payload_size:]
            pData = bytearray(payload_size + 1)

            for i in range(audio_frame_size):
                for j in range(output_channel):
                    pData[3 * audio_frame_size * j + 3 * i] = (recv_data[3 * output_channel * i + 3 * j ] & 0xFF)
                    pData[3 * audio_frame_size * j + 3 * i + 1] = (recv_data[3 * output_channel * i + 3 * j + 1] & 0xFF)
                    pData[3 * audio_frame_size * j + 3 * i + 2] = (recv_data[3 * output_channel * i + 3 * j + 2] & 0xFF)
                    if i == (audio_frame_size-1):
                        tempData = pData[3 * audio_frame_size * j: 3 * audio_frame_size * j + audio_frame_size * 3]
                        a[j].write(tempData)

            # f.write(audio_pkt[-payload_size:])

    test_net_request(dict(cmd='close_audio', session_id=session_id))


if __name__ == "__main__":
    a = {}
    CreateDir()
    test_main()
