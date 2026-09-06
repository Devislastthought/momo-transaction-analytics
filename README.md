# TEAM

## Project Description
This project processes MoMo (Mobile Money) SMS transaction data provided in XML format.
The pipeline parses, cleans, and categorizes the raw SMS data, stores it in a relational
(SQLite) database, and exposes it through a frontend dashboard for analysis and
visualization (transaction volumes, amounts, and categories over time).

## Team Members
- Ivan Ineza Hakizimana — @Ivan70807 — [Role, Backend/ETL]
- Samuel Hezekiah Epodoi — @sam-hez — [Role, Frontend]
- Devis Muhozi — @Devislastthought — [Role, Database/API]

## System Architecture
High-level design diagram: (https://drive.google.com/file/d/1fWVONddyhtNbjNPeAsJQeziU1_lwqy-9/view?usp=sharing)
A static copy is also included in this repo at `docs/momo-architecture-diagram.png`.

## Scrum Board (Trello)
Track our progress here: https://trello.com/b/ne4syt27

## Project Structure
```
.
├── README.md                         # Setup, run, overview
├── .env.example                      # DATABASE_URL or path to SQLite
├── requirements.txt                  # lxml/ElementTree, dateutil, (FastAPI optional)
├── index.html                        # Dashboard entry (static)
├── web/
│   ├── styles.css                    # Dashboard styling
│   ├── chart_handler.js              # Fetch + render charts/tables
│   └── assets/                       # Images/icons (optional)
├── data/
│   ├── raw/                          # Provided XML input (git-ignored)
│   ├── processed/                    # Cleaned/derived outputs for frontend
│   ├── db.sqlite3                    # SQLite DB file
│   └── logs/
│       ├── etl.log                   # Structured ETL logs
│       └── dead_letter/              # Unparsed/ignored XML snippets
├── etl/
│   ├── config.py                     # File paths, thresholds, categories
│   ├── parse_xml.py                  # XML parsing (ElementTree/lxml)
│   ├── clean_normalize.py            # Amounts, dates, phone normalization
│   ├── categorize.py                 # Simple rules for transaction types
│   ├── load_db.py                    # Create tables + upsert to SQLite
│   └── run.py                        # CLI: parse -> clean -> categorize -> load -> export JSON
├── api/                              # Optional (bonus)
│   ├── app.py                        # Minimal FastAPI with /transactions, /analytics
│   ├── db.py                         # SQLite connection helpers
│   └── schemas.py                    # Pydantic response models
├── scripts/
│   ├── run_etl.sh
│   ├── export_json.sh
│   └── serve_frontend.sh
└── tests/
    ├── test_parse_xml.py
    ├── test_clean_normalize.py
    └── test_categorize.py
```

## Setup & Run

1. Clone the repo and create a virtual environment:
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and adjust paths if needed.
3. Place the provided `momo.xml` file in `data/raw/`.
4. Run the ETL pipeline:
   ```bash
   bash scripts/run_etl.sh
   ```
5. Serve the frontend:
   ```bash
   bash scripts/serve_frontend.sh
   ```
   Then open http://localhost:8000 in your browser.

(Optional bonus) Run the API:
```bash
uvicorn api.app:app --reload
```

## Testing
```bash
pytest tests/
```
