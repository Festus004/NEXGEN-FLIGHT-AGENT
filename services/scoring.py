import os
import logging
from typing import List, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt

from config import settings
from schemas import FlightItinerary

logger = logging.getLogger(__name__)

class MultiCriteriaScoringEngine:
    """
    Multi-Criteria Decision Analysis Engine for flight itinerary optimization.
    Calculates weighted utility scores and generates Pareto trade-off scatter plots.
    """
    def __init__(self):
        self.w_price = settings.WEIGHT_PRICE
        self.w_duration = settings.WEIGHT_DURATION
        self.w_layover = settings.WEIGHT_LAYOVER

    def score_and_rank_flights(self, itineraries: List[FlightItinerary]) -> List[FlightItinerary]:
        """
        Calculates utility score for each itinerary:
        Score = w1*(Norm_Price) + w2*(Norm_Duration) + w3*(Norm_Layover)
        Lower values indicate better itineraries.
        """
        if not itineraries:
            return []

        prices = [it.price for it in itineraries]
        durations = [it.total_duration_hours for it in itineraries]
        layovers = [it.layover_count for it in itineraries]

        min_price, max_price = min(prices), max(prices)
        min_dur, max_dur = min(durations), max(durations)
        min_lay, max_lay = min(layovers), max(layovers)

        for it in itineraries:
            norm_price = (it.price - min_price) / (max_price - min_price) if max_price > min_price else 0.0
            norm_dur = (it.total_duration_hours - min_dur) / (max_dur - min_dur) if max_dur > min_dur else 0.0
            norm_lay = (it.layover_count - min_lay) / (max_lay - min_lay) if max_lay > min_lay else 0.0

            # Composite cost score (lower is better)
            composite_score = (self.w_price * norm_price) + (self.w_duration * norm_dur) + (self.w_layover * norm_lay)
            it.score = round(composite_score, 4)

        # Sort itineraries by composite score ascending (best options first)
        ranked_itineraries = sorted(itineraries, key=lambda x: x.score)
        return ranked_itineraries

    def generate_tradeoff_chart(self, itineraries: List[FlightItinerary], output_filename: str = "pareto_tradeoff.png") -> str:
        """
        Generates a 2D Scatter plot (Price vs. Travel Duration)
        to visually represent the trade-offs between cost and travel time.
        """
        if not itineraries:
            return ""

        output_path = os.path.join(os.getcwd(), output_filename)

        durations = [it.total_duration_hours for it in itineraries]
        prices = [it.price for it in itineraries]
        labels = [f"{it.segments[0].airline} (${it.price})" for it in itineraries]

        plt.figure(figsize=(8, 5))
        plt.scatter(durations, prices, color='#0284c7', s=180, edgecolors='#0f172a', linewidth=1.5, zorder=3)

        for i, label in enumerate(labels):
            plt.annotate(
                label,
                (durations[i] + 0.2, prices[i] + 5),
                fontsize=9,
                fontweight='bold',
                color='#1e293b'
            )

        plt.title("Multi-Criteria Optimization: Travel Time vs. Flight Price", fontsize=13, fontweight='bold', pad=12)
        plt.xlabel("Total Travel Time (Hours)", fontsize=11, fontweight='bold')
        plt.ylabel("Price (USD)", fontsize=11, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.5, zorder=1)
        plt.tight_layout()

        try:
            plt.savefig(output_path, dpi=300)
            plt.close()
            logger.info(f"Trade-off analytics chart successfully generated at: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save trade-off chart image: {e}")
            plt.close()
            return ""

# Global Service Singleton
scoring_engine = MultiCriteriaScoringEngine()