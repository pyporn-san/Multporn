import mimetypes
import os
from enum import Enum, unique
from pathlib import Path
from typing import List, Tuple
from urllib.parse import quote, urljoin
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
        """Instantiates a new request handler object."""
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
                 status_forcelist: List[int] = RequestHandler._status_forcelist.copy(), backoff_factor: int = RequestHandler._backoff_factor):
        """
        Start a request session and load soup from <https://multporn.net> for this link.
        """
        super().__init__(timeout, total, status_forcelist, backoff_factor)
        self.__handler = RequestHandler(
            self.timeout, self.total, self.status_forcelist, self.backoff_factor)
        self.__url = urljoin(self.HOME, url)
        self.__response = self.__handler.get(self.__url)
        self.__soup = BeautifulSoup(self.__response.text, "html.parser")
        self.__contentUrls = self.__sanitized = self.__name = self.__tags = self.__ongoing = self.__sections = self.__characters = self.__artists = self.__links = self.__contentType = "Unset"
        if(download):
            self.downloadContent()

    def __str__(self):
        """
        returns the name of the comic
        """
        return self.name

    @property
    def contentUrls(self) -> List[str]:
        """
        Return the url of every image in the comic
        for videos will return an array with the video file link in the first index
        """
        if(self.__contentUrls == "Unset"):
            if(self.contentType == "video"):
                self.__contentUrls = [self.__soup.find("video").source["src"]]
            else:
                self.__contentUrls = [image.find("img")["src"]
                                      for image in self.__soup.find_all("p", "jb-image")]

        return self.__contentUrls

    @property
    def tags(self) -> List[str]:
        """
        Returns a list of tags empty if non found
        """
        if(self.__tags == "Unset"):
            try:
                self.__tags = [i.next.text for i in self.__soup.find(
                    text="Tags: ").find_next().contents]
            except AttributeError:
                self.__tags = []
        return self.__tags

    @property
    def ongoing(self) -> bool:
        """
        Returns true if the comic is ongoing
        """
        if(self.__ongoing == "Unset"):
            try:
                self.__ongoing = "ongoing" in self.__soup.find(
                    text="Section: ").find_next().text.lower()
            except AttributeError:
                self.__ongoing = False
        return self.__ongoing

    @property
    def name(self) -> str:
        """
        Returns the name of the comic
        """
        if(self.__name == "Unset"):
            self.__name = self.__soup.find(
                "meta", attrs={"name": "dcterms.title"})["content"]
        return self.__name

    @property
    def sanitizedName(self) -> str:
        """
        Return the sanitized name of the comic
        """
        if(self.__sanitized == "Unset"):
            self.__sanitized = sanitize_filepath(self.name)
        return self.__sanitized

    @property
    def url(self) -> str:
        """
        Returns the url associated with the comic
        """
        return self.__url

    @property
    def pageCount(self) -> int:
        """
        Return the number of pages
        """
        return len(self.contentUrls)

    @property
    def artists(self) -> List[str]:
        """
        Return a list of artists
        only present for comics
        most likely a single artist but multiple artists are possible that's why the return is a list
        """
        if(self.__artists == "Unset"):
            self.__artists = [i.next.text for i in self.__soup.find(
                text="Author: ").find_next().contents]
        return self.__artists

    @property
    def sections(self) -> List[str]:
        """
        Returns a list of sections that this comic is present in
        only present for comics
        most likely a single section but multiple sections are possible that's why the return is a list
        """
        if(self.__sections == "Unset"):
            self.__sections = [i.next.text for i in self.__soup.find(
                text="Section: ").find_next().contents]
        return self.__sections

    @property
    def characters(self) -> List[str]:
        """
        Returns a list of characters listed in the comic
        Only present for comics
        May be empty even for comics
        """
        if(self.__characters == "Unset"):
            self.__characters = [i.next.text for i in self.__soup.find(
                text="Characters: ").find_next().contents]
        return self.__characters

    @property
    def exists(self) -> bool:
        return self.pageCount > 0

    @property
    def contentType(self) -> str:
        if(self.__contentType == "Unset"):
            self.__contentType = self.url.split("/")[3]
        return self.__contentType

    @property
    def handler(self) -> RequestHandler:
        return self.__handler

    def downloadContent(self, root: Path = Path("Albums/"), printProgress: bool = True):
        """
        Downloads all comic pages that don't already exist in the directory
        logging can be disabled by passing false to printProgress
        """
        Updated = 0
        existingStart = -1
        existingEnd = -1
        paths=[]
        if(isinstance(root,str)):
            root=Path(root)
        root = root.joinpath(sanitize_filepath(self.sanitizedName))
        root.mkdir(parents=True, exist_ok=True)
        fileList = os.listdir(root)
        if(self.contentType == "video"):
            fileName = sanitize_filepath(self.name)
            for file in fileList:
                if(file.startswith(fileName)):
                    if(printProgress):
                        print(f"{fileName} exists! skipping")
                    paths.append(Path(root,file))
                    break
            else:
                try:
                    r = self.__handler.get(
                        self.contentUrls[0], allow_redirects=True)
                    fileName = fileName + \
                        mimetypes.guess_extension(
                            r.headers['content-type'])
                    fpath = sanitize_filepath(Path(root, fileName))
                    # The final filepath is root/comic.sanitizedName/comic.sanitizedName.(guessed extension)
                    with open(fpath, "wb") as f:
                        f.write(r.content)
                    if(printProgress):
                        print(f'"{self.name}" done')
                    paths.append(fpath)
                except Exception as e:
                    fileName += "_SKIPPED"
                    fpath = sanitize_filepath(Path(root, fileName))
                    with open(fpath, "wb") as f:
                        pass
                    if(printProgress):
                        print(f'"{self.name}" skipped becuase {e}')
                    paths.append(fpath)
        else:
            for i in range(self.pageCount):
                fileName = sanitize_filepath(
                    f"{self.name}_{str(i).zfill(len(str(self.pageCount-1)))}")
                for file in fileList:
                    if(file.startswith(fileName)):
                        if(existingStart == -1):
                            existingStart = i
                        existingEnd = i
                        paths.append(Path(root,file))
                        break
                else:
                    Updated += 1
                    if(printProgress and existingStart != -1):
                        if(existingStart == existingEnd):
                            print(
                                f'"{self.name}" page {existingStart+1}/{self.pageCount} exists! skipping')
                        else:
                            print(
                                f'"{self.name}" page {existingStart+1} through {existingEnd+1} out of {self.pageCount} exists! skipping')
                        existingStart = existingEnd = -1
                    try:
                        r = self.__handler.get(
                            self.contentUrls[i], allow_redirects=True)
                        fileName = fileName + \
                            mimetypes.guess_extension(
                                r.headers['content-type'])
                        fpath = sanitize_filepath(Path(root, fileName))
                        with open(fpath, "wb") as f:
                            f.write(r.content)
                        if(printProgress):
                            print(
                                f'"{self.name}" page {i+1}/{self.pageCount} done')
                        paths.append(fpath)
                    except Exception as e:
                        fileName += "_SKIPPED"
                        fpath = sanitize_filepath(Path(root, fileName))
                        with open(fpath, "wb") as f:
                            pass
                        if(printProgress):
                            print(
                                f'"{self.name}" page {i+1}/{self.pageCount} skipped becuase {e}')
                        paths.append(fpath)
            if(printProgress):
                if(not Updated):
                    print(f'Downlaod "{self.__url}" finished with no updates')
                else:
                    print(
                        f'Download of "{self.__url}" done, {Updated} new pages found')
        return paths


