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

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm, chain_type="stuff")

def recommend_game(query, game_name):
    game_docs = docsearch.similarity_search(query, k=5, filter={"game": game_name})
    query = "Unless the game is completly unrelated to the input recommend it and start your answer with 'Yes'. If you definetly can't recommend it startwith No. Take the gamename from metadata. Make relations to my query: " + query
    answer = chain.run(input_documents=game_docs, question=query)
    return answer

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
    docs = docsearch.similarity_search_with_score(query, 100)
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
    for game in games:
        recommendation = recommend_game(query, game)
        print(recommendation)
        if recommendation.lower().strip().startswith("yes"):
            recommendations.append(recommendation[6:])
            counter += 1
        if counter >= k:
            break
    formatted_recommendations = [
        f"## {i+1}. {games[i]} (Similarity Score: {max(similarity_scores[games[i]]):.2%})\n\n{recommendation}"
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
iface2.launch()
