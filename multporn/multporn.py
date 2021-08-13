import mimetypes
from enum import Enum, unique
from functools import cached_property
from pathlib import Path
from typing import List, Tuple, Union
from urllib.parse import quote, urljoin
from urllib.request import getproxies

import requests
from bs4 import BeautifulSoup
from faker import Faker
from pathvalidate import sanitize_filepath
from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from tqdm import tqdm, trange
from urllib3.util.retry import Retry


class RequestHandler(object):
    """
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

    @cached_property
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

    @cached_property
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
    A `multporn <https://multporn.net>`__ comic class

    Basic Usage:
        >>> from multporn import Multporn
        >>> comic = Multporn("https://multporn.net/comics/between_friends")
        >>> print(comic)
        'Between Friends'
    """
    HOME = "https://multporn.net/"

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
        if(download):
            self.downloadContent()

    def __str__(self):
        """
        returns the name of the Multporn object
        """
        return self.name

    @cached_property
    def contentUrls(self) -> List[str]:
        """
        Return the content url of the Multporn object
        for picture albums and comics will return a list of images
        for videos will return an array with the video file link in the first index
        """
        if(self.contentType == "video"):
            return [self.__soup.find("video").source["src"]]
        else:
            return [image.find("img")["src"] for image in self.__soup.find_all("p", "jb-image")]

    @cached_property
    def tags(self) -> List[str]:
        """
        Returns a list of tags empty if non found
        """
        try:
            return [i.next.text for i in self.__soup.find(text="Tags: ").find_next().contents]
        except AttributeError:
            return []

    @cached_property
    def ongoing(self) -> bool:
        """
        Returns true if the Multporn object is ongoing
        Only use with comics and mangas as the concept is meaningless for videos
        """
        try:
            return "ongoing" in self.__soup.find(text="Section: ").find_next().text.lower()
        except AttributeError:
            return False

    @cached_property
    def name(self) -> str:
        """
        Returns the name of the Multporn object
        """
        return self.__soup.find("meta", attrs={"name": "dcterms.title"})["content"]

    @cached_property
    def sanitizedName(self) -> str:
        """
        Return the sanitized name of the Multporn object
        """
        return sanitize_filepath(self.name)

    @cached_property
    def url(self) -> str:
        """
        Returns the url associated with the Multporn object
        """
        return self.__url

    @cached_property
    def thumbnail(self) -> str:
        """
        Returns the thumbnail of the Multporn object
        For picture album such as comics and mangas, it's the first page of the album
        For videos, a screenshot generated by the website itself
        """
        if(self.contentType == "video"):
            return self.__soup.find("video")["poster"]
        else:
            try:
                return self.contentUrls[0]
            except:
                return

    @cached_property
    def pageCount(self) -> int:
        """
        Return the number of pages
        Always 1 for videos
        """
        return len(self.contentUrls)

    @cached_property
    def artists(self) -> List[str]:
        """
        Return a list of artists
        only present for comics
        most likely a single artist but multiple artists are possible
        """
        return [i.next.text for i in self.__soup.find(text="Author: ").find_next().contents]

    @cached_property
    def sections(self) -> List[str]:
        """
        Returns a list of sections that this comic is present in
        only present for comics
        Most likely a single section but multiple sections are possible
        """
        return [i.next.text for i in self.__soup.find(text="Section: ").find_next().contents]

    @cached_property
    def characters(self) -> List[str]:
        """
        Returns a list of characters listed in the comic
        Only present for comics
        May be empty even for comics
        """
        return [i.next.text for i in self.__soup.find(text="Characters: ").find_next().contents]

    @cached_property
    def exists(self) -> bool:
        """
        Returns the existence status of the Multporn object
        """
        try:
            return self.pageCount > 0
        except:
            return False

    @cached_property
    def contentType(self) -> str:
        """
        Returns the content type of the Multporn object as a string
        """
        return self.url.split("/")[3]

    @cached_property
    def handler(self) -> RequestHandler:
        """
        Returns the handler of the Multporn object
        """
        return self.__handler

    def downloadContent(self, root: Union[Path, str] = Path("Albums"), printProgress: bool = True):
        """
        Downloads all comic pages that don't already exist in the directory
        Logging can be disabled by passing false to printProgress
        """
        paths = []
        if(isinstance(root, str)):
            root = Path(root)
        root = root.joinpath(sanitize_filepath(self.sanitizedName))
        root.mkdir(parents=True, exist_ok=True)
        if(self.contentType == "video"):
            url = self.contentUrls[0]
            fpath = root.joinpath(self.sanitizedName)
            printName = self.name
            r = self.handler.get(url, stream=True)
            fpath = fpath.with_suffix(
                mimetypes.guess_extension(r.headers['content-type']))
            total_size_in_bytes = int(
                r.headers.get('content-length', 0))
            with tqdm(total=total_size_in_bytes, disable=not printProgress, unit='iB', unit_scale=True, desc=self.name) as tq:
                with open(sanitize_filepath(fpath), 'wb') as file:
                    for data in r.iter_content(1024):
                        tq.update(len(data))
                        file.write(data)
                if total_size_in_bytes != 0 and tq.n != total_size_in_bytes:
                    with open(sanitize_filepath(fpath.with_name(fpath.name + "_SKIPPED")), "wb") as _:
                        pass
                    tq.set_description(f'{printName} skipped')
                    paths.append(fpath)
                else:
                    paths.append(fpath)
        else:
            with trange(len(self.contentUrls), disable=not printProgress, desc=self.name) as tq:
                for i in tq:
                    fpath = root.joinpath(
                        f"{self.sanitizedName}_{str(i).zfill(len(str(self.pageCount-1)))}")
                    printName = f'"{self.name}" page {i+1}/{self.pageCount}'
                    globResult = list(root.glob(f"{fpath.name}*"))
                    if(globResult):
                        tq.set_description(f"{printName} exists")
                        paths.append(globResult[0])
                        continue
                    else:
                        try:
                            r = self.handler.get(self.contentUrls[i])
                            fpath = fpath.with_suffix(
                                mimetypes.guess_extension(r.headers['content-type']))
                            with open(sanitize_filepath(fpath), "wb") as f:
                                f.write(r.content)
                            tq.set_description(f'{printName} done')
                            paths.append(fpath)
                        except Exception as e:
                            with open(sanitize_filepath(fpath.with_name(fpath.name + "_SKIPPED")), "wb") as _:
                                pass
                            tq.set_description(
                                f'{printName} skipped because {e}')
                            paths.append(fpath)
        return paths


