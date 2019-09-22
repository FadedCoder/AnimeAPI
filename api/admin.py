from django.contrib import admin
from django import forms
from django_admin_json_editor import JSONEditorWidget
from . import models


class EpisodeForm(forms.ModelForm):
    class Meta:
        model = models.Episode
        fields = '__all__'
        DATA_SCHEMA = {
            "type": "array",
            "format": "table",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "title": "Video ID",
                        "type": "string",
                    },
                    "host": {
                        "title": "Video Host",
                        "type": "string",
                    },
                    "date": {
                        "title": "Date",
                        "type": "string",
                    },
                    "type": {
                        "type": "array",
                        "format": "checkbox",
                        "uniqueItems": True,
                        "items": {
                            "type": "string",
                            "enum": ["subbed", "dubbed"]
                        }
                    },
                    "quality": {
                        "title": "Quality",
                        "type": "string",
                    }
                }
            }
        }
        widgets = {
            'links': JSONEditorWidget(DATA_SCHEMA, collapsed=False),
        }


class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm
    raw_id_fields = ['next', 'previous']
    search_fields = ['number', 'slug', 'title', 'anime__title']


class AnimeForm(forms.ModelForm):
    class Meta:
        model = models.Anime
        fields = '__all__'


class AnimeAdmin(admin.ModelAdmin):
    form = AnimeForm
    search_fields = ['slug', 'title', 'mal_id', 'genres']


# Register your models here.
admin.site.register(models.Anime, AnimeAdmin)
admin.site.register(models.Episode, EpisodeAdmin)
admin.site.register(models.ApiToken)
