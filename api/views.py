from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.db.models import F
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from time import sleep
import logging
import json
import datetime
from . import backend
from . import models
from .decorators import api_login_required


logger = logging.getLogger(__name__)

scrape_all_result = None


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def scrape_all(request):
    global scrape_all_result
    if scrape_all_result is None:
        result = backend.scrape_all.delay()
        scrape_all_result = result
        return HttpResponse("Started scrape. Refresh to check results.")
    else:
        result = scrape_all_result.result
        try:
            result = '\n'.join([': '.join(i) for i in result.items()]) if result else ""
        except AttributeError:
            scrape_all_result = None
            return HttpResponse("Faced an error. Stopping...")
        if scrape_all_result.ready():
            scrape_all_result = None
            return HttpResponse("Done!\n\n"+result)
        else:
            return HttpResponse("Not done yet!\n\n"+result)


@api_login_required
def get_anime_by_id(request, anime_id):
    try:
        anime = models.Anime.objects.get(id=anime_id)
        data = model_to_dict(anime)
        resp = {
            'status': 'FOUND',
            'data': data
        }
        status = 200
    except models.Anime.DoesNotExist:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def get_anime_by_slug(request, slug):
    try:
        anime = models.Anime.objects.get(slug=slug)
        data = model_to_dict(anime)
        resp = {
            'status': 'FOUND',
            'data': data
        }
        status = 200
    except models.Anime.DoesNotExist:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def get_episode_by_id(request, episode_id):
    try:
        episode = models.Episode.objects.get(id=episode_id)
        data = model_to_dict(episode)
        resp = {
            'status': 'FOUND',
            'data': data
        }
        status = 200
    except models.Episode.DoesNotExist:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def get_episode_by_slug(request, slug):
    try:
        episode = models.Episode.objects.get(slug=slug)
        data = model_to_dict(episode)
        resp = {
            'status': 'FOUND',
            'data': data
        }
        status = 200
    except models.Episode.DoesNotExist:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def all_episodes_by_id(request, anime_id):
    try:
        anime = models.Anime.objects.get(id=anime_id)
        data = list(anime.episode_set.all().values())
        resp = {
            'status': 'FOUND',
            'data': data
        }
        status = 200
    except models.Anime.DoesNotExist:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def all_episodes_by_slug(request, slug):
    try:
        anime = models.Anime.objects.get(slug=slug)
        data = list(anime.episode_set.all().values())
        resp = {
            'status': 'FOUND',
            'data': data
        }
        status = 200
    except models.Anime.DoesNotExist:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def search(request):
    accepted = ['type', 'status', 'premiered', 'order', 'limit', 'keywords', 'genre', 'latest', 'token']
    filter_attrs = {}
    order_attrs = []
    limit = None
    valid_args = True
    for k, v in request.GET.items():
        if k not in accepted:
            valid_args = False
            continue
        if k in ['type', 'status', 'premiered']:
            filter_attrs.update({k+'__icontains': v.lower()})
        if k == 'order':
            okey, otype = v.split(',')
            otype = '-' if otype == 'desc' else ''
            order_attrs.append(otype+okey)
        if k == 'limit' and v.isdigit():
            limit = int(v)
        if k == 'genre':
            genres = v.split(',')
            filter_attrs.update({'genres__contains': genres})
        if k == 'latest':
            if v == 'today':
                filter_attrs.update({'date__gte': datetime.date.today()})
            elif v == 'yesterday':
                yesterday = datetime.date.today()-datetime.timedelta(days=1)
                filter_attrs.update({'date__gte': yesterday, 'date__lt': datetime.date.today()})
            else:
                filter_attrs.update({'date__gte': v})
    if not valid_args:
            resp = {
                'status': 'ERROR',
                'error': 'Invalid GET parameters!',
            }
            status = 403
            return JsonResponse(resp, status=status)
    keywords = request.GET.get('keywords')
    query = models.Anime.objects
    if keywords:
        if len(keywords) <= 3:
            resp = {
                'status': 'ERROR',
                'error': 'Keyword length must be greater than 3!',
            }
            status = 403
            return JsonResponse(resp, status=status)
        else:
            query = query.annotate(
                similarity=TrigramSimilarity('title', keywords))
            query = query.filter(similarity__gt=0.3).order_by('-similarity')
    query = query.filter(**filter_attrs)
    query = query.order_by(*order_attrs)
    if limit:
        query = query[:limit]
    if len(query) == 0:
        resp = {
            'status': 'NOT FOUND',
        }
        status = 404
    else:
        resp = {
            'status': 'FOUND',
            'data': list(query.values()),
        }
        status = 200
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def latest_anime(request, num):
    data = {
        'ongoing': [{'id': i['anime']} for i in
                    models.Episode.objects.filter(anime__status='ongoing').order_by('anime', '-date').values('anime').distinct('anime')[:num]],  # noqa,
        'latest': [{'id': i['anime']} for i in
                   models.Episode.objects.order_by('anime', '-date').values('anime').distinct('anime')[:num]],  # noqa
    }
    resp = {
        'status': 'FOUND',
        'data': data,
    }
    status = 200
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})


@api_login_required
def list_genres(request):
    genre_list = []
    for g in models.Anime.objects.all():
        genre_list += g.genres
    genre_list = list(set(genre_list))
    resp = {
        'status': 'FOUND',
        'data': genre_list
    }
    status = 404
    return JsonResponse(resp, status=status, json_dumps_params={'indent': 2})
