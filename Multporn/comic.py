import mimetypes
import os
from pathlib import Path

import certifi
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath


class Comic:
    def __init__(self, url: str, parentTag: str = "p", parentClass: str = "jb-image", download=False):
        self.session = requests.sessions.Session()
        self.session.verify = certifi.where()
        self.home = "http://multporn.net/"
        self.url = requests.compat.urljoin(self.home, url)
        soup = BeautifulSoup(requests.get(self.url).text, "html.parser")
        self.imageUrls = [image.find("img")["src"]
                          for image in soup.find_all(parentTag, parentClass)]
        # Loading tags
        try:
            self.tags = [i.next.text for i in soup.find(
                text="Tags: ").find_next().contents]
            self.ongoing = "ongoing" in soup.find(
                text="Section: ").find_next().text.lower()
        except AttributeError:
            self.tags = None
        # Support for older pages that used og:title
        try:
            self.name = sanitize_filepath(
                soup.find("meta", attrs={"name": "dcterms.title"})["content"])
        except TypeError:
            self.name = sanitize_filepath(
                soup.find("meta", attrs={"property": "og:title"})["content"])
        if(download):
            self.downlaodImages(self)

    def __str__(self):
        return self.name

    def downlaodImages(self, output: bool = True, root: Path = Path("Comics/"), printProgress: bool = True):
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
                print(f'Downlaod "{self.url}" finished with no updates')
            else:
                print(
                    f'Download of "{self.url}" done, {Updated} new pages found')


class Utils:
    def fromWebpage(self, url):
        links = []
        global root
        url = input("The webpage to load links from : ")
        parsed = urlparse(url)
        soup = BeautifulSoup(requests.get(url, verify=False).text, "html.parser")
        root = sanitize_filepath(soup.find("meta", property="og:title")["content"])
        try:
            os.mkdir(f"Comics/{root}")
        except:
            pass
        for i in soup.find("table", "views-view-grid").find_all("strong"):
            links.append(f"{parsed[0]}://{parsed[1]}{i.a['href']}")
        return links
