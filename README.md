# RAG chatbot powered by 🔗 Langchain, OpenAI, Google Generative AI

## Instructions <a name="instructions"></a>

To run the app locally (on Windows):

1. Create a virtual environment: `python -m venv langchain_env`
2. Activate the virtual environment : `.\langchain_env\Scripts\activate`
3. Run the following command in the directory: `cd Langchain`
4. Create env: `copy .env.example .env` and fill in the values
5. Install the required dependencies `pip install -r requirements.txt`
6. Run server langchain: `uvicorn src.app:app --host "0.0.0.0" --port 5000 --reload`
