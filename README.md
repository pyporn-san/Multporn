# Python multporn scraper

[![Pip Package](https://github.com/pyporn-san/MPdownloader/workflows/Upload%20Python%20Package/badge.svg)](https://pypi.org/project/Multporn/) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/0d152a094f5c481e8b886be58e13aeaf)](https://app.codacy.com/gh/pyporn-san/Multporn?utm_source=github.com&utm_medium=referral&utm_content=pyporn-san/Multporn&utm_campaign=Badge_Grade)

multporn is a Python library used to interact with [multporn.net (NSFW)](https://multporn.net/) via python.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the latest release of multporn.

```bash
pip install multporn
```

## Usage

```python
from multporn import Multporn

comic = Multporn("https://multporn.net/comics/between_friends")

# Between Friends
print(comic)

 # ['Best', 'Blowjob', 'Cunnilingus', 'Lolicon', 'Oral sex', 'Stockings', 'Straight', 'Straight Shota', 'Virgin']
print(comic.tags)

# Downloads the comic to /Comics/Between Friends/
comic.downloadImages()
```

Also see [Multporn-cli](https://github.com/pyporn-san/Multporn-CLI/) as an implementation example

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[GPL V3.0](https://choosealicense.com/licenses/gpl-3.0/)
