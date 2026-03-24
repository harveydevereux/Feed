from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from pathlib import Path
from bs4 import BeautifulSoup
from urllib import request
import datetime
from pathlib import Path
import yaml
from typing import Tuple
import logging
from time import time

@dataclass(kw_only=True)
class Entry():
    title: str
    url: str
    preview_image_url: str = ""

class Source(ABC):

    def __init__(self, data: Path):
        start = time()
        self.log = logging.getLogger(__name__)
        logging.basicConfig(filename=data/"feed.log", level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        self.log.info(f"  Initialising {self.name}")

        self._data = data / f"{self.id}.yml"
        self._entries = {}
        self._remote_entries = {}
        if self._data.exists():
            with open(self._data, "r", encoding="utf-8") as io:
                raw_entries = yaml.safe_load(io)

            if raw_entries is not None:
                for date in raw_entries:
                    self._entries[datetime.date.fromisoformat(date)] = [Entry(**entry) for entry in raw_entries[date]]

        self.log.info(f"    Took: {round(time()-start, 2)} s")

    @property
    def _remote_can_be_empty(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    def id(self) -> str:
        return type(self).__name__.lower()

    @property
    def entries(self) -> dict:
        return self._entries

    @property
    def urls(self) -> set:
        return set(entry.url for _, entries in self._entries.items() for entry in entries)

    @property
    @abstractmethod
    def url(self) -> str:
        return NotImplemented

    def get(self):
        start = time()
        self.log.info(f"  Getting {self.name}")
        page = request.urlopen(self.url)
        data = page.read()
        soup = BeautifulSoup(data, 'html.parser')
        self._remote_entries = self._get_remote_entries(soup)

        if not self._remote_can_be_empty and len(self._remote_entries) == 0:
            self.log.warning(f"Warning {self.name} found no sources.")

        self.log.info(f"    Took: {round(time() - start, 2)} s")

    def new_entries(self) -> list[Tuple[datetime.date, Entry]]:
        new = []
        seen_urls = set(entry.url for date in self.entries for entry in self.entries[date])
        for date, entries in self._remote_entries.items():
            for entry in entries:
                if entry.url not in seen_urls:
                    new.append((date, entry))
        return new

    def commit(self):
        seen_urls = set(entry.url for date in self.entries for entry in self.entries[date])
        for date, entries in self._remote_entries.items():
            for entry in entries:
                if entry.url not in seen_urls:
                    if date in self._entries:
                        self._entries[date].append(entry)
                    else:
                        self._entries[date] = [entry]

        with open(self._data, "w", encoding="utf-8") as io:
            data = {}
            for date, entries in self._entries.items():
                data[str(date)] = [asdict(entry) for entry in entries]
            yaml.dump(data, io)

    @abstractmethod
    def _get_remote_entries(self, soup: BeautifulSoup) -> dict:
        return NotImplemented