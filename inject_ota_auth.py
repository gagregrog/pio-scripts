"""
Pre-build script: reads OTA_PASSWORD and IP from .env and injects them
as espota uploader flags so `pio run -t upload` (OTA env) authenticates
and targets the correct device without hardcoding credentials in
platformio.ini.

Usage in platformio.ini:
    extra_scripts = pre:scripts/inject_ota_auth.py
    upload_protocol = espota

Required .env keys:
    OTA_PASSWORD=yourpassword
    IP=192.168.x.x

If either key is absent it is omitted from the upload command (espota
will prompt or fail depending on the device configuration).
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


def inject_auth(source, target, env):
    env_vars = read_dotenv(env["PROJECT_DIR"])
    password = env_vars.get("OTA_PASSWORD", "")
    if password:
        env.Append(UPLOADERFLAGS=["--auth", password])
    ip = env_vars.get("IP", "")
    if ip:
        env["UPLOAD_PORT"] = ip


env.AddPreAction("upload", inject_auth)
