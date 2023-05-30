import gradio as gr
from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone
import os
import dotenv
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
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

def generate_score_dict(docs):
    game_scores = {}
    for doc, score in docs:
        game_name = doc.metadata['game'][0]
        if game_name in game_scores:
            game_scores[game_name].append(score)
        else:
            game_scores[game_name] = [score]
    return game_scores


def recommend_games(query, k=5):
    docs = docsearch.similarity_search_with_score(query, 200)
    games = []
    similarity_scores = generate_score_dict(docs)
    seen = set()
    for doc, score in docs:
        game_name = doc.metadata["game"][0]
        if game_name not in seen:
            games.append(game_name)
            seen.add(game_name)
    # Add the last game to the list
    games.append(docs[-1][0].metadata["game"][0])
    recommendations = []
    counter = 0
    recommend_games = []
    for game in games:
        recommendation = recommend_game(query, game)
        print(recommendation)
        if recommendation.lower().strip().startswith("yes"):
            recommendations.append(recommendation[5:])
            recommend_games.append(game)
            counter += 1
        if counter >= k:
            break
    # Recommend the 100th game
    recommendations.append(recommend_game(query, games[-1])[5:])
    recommend_games.append(games[-1])
    formatted_recommendations = [
        f"## {i+1}. {recommend_games[i]} (Similarity Score: {max(similarity_scores[recommend_games[i]]):.2%})\n\n{recommendation}"
        for i, recommendation in enumerate(recommendations)
    ]  # add index, game title, maximum similarity score, markdown formatting, and new lines
    return "\n".join(formatted_recommendations)

iface2 = gr.Interface(
    fn=recommend_games,
    inputs=[
        gr.inputs.Textbox(lines=2, placeholder="Describe a game you would like", label="Game Description"),
        gr.inputs.Slider(minimum=1, maximum=10, step=1, default=5, label="Number Games to Recommend"),
    ],
    outputs="markdown"
)
iface2.launch(auth=("username", "password"))
