#!/usr/bin/python2
from urllib2 import urlopen, HTTPError
import os

base_url = 'http://download.tomtom.com/sweet/fitness/Firmware'
fwconfig = '/FirmwareVersionConfigV2.xml'

product_ids = (
    'E9030000', #Runner
    'EA030000', #Multi-Sport
)

# http://us.support.tomtom.com/app/answers/detail/a_id/17441/~/what%E2%80%99s-new-in-the-latest-software-for-my-runner-or-multi-sport-watch%3F
fw_vers = ['1_8_25', '1_8_19', '1_8_5', '1_7_25', '1_7_22', '1_7_16', '1_6_13', '1_5_4', '1_5_1', '1_4_1', '1_3_1', '1_2_0']
ble_fw_vers = map(str, range(22,0,-1))

files = (
    '0x000000F0', # FILE_SYSTEM_FIRMWARE
    '0x00010200', # FILE_GPS_FIRMWARE
    '0x00850000', # FILE_MANIFEST1
    '0x00850001', # FILE_MANIFEST2
) + tuple('0x008100%02X'%ii for ii in range(32)) # localization files (0,1,...)

######################################################################

def mkdir_p(path):
    comp, rest = [], path
    while rest:
        rest, last = os.path.split(rest)
        comp.append(last)
    comp.reverse()

    for ii in range(len(comp)):
        partial = os.path.join(*comp[:ii+1])
        if not os.path.isdir(partial):
            os.mkdir(partial)

def download_file(url, p):
    if os.path.exists(p):
        print "%s exists, skipping download" % p
    else:
        print "downloading %s from %s..." % (p, url)
        try:
            data = urlopen(url).read()
        except HTTPError as e:
            print e.code, e.reason
        else:
            mkdir_p(os.path.dirname(p))
            open(p,"wb").write(data)

for pid in product_ids:
    for bfwv in ble_fw_vers:
        p = os.path.join(pid, 'BLE', bfwv, '0x00000012')
        url = base_url + '/%s/BLE/%s/0x00000012'%(pid,bfwv)
        download_file(url, p)
    for fwv in fw_vers:
        for f in files:
            p = os.path.join(pid, fwv, f)
            url = base_url + '/%s/%s/%s'%(pid,fwv,f)
            download_file(url, p)
