import gradio as gr
import requests
from bs4 import BeautifulSoup
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
import os
import dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage
)

dotenv.load_dotenv('env')
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
PINECONE_API_ENV = os.environ['PINECONE_API_ENV']

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_API_ENV
)
index_name = "langchain" 

docsearch = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)

chat = ChatOpenAI(temperature=0)

def recommend_game(query, game_name):
    game_docs = docsearch.similarity_search(query, k=5, filter={"game": game_name})
    game_docs_content = " ".join(doc.page_content for doc in game_docs)
    game_docs_metadata = "Metadata: " + str(game_docs[0].metadata) if game_docs else ""
    messages = [
        SystemMessage(content="Unless the game is too bad, ALWAYS start your answer with 'Yes'. Otherwise, start with No. Describe the game in your response in a positive way without overdoing it. Don't write in the first person. Don't say 'I recommend' or 'I don't recommend' start the desccription right after the Yes or No."),
        HumanMessage(content=game_docs_content + " " + game_docs_metadata)
    ]
    answer = chat(messages)
    return answer.content 

def get_steam_url(game_name):
    game_name = game_name.replace(' ', '+')
    search_url = f"https://store.steampowered.com/search/?term={game_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_link = soup.find('a', {'class': 'search_result_row ds_collapse_flag'})
    if game_link:
        return game_link['href']
    else:
        return None

def generate_score_dict(docs):
    game_scores = {}
    for doc, score in docs:
        game_name = doc.metadata['game'][0]
        if game_name in game_scores:
            game_scores[game_name].append(score)
        else:
            game_scores[game_name] = [score]
    return game_scores

def recommend_least_similar_games(query, k=5):
    docs = docsearch.similarity_search_with_score(query, 10839)
    games = []
    similarity_scores = generate_score_dict(docs)
    seen = set()
    for doc, score in docs:
        game_name = doc.metadata["game"][0]
        if game_name not in seen:
            games.append(game_name)
            seen.add(game_name)
    recommendations = []
    counter = 0
    recommended_games = []
    for game in reversed(games):
        recommendation = recommend_game(query, game)
        print(recommendation)
        if recommendation.lower().strip().startswith("yes"):
            recommendations.append(recommendation[5:])
            recommended_games.append(game)
            counter += 1
        if counter >= k:
            break
    return recommendations, similarity_scores, recommended_games

def recommend_most_similar_games(query, k=5):
    docs = docsearch.similarity_search_with_score(query, 200)
    games = []
    similarity_scores = generate_score_dict(docs)
    seen = set()
    for doc, score in docs:
        game_name = doc.metadata["game"][0]
        if game_name not in seen:
            games.append(game_name)
            seen.add(game_name)
    recommendations = []
    counter = 0
    recommended_games = []
    for game in games:
        recommendation = recommend_game(query, game)
        print(recommendation)
        if recommendation.lower().strip().startswith("yes"):
            recommendations.append(recommendation[5:])
            recommended_games.append(game)
            counter += 1
        if counter >= k:
            break
    return recommendations, similarity_scores, recommended_games

def recommend_games(query, k=5, least_similar=False):
    if least_similar:
        recommendations, similarity_scores, recommended_games = recommend_least_similar_games(query, k)
    else:
        recommendations, similarity_scores, recommended_games = recommend_most_similar_games(query, k)
    
    formatted_recommendations = []
    for i, recommendation in enumerate(recommendations):
        game_name = recommended_games[i]
        steam_url = get_steam_url(game_name)
        
        if steam_url:
            game_title = f'<span style="text-decoration: none; cursor: pointer; color: inherit;" onclick="window.open(\'{steam_url}\',\'_blank\')">{game_name}</span>'
        else:
            game_title = game_name
        formatted_recommendation = f"## {i+1}. {game_title} (Similarity Score: {max(similarity_scores[game_name]):.2%})\n\n{recommendation}"
        formatted_recommendations.append(formatted_recommendation)
    
    return "\n".join(formatted_recommendations)

