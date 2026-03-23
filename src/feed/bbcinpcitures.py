from feed.utils import months
from feed.source import Entry, Source

from bs4 import BeautifulSoup
import datetime
from pathlib import Path

class BBCInPictures(Source):

    def __init__(self, data: Path):
        super().__init__(data)

    @property
    def url(self) -> str:
        return "https://www.bbc.co.uk/news/in_pictures"

    def _get_remote_entries(self, soup: BeautifulSoup):
        listitems = soup.find_all('li')
        remote_entries = {}

        for listitem in listitems:
            link = listitem.find('a')
            picture = listitem.find('picture')
            picture_url = ""
            if link is not None and picture is not None:
                for div in listitem.find_all("div"):
                    found = False
                    if div.text == "Posted":
                        for span in div.parent.find_all("span"):
                            if span.has_attr("aria-hidden"):
                                sdate = span.text.strip().lower()
                                if " " not in sdate:
                                    if "h" in sdate:
                                        d = datetime.timedelta(hours=int(sdate.split('h')[0]))
                                        date = datetime.datetime.now()-d
                                        date = datetime.date(date.year, date.month, date.day)
                                    elif 'd' in sdate:
                                        d = datetime.timedelta(days=int(sdate.split('d')[0]))
                                        date = datetime.date.today()-d
                                    else:
                                        date = datetime.datetime.now()
                                        date = datetime.date(date.year, date.month, date.day)
                                else:
                                    d, m = sdate.split(' ')
                                    d = int(d)
                                    m = months[m]
                                    y = datetime.date.today().year
                                    date = datetime.date(y, m, d)
                                img = picture.find('img')
                                if img is not None:
                                    picture_url = img["src"]
                                title = link.text
                                link = "https://www.bbc.co.uk"+link["href"]
                                entry = Entry(url=link, title=title, preview_image_url=picture_url)
                                if date in remote_entries:
                                    remote_entries[date].append(entry)
                                else:
                                    remote_entries[date] = [entry]
                                found = True
                                break
                    if found:
                        break

        return remote_entries