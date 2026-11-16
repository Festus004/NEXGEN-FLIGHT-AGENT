import os
import gradio as gr
from schemas import UserQueryRequest
from agent.agent import flight_agent

def run_flight_booking_agent(user_query: str):
    """
    Handler function connecting Gradio UI inputs to our Multi-Agent system.
    """
    if not user_query.strip():
        return "Please enter a travel request.", "", None, ""

    # Execute agent workflow
    request = UserQueryRequest(query=user_query)
    response = flight_agent.process_query(request)

    # Format Extracted Intent Summary
    intent = response.extracted_intent
    intent_summary = f"""
    ### 🎯 Parsed Travel Intent (NLP Engine)
    - **Origin:** `{intent.origin or 'Not Specified'}`
    - **Destination:** `{intent.destination or 'Not Specified'}`
    - **Max Budget:** `${intent.max_budget if intent.max_budget else 'No Limit'}`
    - **Max Layover:** `{intent.max_layover_hours or 'Flexible'} Hours`
    """

    # Format Flight Cards Output
    flight_cards_markdown = "### ✈️ Top Recommended Flights (Scored & Ranked)\n\n"
    for idx, flight in enumerate(response.top_flights[:3]):
        seg = flight.segments[0]
        flight_cards_markdown += f"""
        ---
        #### Option {idx+1}: {seg.airline} ({seg.flight_number})
        - **Price:** `${flight.price} {flight.currency}`
        - **Total Duration:** `{flight.total_duration_hours} Hours`
        - **Route:** `{flight.origin}` ➔ `{flight.destination}`
        - **Layovers:** `{flight.layover_count} Layover(s)` ({flight.layover_duration_hours} hrs)
        - **Utility Optimization Score:** `{flight.score}` *(Lower is better)*
        
        """

    # Format Policy RAG Output
    policy_markdown = f"""
    ### 📋 Airline Policy Context (FAISS RAG Engine)
    **Retrieved Knowledge:**
    > {response.policy_summary}
    """

    # Chart path
    chart_path = response.tradeoff_chart_path if (response.tradeoff_chart_path and os.path.exists(response.tradeoff_chart_path)) else None

    return intent_summary, flight_cards_markdown, chart_path, policy_markdown

# Build Gradio UI Dashboard
with gr.Blocks(theme=gr.themes.Soft(), title="NextGen Autonomous AI Flight Booking Agent") as demo:
    gr.Markdown(
        """
        # ✈️ Autonomous AI Flight Booking Agent
        ### *Natural Language Flight Discovery, Policy RAG & Multi-Criteria Optimization*
        **Department of Computer & Communication Engineering | Sri Eshwar College of Engineering**
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            query_input = gr.Textbox(
                label="Enter Your Travel Request (Natural Language)",
                placeholder="e.g., Find me a flight to London under $700 next weekend with minimal layover",
                lines=3
            )
            submit_btn = gr.Button("🔍 Discover & Optimize Flights", variant="primary")
            
            intent_output = gr.Markdown(label="Parsed Intent")
            policy_output = gr.Markdown(label="Policy Summary")

        with gr.Column(scale=1):
            flights_output = gr.Markdown(label="Top Recommended Options")
            chart_output = gr.Image(label="Multi-Criteria Data Analytics (Price vs. Travel Time)", type="filepath")

    # Wire event handler
    submit_btn.click(
        fn=run_flight_booking_agent,
        inputs=[query_input],
        outputs=[intent_output, flights_output, chart_output, policy_output]
    )

    gr.Examples(
        examples=[
            ["Find me a flight to London under $700 next weekend with minimal layover"],
            ["Book a cheap direct flight to Delhi under $500"],
            ["Find me a flight to Chennai with Emirates under $800"]
        ],
        inputs=[query_input]
    )

if __name__ == "__main__":
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    demo.launch(server_name="127.0.0.1", server_port=7860, share=True)