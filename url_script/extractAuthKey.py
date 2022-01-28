import os
import re
from typing import List, Optional
from urllib.parse import unquote
import tempfile


def get_tempdir():
    """Gets the temporary directory to be used by genshin.py"""
    directory = os.path.join(tempfile.gettempdir(), "genshin.py")
    os.makedirs(directory, exist_ok=True)
    return directory

AUTHKEY_FILE = os.path.join(get_tempdir(), "genshin_authkey.txt")

def get_logfile() -> Optional[str]:
    """Find a Genshin Impact logfile
    :returns: A logfile path or None if no genshin installation exists
    """
    mihoyo_dir = os.path.expanduser("~/AppData/LocalLow/miHoYo/")
    for name in ["Genshin Impact", "原神", "YuanShen"]:
        output_log = os.path.join(mihoyo_dir, name, "output_log.txt")
        if os.path.isfile(output_log):
            return output_log

    return None  # no genshin installation


def _read_logfile(logfile: Optional[str] = None) -> str:
    """Returns the contents of a logfile
    :param logfile: A path to a logfile
    """
    logfile = logfile or get_logfile()
    if logfile is None:
        raise FileNotFoundError("No Genshin Installation was found, could not get gacha data.")
    with open(logfile) as file:
        return file.read()

def extract_url() -> Optional[str]:
    matchList = re.findall("^OnGetWebViewPageFinish:https://webstatic-sea.mihoyo.com.*log$", _read_logfile(get_logfile()), re.MULTILINE)
    if len(matchList) == 1:
        return matchList[0].split("OnGetWebViewPageFinish:")[1]
    return None
        
        
if __name__ == "__main__":
    url = extract_url()
    if url is None:
        print("The url is not generated by your game, please open you game and the history window in wish so the url can be generated in log file")
    else:
        print(url)