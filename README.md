# 🚀 Lead Finder Agent — Buyer Discovery (LangGraph + Apify + Streamlit)

AI-powered Buyer Discovery workflow that automatically finds importers, wholesalers, and distributors for any `product + location` and returns validated leads (company + procurement contacts) as JSON/CSV.  
Built with **LangGraph** (multi-agent orchestration), **Apify** scrapers (Google Places, Google SERP, LinkedIn Profile Scraper), **Pydantic** schemas, and a **Streamlit** UI for running & exporting results.

**Problem:** Exporters and manufacturers spend huge manual effort finding reliable buyers in target markets.  
**Solution:** Automate discovery, enrichment, and validation of B2B leads so sales teams get production-ready contacts fast.

---

## 🔖 Table of contents
1. [High-level architecture & flow (visual)](#high-level-architecture--flow-visual)  
2. [Deep explanation — each component](#deep-explanation---each-component)  
3. [Data model / schema (example)](#data-model--schema-example)  
4. [How it works — step-by-step run](#how-it-works---step-by-step-run)  
5. [Install & Run (copy-paste)](#install--run-copy-paste)  
6. [Streamlit UI usage](#streamlit-ui-usage)  
7. [Troubleshooting & common fixes](#troubleshooting--common-fixes)  
8. [Testing, deployment & scaling notes](#testing-deployment--scaling-notes)  
9. [Security, costs & ethics](#security-costs--ethics)  
10. [Future ideas & roadmap](#future-ideas--roadmap)  
11. [Example files & useful snippets](#example-files--useful-snippets)  
12. [License & credits](#license--credits)

---

## High-level architecture & flow (visual)

```mermaid
flowchart TD
  A[User: product and location (Streamlit)] --> B[Company Scraper Agent]
  B --> C[Company List (normalized)]
  C --> D[LinkedIn Discovery (Google SERP Scraper)]
  D --> E[LinkedIn Profile Scraper (Apify)]
  E --> F[Validator Agent]
  F --> G[Output Formatter Agent]
  G --> H[Streamlit UI / JSON / CSV / DB]

  subgraph External_Services
    X[Apify Actors: Google Places, SERP, LinkedIn Profile Scraper]
    Y[Optional: Email Finder (Hunter / ZeroBounce)]
    Z[Optional DB: Postgres / MongoDB / Vector DB]
  end

## High-level architecture & flow (visual)
  B -.-> X
  D -.-> X
  E -.-> X
  F -.-> Y
  G -.-> Z

sequenceDiagram
  participant User
  participant UI as Streamlit
  participant G as CompanyScraper
  participant S as GoogleSERP
  participant L as LinkedInProfileScraper
  participant V as Validator
  participant DB as Storage

  User->>UI: submit(product, location)
  UI->>G: run company search
  G-->>UI: list of companies
  UI->>S: search LinkedIn URLs per company
  S-->>UI: LinkedIn profile URLs
  UI->>L: scrape LinkedIn profiles
  L-->>UI: profile details
  UI->>V: validate & score leads
  V-->>DB: save validated leads
  UI-->>User: show JSON/CSV and table

Deep explanation — each component
1. Entry (Streamlit UI)

Accepts product and location, builds an initial BuyerState, invokes LangGraph.

Shows progress, preview table, JSON/CSV download.

2. Company Scraper Agent

Uses Apify Google Places / Maps to fetch candidate companies.

Output: CompanyInfo objects (name, phone, website, category).

3. LinkedIn Discovery (Google SERP)

Query: Procurement Manager {company_name} {location} site:linkedin.com/in/

Gets LinkedIn URLs from Google SERP scraper.

4. LinkedIn Profile Scraper

Calls dev_fusion/Linkedin-Profile-Scraper on Apify.

Returns structured details: fullName, headline, email (if public), companyName, etc.

5. Validator Agent

Keeps leads with at least one valid email or LinkedIn profile.

Can be extended with email verification & phone normalization.

6. Output Formatter Agent

Standardizes schema and prepares JSON/CSV output for UI & download.


Example final JSON
{
  "company_name": "JPRL GENERAL TRADING LLC",
  "website": null,
  "email": null,
  "phone": "+971 50 145 2890",
  "procurement_contacts": [
    {
      "name": "Naresh Kumar",
      "designation": "General Manager (Intl. Business)",
      "email": null,
      "linkedin": "https://in.linkedin.com/in/naresh-kumar-5453068"
    }
  ]
}


How it works — step-by-step run

Streamlit creates BuyerState(location="Dubai", product="Rice").

LangGraph executes agents in order:

Company Scraper → LinkedIn Discovery → LinkedIn Profile Scraper → Validator → Output Formatter.

Streamlit UI displays results, table, JSON, CSV download.



# 1. clone
git clone https://github.com/your-username/Lead_Finder_Agent.git
cd Lead_Finder_Agent

# 2. create venv
python -m venv .venv
# activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. install deps
pip install -r requirements.txt

# 4. set your Apify token
echo "APIFY_TOKEN=apify_api_XXXXXXXXXXXX" > .env

# 5. run Streamlit
streamlit run app.py


requirements.txt

apify-client
python-dotenv
pydantic
streamlit
requests
langgraph
phonenumbers
rapidfuzz

License & credits

MIT License © 2025 — use, adapt, and contribute.
Built by you — powered by LangGraph, Apify, Pydantic, and Streamlit.



---

✅ This version is **ready to paste into your README.md** — diagrams will render properly on GitHub.  

Do you also want me to add **GitHub shields/badges** (Python, Streamlit, LangGraph, Apify) at the top so it looks even more professional?

