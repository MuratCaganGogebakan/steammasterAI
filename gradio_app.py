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
        SystemMessage(content="Unless the game is completely unrelated to the input recommend it and start your answer with 'Yes'. If you definitely can't recommend it start with No. Don't say the game name in your response. Describe the game in your recommendation. Don't write in the first person. Don't say 'I recommend' or 'I don't recommend' start the desccription right after the Yes or No."),
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
    docs = docsearch.similarity_search_with_score(query, 5134)
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

iface2 = gr.Interface(
    fn=recommend_games,
    inputs=[
        gr.inputs.Textbox(lines=2, placeholder="Describe a game you would like", label="Game Description"),
        gr.inputs.Slider(minimum=1, maximum=10, step=1, default=5, label="Number of Games to Recommend"),
        gr.inputs.Checkbox(default=False, label="Recommend Least Similar Games")
    ],
    outputs="markdown",
    flagging_options=[("👍      Like", "Like"), ("👎      Dislike", "Dislike")]
)
#iface2.launch(auth=("username", "password"))
iface2.launch()
