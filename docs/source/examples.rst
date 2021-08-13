========
Examples
========

basic usage of the Multporn library

.. code-block:: python

    from multporn import Multporn

    comic = Multporn("https://multporn.net/comics/between_friends")

    # Between Friends
    print(comic)

    # ['Best', 'Blowjob', 'Cunnilingus', 'Lolicon', 'Oral sex', 'Stockings', 'Straight', 'Straight Shota', 'Virgin']
    print(comic.tags)

    # Downloads the comic to /Comics/Between Friends/
    comic.downloadContent()