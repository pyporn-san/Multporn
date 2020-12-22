![Pip Package](https://github.com/pyporn-san/MPdownloader/workflows/Upload%20Python%20Package/badge.svg)
# python multporn scraper

multporn is a Python library used to interact with [multporn](https://multporn.net/) via python.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install multporn.

```bash
pip install multporn
```

## Usage

```python
from multporn import Multporn

comic = Multporn("https://multporn.net/comics/between_friends")

print(comic) # Between Friends
print(comic.tags) # ['Best', 'Blowjob', 'Cunnilingus', 'Lolicon', 'Oral sex', 'Stockings', 'Straight', 'Straight Shota', 'Virgin']
comic.downloadImages() # Downloads the comic to /comic/Between Friends/
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPL V3.0](https://choosealicense.com/licenses/gpl-3.0/)
