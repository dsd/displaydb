import sys
import struct
import hashlib

def hexstr(string):
    return ' '.join(x.encode('hex') for x in string)

def bswap16(x):
    return ((x & 0xff) << 8) | (x >> 8)

def edidparse(data, fd):
    fmt = "<8sHHLBBBBBBBBBBBBBHHHBBB16s18s18s18s18sBB"
    hdr, mfgid, productcode, sn, mfgweek, mfgyear, edidver, edidrev, vip, max_h, max_v, gamma, features, rglsb, bwlsb, rxmsb, rymsb, gxymsb, bxymsb, wpmsb, et1, et2, et3, sti, desc1, desc2, desc3, desc4, nr_exts, csum = struct.unpack(fmt, data[0:128])

    if hdr == "\x00\xff\xff\xff\xff\xff\xff\x00":
        print >> fd, "Fixed header OK"
    else:
        print >> fd, "Bad fixed header"

    mfgid = bswap16(mfgid)
    mfg1 = (mfgid >> 10) & 0x1f
    mfg2 = (mfgid >> 5) & 0x1f
    mfg3 = mfgid & 0x1f
    mfg1 += ord('A') - 1
    mfg2 += ord('A') - 1
    mfg3 += ord('A') - 1
    print >> fd, "Manufacturer ID: " + chr(mfg1) + chr(mfg2) + chr(mfg3)

    print >> fd, "Product code", productcode
    print >> fd, "Serial number", sn
    print >> fd, "Manufactured week " + str(mfgweek) + ", " + str(1990 + mfgyear)
    print >> fd, "EDID version " + str(edidver) + "." + str(edidrev)
    print >> fd

    if vip & 0x80:
        print >> fd, "Digital input"
        if vip & 0x1:
            print >> fd, "Compatible with VESA DFP 1.x TMDS CRGB, 1 pixel per clock, up to 8 bits per color, MSB aligned"
    else:
        print >> fd, "Analog input"
        print >> fd, "Video white and sync levels:", hex((vip >> 5) & 0x3)
        if vip & 0x1:
            print >> fd, "VSync pulse must be serrated when composite or sync-on-green is used."
        if vip & 0x2:
            print >> fd, "Sync on green supported"
        if vip & 0x4:
            print >> fd, "Composite sync (on HSync) supported"
        if vip & 0x8:
            print >> fd, "Separate sync supported"
        if vip & 0x10:
            print >> fd, "Blank-to-black setup (pedestal) expected"
        # also fix features parsing for analog display type

    print >> fd, "Max size: %dcm x %dcm" % (max_h, max_v)
    print >> fd, "Gamma", hex(gamma)

    if features & 0x1:
        print >> fd, "GTF supported"
    if features & 0x2:
        print >> fd, "Preferred timing mode specified in descriptor block 1."
    if features & 0x4:
        print >> fd, "Standard sRGB colour space"
    if features & 0x20:
        print >> fd, "DPMS active-off supported"
    if features & 0x40:
        print >> fd, "DMPS suspend supported"
    if features & 0x80:
        print >> fd, "DPMS standby supported"

    dtype = (features & 0x18) >> 3
    if vip & 0x80:
        print >> fd, "Digital display type %d:" % dtype,
        if dtype == 0:
            print >> fd, "RGB444"
        elif dtype == 1:
            print >> fd, "RGB444 + YCrCb444"
        elif dtype == 2:
            print >> fd, "RGB444 + YCrCb422"
        elif dtype == 3:
             print >> fd, "RGB444 + YCrCb444 + YCrCb422"
    else:
        print >> fd, "Analog display type %d:" % dtype,
        if dtype == 0:
            print >> fd, "Monochrome/greyscale"
        elif dtype == 1:
            print >> fd, "RGB"
        elif dtype == 2:
            print >> fd, "Non-RGB"
        elif dtype == 3:
            print >> fd, "Undefined"
    print >> fd

    print >> fd, "CHROMACITY"
    print >> fd, "Red and green least significant bits", hex(rglsb)
    print >> fd, "Blue and white least significant 2 bits", hex(bwlsb)
    print >> fd, "Red x most significant 8 bits", hex(rxmsb)
    print >> fd, "Red y most significant 8 bits", hex(rymsb)
    print >> fd, "Green x and y most significant 8 bits", hex(gxymsb)
    print >> fd, "Blue x and y most significant 8 bits", hex(bxymsb)
    print >> fd, "Default white point x and y most significant 8 bits", hex(wpmsb)
    print >> fd

    print >> fd, "ESTABLISHED TIMINGS %x %x %x" % (et1, et2, et3)
    if et1 & 0x1:
        print >> fd, "800x600 @ 60 Hz"
    if et1 & 0x2:
        print >> fd, "800x600 @ 56 Hz"
    if et1 & 0x4:
        print >> fd, "640x480 @ 75 Hz"
    if et1 & 0x8:
        print >> fd, "640x480 @ 72 Hz"
    if et1 & 0x10:
        print >> fd, "640x480 @ 67 Hz"
    if et1 & 0x20:
        print >> fd, "640x480 @ 60 Hz"
    if et1 & 0x40:
        print >> fd, "720x400 @ 88 Hz"
    if et1 & 0x80:
        print >> fd, "720x400 @ 70 Hz"
    if et2 & 0x1:
        print >> fd, "1280x1024 @ 75 Hz"
    if et2 & 0x2:
        print >> fd, "1024x768 @ 75 Hz"
    if et2 & 0x4:
        print >> fd, "1024x768 @ 72 Hz"
    if et2 & 0x8:
        print >> fd, "1024x768 @ 60 Hz"
    if et2 & 0x10:
        print >> fd, "1024x768 @ 87 Hz interlaced"
    if et2 & 0x20:
        print >> fd, "832x624 @ 75 Hz"
    if et2 & 0x40:
        print >> fd, "800x600 @ 75 Hz"
    if et2 & 0x80:
        print >> fd, "800x60 @ 72 Hz"
    if et3 & 0x80:
        print >> fd, "1152x870 @ 75 Hz"
    if et3 & 0x7f:
        print >> fd, "MFG-specific:", hex(et3 & 0x7f)
    print >> fd
    
    print >> fd, "STANDARD TIMING INFO"
    for i in range(0, 16, 2):
        b0 = ord(sti[i])
        b1 = ord(sti[i + 1])
        if b0 == 1 and b1 == 1:
            continue
        xres = (b0 + 31) * 8
        ratio = b1 >> 6
        if ratio == 0:
            frac = 16/10.
        elif ratio == 1:
            frac = 4/3.
        elif ratio == 2:
            frac = 5/4.
        if ratio == 3:
            frac = 16/9.
        yres = int(xres / frac)
        freq = (b1 & 0x3f) + 60
        print >> fd, "%dx%d @ %dHz" % (xres, yres, freq)
    print >> fd

    parse_desc(desc1, fd)
    parse_desc(desc2, fd)
    parse_desc(desc3, fd)
    parse_desc(desc4, fd)

    print >> fd, "Number of extensions:", nr_exts
    print >> fd, "Checksum", hex(csum)
    print >> fd

    if nr_exts == 0:
        return

    if nr_exts != 1:
        print >> fd, "FIXME can only handle 1 extension"
        return

    tag = ord(data[128])
    if tag != 2:
        print >> fd, "Unhandled extension %d", tag
        return
    
    data = data[128:]
    tag, revno, dtdstart, dtdinfo = struct.unpack("<BBBB", data[0:4])
    print >> fd, "CEA EDID Timing Extension revision", revno
    print >> fd, "DTDs begin at", dtdstart
    print >> fd, "%d native formats in DTDs in this block" % (dtdinfo & 0xf)
    if dtdinfo & 0x10:
        print >> fd, "Display supports YCbCr 4:2:2"
    if dtdinfo & 0x20:
        print >> fd, "Display supports YCbCr 4:4:4"
    if dtdinfo & 0x40:
        print >> fd, "Display supports basic audio"
    if dtdinfo & 0x80:
        print >> fd, "Display supports underscan"
    print >> fd
    
    if dtdstart > 4: # we have some Data Blocks
        i = 4
        while i < dtdstart:
            i += parse_data_block(data[i:], fd)
    
    if dtdstart > 0:
        i = dtdstart
        while data[i:i + 2] != "\x00\x00" and len(data[i:]) >= 18:
            parse_desc(data[i:i + 18], fd)
            i += 18
    
    print >> fd, "Checksum: %x" % ord(data[127])
    print >> fd, "CEA block md5sum: %s" % hashlib.md5(data).hexdigest()

