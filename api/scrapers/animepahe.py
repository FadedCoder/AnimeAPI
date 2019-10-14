from celery.decorators import task
from celery import group
from datetime import datetime
from api import models
from bs4 import BeautifulSoup
from .utils import natural_keys, kwargs2dict
import asyncio
import aiohttp
import json
import re


find_id_regex = re.compile(r"\/api\?m\=release\&id\=(\d+)")
mp4upload_id_regex = re.compile(r'https:\/\/mp4upload.com\/embed-(\w+).html')


def animepahe_scraper(status):
    asyncio.run(_animepahe_scraper(status))


async def _animepahe_scraper(status):
    async with aiohttp.ClientSession() as sess:
        await _scrape_all(status, sess)


async def _scrape_all(status, sess):
    async with sess.get('https://animepahe.com/anime') as resp:
        rtext = await resp.text()
    soup = BeautifulSoup(rtext, 'html.parser')
    z = soup.find_all('ul', attrs={'role': 'tabpanel'})
    y = []
    for i in z:
        y += i.find_all('li')
    rlist = {i.h2.string: 'https://animepahe.com'+i.h2.a.attrs.get('href') for i in y}
    rlist_items = list(rlist.items())
    for enum, (title, link) in enumerate(rlist_items):
        try:
            anime = models.Anime.objects.get(title=title)
        except (models.Anime.DoesNotExist, models.Anime.MultipleObjectsReturned):
            continue
        async with sess.get(link) as resp:
            rtext = await resp.text()
        aid = find_id_regex.findall(rtext)
        if len(aid) >= 1:
            aid = aid[0]
        else:
            continue
        async with sess.get(f"https://animepahe.com/api?m=release&id={aid}&l=30&sort=episode_asc&page=1") as resp:  # noqa
            _eplist = await resp.json()
        _eplist = _eplist.get('data', None)
        if _eplist is None:
            continue
        epdata = []
        for i in _eplist:
            links = []
            providers = ['kwik', 'mp4upload', 'streamango', 'openload']
            _link_set = [await scrape_provider_for_links(i['id'], x, sess) for x in providers]
            for _links in _link_set:
                if _links:
                    links += _links
            if links == []:
                continue
            epn = i['episode']
            if epn.isdigit():
                epn = int(epn)
            elif epn.replace('.','',1).isdigit() and epn.count('.') < 2:
                epn = float(epn)
            epdata.append(
                {
                    'title': i.get('title', ''),
                    'number': str(epn),
                    'videos': links,
                }
            )
        prev = None
        eplist = []
        for epr in sorted(epdata, key=natural_keys):
            try:
                prev, _ = models.Episode.objects.update_or_create(
                    anime=anime, number=(epr.get('number', '0') or '0'),
                    defaults=kwargs2dict(
                        number=(epr.get('number', '0') or '0'), anime=anime,
                        title=epr.get('title'), previous=prev,
                        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                )
            except models.Episode.MultipleObjectsReturned:
                continue
            for x in epr['videos']:
                models.Link.objects.update_or_create(
                    episode=prev, host=x['host'], type=x['type'], quality=x.get('quality'),
                    defaults=kwargs2dict(
                        video_id=x['id'], episode=prev, host=x['host'],
                        type=x['type'], quality=x.get('quality'), date=x['date']
                    )
                )
            eplist.append(prev)
        next = None
        for epr in reversed(eplist):
            epr.next = next
            next = epr
            epr.save()
        status({
            "percent_done": f'{enum/len(rlist_items)*100:.2f}%',
            "status": f"Animepahe: Uploading anime {title} and it's episodes. Done {enum}/{len(rlist_items)}."  # noqa
        })


async def scrape_provider_for_links(id, provider, sess):
    async with sess.get(f"https://animepahe.com/api?m=embed&id={id}&p={provider}") as resp:  # noqa
        data = await resp.json()
    if data == []:  # Provider does not work for this anime.
        return
    _ed = list(data['data'].values())[0]

    def get_id(id):
        if provider == 'mp4upload':
            return mp4upload_id_regex.findall(id)[0]
        else:
            return id.split('/')[-1]
    links = [{
        'id': get_id(v['url']),
        'quality': quality,
        'host': provider,
        'type': 'subbed',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    } for quality, v in _ed.items()]
    return links
