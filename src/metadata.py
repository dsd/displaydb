from ConfigParser import ConfigParser

def parse_metadata(filename):
    parser = ConfigParser()
    parser.read(filename)
    ret = { }

    # Ensure required fields are present
    ret["submitter"] = parser.get("display", "submitter")
    ret["vendor"] = parser.get("display", "vendor")
    ret["model"] = parser.get("display", "model")

    if "notes" in parser.options("display"):
        ret["notes"] = parser.get("display", "notes")

    typ = parser.get("display", "type")
    if typ not in ("TV", "Panel", "Monitor"):
        raise Exception("Bad type: %s" % typ)
    ret["type"] = typ

    tech = parser.get("display", "technology")
    if tech not in ("CRT", "LCD", "Plasma"):
        raise Exception("Bad technology: %s" % tech)
    ret["technology"] = tech

    if "overscan" in parser.options("display"):
        overscan = parser.get("display", "overscan")
        if overscan not in ("Yes", "No"):
            raise Exception("Bad overscan: %s" % overscan)
        ret["overscan"] = overscan

    if "overscan_configurable" in parser.options("display"):
        overscan = parser.get("display", "overscan_configurable")
        if overscan not in ("Yes", "No"):
            raise Exception("Bad overscan configurable: %s" % overscan)
        ret["overscan_configurable"] = overscan

    if "overscan_notes" in parser.options("display"):
        ret["overscan_notes"] = parser.get("display", "overscan_notes")

    return ret
