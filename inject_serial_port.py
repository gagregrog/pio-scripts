"""
Pre-build script: reads PORT from .env and injects it as MONITOR_PORT
and UPLOAD_PORT so `pio run -t upload` and `pio device monitor` use the
correct serial device without hardcoding it in platformio.ini.

Usage in platformio.ini:
    extra_scripts = pre:scripts/inject_serial_port.py

Required .env key:
    PORT=/dev/cu.usbserial-0001   (or COMx on Windows)

If PORT is absent the upload/monitor port falls back to PlatformIO's
auto-detection.
"""

Import("env")
import os


def read_dotenv(project_dir):
    env_vars = {}
    try:
        with open(os.path.join(project_dir, ".env")) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env_vars


env_vars = read_dotenv(env["PROJECT_DIR"])
port = env_vars.get("PORT", "")

if port:
    env["MONITOR_PORT"] = port


def inject_upload_port(source, target, env):
    env_vars = read_dotenv(env["PROJECT_DIR"])
    port = env_vars.get("PORT", "")
    if port:
        env["UPLOAD_PORT"] = port


env.AddPreAction("upload", inject_upload_port)
