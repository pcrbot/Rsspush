import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
from feedparser import FeedParserDict
import peewee as pw
from .aiohttpx import get
BASE_URL = "https://rsshub.akiraxie.me/"


class Rss:
    def __init__(self, url: str, limit: int = 1) -> None:
        super().__init__()
        self.url = url
        self.limit = limit
        
    @property
    async def feed(self) -> FeedParserDict:
        ret = await get(self.url, params={'limit': self.limit,'timeout':5})
        return feedparser.parse(ret.content)

    @property
    async def feed_entries(self) -> Optional[List]:
        feed = await self.feed
        if len(feed.entries) != 0:
            return feed.entries
        else:
            return

    @property
    async def has_entries(self) -> bool:
        return (await self.feed_entries) is not None

    @staticmethod
    def format_time(timestr: str) -> str:
        try:
            struct_time = time.strptime(timestr, '%a, %d %b %Y %H:%M:%S %Z')
        except:
            struct_time = time.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ')
        dt = datetime.fromtimestamp(time.mktime(struct_time))
        return str(dt+timedelta(hours=8))

    @staticmethod
    def _get_rssdic(entry: FeedParserDict) -> Dict:
        ret = {'标题': entry.title,
               '时间': entry.updated,
               '链接': entry.link, }
        try:
            ret['时间'] = Rss.format_time(ret['时间'])
        except:
            pass
        return ret

    async def get_new_entry_info(self) -> Optional[Dict]:
        try:
            entries = await self.feed_entries
            return Rss._get_rssdic(entries[0])
        except:
            return None

    async def get_all_entry_info(self) -> Optional[List[Dict]]:
        try:
            ret = []
            entries = await self.feed_entries
            lmt=min(len(entries),self.limit)
            for entry in entries[:lmt]:
                entrydic = self._get_rssdic(entry)
                ret.append(entrydic)
            return ret
        except:
            return None

    @property
    async def last_update(self) -> Optional[str]:
        try:
            return (await self.get_new_entry_info())['时间']
        except:
            return None


db = pw.SqliteDatabase(
    os.path.join(os.path.dirname(__file__), 'rssdata.db')
)


class Rssdata(pw.Model):
    url = pw.TextField()
    name = pw.TextField()
    date = pw.TextField()
    group = pw.IntegerField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey('url', 'group')


def init():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'rssdata.db')):
        db.connect()
        db.create_tables([Rssdata])
        db.close()


init()
