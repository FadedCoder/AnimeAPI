from celery.decorators import task
import celery
from .scrapers.animeapi import animeapi_scraper
from .scrapers.animepahe import animepahe_scraper


@task
def scrape_all():
    def status(res):
        scrape_all.backend.store_result(
            scrape_all.request.id, state=celery.states.PENDING, status="PROGRESS",
            result=res)
    animeapi_scraper(status)
    animepahe_scraper(status)
