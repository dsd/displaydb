from edidparse import edidparse
from metadata import parse_metadata
from glob import glob
import sys
import os
import subprocess
import shutil

shutil.rmtree("output")
if not os.path.exists("output"):
    os.makedirs("output")

for displaycfg in glob("displays/*.ini"):
    edid_base_path = displaycfg.rstrip(".ini")
    display = os.path.basename(edid_base_path)
    print "Processing", display
    meta = parse_metadata(displaycfg)
    if not meta:
        print "Failed to parse ini metadata"

    edids = glob(edid_base_path + ".*")
    if len(edids) == 1: # expecting 1 ini match
        print "No EDIDs found"
        sys.exit(1)

    for edid in edids:
        if edid.endswith(".ini"):
            continue
        conntype = edid.rsplit(".", 1)[1]
        if conntype not in ("HDMI", "VGA", "DVI"):
            print "Unrecognised connection type", conntype
            sys.exit(1)

        outfile = open("output/%s.%s.txt" % (display, conntype), "w")
        print >> outfile, "Submitter:", meta["submitter"]
        print >> outfile, "Vendor:", meta["vendor"]
        print >> outfile, "Model:", meta["model"]
        print >> outfile, "Connection type:", conntype
        print >> outfile, "Display type:", meta["type"]
        print >> outfile, "Display technology:", meta["technology"]
        if "notes" in meta.keys():
            print >> outfile, "Notes:", meta["notes"]
        print >> outfile

        if "overscan" in meta.keys():
            print >> outfile, "Overscan HD by default:", meta["overscan"]
        if "overscan_configurable" in meta.keys():
            print >> outfile, "Overscan configurable:", meta["overscan_configurable"]
        if "overscan_notes" in meta.keys():
            print >> outfile, "Overscan notes:", meta["overscan_notes"]
        print >> outfile

        data = open(edid, "r").read()
        edidparse(data, outfile)

        print >> outfile
        outfile.flush()
        subprocess.call(["xxd", edid], stdout=outfile)
