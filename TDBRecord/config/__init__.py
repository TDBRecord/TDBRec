import TDBRecord as tdbra

import pathlib
import subprocess
from tempfile import gettempdir
from time import time
import json

DEFAULT_CONFIG = {
    "remote_streamlink": "", # Remote streamlink server, if not set, use local streamlink e.g. "http://www.example.com/api/get"
    "downloadPath": "./download/",
    "ffmpeg": "ffmpeg", # ffmpeg path, if not set, use PATH ffmpeg
    "users": [
        {
            "name": "ExampleUser1",
            "platform": "twitch | afreecatv"
        },
        {
            "name": "ExampleUser2",
            "platform": "twitch | afreecatv"
        }
    ],
}

PLATFORMS = ["twitch", "afreecatv"]

def check_config(conf: dict = {}):
    tdbr = False
    if not conf:
        if not tdbra.conf:
            tdbra.logger.error("No config found")
            raise ValueError("No config found")
        conf = tdbra.conf
        tdbr = True

    if not conf["users"]:
        tdbra.logger.error("No user found in config file")
        raise ValueError("No user found in config file")
    
    for user in conf["users"]:
        if not user["name"]:
            tdbra.logger.error("User name not found in config file")
            raise ValueError("User name not found in config file")
        if not user["platform"]:
            tdbra.logger.error("User platform not found in config file")
            raise ValueError("User platform not found in config file")
        if user["platform"] not in PLATFORMS:
            tdbra.logger.error("User platform not found in config file")
            raise ValueError("User platform not found in config file")
    
    if not conf["downloadPath"]:
        tdbra.error("Download path not found in config file")
        raise ValueError("Download path not found in config file")
    else:
        downloadPath = pathlib.Path(conf["downloadPath"])
        downloadPath.mkdir(parents=True, exist_ok=True)

    if not conf["ffmpeg"]:
        conf["ffmpeg"] = "ffmpeg"
    
    if "gdc" in conf:
        import gdc
        tdbra.gdc = gdc
        
    
    # check ffmpeg is installed
    try:
        subprocess.run([conf["ffmpeg"], "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        tdbra.logger.error("ffmpeg not found")
        raise ValueError("ffmpeg not found")
    except FileNotFoundError:
        tdbra.logger.error("ffmpeg not found")
        raise ValueError("ffmpeg not found")
    
    if tdbr: 
        tdbra.conf = conf
        tdbra.downloadPath = downloadPath
    return conf, downloadPath

def reload():
    try:
        conf = json.loads(tdbra.confPath.read_text())
    except json.JSONDecodeError:
        tdbra.logger.error("Cannot decode Json file. Config not updated.")
        return False
    except FileNotFoundError:
        tdbra.logger.error("Config file not found. Config not updated.")
        return False
    try:
        conf, downloadPath = check_config(conf)
        tdbra.conf = conf
        tdbra.downloadPath = downloadPath
        tdbra.logger.info("Config updated.")
        return True
    except Exception as e:
        tdbra.logger.error(f"Config check error with <{e}>. Config not updated.")
        return False
