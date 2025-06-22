#!/usr/bin/python3
# Usage: autosubset [options] <font-file> < <used-text>
# * Automatically split the font file into two parts:
#   1. The part that only provides the characters read from stdin, which will be
#      used for the current version of the web page
#   2. The remainder of the font, just as a fallback, in case you should ever
#      change the contents.
# * Output @font-face rules

import argparse
import base64
import pathlib
import re
import subprocess
import sys

from fontTools import ttLib


VERSION = '0.3.0'


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


def get_args():
    parser = argparse.ArgumentParser(description="autosubset – "
                                     "Automatically create an optimized subset font "
                                     "using fonttool's pyftsubset")
    parser.add_argument('--version',
                        action='version', version=VERSION)
    parser.add_argument('--quiet',
                        action='store_true',
                        help="Suppresses the HTML+CSS output to stdout")
    parser.add_argument('--svg',
                        action='store_true',
                        help="Creates output for inclusion into SVG <style> element. Suppresses all other output.")
    parser.add_argument('--digits',
                        action='store_true',
                        help="""Also include all digits, independent of whether they
                appear in the input. This is useful if you also have some
                counters elsewhere.""")
    parser.add_argument('--ascii-letters',
                        action='store_true',
                        help="""Also include a-z and A-Z, independent of whether they
                appear in the input.""")
    parser.add_argument('--ascii-printable', '--ascii',
                        action='store_true',
                        help="""Also include space to tilde (0x20-0x7f), independent of
                whether they appear in the input.""")
    parser.add_argument('font_file',
                        nargs='+',
                        help="""The files to subset into <basename>.subset.woff2""")
    return parser.parse_args()


def main():
    args = get_args()
    text = sys.stdin.read().replace('\n', '')
    char_ords = set([ord(c) for c in text])
    if args.digits:
        char_ords = char_ords.union(range(0x30, 0x3a))
    if args.ascii_letters:
        char_ords = char_ords.union(range(0x41, 0x5b), range(0x61, 0x7b))
    if args.ascii_printable:
        char_ords = char_ords.union(range(0x20, 0x7f))

    ranges = set2ranges(char_ords)
    html = ""
    css = ""
    if args.svg:
        for full in args.font_file:
            font = ttLib.TTFont(full)
            basename = pathlib.PurePath(full).stem
            fontFamilyName = font['name'].getDebugName(1)
            fontWeight = font['name'].getDebugName(2)
            numericWeight = font['OS/2'].usWeightClass
            result = subprocess.run(['pyftsubset', '--output-file=/dev/stdout',
                                     '--unicodes=' + ranges,
                                     '--flavor=woff2', '--with-zopfli', full], check=True, capture_output=True)
            b64 = base64.b64encode(bytes(result.stdout))
            print(f"""@font-face{{font-family:"{fontFamilyName}";font-weight:{numericWeight};src:local("{fontFamilyName}"),url(data:font/woff2;charset=utf-8;base64,{bytes.decode(b64)})}}""")
    else:
        for full in args.font_file:
            dot = full.rindex('.')
            minus = full.find('-')
            if minus >= 0:
                base = full[:minus]
            else:
                base = full[:dot]
            fmt = full[dot+1:]
            subset = full[:dot] + '.subset' + full[dot:]
            subprocess.run(['pyftsubset', '--unicodes=' + ranges,
                            '--flavor=woff2', '--with-zopfli', full], check=True)
            html += f"""
    <link rel="preload" href="{subset}" as="font" type="font/woff2" />"""
            css += f"""
    @font-face {{ font-family: {base}; src: url({subset}) format(woff2); unicode-range: {ranges}; }}
    @font-face {{ font-family: {base}; src: url({full}) format({fmt}); }}"""
        if not args.quiet:
            print(f"// HTML code:{html}\n// CSS code:{css}")
