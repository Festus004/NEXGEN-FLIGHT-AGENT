import json
import logging
from typing import Dict, Any

from config import settings
from schemas import (
    UserQueryRequest,
    ExtractedFlightIntent,
    AgentResponse,
    PolicyQueryRequest
)
from services.amadeus_service import amadeus_service
from services.rag_service import rag_service
from services.scoring import scoring_engine

logger = logging.getLogger(__name__)

class FlightAgentOrchestrator:
    """
    Multi-Agent Orchestrator using Groq / Llama-3.1 for Intent Extraction
    and routing across Amadeus API, FAISS RAG, and Scoring Engine.
    """
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.LLM_MODEL_NAME
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        if self.api_key:
            try:
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    groq_api_key=self.api_key,
                    model_name=self.model_name,
                    temperature=0.0
                )
                logger.info("ChatGroq LLM initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize ChatGroq ({e}). Using rule-based fallback intent extractor.")
        else:
            logger.info("GROQ_API_KEY not found. Using fallback intent parser.")

    def parse_intent(self, query: str) -> ExtractedFlightIntent:
        """Parses natural language query into structured ExtractedFlightIntent."""
        if self.llm:
            try:
                prompt = (
                    "You are an expert flight intent extraction system. "
                    "Extract the following travel parameters from the user query into valid JSON:\n"
                    "- origin (3-letter IATA code, e.g., SFO, JFK, DEL, LHR)\n"
                    "- destination (3-letter IATA code, e.g., JFK, LHR, BOM)\n"
                    "- departure_date (YYYY-MM-DD format if mentioned)\n"
                    "- return_date (YYYY-MM-DD format if mentioned)\n"
                    "- max_budget (numeric value in USD if mentioned)\n"
                    "- max_layover_hours (numeric value if mentioned)\n"
                    "- preferred_airline (string if mentioned)\n\n"
                    f"User Query: \"{query}\"\n\n"
                    "Return ONLY valid JSON matching these keys."
                )
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                
                # Extract JSON block
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                data = json.loads(content)
                return ExtractedFlightIntent(**data)
            except Exception as e:
                logger.error(f"LLM intent parsing failed ({e}). Reverting to heuristic extraction.")

        # Heuristic fallback intent parser
        return self._heuristic_intent_parser(query)

    def _heuristic_intent_parser(self, query: str) -> ExtractedFlightIntent:
        """Simple rule-based parser for offline/demo scenarios."""
        query_lower = query.lower()
        
        origin = "SFO"
        destination = "JFK"
        budget = 700.0

        if "london" in query_lower or "lhr" in query_lower:
            destination = "LHR"
        elif "delhi" in query_lower or "del" in query_lower:
            destination = "DEL"
        elif "chennai" in query_lower or "maa" in query_lower:
            destination = "MAA"

        if "under $" in query_lower:
            try:
                parts = query_lower.split("under $")[1].split()[0]
                budget = float(parts)
            except Exception:
                pass
        elif "under " in query_lower:
            try:
                parts = query_lower.split("under ")[1].split()[0]
                budget = float(parts.replace("$", ""))
            except Exception:
                pass

        return ExtractedFlightIntent(
            origin=origin,
            destination=destination,
            max_budget=budget,
            max_layover_hours=3.0
        )

    def process_query(self, request: UserQueryRequest) -> AgentResponse:
        """Full execution pipeline: Intent -> API -> RAG -> Scoring -> Plot."""
        logger.info(f"Processing query: {request.query}")
        
        # Step 1: Intent Extraction
        intent = self.parse_intent(request.query)

        # Step 2: Amadeus API Search
        raw_flights = amadeus_service.search_flights(intent)

        # Step 3: Multi-Criteria Scoring & Ranking
        ranked_flights = scoring_engine.score_and_rank_flights(raw_flights)

        # Step 4: Generate Trade-off Analytics Chart
        chart_path = scoring_engine.generate_tradeoff_chart(ranked_flights)

        # Step 5: Query Airline Policy RAG if airline detected
        top_airline = ranked_flights[0].segments[0].airline if ranked_flights else "Emirates"
        policy_resp = rag_service.query_policy(
            PolicyQueryRequest(airline=top_airline, question="cabin baggage and cancellation policy")
        )

        return AgentResponse(
            user_query=request.query,
            extracted_intent=intent,
            top_flights=ranked_flights,
            tradeoff_chart_path=chart_path,
            policy_summary=policy_resp.answer,
            status="success"
        )

# Global Orchestrator Singleton
flight_agent = FlightAgentOrchestrator()