# NEXGEN Flight Agent

NEXGEN Flight Agent is an autonomous AI flight booking assistant that accepts natural-language travel requests, extracts intent, searches flight options, retrieves airline policy context using FAISS + sentence embeddings, and ranks flights using a multi-criteria scoring model.

It combines:

- Gradio-based UI for interactive travel discovery
- FastAPI API endpoints for backend integration
- Amadeus flight search integration
- FAISS vector retrieval for airline policy knowledge
- Multi-objective flight scoring and Pareto-style tradeoff visualization
- Optional Groq LLM-based intent extraction with rule-based fallback

## Features

- Natural-language flight discovery
- Structured intent parsing for origin, destination, budget, layovers, and airline preference
- Flight search and ranking using price, duration, and layover tradeoffs
- Policy RAG lookup for baggage and cancellation rules
- Visual analytics chart for flight comparison
- Local demo app and REST backend API

## Tech Stack

- Python 3.10+
- FastAPI
- Gradio
- LangChain
- LangChain Community
- FAISS
- Sentence Transformers
- Matplotlib
- Amadeus / Duffel APIs
- Groq LLM integration

## Project Structure

```text
NEXGEN-FLIGHT-AGENT/
├── app.py                     # Gradio demo UI
├── main.py                   # FastAPI backend entry point
├── config.py                 # Central settings and environment vars
├── schemas.py                # Request/response models
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment file
├── .gitignore                # Ignore local secrets and build output
├── faiss_policy_index/       # Saved FAISS policy index
├── pareto_tradeoff.png       # Example tradeoff chart
├── agent/
│   └── agent.py              # Multi-agent orchestration logic
├── services/
│   ├── amadeus_service.py    # Flight search service
│   ├── rag_service.py        # FAISS + embeddings retrieval service
│   ├── scoring.py            # Multi-criteria ranking and chart generation
│   └── __init__.py
└── README.md
```

## Environment Setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows PowerShell
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the variables below:

```env
GROQ_API_KEY=your_groq_key
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
AMADEUS_HOSTNAME=test
DUFFEL_API_TOKEN=your_duffel_token
```

> Keep this file local and never commit it to GitHub.

## Run the Project

### Gradio UI

```bash
python app.py
```

The app launches locally on:

- `http://127.0.0.1:7860`

### FastAPI backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then access:

- `http://localhost:8000/`
- `http://localhost:8000/docs`

## Example Queries

- Find me a flight to London under $700 next weekend with minimal layover
- Book a cheap direct flight to Delhi under $500
- Find me a flight to Chennai with Emirates under $800

## Notes

- If the Groq key is missing, the app automatically falls back to a rule-based query parser.
- If the FAISS index does not exist, the application creates it on first run.
- The policy RAG and ranking logic are designed to be lightweight and easy to extend.

## License

This project is intended for educational and prototype use.

## Repository

GitHub:
[https://github.com/Festus004/NEXGEN-FLIGHT-AGENT.git](https://github.com/Festus004/NEXGEN-FLIGHT-AGENT.git)
