"""Manage settings"""

import atexit
from configparser import ConfigParser, ExtendedInterpolation
from os import mkdir
from os.path import expanduser, join
from typing import Any, Dict, Mapping

from genericpath import exists

PATH = expanduser("~/.acdb")
CONFIG = join(PATH, 'config.conf')


class Settings:
    """Settings"""
    _DEFAULTS: Dict[str, Dict[str, Any]] = {
        "style": {
            "head": "st_Bold+fg_BrightBlue",
            "char": "st_Bold+st_Underline+fg_Green"
        },
        "config": {
            "cache_time": [5, 0, 0, 0]
        }
    }
    _instance = None
    """Edit configurations set in config file"""
    def __init_subclass__(cls) -> None:
        raise NotImplementedError("no.")

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        obj = object.__new__(cls)
        return obj

    def __init__(self) -> None:
        self._data = ConfigParser(interpolation=ExtendedInterpolation())

    def _sections(self):
        return self._data.sections()

    @property
    def style(self) -> Mapping[str, Any]:
        """Style config"""
        return self._data['style'] if 'style' in self._sections() else self._DEFAULTS['style']

    @property
    def config(self) -> Mapping[str, Any]:
        """Main Config"""
        return self._data['config'] if 'config' in self._sections() else self._DEFAULTS['config']

    def save(self):
        """Save configuration."""
        if not exists(PATH):
            mkdir(PATH)

        if len(self._data.sections()) == 0:
            self._data.read_dict(self._DEFAULTS)

        with open(CONFIG, 'w', encoding='utf-8') as file:
            self._data.write(file)

    def __repr__(self) -> str:
        return "<Config>"

Setting = Settings()

atexit.register(Setting.save)
