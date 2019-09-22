from celery.decorators import task
from celery import group
from datetime import datetime
import requests
import json
from api import models
from .utils import natural_keys, kwargs2dict
from bs4 import BeautifulSoup
import re


find_id_regex = re.compile(r"\/api\?m\=release\&id\=(\d+)")
mp4upload_id_regex = re.compile(r'https:\/\/mp4upload.com\/embed-(\w+).html')


def animepahe_scraper(status):
    r = requests.get('https://animepahe.com/anime')
    soup = BeautifulSoup(r.text, 'html.parser')
    z = soup.find_all('ul', attrs={'role': 'tabpanel'})
    y = []
    for i in z:
        y += i.find_all('li')
    rlist = {i.h2.string: 'https://animepahe.com'+i.h2.a.attrs.get('href') for i in y}
    rlist_items = list(rlist.items())
    for enum, (title, link) in enumerate(rlist_items):
        try:
            anime = models.Anime.objects.get(title=title)
        except models.Anime.DoesNotExist:
            continue
        r = requests.get(link)
        aid = find_id_regex.findall(r.text)[0]
        r = requests.get(f"https://animepahe.com/api?m=release&id={aid}&l=30&sort=episode_asc&page=1")  # noqa
        _eplist = json.loads(r.text).get('data', None)
        if _eplist is None:
            continue
        epdata = []
        for i in _eplist:
            links = []
            providers = ['kwik', 'mp4upload', 'streamango', 'openload']
            _link_set = [scrape_provider_for_links(i['id'], x) for x in providers]
            for _links in _link_set:
                if _links:
                    links += _links
            if links == []:
                continue
            epdata = [
                {
                    'title': i.get('title', ''),
                    'number': str(int(i['episode'])),
                    'videos': links,
                }
                for i in _eplist
            ]
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
            if prev.links:
                prev.links = prev.links + epr['videos']
            else:
                prev.links = epr['videos']
            prev.links = list({x['host']+x.get('quality', ''): x for x in prev.links}.values())
            prev.save()
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


def scrape_provider_for_links(id, provider):
    r = requests.get(f"https://animepahe.com/api?m=embed&id={id}&p={provider}")
    data = json.loads(r.text)
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
