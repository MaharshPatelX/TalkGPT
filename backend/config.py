import os
from dotenv import load_dotenv

load_dotenv()

# Database
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "talkgpt"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# CORS
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

# LangChain
LANGCHAIN_MODEL = "gpt-4o-mini"
LANGCHAIN_TEMPERATURE = 0.7
LANGCHAIN_MAX_TOKENS = 1000