description="""
<h3>Welcome to the Game Recommendation System!</h3>
<p>Describe the type of game you're looking for, specify the number of games to recommend, and optionally choose to include least similar games. Click 'Submit' to get personalized game recommendations.</p>
<p>Please leave a review after testing the system: <a href='https://docs.google.com/forms/d/e/1FAIpQLSdc9eucovf6yKGGDDt9yFErvoPS129jNmuzK3S8wj2Acm_vkw/viewform' target='_blank'>Review Form</a></p>
"""
iface2 = gr.Interface(
    fn=recommend_games,
    inputs=[
        gr.inputs.Textbox(lines=2, placeholder="Write your game description here.", label="Describe a game you would like:"),
        gr.inputs.Slider(minimum=1, maximum=5, default=3,step=1, label="Number of Games to Recommend"),
    ],
    outputs="markdown",
    examples=[
        ["I'm looking for a sandbox-style game with pixelated graphics that offers both single-player and multiplayer modes. I enjoy games where I can explore and modify an open world, digging into the earth, gathering resources, and building structures. I want a game with a progression system that's tied to combating various bosses and enemies. The game should include crafting mechanics, allowing me to utilize the resources I gather to create new items, tools, and weapons. I'd also appreciate if the game had different biomes and events to keep the gameplay engaging and dynamic."],
        ["I want a game such that it offers an immersive first-person shooter (FPS) experience with a highly detailed and engrossing linear story. The game should excel at blending intense FPS gameplay with a captivating narrative that keeps me engaged throughout. I desire a world that feels alive, with a rich background that adds depth and complexity to the overall experience. Furthermore, I would appreciate the inclusion of optional story elements that allow me to explore the game's lore and history in greater detail."],
        ["I'm searching for a strategy game that requires tactical thinking and planning. I want a game that allows me to manage resources, build bases, and command units to engage in battles. It should also have both single-player and multiplayer modes, and I would like to have the ability to play against AI opponents as well. The game should offer a variety of maps, units, and tech upgrades, allowing for diverse gameplay. Additionally, I would prefer a game that features a well-thought-out storyline to provide context for the game's events."],
        ["I am in need of a horror game that is truly terrifying and atmospheric. It should be a single-player game, preferably played in a first-person perspective. I want it to be rich in narrative, with a story that's eerie, unsettling, and suspenseful. The game should contain survival elements such as managing health, inventory, and possibly sanity. It should also offer puzzle-solving elements that enhance the tension and fear. The graphics should be high-quality, and the sound design should be excellently crafted to contribute to the overall horror experience."],
        ["I crave a role-playing game (RPG) set in a vast open world with impressive 3D graphics. The game should allow me to fully customize my character, and the story should be influenced by my decisions and actions throughout the game. I want the game to offer a variety of quests and side missions, with an emphasis on exploration. The game should also feature a robust combat system, including a variety of weapons and spells. I appreciate it if there's a variety of NPCs with interesting backstories, adding to the richness of the game world."],
        ["I'm after an action-adventure game with platforming elements set in a rich, colorful world. The game should offer a well-balanced mix of exploration, combat, and puzzle-solving. It should have a compelling story that unfolds as I progress, and it's essential that the characters are likable and well-developed. I would also like a game with a progression system that allows me to unlock new abilities or power-ups as I advance. The game should ideally have smooth and responsive controls, and the graphics should be vibrant and engaging."],
        ["I'm interested in a racing game with a realistic driving experience. It should feature a variety of cars and tracks, and the graphics should be high-quality to enhance the sense of speed and immersion. I'm looking for a game that provides both single-player and multiplayer modes, including competitive races and time trials. It would be great if the game also offered customization options for cars and had a progression system for unlocking new vehicles and tracks. Weather changes and day-night cycles for added realism would be a plus."],
        ["I'm seeking a puzzle game that really challenges my thinking and problem-solving skills. The game should have a variety of puzzle types and a progressive difficulty curve. A relaxing soundtrack and aesthetically pleasing visuals are a must. I would also appreciate it if there was some form of narrative or theme tying the puzzles together. I don't necessarily need a multiplayer mode, but some form of leaderboard to compare scores or times with other players could be interesting."]    
        ],
    title="SteammmasterAI",
    description=description,
    allow_flagging=True,
    flagging_options=[("👍 Like", "Like"), ("👎 Dislike", "Dislike")],
    submit_button="Get Recommendations"
)

iface2.launch(auth=("testuser", "password"))
