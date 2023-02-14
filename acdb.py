"""ACDB"""

from gzip import compress, decompress
from os import mkdir, stat
from os.path import exists, expanduser, join
from time import strftime
from typing import List, Optional, Union
from urllib.request import Request, urlopen
from datetime import datetime, timedelta

from argh import ArghParser, arg, wrap_errors
from bs4 import BeautifulSoup
from colorful_string import Combination
from settings import Setting

USERAGENT = "Mozilla/5.0 (Linux; Android 10.0; 00-AAAAAA) AppleWebKit/537.36\
 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36"

MONTH = ("January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December")
API = "https://www.animecharactersdatabase.com/birthdays.php?theday={day}&themonth={month}"

PATH = expanduser("~/.acdb")

style0 = Combination.from_string(Setting.style['head'])
char0 = Combination.from_string(Setting.style['char'])

if not exists(PATH):
    mkdir(PATH)

# urllib seems good to use


def mkrequest(url):
    """Create a basic request"""
    return Request(url, headers={"User-Agent": USERAGENT})


def mkrequest2(day: int, month: int):
    """Create timed request. Hint, make sure the month has only 3 char."""
    return (mkrequest(API.format(day=day, month=MONTH[month-1])),
            join(PATH, f"{day}-{MONTH[month-1]}.html"))


def autorequest():
    """Create current timed request"""
    return mkrequest(API.format(day=strftime("%d"), month=strftime("%b")))


def day_month():
    """Day month"""
    return int(strftime("%d")), int(strftime("%m"))


def is_valid(cache_file: str):
    """Is cache file valid?"""
    try:
        stated = stat(cache_file)
    except FileNotFoundError:
        return False

    created_at = datetime.fromtimestamp(stated.st_ctime)
    now = datetime.now()
    cache_time: List[int] = Setting.config['cache_time']
    delta = timedelta(days=cache_time[0],
                      hours=cache_time[1],
                      minutes=cache_time[2],
                      seconds=cache_time[3])
    if (now - created_at).days == delta:
        return False
    return True


def read_url(url: Union[str, Request], target: str):
    """Read from url/api or cache (cache age is 5 days)"""
    if not is_valid(target):
        req = mkrequest(url) if isinstance(url, str) else url
        with urlopen(req) as request:
            data: bytes = request.read()

        with open(target, 'wb') as target_file:
            target_file.write(compress(data))

        return data.decode()

    with open(target, 'rb') as target_file:
        return decompress(target_file.read()).decode()


@wrap_errors([ValueError, Exception], processor=lambda x: f"{type(x).__name__}: {x!s}")
@arg("--day", '-d', help="days in [01-31]", type=int)
@arg("--month", '-m', help="month as in [01-12]", type=int)
def main(day: Optional[int] = None, month: Optional[int] = None):
    """Main"""
    if day is None:
        day = day_month()[0]
    if month is None:
        month = day_month()[1]

    if day <= 0 or day >= 32:
        raise ValueError("Day must be around 1-31")
    if month <= 0 and month >= 13:
        raise ValueError("Month must be around 1-12")

    theday = f"{day}-{MONTH[month-1]}"
    tday = style0(theday)
    tfile = join(PATH, theday)

    todayfmt = f"{theday:=^20}".replace(theday, tday)
    print(todayfmt)

    req, tfile = mkrequest2(day, month)

    html = read_url(req, tfile)

    btml = BeautifulSoup(html, features="html.parser")
    characters = []
    for tag in btml.select("#tile1 > ul > li"):
        # #tile1 > ul:nth-child(1) > li:nth-child(2) > div:nth-child(3)
        tag0 = tag.find("div", attrs={'class': 'tile1bottom'})
        if tag0 is None:
            continue
        if tag0.text in characters:
            continue
        characters.append(tag0.text)
    characters.sort()

    for char in characters:
        print(f"> {char0(char)}")


if __name__ == "__main__":
    parser = ArghParser()
    parser.set_default_command(main)
    parser.dispatch()
