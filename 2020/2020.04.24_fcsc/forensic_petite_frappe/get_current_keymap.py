#!/usr/bin/env python3
"""Get the current keymap from the X11 server

Example: ./get_current_keymap.py > azerty_keymap.json
"""
import collections
import json
import re
import subprocess


keymap = collections.OrderedDict()
for line in subprocess.Popen(['xmodmap', '-pke'], stdout=subprocess.PIPE).stdout:
    # Example of lines:
    #   keycode  24 = a A a A ae AE ae AE
    #   keycode  25 = z Z z Z acircumflex Acircumflex acircumflex Acircumflex
    m = re.match('^keycode +([0-9]+) = (.+)$', line.decode().rstrip())
    if not m:
        continue
    key_code_str, key_chars = m.groups()
    key_code = int(key_code_str)
    keymap[key_code] = key_chars.split(' ')[0]


print(json.dumps(keymap, indent=2))
