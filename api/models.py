from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.template.defaultfilters import slugify
from time import time


class Anime(models.Model):
    title = models.CharField(max_length=400)
    slug = models.SlugField(max_length=250, allow_unicode=True)
    mal_id = models.IntegerField(blank=True, null=True)
    synopsis = models.TextField(blank=True, null=True)
    english = models.CharField(max_length=400, blank=True, null=True)
    japanese = models.CharField(max_length=400, blank=True, null=True)
    synonyms = models.CharField(max_length=400, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    aired = models.CharField(max_length=50, blank=True, null=True)
    premiered = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    rating = models.CharField(max_length=100, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    genres = ArrayField(models.TextField(), blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} | {self.japanese}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.id} {self.title[:240]}"[:255])
        super(Anime, self).save()
        self.slug = slugify(f"{self.id} {self.title[:240]}"[:255])
        return super(Anime, self).save()


class Episode(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    number = models.CharField(max_length=20)
    title = models.CharField(max_length=400, blank=True, null=True)
    slug = models.SlugField(max_length=250, allow_unicode=True)
    description = models.TextField(blank=True, null=True)
    english_name = models.CharField(max_length=400, blank=True, null=True)
    default_name = models.CharField(max_length=400, blank=True, null=True)
    date = models.DateTimeField()
    image = models.URLField(blank=True, null=True)
    aired = models.CharField(max_length=50, blank=True, null=True)
    links = JSONField(blank=True, null=True)
    next = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='next_ep', blank=True, null=True)
    previous = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='prev_ep', blank=True, null=True)

    def __str__(self):
        return f"{self.anime.title} > Episode {self.number}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.id} {self.anime.title[:220]} Episode {self.number}"[:255])
        super(Episode, self).save()
        self.slug = slugify(f"{self.id} {self.anime.title[:220]} Episode {self.number}"[:255])
        return super(Episode, self).save()


class ApiToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} > {self.token}"
