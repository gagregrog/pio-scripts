"""
Pre-build script: reads the specified keys from .env and emits them as
-D KEY="VALUE" compiler flags for use in platformio.ini build_flags.

Usage in platformio.ini:
    build_flags = !python scripts/hydrate_build_flags.py KEY1 KEY2 ...

Keys not found in .env are silently skipped. Specifying the keys as
arguments keeps the injected flags visible directly in platformio.ini.

Example .env:
    OTA_PASSWORD=secret
    TZ_STRING=PST8PDT,M3.2.0,M11.1.0
"""

import sys

keys = set(sys.argv[1:])
flags = []

try:
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key in keys:
                flags.append('-D {}=\\"{}\\"'.format(key, value.strip()))
except FileNotFoundError:
    print("WARNING: .env file not found", file=sys.stderr)

print(" ".join(flags))
