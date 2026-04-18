"""
Pre-build script: gzip-compresses src/web/web_ui.html and writes
src/web/web_ui_html.h as a uint8_t byte array for serving with
Content-Encoding: gzip.

Usage in platformio.ini:
    extra_scripts = pre:scripts/compress_html.py

Edit web_ui.html directly — do not edit the generated header. The header
is re-generated automatically before each device build.

WebUI.cpp includes the header and serves HTML_GZ (length HTML_GZ_LEN)
with the appropriate Content-Encoding response header.
"""

Import('env')

import gzip
import os

project_dir = env['PROJECT_DIR']
src = os.path.join(project_dir, 'src', 'web', 'web_ui.html')
dst = os.path.join(project_dir, 'src', 'web', 'web_ui_html.h')

with open(src, 'rb') as f:
    compressed = gzip.compress(f.read(), compresslevel=9)

with open(dst, 'w') as f:
    f.write('// Auto-generated from web_ui.html — do not edit directly.\n')
    f.write('// Re-generated automatically on each device build.\n')
    f.write('#pragma once\n')
    f.write('#include <stdint.h>\n\n')
    f.write(f'static const uint32_t HTML_GZ_LEN = {len(compressed)}U;\n')
    f.write('static const uint8_t HTML_GZ[] = {\n')
    for i in range(0, len(compressed), 16):
        chunk = compressed[i:i+16]
        f.write('    ' + ', '.join(f'0x{b:02x}' for b in chunk))
        f.write(',\n' if i + 16 < len(compressed) else '\n')
    f.write('};\n')

print(f'compress_html: {os.path.getsize(src)} -> {len(compressed)} bytes '
      f'({100 - 100 * len(compressed) // os.path.getsize(src)}% reduction)')
