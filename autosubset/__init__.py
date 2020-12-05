#!/usr/bin/python3
# Usage: autosubset <font-file> < <used-text>
# * Automatically split the font file into two parts:
#   1. The part that only provides the characters read from stdin, which will be
#      used for the current version of the web page
#   2. The remainder of the font, just as a fallback, in case you should ever
#      change the contents.
# * Output @font-face rules

import subprocess
import sys


VERSION = '0.1.0'


def range_string(start, end):
    if start == end:
        return 'U+%x' % start
    else:
        return 'U+%x-%x' % (start, end)


def set2ranges(s):
    """Input: A set of numbers.
    Output: A sequence of ranges (as a string)"""
    ranges = []
    range_start = range_end = None
    for elem in sorted(s):
        if range_start is None:
            # Start a new range
            range_start = range_end = elem
        elif range_end + 1 == elem:
            # Extend range
            range_end = elem
        else:
            # Not contiguous: flush and start new set
            ranges.append(range_string(range_start, range_end))
            range_start = range_end = elem
    if range_start is None:
        # Never started a set
        return ''
    else:
        # Guaranteed to have a pending set
        ranges.append(range_string(range_start, range_end))
    return ','.join(ranges)


text = sys.stdin.read().replace('\n', '')
char_ords = set([ord(c) for c in text])
ranges = set2ranges(char_ords)
full = sys.argv[1]
dot = full.rindex('.')
minus = full.find('-')
if minus >= 0:
    base = full[:minus]
else:
    base = full[:dot]
fmt = full[dot+1:]
subset = full[:dot] + '.subset' + full[dot:]
subprocess.run(['pyftsubset', '--unicodes=' + ranges,
    '--flavor=woff2', '--with-zopfli', sys.argv[1]], check=True)
print(f"""<link rel="preload" href="{subset}" as "font" type="font/woff2">
@font-face {{ font-family: {base}; src: url({subset}) format(woff2); unicode-range: {ranges}; }}
@font-face {{ font-family: {base}; src: url({full}) format({fmt}); }}""")
