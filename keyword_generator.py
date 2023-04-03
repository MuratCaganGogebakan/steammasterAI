import requests
import dotenv
import os

dotenv.load_dotenv('env')

API_KEY = os.environ.get('OPENAI_API_KEY')

session = requests.Session()

basePrompt = [{
    "role": "system",
    "content": """I need to categorize 500 steam games using only comments of them. I need to start by identifying keywords. 
    Don't write anything that is not a keyword, if there is no keyword write "None".
    I will use those keywords to index games in a database.
    The keywords should be general keywords for the game, not specific to a certain review.
    All keywords should be things that can be shared by multiple games.
    Don't write sentences, just write keywords.
    Separate keywords with commas.
    Example keywords: Multiplayer, Co-op, PVP, FPS, RPG, hours of gameplay, regular updates, 2D, 3D, puzzle, action, adventure, crafting, survival, sandbox, etc.
    Don't write keywords that are unrelated to the game.
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
    with open('reviews.txt', 'r') as f:
        reviews = f.read().split('__review_end__')
    return reviews

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
    combined_reviews = aggregate_reviews(read_reviews())
    keywords = []
    for review in combined_reviews:
        keywords.extend(get_keywords(review))
    for i in range(len(keywords)):
        if "keywords: " in keywords[i]:
            keywords[i] = keywords[i].replace("keywords: ", "")
    return keywords

if __name__ == "__main__":
    print(get_keywords_for_reviews())
#     print(get_keywords("""Other developers: Promise to update their game, never update it.

# Terraria developers: Promise to stop updating their game, update it anyways.
# Other developers: Promise to update their game, never update it.

# Terraria developers: Promise to stop updating their game, update it anyways.
# pretty fun, just discovered this cool boss called the "Wall of Flesh"
# i like when eye of cthulhu goes urraaeuh
# spawn in, talk to the videogame equivalent of wikipedia, kill slimes and cut trees. fight a floating eyeball, a huge worm, and a giant skeleton. loot a religious gravesite and arm yourself with a lightsaber and a machinegun-shark. then go to hell and fight a wall of flesh that shoots lasers. build a wooden commie block for npcs like an enviromentalist, a furry or a terrorist. fight floating eyeball, huge worm, and giant skeleton again, but this time they're made of metal and shoot lasers. kill a giant plant and terrorize an ancient underground civilization to summon their guardian diety. survive an invasion from goblins, pirates, aliens, and 20th century classic horror movie monsters. go back to religious gravesite and murder all its followers, then fight their priest. arm yourself with a nyan cat sword and a machinegun-dolphin and fight off a galactic invasion, then kill the god of the universe.

# repeat for 1000+ hours, 10/10 one of the best videogames of all time
# Devs promised the game's getting its last update 2 years ago. Still continues to release amazing updates to this day. One of the most based games ever made.
# you can fish
# got my friends terraria 4-pack

# never played with any of them

# 10/10 cures loneliness
# one of the greatest games i've ever played
# 2,300 hours in and i still am nowhere near sick of it
# for new player drop the guide voodoo doll in lava in hell for gold
# Those who call it 2D Minecraft are simply weak...


# """))