def parse_detailed(desc, fd):
    fmt = "<H16B"
    pixclk, hactive, hblank, hextra, vactive, vblank, vextra, hsyncoff, hsyncwidth, vsync, syncextra, hdisp, vdisp, dispextra, hborder, vborder, features = struct.unpack(fmt, desc)

    hactive = (hextra & 0xf0) << 4 | hactive
    hblank = (hextra & 0xf) << 8 | hblank
    hsyncoff = (syncextra & 0xc0) << 2 | hsyncoff
    hsyncwidth = (syncextra & 0x30) << 4 | hsyncwidth
    htotal = hactive + hblank

    vactive = (vextra & 0xf0) << 4 | vactive
    vblank = (vextra & 0xf) << 8 | vblank
    vsyncoff = (syncextra & 0x0c) << 2 | (vsync & 0xf0) >> 4
    vsyncwidth = (syncextra & 0x03) << 4 | (vsync & 0xf)
    vtotal = vactive + vblank

    print >> fd, "Detailed timing:", hexstr(desc)
    print >> fd, "Visible: %dx%d" % (hactive, vactive)
    print >> fd, "Horizontal blanking: %dpx total, sync pulse %dpx at offset %d" % (hblank, hsyncwidth, hsyncoff)
    print >> fd, "Vertical blanking: %dpx total, sync pulse %dpx at offset %d" % (vblank, vsyncwidth, vsyncoff)
    print >> fd, "Total: %dx%d" % (htotal, vtotal)
    print >> fd, "Pixel clock: %f MHz (vertical refresh: %f Hz)" % (pixclk / 100., float(pixclk * 10000)/(htotal * vtotal))
    print >> fd

