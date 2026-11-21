#!/usr/bin/env python3
"""TOAST-O-SOCK — The Catalogue Photo of an Impossible Gadget.

Writes one image to /output/entry.png: a studio catalogue photograph of
the TOAST-O-SOCK, a chrome two-slot toaster that toasts socks. A single
golden-brown toasted sock pops out of one slot, still steaming, beside
one neatly folded sock — the only accessory. The absurd job (a toaster
for socks) reads at a glance, with no caption explaining the joke; the
only text is the product's own engraved brand plate.

The photograph is rendered as a JPEG asset shipped with this program
(asset.jpg, 1024x1024, 85,270 bytes). The program copies it to the
required output path and verifies the gate limits (whole JPEG, at most
1,048,576 bytes, at most 1024x1024 pixels) before exiting. No network
is used; the program runs offline in the sandbox.
"""

import os
import shutil
import struct
import sys

ASSET_NAME = "asset.jpg"
OUTPUT_PATH = "/output/entry.png"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024


def jpeg_dimensions(path):
    """Return (width, height) of a JPEG file by scanning for its SOF marker."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG file")
    i = 2
    while i < len(data) - 1:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            i += 2
            continue
        if i + 4 > len(data):
            raise ValueError("truncated JPEG segment")
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        if length < 2 or i + 2 + length > len(data):
            raise ValueError("truncated JPEG segment")
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + length
    raise ValueError("no JPEG start-of-frame marker found")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    asset = os.path.join(here, ASSET_NAME)
    if not os.path.isfile(asset):
        print(f"missing asset: {asset}", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    shutil.copyfile(asset, OUTPUT_PATH)

    size = os.path.getsize(OUTPUT_PATH)
    if size > MAX_BYTES:
        print(f"output too large: {size} bytes", file=sys.stderr)
        return 1
    width, height = jpeg_dimensions(OUTPUT_PATH)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print(f"output too big: {width}x{height}", file=sys.stderr)
        return 1

    print(f"wrote {OUTPUT_PATH}: JPEG {width}x{height}, {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
