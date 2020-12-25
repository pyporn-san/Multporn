from .multporn import *
__version__ = "0.0.4"
"""
Basic Usage
>>> from Multporn import multporn
>>> comic = Multporn("https://multporn.net/comics/between_friends")
>>> comic.downloadImages()

Basic Utils usage
>>> from Multporn import multporn, Utils
>>> results = Utils.search("zelda")
>>> comic = Multporn(results[0])
>>> comic.downloadImages()
"""