import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Autonomous AI Flight Booking Agent"
    VERSION: str = "1.0.0"
    
    # GROQ / LLM API Configurations
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL_NAME: str = "llama-3.1-8b-instant"
    
    # Amadeus API Credentials
    AMADEUS_CLIENT_ID: str = os.getenv("AMADEUS_CLIENT_ID", "")
    AMADEUS_CLIENT_SECRET: str = os.getenv("AMADEUS_CLIENT_SECRET", "")
    AMADEUS_HOSTNAME: str = os.getenv("AMADEUS_HOSTNAME", "test") # 'test' or 'production'
    
    # Vector DB / FAISS Configs
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "faiss_policy_index"
    
    # Scoring Weights (Multi-Criteria Data Science Model)
    WEIGHT_PRICE: float = 0.5
    WEIGHT_DURATION: float = 0.3
    WEIGHT_LAYOVER: float = 0.2

    # Duffel API Credentials
    DUFFEL_API_TOKEN: str = os.getenv("DUFFEL_API_TOKEN", "")

settings = Settings()