def parse_desc(desc, fd):
    if desc[0:2] != "\x00\x00":
        parse_detailed(desc, fd)
        return

    if desc[2] != "\x00" or desc[4] != "\x00":
        print >> fd, "Non-zero bytes :/"

    dtype = ord(desc[3])
    print >> fd, "Other descriptor type %x" % dtype
    extra = desc[5:18]
    
    if dtype == 0xff:
        print >> fd, "Serial number", extra.split("\n")[0]
    elif dtype == 0xf3:
        print >> fd, "Unspecified text", extra.split("\n")[0]
    elif dtype == 0xfd:
        print >> fd, "Monitor range limits"
        minv, maxv, minh, maxh, maxpix, etitype, reserved, starfreq, gtfc, gtfm, gtfk, gtfj = struct.unpack("<9BHBB", extra)
        print >> fd, "Vertical field rate: %dHz - %dHz" % (minv, maxv)
        print >> fd, "Horizontal field rate: %dkHz - %dkHz" % (minh, maxh)
        print >> fd, "Maximum pixel clock: %dMHz" % (maxpix * 10)
        if etitype == 0:
            print >> fd, "No extended timing info"
            if desc[11:18] != "\x0a      ":
                print >> fd, "Bad padding", hexstr(desc[11:18])
        elif etitype == 2:
            if reserved != 0:
                print >> fd, "Bad reserved byte"
            print >> fd, "Start freq for secondary curve: %dkHz" % (startfreq * 2)
            print >> fd, "GTF C=%d M=%d K=%d J=%d" % ((gtfc / 2.), gtfm, gtfk, (gtfj / 2.))
        else:
            print >> fd, "Unrecognised extended timing info type", etitype
    elif dtype == 0xfc:
        print >> fd, "Monitor name", extra.split("\x0a\x20\x20")[0]
    elif dtype == 0xfb:
        print >> fd, "Additional WP data", hexstr(extra)
    elif dtype == 0xfa:
        print >> fd, "Additional standard timing info", hexstr(extra)
    else:
        print >> fd, "Unrecognised other descriptor", hexstr(desc)

    print >> fd

