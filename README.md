# pio-scripts

PlatformIO pre-build scripts for ESP32 Arduino projects. Add as a git submodule:

```bash
git submodule add git@github.com:gagregrog/pio-scripts.git scripts
```

Each script reads from a `.env` file in the project root. Add `.env` to `.gitignore` — it holds device-specific values that should not be committed.

---

## hydrate_build_flags.py

Reads named keys from `.env` and emits them as `-D KEY="VALUE"` compiler flags.

**platformio.ini:**
```ini
build_flags = !python scripts/hydrate_build_flags.py KEY1 KEY2
```

**Example .env:**
```
OTA_PASSWORD=secret
TZ_STRING=PST8PDT,M3.2.0,M11.1.0
```

Keys not present in `.env` are silently skipped. List only the keys you want exposed as build flags — this keeps the intent visible in `platformio.ini`.

---

## inject_serial_port.py

Reads `PORT` from `.env` and sets it as both `UPLOAD_PORT` and `MONITOR_PORT` so you don't hardcode the serial device in `platformio.ini`. Falls back to PlatformIO auto-detection if `PORT` is absent.

**platformio.ini:**
```ini
extra_scripts = pre:scripts/inject_serial_port.py
```

**Example .env:**
```
PORT=/dev/cu.usbserial-0001
```

On Windows use `COMx` (e.g. `PORT=COM3`).

---

## inject_ota_auth.py

Reads `OTA_PASSWORD` and `IP` from `.env` and injects them as `espota` uploader flags so OTA uploads authenticate without hardcoding credentials.

**platformio.ini:**
```ini
[env:esp32ota]
extends = env:esp32dev
extra_scripts =
    pre:scripts/inject_serial_port.py
    pre:scripts/inject_ota_auth.py
upload_protocol = espota
```

**Example .env:**
```
OTA_PASSWORD=secret
IP=192.168.1.42
```

If either key is absent it is omitted from the upload command (espota will prompt or fail depending on device configuration).

---

## compress_html.py

Gzip-compresses `src/web/web_ui.html` and writes it as a `uint8_t` byte array to `src/web/web_ui_html.h`. Include the generated header in your WebUI module and serve `HTML_GZ` (length `HTML_GZ_LEN`) with `Content-Encoding: gzip`.

Edit `web_ui.html` directly — the header is regenerated automatically on each device build.

**platformio.ini:**
```ini
extra_scripts = pre:scripts/compress_html.py
```

No `.env` keys required.
