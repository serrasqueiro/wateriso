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

_IDX_COMMENT = -1


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
    code = dump_text(out, err, name, kind, pa)
    # Dump whatever was not used
    dump_partner_areas(pa, err, debug)
    return code


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
            num_id = int(c_id)
            tup = pa.get(num_id)
            if tup:
                pa_name, _ = tup
                print("#\t{} = {}".format(c_id, pa_name))
                assert pa[num_id][1] == []
                pa[num_id][1].append(line)
            print("")
    return 0


def _load_partner_areas(path=None, debug=0):
    """ Best-effort read of partnerAreas.json """

    def _sanity_check(dct):
        keys = list(dct.keys())
        keys.sort()
        if keys[0] == "_comment":
            del keys[0]
        if keys[0] == "_status":
            del keys[0]
        is_ok = keys == ["id", "text"]
        if not is_ok:
            print("Uops:", dct)
        return is_ok

    pa = {_IDX_COMMENT: ("_comment", dict(),)
          }
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
        comment = entry.get("_comment")
        if entry.get("_status"):
            comment = "STATUS: {}".format(entry["_status"])  # Status overrides comment!
        assert _sanity_check(entry)
        if c_id == "all":
            continue
        num_id = int(c_id)
        assert num_id >= 0
        pa[num_id] = (text, [])
        if comment:
            pa[_IDX_COMMENT][1][num_id] = comment
    return pa


def dump_partner_areas(pa, err, debug=0):
    msgs = dict()
    if pa is None:
        return -1
    for c_id, (utf_text, hit) in pa.items():
        text = simple_ascii(utf_text)
        comment = pa[_IDX_COMMENT][1].get(c_id)
        s_extra = " ; # {}".format(comment) if comment else ""
        if debug > 0:
            print("Debug: pa[{}] = ({}, {})"
                  "".format(c_id, text, hit))
        elif c_id > 0:
            if hit == []:
                msg = "No hit for pa[{}] = {}{}".format(c_id, text, s_extra)
                msgs[c_id] = msg
    keys = list(msgs.keys())
    keys.sort()
    for key in keys:
        err.write("{}\n".format(msgs[key]))
    return 0


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
