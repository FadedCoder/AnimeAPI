from datetime import datetime
import requests
import json
from api import models
from .utils import natural_keys, kwargs2dict


def animeapi_scraper(status):
    status({"percent_done": '0%', "status": "Fetching data and loading..."})
    r = requests.get('https://animeapi.com/anime')
    data = json.loads(r.text)['data']
    for i, r in enumerate(data):
        try:
            aniem, created = models.Anime.objects.update_or_create(
                title=r.get('title'), type=r.get('type'),
                defaults=kwargs2dict(
                    title=r.get('title'), synopsis=r.get('synopsis'), english=r.get('english'),
                    japanese=r.get('japanese'), synonyms=r.get('synonyms'), type=r.get('type'),
                    premiered=r.get('premiered'), duration=r.get('duration'),
                    image=r.get('image'), status=r.get('status'), rating=r.get('rating'),
                    aired=r.get('aired'), score=float(r.get('score', 0.0) or 0.0),
                    mal_id=int(r.get('mal_id', 0) or 0), total=int(r.get('total', 0 or 0)),
                    genres=[i.strip() for i in r.get('genres', '').split(',')],
                    date=datetime.strptime(r['date'], '%Y-%m-%d %H:%M:%S') if r['date'] else None,
                )
            )
        except models.Anime.MultipleObjectsReturned as e:
            print(r)
            print(e)
            raise models.Anime.MultipleObjectsReturned
        _epdata = None
        if created or int(r.get('total', 0) or 0) != aniem.total:
            got_data = False
            while not got_data:
                try:
                    re = requests.get(f'https://animeapi.com/anime/{r["id"]}/episodes')
                    got_data = True
                except requests.exceptions.RequestException:
                    status({
                        "percent_done": f'{i/len(data)*100:.2f}%',
                        "status": f"Faced error in anime {r['title']}. Retrying in 10s."
                    })
            _epdata = json.loads(re.text).get('data')
        if _epdata:
            epdata = []
            for z in _epdata:
                if z and z['number'] and '-' not in z['number']:
                    epdata.append(z)
            prev = None
            eplist = []
            for epr in sorted(epdata, key=natural_keys):
                prev, _ = models.Episode.objects.update_or_create(
                    anime=aniem, number=(epr.get('number', '0') or '0'),
                    defaults=kwargs2dict(
                        number=(epr.get('number', '0') or '0'), anime=aniem,
                        title=epr.get('title'), description=epr.get('description'),
                        english_name=epr['name'].get('english'),
                        default_name=epr['name'].get('default'), image=epr.get('image'),
                        aired=epr.get('aired'), previous=prev,
                        date=datetime.strptime(r['date'], '%Y-%m-%d %H:%M:%S') if r['date'] else None  # noqa
                    )
                )
                for x in epr['videos']:
                    models.Link.objects.update_or_create(
                        episode=prev, host=x['host'], type=x['type'], quality=x.get('quality'),
                        defaults=kwargs2dict(video_id=x['id']))
                eplist.append(prev)
            next = None
            for epr in reversed(eplist):
                epr.next = next
                next = epr
                epr.save()
        status({
            "percent_done": f'{i/len(data)*100:.2f}%',
            "status": f"AnimeAPI: Uploading anime {r['title']} and it's episodes. Done {i}/{len(data)}."
        })
