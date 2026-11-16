from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. User Input & Intent Extraction Schemas ---
class UserQueryRequest(BaseModel):
    query: str = Field(..., example="Find me a flight to London under $700 next weekend with minimal layover")
    user_id: Optional[str] = "guest_user"

class ExtractedFlightIntent(BaseModel):
    origin: Optional[str] = Field(None, description="3-letter IATA code for origin, e.g., SFO, JFK, MAA")
    destination: Optional[str] = Field(None, description="3-letter IATA code for destination, e.g., LHR, DEL")
    departure_date: Optional[str] = Field(None, description="YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="YYYY-MM-DD format if round-trip")
    max_budget: Optional[float] = Field(None, description="Maximum budget in USD/INR")
    max_layover_hours: Optional[float] = Field(None, description="Maximum layover time preferred")
    preferred_airline: Optional[str] = Field(None, description="Preferred airline name or code")

# --- 2. Flight Result & Itinerary Schemas ---
class FlightSegment(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    airline: str
    flight_number: str
    duration_minutes: int

class FlightItinerary(BaseModel):
    id: str
    origin: str
    destination: str
    price: float
    currency: str = "USD"
    total_duration_hours: float
    layover_count: int
    layover_duration_hours: float
    segments: List[FlightSegment]
    score: Optional[float] = 0.0  # Populated by Multi-Criteria Scoring Engine

# --- 3. Policy RAG Query Schemas ---
class PolicyQueryRequest(BaseModel):
    airline: str
    question: str = Field(..., example="What is the cabin baggage limit?")

class PolicyQueryResponse(BaseModel):
    airline: str
    question: str
    answer: str
    source_documents: List[str]

# --- 4. Final Agent Response Schema --
class AgentResponse(BaseModel):
    user_query: str
    extracted_intent: ExtractedFlightIntent
    top_flights: List[FlightItinerary]
    tradeoff_chart_path: Optional[str] = None
    policy_summary: Optional[str] = None
    status: str = "success"