class Webpage:

    """
    A Webpage class that bundles together everything related to <https://multporn.net>
    If you're confused what I mean by "webpage", this is an example (obviously NSFW): <https://multporn.net/category/cosplay>
    """

    def __init__(self, url):
        """
        initializing the webpage object
        """
        self.__url = url
        self.__soup = BeautifulSoup(requests.get(url).text, "html.parser")
        self.__name = self.__links = "Unset"

    @cached_property
    def links(self) -> List[str]:
        """
        return all links found in this webpage
        """
        if (self.__links == "Unset"):
            self.__links = [urljoin(Multporn.HOME, i.a['href']) for i in self.__soup.find(
                "table", "views-view-grid").find_all("strong")]
        return self.__links

    @cached_property
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
    def Search(query: str, page: int = 1, queryType: Types = Types.All, sort: Sort = Sort.Relevant, handler=RequestHandler()):
        """
        Return a dict with 2 keys link, thumb and name
        searches on page `page` that match this search `query` sorted by `sort`
        filter by type with `queryType`
        """
        searchHome = urljoin(Multporn.HOME, "/search/")
        searchUrl = urljoin(
            searchHome, f"?views_fulltext={quote(query)}&type={queryType.value}&sort_by={sort.value}&page={page-1}")
        Response = handler.get(searchUrl)
        soup = BeautifulSoup(Response.text, "html.parser")
        # links
        try:
            links = [urljoin(Multporn.HOME, i.a['href']) for i in soup.find(
                "div", attrs={"class": "view-content"}).find_all("strong")]
        except AttributeError:
            return []
        # thumbs
        thumbs = soup.find(
            "div", attrs={"class": "view-content"}).find_all("img")
        try:
            thumbs = [i['src'] for i in thumbs]
        except:
            thumbs = thumbs[1::2]
            thumbs = [i['src'] for i in thumbs]
        # names
        names = [i.string for i in soup.find(
            "div", attrs={"class": "view-content"}).find_all("strong")]
        r = []
        for i in range(len(links)):
            r.append({"link": links[i], "thumb": thumbs[i], "name": names[i]})
        return r
