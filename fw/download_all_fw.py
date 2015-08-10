#!/usr/bin/python2
import requests, os, hashlib, time

base_url = 'http://download.tomtom.com/sweet/fitness/Firmware'
fwconfig = '/FirmwareVersionConfigV2.xml'

product_ids = (
    ('E9030000', 'Runner'),
    ('EA030000', 'Multi-Sport'),
    ('EB030000', 'Runner Cardio'),
    ('EC030000', 'Multi-Sport Cardio'),
)

# http://us.support.tomtom.com/app/answers/detail/a_id/17441/~/what%E2%80%99s-new-in-the-latest-software-for-my-runner-or-multi-sport-watch%3F
fw_vers = ['1_2_0', '1_3_1', '1_4_1', '1_5_1', '1_5_4', '1_6_13', '1_7_16', '1_7_22', '1_7_25', '1_8_5', '1_8_19', '1_8_25', '1_8_32', '1_8_34', '1_8_35', '1_8_42']
ble_fw_vers = map(str, range(0, 24+1))

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

def download_file(sess, url, p, cache):
    print "  downloading %s from %s..." % (p, url),
    r = sess.head(url)
    if r.ok:
        md5 = r.headers.get('etag')[1:-1].split(':')[0]
        if md5 not in cache:
            if os.path.exists(p): os.unlink(p)
            mkdir_p(os.path.dirname(p))
            open(p, 'wb').write( sess.get(url).content )
            print "saved"
            cache[md5] = p
        else:
            if cache[md5]==p:
                print "already in cache"
            else:
                if os.path.exists(p): os.unlink(p)
                dest = os.path.relpath(cache[md5], os.path.dirname(p))
                mkdir_p(os.path.dirname(p))
                os.symlink(dest, p)
                print "symlinked to %s" % dest
    else:
        print "not found, skipping."

print "Building cache of MD5s for files we already have..."
cache = {}
for dp, dn, fns in os.walk('all_fw'):
    for fn in fns:
        fp = os.path.join(dp, fn)
        if not os.path.islink(fp):
            md5 = hashlib.new('md5', open(os.path.join(dp, fn), "rb").read()).hexdigest()
            cache[md5] = fp
            #print "  %s: %s" % (md5, fp)

#import pprint
#pprint.pprint( cache )
#raise SystemExit

s = requests.Session()
for pid, product in product_ids:
    print "%s (%s):" % (product, pid)
    for bfwv in ble_fw_vers:
        p = os.path.join('all_fw', pid, 'BLE', bfwv, '0x00000012')
        url = base_url + '/%s/BLE/%s/0x00000012'%(pid,bfwv)
        while True:
            try:
                download_file(s, url, p, cache)
                break
            except requests.exceptions.ConnectionError:
                print "Waiting 5s..."
                time.sleep(5)

    for fwv in fw_vers:
        for f in files:
            p = os.path.join('all_fw', pid, fwv, f)
            url = base_url + '/%s/%s/%s'%(pid,fwv,f)
            while True:
                try:
                    download_file(s, url, p, cache)
                    break
                except requests.exceptions.ConnectionError:
                    print "Waiting 5s..."
                    time.sleep(5)
