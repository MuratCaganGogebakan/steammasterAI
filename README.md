# SteammasterAI
## Project Overview

This project is a game recommendation system that uses OpenAI APIs and the Langchain framework, a powerful tool for developing applications powered by language models. The recommendation system also leverages the capabilities of Gradio to provide a user interface for easy interaction with the model and Pinecone for building high-performance vector search applications. The system collects and processes reviews from Steam, a popular gaming platform, to generate meaningful game recommendations based on user input.

## Code Structure

The codebase contains the following main scripts and notebook:

**chunk_splitter.py:** This script handles the splitting and combining of the game reviews to prepare them for processing.

**get_comments.py:** This script is responsible for scraping reviews from the Steam platform.

**gradio_app.py:** This script sets up the Gradio interface and implements the game recommendation logic using Langchain and Pinecone.

**populate_db.ipynb:** This Jupyter notebook script populates the Pinecone vector database using game reviews.

## Setup and Running the Project

Here are the steps you can follow to set up and run this game recommendation system.

### Prerequisites

    Python 3.7 or higher
    Jupyter Notebook
    Required Python libraries: langchain, gradio, pinecone, beautifulsoup4, requests

You can install the necessary libraries using pip:
```
pip install langchain gradio pinecone beautifulsoup4 requests
```
Clone the Repository
```
git clone <repo_url>
cd <repo_dir>
```
### Environment Variables

Create a .env file in the project's root directory and add the following keys:
```
OPENAI_API_KEY=<openai_api_key>
PINECONE_API_KEY=<pinecone_api_key>
PINECONE_API_ENV=<pinecone_api_env>
```
### Run the Project

First, run get_comments.py to scrape reviews from Steam:
```
python get_comments.py
```
Then, run chunk_splitter.py to prepare the reviews:
```
python chunk_splitter.py
```
Next, run populate_db.ipynb in Jupyter Notebook to populate the Pinecone database.

Finally, run gradio_app.py to start the Gradio interface:
```
python gradio_app.py
```
Access the Gradio interface at http://localhost:7860/.
## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the issues page if you want to contribute.
Acknowledgments

Thanks to the creators of Langchain, Gradio, and Pinecone for their excellent tools that made this project possible. Also, a big shout out to the OpenAI team for their APIs.

## Contact

If you want to contact me about the project, you can contact me through this email:
gogebakan.cagan@gmail.com