cea_display_modes=(
    "Invalid mode 0",
    "DMT0659   4:3                640x480p @ 59.94/60Hz",
    "480p      4:3                720x480p @ 59.94/60Hz",
    "480pH    16:9                720x480p @ 59.94/60Hz",
    "720p     16:9               1280x720p @ 59.94/60Hz",
    "1080i    16:9              1920x1080i @ 59.94/60Hz",
    "480i      4:3          720(1440)x480i @ 59.94/60Hz",
    "480iH    16:9          720(1440)x480i @ 59.94/60Hz",
    "240p      4:3          720(1440)x240p @ 59.94/60Hz",
    "240pH    16:9          720(1440)x240p @ 59.94/60Hz",
    "480i4x    4:3             (2880)x480i @ 59.94/60Hz",
    "480i4xH  16:9             (2880)x480i @ 59.94/60Hz",
    "240p4x    4:3             (2880)x240p @ 59.94/60Hz",
    "240p4xH  16:9             (2880)x240p @ 59.94/60Hz",
    "480p2x    4:3               1440x480p @ 59.94/60Hz",
    "480p2xH  16:9               1440x480p @ 59.94/60Hz",
    "1080p    16:9              1920x1080p @ 59.94/60Hz",
    "576p      4:3                720x576p @ 50Hz",
    "576pH    16:9                720x576p @ 50Hz",
    "720p50   16:9               1280x720p @ 50Hz",
    "1080i25  16:9              1920x1080i @ 50Hz*",
    "576i      4:3          720(1440)x576i @ 50Hz",
    "576iH    16:9          720(1440)x576i @ 50Hz",
    "288p      4:3          720(1440)x288p @ 50Hz",
    "288pH    16:9          720(1440)x288p @ 50Hz",
    "576i4x    4:3             (2880)x576i @ 50Hz",
    "576i4xH  16:9             (2880)x576i @ 50Hz",
    "288p4x    4:3             (2880)x288p @ 50Hz",
    "288p4xH  16:9             (2880)x288p @ 50Hz",
    "576p2x    4:3               1440x576p @ 50Hz",
    "576p2xH  16:9               1440x576p @ 50Hz",
    "1080p50  16:9              1920x1080p @ 50Hz",
    "1080p24  16:9              1920x1080p @ 23.98/24Hz",
    "1080p25  16:9              1920x1080p @ 25Hz",
    "1080p30  16:9              1920x1080p @ 29.97/30Hz",
    "480p4x    4:3             (2880)x480p @ 59.94/60Hz",
    "480p4xH  16:9             (2880)x480p @ 59.94/60Hz",
    "576p4x    4:3             (2880)x576p @ 50Hz",
    "576p4xH  16:9             (2880)x576p @ 50Hz",
    "1080i25  16:9  1920x1080i(1250 Total) @ 50Hz*",
    "1080i50  16:9              1920x1080i @ 100Hz",
    "720p100  16:9               1280x720p @ 100Hz",
    "576p100   4:3                720x576p @ 100Hz",
    "576p100H 16:9                720x576p @ 100Hz",
    "576i50    4:3          720(1440)x576i @ 100Hz",
    "576i50H  16:9          720(1440)x576i @ 100Hz",
    "1080i60  16:9              1920x1080i @ 119.88/120Hz",
    "720p120  16:9               1280x720p @ 119.88/120Hz",
    "480p119   4:3                720x480p @ 119.88/120Hz",
    "480p119H 16:9                720x480p @ 119.88/120Hz",
    "480i59    4:3          720(1440)x480i @ 119.88/120Hz",
    "480i59H  16:9          720(1440)x480i @ 119.88/120Hz",
    "576p200   4:3                720x576p @ 200Hz",
    "576p200H 16:9                720x576p @ 200Hz",
    "576i100   4:3          720(1440)x576i @ 200Hz",
    "576i100H 16:9          720(1440)x576i @ 200Hz",
    "480p239   4:3                720x480p @ 239.76/240Hz",
    "480p239H 16:9                720x480p @ 239.76/240Hz",
    "480i119   4:3          720(1440)x480i @ 239.76/240Hz",
    "480i119H 16:9          720(1440)x480i @ 239.76/240Hz",
    "720p24   16:9               1280x720p @ 23.98/24Hz",
    "720p25   16:9               1280x720p @ 25Hz",
    "720p30   16:9               1280x720p @ 29.97/30Hz",
    "1080p120 16:9              1920x1080p @ 119.88/120Hz"
)

def parse_data_block(data, fd):
    info = ord(data[0])
    length = info & 0x1f
    typ = (info & 0xe0) >> 5
    print >> fd, "Data block type %d, %d bytes follow" % (typ, length)
    print >> fd, hexstr(data[0:length + 1])
    if typ == 1:
        print >> fd, "AUDIO"
    elif typ == 2:
        print >> fd, "VIDEO"
        for i in range(1, length+1):
            tmp = ord(data[i])
            resno = tmp & 0x7f
            if tmp & 0x80:
                print >> fd, "Native",
            else:
                print >> fd, "Non-native",
            print >> fd, "resolution %d:" % resno,
            print >> fd, cea_display_modes[resno]
    elif typ == 3:
        print >> fd, "VENDOR SPECIFIC"
    elif typ == 4:
        print >> fd, "SPEAKER ALLOCATION"
    else:
        print >> fd, "Unrecognised type", typ
    print >> fd
    return length + 1

if __name__ == "__main__":
    edidparse(open(sys.argv[1], "r").read(), sys.stdout)
