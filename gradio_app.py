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
    query = "Reccommend this game to me, If you wouldn't reccommend it always start your answer wtih a No. Make relations to my query: " + query
    answer = chain.run(input_documents=game_docs, question=query)
    return answer

def recommend_games(query, k=5):
    docs = docsearch.similarity_search_with_score(query, k)
    games = []
    for i in range(len(docs)):
        games.append(docs[i][0].metadata["game"][0])
    # Make the games unique
    games = list(set(games))
    recommendations = []
    for game in games:
        recommendations.append(recommend_game(query, game))
    formatted_recommendations = [f"## {i+1}. {games[i]}\n\n{recommendation}" for i, recommendation in enumerate(recommendations)]  # add index, markdown formatting and new lines
    return "\n".join(formatted_recommendations)

iface2 = gr.Interface(
    fn=recommend_games,
    inputs=[
        gr.inputs.Textbox(lines=2, placeholder="Describe a game you would like", label="Game Description"),
    ],
    outputs="markdown"
)
iface2.launch()
