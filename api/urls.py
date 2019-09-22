from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('scrape-all/', views.scrape_all, name='scrape_all'),
    # API URLs
    path('anime/<int:anime_id>/', views.get_anime_by_id, name='anime_by_id'),
    path('anime/slug/<str:slug>/', views.get_anime_by_slug, name='anime_by_slug'),
    path('episode/<int:episode_id>/', views.get_episode_by_id, name='episode_by_id'),
    path('episode/slug/<str:slug>/', views.get_episode_by_slug, name='episode_by_slug'),
    path('anime/<int:anime_id>/episodes/', views.all_episodes_by_id, name='all_episodes_by_id'),
    path('anime/slug/<str:slug>/episodes/', views.all_episodes_by_slug, name='all_episodes_by_slug'),
    path('anime/search/', views.search, name='search'),
    path('genre/', views.list_genres, name='all_genres'),
]