class Webpage:

    """
    A Webpage class that bundles together everything related to <https://multporn.net>
    If you're confused what I mean by "webpage", this is an example (oviously NSFW): <https://multporn.net/category/cosplay>
    """

    def __init__(self, url):
        """
        initializing the webpage object
        """
        self.__url = url
        self.__soup = BeautifulSoup(requests.get(url).text, "html.parser")
        self.__name = self.__links = "Unset"

    @property
    def links(self) -> List[str]:
        """
        return all links found in this webpage
        """
        if (self.__links == "Unset"):
            self.__links = [urljoin(Multporn.HOME, i.a['href']) for i in self.__soup.find(
                "table", "views-view-grid").find_all("strong")]
        return self.__links

    @property
    def name(self) -> str:
        """
        Return the name of this webpage
        usually is a category, character, author, etc
        """
        if(self.__name == "Unset"):
            self.__name = self.__soup.find(
                "meta", attrs={"name": "dcterms.title"})["content"]
        return self.__name


@unique
class Sort(Enum):
    """
    Known search sort options. Defaults to `Relevant`.
    """
    Relevant = "search_api_relevance"
    Author = "Author"


@unique
class Types(Enum):
    """
    Known types of content
    """
    All = "All"
    Comics = "1"
    HentaiManga = "2"
    GayComics = "3"
    CartoonPictures = "4"
    HentaiPictures = "5"
    Games = "6"
    Flash = "7"
    CartoonVideos = "8"
    HentaiVideos = "9"
    GIFAnimations = "10"
    Rule63 = "11"
    AuthorsAlbums = "12"
    Humor = "13"


class Utils(object):
    """
    A class used to help with various multporn related tasks
    """

    @staticmethod
    def Search(query: str, page: int = 1, queryType: Types = Types.All, sort: Sort = Sort.Relevant, handler=RequestHandler(), returnMultporn: bool = False):
        """
        Return a list of `Multporn` objects on page `page` that match this search
        `query` sorted by `sort` filter by type with `queryType`
        """
        searchHome = urljoin(Multporn.HOME, "/search/")
        searchUrl = urljoin(
            searchHome, f"?search_api_views_fulltext={quote(query)}&type={queryType.value}&sort_by={sort.value}&page={page-1}")
        Response = handler.get(searchUrl)
        soup = BeautifulSoup(Response.text, "html.parser")
        try:
            links = [urljoin(Multporn.HOME, i.a['href']) for i in soup.find(
                "div", attrs={"class": "view-content"}).find_all("strong")]
        except AttributeError:
            return []
        if(returnMultporn):
            return [Multporn(link) for link in links]
        else:
            return links
