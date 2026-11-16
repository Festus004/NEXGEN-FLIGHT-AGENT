import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import settings
from schemas import (
    UserQueryRequest,
    AgentResponse,
    PolicyQueryRequest,
    PolicyQueryResponse
)
from agent.agent import flight_agent
from services.rag_service import rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="REST API for Autonomous AI Flight Booking Agent (NextGen-LMS Ecosystem)"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "version": settings.VERSION
    }

@app.post("/api/v1/search", response_model=AgentResponse)
def search_flights_api(request: UserQueryRequest):
    """
    Main conversational agent endpoint.
    Accepts natural language user query and returns structured itinerary options,
    multi-criteria scores, policy RAG answer, and trade-off chart path.
    """
    try:
        response = flight_agent.process_query(request)
        return response
    except Exception as e:
        logger.error(f"Error processing flight search query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/policy", response_model=PolicyQueryResponse)
def query_policy_api(request: PolicyQueryRequest):
    """
    Direct RAG search endpoint for airline baggage and cancellation rules.
    """
    try:
        return rag_service.query_policy(request)
    except Exception as e:
        logger.error(f"Error executing policy RAG lookup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/chart")
def get_tradeoff_chart(filename: str = "pareto_tradeoff.png"):
    """
    Serves generated matplotlib scatter plot image.
    """
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Trade-off analytics chart not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)