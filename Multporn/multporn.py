import mimetypes
import os
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urljoin
from urllib.request import getproxies


import requests
from bs4 import BeautifulSoup
from faker import Faker
from pathvalidate import sanitize_filepath
from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry


class RequestHandler(object):

    """
    RequestHandler
    ==============
    Defines a synchronous request handler class that provides methods and
    properties for working with REST APIs that is backed by the `requests`
    library.
    """
    _timeout = (5, 5)
    _total = 5
    _status_forcelist = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1
    _fake = Faker()

    def __init__(self,
                 timeout: Tuple[float, float] = _timeout,
                 total: int = _total,
                 status_forcelist: List[int] = _status_forcelist.copy(),
                 backoff_factor: int = _backoff_factor):
        """
        Instantiates a new request handler object.
        """
        self.timeout = timeout
        self.total = total
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor

    @property
    def retry_strategy(self) -> Retry:
        """
        The retry strategy returns the retry configuration made up of the
        number of total retries, the status forcelist as well as the backoff
        factor. It is used in the session property where these values are
        passed to the HTTPAdapter.
        """
        return Retry(total=self.total,
                     status_forcelist=self.status_forcelist,
                     backoff_factor=self.backoff_factor
                     )

    @property
    def session(self) -> Session:
        """
        Creates a custom session object. A request session provides cookie
        persistence, connection-pooling, and further configuration options
        that are exposed in the RequestHandler methods in form of parameters
        and keyword arguments.
        """
        assert_status_hook = lambda response, * \
            args, **kwargs: response.raise_for_status()
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
        session.hooks['response'] = [assert_status_hook]
        session.headers.update({
            "User-Agent": RequestHandler._fake.chrome(version_from=80, version_to=86, build_from=4100, build_to=4200)
        })
        return session

    def get(self, url: str, params: dict = None, **kwargs) -> Response:
        """
        Returns the GET request encoded in `utf-8`. Adds proxies to this session
        on the fly if urllib is able to pick up the system's proxy settings.
        """
        response = self.session.get(
            url, timeout=self.timeout, params=params, proxies=getproxies(), **kwargs)
        response.encoding = 'utf-8'
        return response


class Multporn(RequestHandler):

    """
    A <https://multporn.net> comic class

    Basic Usage
    -----------
        >>> from multporn import Multporn
        >>> comic = Multporn("https://multporn.net/comics/between_friends")
        >>> print(comic)
        'Between Friends'
    """
    HOME = "http://multporn.net/"

    def __init__(self, url: str, download: bool = False, timeout: Tuple[float, float] = RequestHandler._timeout,
                 total: int = RequestHandler._total,
                 status_forcelist: List[int] = RequestHandler._status_forcelist.copy(),
                 backoff_factor: int = RequestHandler._backoff_factor):
        """
        Start a request session and load soup from <https://multporn.net> for this link.
        """
        super().__init__(timeout, total, status_forcelist, backoff_factor)
        self.__handler = RequestHandler(
            self.timeout, self.total, self.status_forcelist, self.backoff_factor)
        self.__url = urljoin(self.HOME, url)
        self.__response = self.__handler.get(self.__url)
        self.__soup = BeautifulSoup(self.__response.text, "html.parser")
        if(download):
            self.downlaodImages(self)

    @property
    def imageUrls(self) -> List[str]:
        """
        Return the url of every image in the comic
        """
        imageUrls = [image.find("img")["src"]
                     for image in self.__soup.find_all("p", "jb-image")]
        return imageUrls

    @property
    def tags(self) -> List[str]:
        """
        Returns a list of tags empty if non found
        """
        try:
            tags = [i.next.text for i in self.__soup.find(
                text="Tags: ").find_next().contents]
        except AttributeError:
            tags = None
        return tags

    @property
    def ongoing(self) -> bool:
        """
        Returns true if the comic is ongoing
        """
        try:
            ongoing = "ongoing" in self.__soup.find(
                text="Section: ").find_next().text.lower()
        except AttributeError:
            ongoing = False
        return ongoing

    @property
    def name(self):
        """
        Returns the name of the comic
        Some older comics had the name in a different location
        """
        try:
            name = sanitize_filepath(
                self.__soup.find("meta", attrs={"name": "dcterms.title"})["content"])
        except TypeError:
            name = sanitize_filepath(
                self.__soup.find("meta", attrs={"property": "og:title"})["content"])
        return name

    def __str__(self):
        """
        returns the name of the comic
        """
        return self.name

    def downloadImages(self, output: bool = True, root: Path = Path("Comics/"), printProgress: bool = True):
        """
        Downloads all comic pages that don't already exist in the directory
        logging can be disabled by passing false to printProgress
        """
        Updated = 0
        existingStart = -1
        existingEnd = -1
        root = root.joinpath(self.name)
        root.mkdir(parents=True, exist_ok=True)
        for i in range(len(self.imageUrls)):
            fileExists = False
            fileName = f"{self.name}_{str(i).zfill(len(str(len(self.imageUrls)-1)))}"
            # Check for existing pictures/pages
            for file in os.listdir(root):
                if(file.startswith(fileName)):
                    if existingStart == -1:
                        existingStart = existingEnd = i
                    else:
                        existingEnd = i
                    fileExists = True
                    break
            if(fileExists == False):
                Updated += 1
                if(existingStart != -1):
                    if(printProgress):
                        if(existingStart == existingEnd):
                            print(
                                f'"{self.name}" page {existingStart+1}/{len(self.imageUrls)} exists! skipping')
                        else:
                            print(
                                f'"{self.name}" page {existingStart+1} through {existingEnd+1} out of {len(self.imageUrls)} exists! skipping')
                    existingStart = existingEnd = -1
                r = requests.get(
                    self.imageUrls[i], allow_redirects=True)
                fileName = fileName + \
                    mimetypes.guess_extension(r.headers['content-type'])
                fpath = sanitize_filepath(Path(root, fileName))
                open(fpath, "wb").write(r.content)
                if(printProgress):
                    print(f'"{self.name}" page {i+1}/{len(self.imageUrls)} done')
        if(printProgress):
            if(not Updated):
                print(f'Downlaod "{self.__url}" finished with no updates')
            else:
                print(
                    f'Download of "{self.__url}" done, {Updated} new pages found')


class Webpage:

    """
    A Webpage class that bundles together everything related to <https://multporn.net>
    If you're confused what I mean by "webpage", this is and example(oviously NSFW): <https://multporn.net/category/cosplay>
    """
    def __init__(self, url):
        """
        initializing the webpage object
        """
        self.__url = url
        self.__soup = BeautifulSoup(requests.get(url).text, "html.parser")

    @property
    def links(self) -> list:
        """
        return all links found in this webpage
        """
        links = [urljoin(Multporn.HOME, i.a['href']) for i in self.__soup.find(
            "table", "views-view-grid").find_all("strong")]
        return links

    @property
    def name(self) -> str:
        """
        Return the name of this webpage
        usually is a category, character, author, etc
        """
        try:
            self.__name = sanitize_filepath(
                self.__soup.find("meta", attrs={"name": "dcterms.title"})["content"])
        except TypeError:
            self.__name = sanitize_filepath(
                self.__soup.find("meta", attrs={"property": "og:title"})["content"])
        return self.__name
