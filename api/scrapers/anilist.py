import requests


def anilist_scraper():
    query = """
query (
    $page: Int
    $season: MediaSeason
    $seasonYear: Int
    $malIdIn: [Int]
    $aniIdIn: [Int]
    $sort: [MediaSort]
    $status: MediaStatus
  ) {
    Page (page: $page) {
      pageInfo {
        total
        currentPage
        lastPage
        hasNextPage
        perPage
      }
      media(
    season: $season,
    seasonYear: $seasonYear
    idMal_in: $malIdIn,
    id_in: $aniIdIn,
    sort: $sort
    status: $status
    isAdult: false
    ) {
        id
        description
        idMal
        title {
          romaji
          native
          english
        }
        studios {
          edges {
            node {
              name
            }
          }
    }
    format
        genres
        status
        coverImage {
          large
        }
        episodes
        startDate {
          year
          month
          day
        }
        nextAiringEpisode {
          id
          episode
          airingAt
          timeUntilAiring
        }
      }
    }
  }
    """
    variables = {}
    data = requests.post(
        "https://graphql.anilist.co",
        json={'query': query, 'variables': variables})
    return data.text


print(anilist_scraper())
