import TDBRecord as tdbra

from subprocess import Popen, PIPE, DEVNULL
from streamlink import Streamlink
from requests import get
from pathlib import Path
import time

session = Streamlink()
urlstore = {
    "twitch": "https://twitch.tv/{user}",
    "afreecatv": "https://play.afreecatv.com/{user}",
}

def worker(user: str, platform: str) -> None:
    """
    Standalone video downloader
    """
    logger = tdbra.data[f"{user}.{platform}"]["logger"]
    downloadPath = tdbra.downloadPath / Path(f"{user}.{platform}/")
    downloadPath.mkdir(parents=True, exist_ok=True)
    filename = f"{platform}.{user}.{time.strftime('%y%m%d.%H%M%S')}.mp4"
    m3uPlaylistUri = stream(user, platform)

    logger.info("FFMPEG Downloader started.")
    ffmpeg = Popen([
        "ffmpeg",
        "-y",
        "-i",
        m3uPlaylistUri,
        "-c",
        "copy",
        f"{downloadPath}/{filename}"
    ], stdin=PIPE, stdout=DEVNULL, stderr=PIPE)
    while True:
        if tdbra.data[f"{user}.{platform}"]["exit"]:
            # send "q" to ffmpeg
            ffmpeg.communicate(input=b"q")
            for i in range(10):
                if ffmpeg.poll() is not None:
                    logger.info("FFMPEG Downloader finished with status 0.")
                    del(tdbra.data[f"{user}.{platform}"])
                    return
                time.sleep(1)
            ffmpeg.kill()
            logger.warning("FFMPEG Downloader killed.")
            break
        if ffmpeg.poll() is not None:
            logger.info("FFMPEG Downloader finished with status 0.")
            tdbra.data[f"{user}.{platform}"]["end"] = True
            break
        time.sleep(1)
    del(tdbra.data[f"{user}.{platform}"])
    pass

def stream(user: str, platform: str) -> str:
    return _streamget(urlstore[platform].format(user=user), platform)

def _streamget(url: str, platform: str) -> str:
    if tdbra.conf["remote_streamlink"] and platform == "twitch":
        return get(f"{tdbra.conf['remote_streamlink']}/{url.split('/')[-1]}?quality=best").text
    else:
        return session.streams(url)["best"].url

def checkStatus(user: str, platform: str) -> bool:
    if session.streams(urlstore[platform].format(user=user)):
        return True
    else:
        return False