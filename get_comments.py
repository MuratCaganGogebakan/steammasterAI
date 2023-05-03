import requests
from bs4 import BeautifulSoup
import json

def get_reviews(appid, params):
        url = 'https://store.steampowered.com/appreviews/'
        response = requests.get(url=url+appid, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        return response.json()

def get_n_reviews(appid, n=100):
    reviews = []
    cursor = '*'
    params = {
            'json' : 1,
            'filter' : 'all',
            'language' : 'english',
            'day_range' : 9223372036854775807,
            'review_type' : 'all',
            'purchase_type' : 'all'

            }

    while n > 0:
        params['cursor'] = cursor.encode()
        params['num_per_page'] = min(100, n)
        n -= 100

        response = get_reviews(appid, params)
        cursor = response['cursor']
        reviews += response['reviews']

        if len(response['reviews']) < 100: break

    reviews = [review['review'] for review in reviews]
    
    return clean_reviews(reviews)

def clean_reviews(reviews):
    # Remove non-ascii characters
    reviews = [review.encode('ascii', 'ignore').decode('ascii') for review in reviews]
    # Remove newlines
    reviews = [review.replace('\n', ' ') for review in reviews]
    # Remove too short reviews
    reviews = [review for review in reviews if len(review) > 200]
    # Delete words that are too long
    reviews = [review for review in reviews if len(max(review.split(' '), key=len)) < 20]
    return reviews


def get_game_name(appid):
    cookies = {'birthtime': '568022401'} # To bypass age check
    response = requests.get(url=f'https://store.steampowered.com/app/{appid}', headers={'User-Agent': 'Mozilla/5.0'}, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find(id='appHubAppName').text


def get_n_appids(n=1, filter_by='topsellers'):
    appids = []
    url = f'https://store.steampowered.com/search/?category1=998&filter={filter_by}&page='
    page = 0

    while page*25 < n:
        page += 1
        response = requests.get(url=url+str(page), headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find_all(class_='search_result_row'):
            appids.append(row['data-ds-appid'])

    return appids[:n]

reviews = {}
for appid in get_n_appids(500):
    print(appid)
    reviews[get_game_name(appid)] = get_n_reviews(appid, 25)

with open('reviews.json', 'w') as f:
    json.dump(reviews, f)


    