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
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_API_ENV  # next to api key in console
)
index_name = "langchain" 

docsearch = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm, chain_type="stuff")

def reccomend_games(query, k=10):
    docs = docsearch.similarity_search_with_score(query, k)
    answers = []
    #reccomended_games = []
    for i in range(k):
        first_docs = docs[i:i+1]
        first_docs = [doc[0] for doc in first_docs]
        print(first_docs)
        #reccomend_games.append(first_docs[0])
        query = "Recommend this game to me. Make relations to my query: " + query
        answer = chain.run(input_documents=first_docs, question=query)
        answers.append(answer)
        #print(answer)
    return answers

query = input("Describe a game you would like to play: ")
reccomend_games(query)