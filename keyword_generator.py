import requests
import dotenv
import os
import json
from time import sleep

dotenv.load_dotenv('env')

API_KEY = os.environ.get('OPENAI_API_KEY')

session = requests.Session()

basePrompt = [{
    "role": "system",
    "content": """Generate keywords for a game using reviews. 
    Don't generate too many keywords, just the most important ones.
    Don't responde with anything that is not a keyword, if there is no keyword write "None".
    Keywords should be general keywords for the game, not specific to a certain review.
    All keywords should be things that can be shared by multiple games.
    Don't write sentences, just write keywords.
    Use commas as separators.
    Example keywords: Multiplayer, Co-op, PVP, FPS, RPG, hours of gameplay, regular updates, 2D, 3D, puzzle, action, adventure, crafting, survival, sandbox, etc.
    Don't write unrelated keywords, like "fun" or "good".
    """,
}]

def make_request(userPrompt, systemPrompt):
    url = 'https://api.openai.com/v1/chat/completions'
    response = session.post(url, json={
        "model": "gpt-3.5-turbo",
        "messages": systemPrompt + [{"role": "user", "content": userPrompt}],
        "temperature": 0
    },
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    })
    return response.json()

def get_keywords(message):
    response = make_request(message, basePrompt)
    content = response['choices'][0]['message']['content']
    content = content.replace('.', '')
    content = content.lower().split(',')
    content = [x.strip() for x in content]
    return content

def read_reviews():
    with open('reviews.json', 'r') as f:
        reviewsdict = json.load(f)
    return reviewsdict

def aggregate_reviews(reviews):
    combined_reviews = []
    for review in reviews:
        if combined_reviews == []:
            combined_reviews.append(review)
        elif len(combined_reviews[-1]) < 2000 and (len(combined_reviews[-1]) + len(review)) < 2500:
            combined_reviews[-1] += review
        elif len(combined_reviews[-1]) > 2000:
            combined_reviews.append(review)
    return combined_reviews

def get_keywords_for_reviews():
    reviewsdict = read_reviews()
    for game in reviewsdict:
        print(game)
        combined_reviews = aggregate_reviews(reviewsdict[game])
        keywords = []
        for review in combined_reviews:
            keywords.extend(get_keywords(review))
            # Wait for rate limit
            sleep(21)
        for i in range(len(keywords)):
            if "keywords: " in keywords[i]:
                keywords[i] = keywords[i].replace("keywords: ", "")
        print(keywords)
        reviewsdict[game] = keywords
    return reviewsdict

if __name__ == "__main__":
    reviewsdict = get_keywords_for_reviews()
    with open('keywords.json', 'w') as f:
        json.dump(reviewsdict, f, indent=4)
