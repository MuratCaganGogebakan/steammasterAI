# SteammasterAI

## Project Overview
SteammasterAI is a state-of-the-art game recommendation system that uses OpenAI APIs, Pinecone, and BeautifulSoup in combination with Python. By utilizing the potent capabilities of these technologies, our system accurately and efficiently delivers game recommendations based on user preferences.

The system operates by first gathering and processing game reviews from Steam, a leading digital platform in the gaming industry. This data, once processed, is then used to generate meaningful game recommendations that align closely with the desires expressed by users.

## Code Structure

Our codebase is structured into several critical scripts and one notebook that perform various tasks:

**chunk_splitter.py:** This script is responsible for splitting and aggregating the game reviews into chunks. These chunks are later used to generate vector embeddings.

**get_comments.py:** This script scrapes game reviews from the Steam platform, providing the raw data that our system processes.

**gradio_app.py:** This script orchestrates the recommendation system. It employs the Langchain framework to integrate OpenAI APIs, sets up the Gradio interface for user interaction, and uses Pinecone to retrieve similar game reviews.

**populate_db.ipynb:** A Jupyter notebook that populates the Pinecone vector database with the vector embeddings of the review chunks.

## Setup and Running the Project

To setup and run the SteammasterAI system, follow these steps:

### Prerequisites

Ensure you have the following:

- Python 3.7 or higher
- Jupyter Notebook
- The necessary Python libraries: langchain, gradio, pinecone, beautifulsoup4, requests

You can install the libraries using pip:
```
pip install langchain gradio pinecone beautifulsoup4 requests
```

### Clone the Repository

```
git clone <repo_url>
cd <repo_dir>
```

### Setup Environment Variables

Create a .env file in the root directory of the project and add the following keys:

```
OPENAI_API_KEY=<openai_api_key>
PINECONE_API_KEY=<pinecone_api_key>
PINECONE_API_ENV=<pinecone_api_env>
```

### Run the Project

1. Execute `get_comments.py` to scrape game reviews from Steam:
```
python get_comments.py
```
2. Run `chunk_splitter.py` to prepare the review chunks:
```
python chunk_splitter.py
```
3. Run `populate_db.ipynb` in Jupyter Notebook to populate the Pinecone vector database with the review embeddings.
4. Finally, start the Gradio interface with `gradio_app.py`:
```
python gradio_app.py
```
You can access the Gradio interface at http://localhost:7860/.

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to explore the issues page if you wish to contribute. 

## Acknowledgments
We express our gratitude to the creators of Langchain, Gradio, and Pinecone, whose excellent tools have greatly contributed to the success of this project. Also, a special thanks to the OpenAI team for their remarkable APIs.

## Contact
For inquiries or feedback about the project, feel free to reach out via email at gogebakan.cagan@gmail.com.
