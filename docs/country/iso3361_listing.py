# -*- coding: utf-8 -*-

"""
iso3361_listing.py
~~~~~~~~~~~~~~~~~~~

This module lists ISO-3361 text files comprehensively
"""

import sys
import json
import os.path
from waxpage.redit import char_map

ISO_3361_LIST_FILE = "ISO_3361_list.txt"
PARTNER_AREAS_JSON = "partnerAreas.json"


def main():
    """ Main script """
    code = runner(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""{} [text_file]
"""
              "".format(__file__))
        code = 0
    assert isinstance(code, int)
    sys.exit(code)


def runner(out, err, args):
    """ Generic run """
    if args:
        param = args
    else:
        param = [os.path.join(my_path(), ISO_3361_LIST_FILE)]
    name = param[0]
    del param[0]
    if param:
        return None
    return run_list(out, err, name)


def run_list(out, err, name, debug=0):
    """ Script run for a list """
    with open(name, "rb") as fd:
        lines = fd.read(40).decode("ascii").split("\n")
        if len(lines) < 2:
            err.write("Invalid file: {}\n".format(name))
            return 1
    kind = lines[0].split("coding:")[1].strip().split(" ")[0]
    if kind == "":
        kind = "ascii"
    pa = _load_partner_areas()
    if pa is None:
        err.write("No partner areas found: {}\n".format(PARTNER_AREAS_JSON))
    else:
        if debug > 0:
            print(pa)
    return dump_text(out, err, name, kind, pa)


def dump_text(out, err, name, kind, pa, show_area=True, debug=0):
    if debug > 0:
        print("Reading '{}', of kind '{}'".format(name, kind))
    lines = open(name, "r", encoding=kind).read().split("\n")
    idx = 0
    for line in lines:
        assert line == line.strip()
        if not line or line[0] == "#":
            continue
        plain = simple_ascii(line)
        if debug > 0:
            print("Debug: '{}' {} '{}'"
                  "".format(plain, "=" if plain == line else "!=", line))
        trip = line.split("\t")
        if len(trip) > 1:
            trip = plain.replace(" ", "_").split("\t")
            # The country name stays at the last column
            trip = trip[1:] + trip[:1]
            s = " ".join(trip)
        else:
            s = plain
        lean = s.replace("_", " ")
        out.write("{}\n".format(lean))
        if show_area and pa:
            c_id = lean.split(" ")[2]
            pa_id = pa.get(c_id)
            if pa_id:
                print("#\t{} = {}".format(c_id, pa_id))
            print("")
    return 0


def _load_partner_areas(path=None, debug=0):
    """ Best-effort read of partnerAreas.json """
    pa = dict()
    if path is None:
        table = PARTNER_AREAS_JSON
    else:
        table = path
    try:
        full = json.load(open(table))
    except FileNotFoundError:
        full = None
    if full is None and path is None:
        table = os.path.join(my_path(), table)
        if debug > 0:
            print("Debug: Retrying:", table)
        full = json.load(open(table))
    there = full["results"]
    for entry in there:
        c_id, text = entry["id"], entry["text"]
        if c_id == "all":
            continue
        assert int(c_id) >= 0
        pa[c_id] = text
    return pa


def simple_ascii(s, special=None):
    """ Similar to simpler_ascii(), but allows a few extra chars. """
    if special is None:
        conv = {0xc5: "A", # A with ring above
                0xe5: "a", # a with ring above
                }
    else:
        conv = dict()
    plain = ""
    for a_chr in s:
        to_s = conv.get(ord(a_chr))
        if to_s is None:
            to_s = char_map.simpler_ascii(a_chr)
        plain += to_s
    return plain


def my_path():
    """ My script path """
    return os.path.dirname(_script_path())


def _script_path():
    """ This script's complete filename """
    return os.path.abspath(__file__)


#
# Main script
#
if __name__ == "__main__":
    main()
