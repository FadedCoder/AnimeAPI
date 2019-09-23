from django.contrib import admin
from django import forms
from . import models


class EpisodeForm(forms.ModelForm):
    class Meta:
        model = models.Episode
        fields = '__all__'


class LinkAdminInline(admin.TabularInline):
    model = models.Link


class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm
    inlines = [LinkAdminInline]
    raw_id_fields = ['next', 'previous', 'anime']
    search_fields = ['number', 'slug', 'title', 'anime__title']
    list_filter = ['anime__title']
    suit_list_filter_horizontal = ['anime__title']


class AnimeForm(forms.ModelForm):
    class Meta:
        model = models.Anime
        fields = '__all__'


class AnimeAdmin(admin.ModelAdmin):
    form = AnimeForm
    search_fields = ['slug', 'title', 'mal_id', 'genres']


class LinkForm(forms.ModelForm):
    class Meta:
        model = models.Link
        fields = '__all__'


class LinkAdmin(admin.ModelAdmin):
    form = LinkForm
    raw_id_fields = ['episode']


# Register your models here.
admin.site.register(models.Anime, AnimeAdmin)
admin.site.register(models.Episode, EpisodeAdmin)
admin.site.register(models.Link, LinkAdmin)
admin.site.register(models.ApiToken)
