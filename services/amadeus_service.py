import logging
from typing import List, Optional
from datetime import datetime, timedelta

from config import settings
from schemas import ExtractedFlightIntent, FlightItinerary, FlightSegment

logger = logging.getLogger(__name__)

class FlightDataService:
    """
    Service layer integrating Duffel Flight API with a robust fallback
    mock generator for reliable offline/demo runs.
    """
    def __init__(self):
        self.duffel_token = settings.DUFFEL_API_TOKEN
        self.client = None
        
        if self.duffel_token:
            try:
                from duffel_api import Duffel
                self.client = Duffel(access_token=self.duffel_token)
                logger.info("Duffel API Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Duffel client: {e}. Using fallback mock generator.")
        else:
            logger.info("No Duffel API token found. Using robust flight mock generator.")

    def search_flights(self, intent: ExtractedFlightIntent) -> List[FlightItinerary]:
        origin = intent.origin or "SFO"
        destination = intent.destination or "JFK"
        departure_date = intent.departure_date or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        if self.client:
            try:
                offer_request = (
                    self.client.offer_requests.create()
                    .passengers([{"type": "adult"}])
                    .slices([{
                        "origin": origin,
                        "destination": destination,
                        "departure_date": departure_date
                    }])
                    .return_offers()
                    .execute()
                )
                return self._parse_duffel_response(offer_request.offers)
            except Exception as e:
                logger.error(f"Duffel API query failed ({e}). Reverting to mock flight generator.")

        return self._generate_mock_flights(origin, destination, departure_date, intent.max_budget)

    def _parse_duffel_response(self, offers: list) -> List[FlightItinerary]:
        parsed_itineraries = []
        for idx, offer in enumerate(offers[:5]):
            price = float(offer.total_amount)
            currency = offer.total_currency
            slice_data = offer.slices[0]
            segments = slice_data.segments
            
            parsed_segments = []
            total_duration_mins = 0
            
            for seg in segments:
                dep_time = seg.departing_at
                arr_time = seg.arriving_at
                
                dep_dt = datetime.fromisoformat(dep_time.replace("Z", "+00:00"))
                arr_dt = datetime.fromisoformat(arr_time.replace("Z", "+00:00"))
                dur_mins = int((arr_dt - dep_dt).total_seconds() / 60)
                total_duration_mins += dur_mins
                
                parsed_segments.append(
                    FlightSegment(
                        departure_airport=seg.origin.iata_code,
                        arrival_airport=seg.destination.iata_code,
                        departure_time=dep_time,
                        arrival_time=arr_time,
                        airline=seg.marketing_carrier.name,
                        flight_number=f"{seg.marketing_carrier.iata_code}{seg.flight_number}",
                        duration_minutes=dur_mins
                    )
                )

            layover_count = len(segments) - 1
            layover_dur_hours = (layover_count * 1.5)
            total_dur_hours = round((total_duration_mins / 60.0) + layover_dur_hours, 2)

            parsed_itineraries.append(
                FlightItinerary(
                    id=f"DUFF-{idx+101}",
                    origin=segments[0].origin.iata_code,
                    destination=segments[-1].destination.iata_code,
                    price=price,
                    currency=currency,
                    total_duration_hours=total_dur_hours,
                    layover_count=layover_count,
                    layover_duration_hours=layover_dur_hours,
                    segments=parsed_segments
                )
            )
        return parsed_itineraries

    def _generate_mock_flights(self, origin: str, destination: str, dep_date: str, max_budget: Optional[float]) -> List[FlightItinerary]:
        airlines = ["Emirates", "Delta Air Lines", "United Airlines", "British Airways", "Lufthansa"]
        base_price = max_budget * 0.85 if max_budget else 650.0

        return [
            FlightItinerary(
                id="FL-101",
                origin=origin,
                destination=destination,
                price=round(base_price * 1.15, 2),
                currency="USD",
                total_duration_hours=6.5,
                layover_count=0,
                layover_duration_hours=0.0,
                segments=[
                    FlightSegment(
                        departure_airport=origin,
                        arrival_airport=destination,
                        departure_time=f"{dep_date}T08:00:00",
                        arrival_time=f"{dep_date}T14:30:00",
                        airline=airlines[0],
                        flight_number="EK-201",
                        duration_minutes=390
                    )
                ]
            ),
            FlightItinerary(
                id="FL-102",
                origin=origin,
                destination=destination,
                price=round(base_price * 0.85, 2),
                currency="USD",
                total_duration_hours=9.5,
                layover_count=1,
                layover_duration_hours=2.0,
                segments=[
                    FlightSegment(
                        departure_airport=origin,
                        arrival_airport="ORD",
                        departure_time=f"{dep_date}T09:30:00",
                        arrival_time=f"{dep_date}T13:00:00",
                        airline=airlines[1],
                        flight_number="DL-405",
                        duration_minutes=210
                    ),
                    FlightSegment(
                        departure_airport="ORD",
                        arrival_airport=destination,
                        departure_time=f"{dep_date}T15:00:00",
                        arrival_time=f"{dep_date}T19:00:00",
                        airline=airlines[1],
                        flight_number="DL-812",
                        duration_minutes=240
                    )
                ]
            )
        ]

# Global Service Singleton
amadeus_service = FlightDataService()