# 🚀 Lead Finder Agent — Buyer Discovery (LangGraph + Apify + Streamlit)

AI-powered Buyer Discovery workflow that automatically finds importers, wholesalers, and distributors for any `product + location` and returns validated leads (company + procurement contacts) as JSON/CSV.  
Built with **LangGraph** (multi-agent orchestration), **Apify** scrapers (Google Places, Google SERP, LinkedIn Profile Scraper), **Pydantic** schemas, and a **Streamlit** UI for running & exporting results.

**Problem:** Exporters and manufacturers spend huge manual effort finding reliable buyers in target markets.  
**Solution:** Automate discovery, enrichment, and validation of B2B leads so sales teams get production-ready contacts fast.



<img width="173" height="531" alt="graph" src="https://github.com/user-attachments/assets/13b9c619-9255-4e49-93ce-29e821cc62e2" />

---

## 🔖 Table of Contents
1. [High-Level Architecture & Flow (Text Description)](#high-level-architecture--flow-text-description)  
2. [Deep Explanation — Each Component](#deep-explanation--each-component)  
3. [Data Model / Schema (Example)](#data-model--schema-example)  
4. [How It Works — Step-by-Step Run](#how-it-works--step-by-step-run)  
5. [Install & Run (Copy-Paste)](#install--run-copy-paste)  
6. [Streamlit UI Usage](#streamlit-ui-usage)  
7. [Troubleshooting & Common Fixes](#troubleshooting--common-fixes)  
8. [Testing, Deployment & Scaling Notes](#testing-deployment--scaling-notes)  
9. [Security, Costs & Ethics](#security-costs--ethics)  
10. [Future Ideas & Roadmap](#future-ideas--roadmap)  
11. [Example Files & Useful Snippets](#example-files--useful-snippets)  
12. [License & Credits](#license--credits)

---

## High-Level Architecture & Flow (Text Description)



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



  

The workflow processes user input (product and location via Streamlit) through a series of agents and external services:
- **User Input** → **Company Scraper Agent** → **Company List (normalized)** → **LinkedIn Discovery (Google SERP Scraper)** → **LinkedIn Profile Scraper (Apify)** → **Validator Agent** → **Output Formatter Agent** → **Streamlit UI / JSON / CSV / DB**.
- **External Services** include Apify Actors (Google Places, SERP, LinkedIn Profile Scraper), optional Email Finder (Hunter/ZeroBounce), and optional databases (Postgres/MongoDB/Vector DB).
- The process involves scraping, validation, and formatting, with data flowing from one agent to the next, utilizing external tools as needed.

## Deep Explanation — Each Component

1. **Entry (Streamlit UI)**  
   Accepts product and location, a run label, and optional parameters (max companies).  
   Builds an initial BuyerState and invokes the LangGraph pipeline.  
   Shows progress, preview table, JSON, CSV downloads and allows re-runs.

2. **Company Scraper Agent**  
   Goal: produce a clean list of candidate companies (company_name, website, phone, partial address).  
   Preferred sources:  
   - Apify Google Places / Google Maps actor – good for local importers/distributors.  
   - Apify Alibaba / IndiaMART / Trade portal actors – supplier listings.  
   - Apify Google Search actor with domain filters (e.g., site:tradeindia.com) if portal scrapers miss targets.  
   Output: list of CompanyInfo (Pydantic) or plain dicts.

3. **LinkedIn Discovery (Google SERP)**  
   Query pattern: `Procurement Manager {company_name} {location} site:linkedin.com/in/`.  
   Use Apify Google SERP Scraper to fetch candidate LinkedIn profile URLs.  
   Filter results: keep those whose title or description mentions the company name (or use fuzzy matching).

4. **LinkedIn Profile Scraper**  
   Feed found LinkedIn profile URLs into dev_fusion/Linkedin-Profile-Scraper (Apify actor).  
   Actor returns structured profile items: fullName, headline, linkedinUrl, companyName, email (sometimes), location, etc.

5. **Validator Agent**  
   MVP logic: keep leads with company.email OR any procurement contact with email OR linkedin.  
   Production improvements:  
   - Email format validation (EmailStr), deliverability checks (ZeroBounce/Hunter), phone normalization (phonenumbers), fuzzy deduplication (rapidfuzz).  
   - Confidence scoring combining website, email, phone, procurement contact presence.

6. **Output Formatter Agent**  
   Standardize final schema and return JSON/CSV.  
   Optionally persist to DB (Postgres/Mongo) or push to CRM (HubSpot/Salesforce).

## Data Model / Schema (Example)




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
  

How It Works — Step-by-Step Run

Streamlit constructs BuyerState(location="Dubai", product="Rice").
compiled_graph.invoke(...) runs the LangGraph workflow:

company_scraper_agent: calls Apify Google Places actor → collects 5–20 places (company names, phones, websites).
linkedin_contact_agent:
For each company, run Apify Google SERP scraper with Procurement Manager {company} {location} site:linkedin.com/in/.
Filter SERP results for best matches.
Pass top profile URLs to Apify LinkedIn Profile Scraper → get structured contacts.
validator_agent: filter leads with at least one usable contact (email or linkedin).
output_agent: format & return the result.


Streamlit receives final state and shows preview table, JSON output, and CSV/JSON downloads.

Install & Run (Copy-Paste)
Assumes repo Lead_Finder_Agent with core/ modules (graph, node, schema), app.py (Streamlit), and requirements.txt.
bash# 1. Clone the repo
git clone https://github.com/your-username/Lead_Finder_Agent.git
cd Lead_Finder_Agent

# 2. Create Python venv (recommended)
python -m venv .venv

# Windows PowerShell activate
.\.venv\Scripts\Activate.ps1

# or Windows cmd
.\.venv\Scripts\activate

# or use conda (alternative)
# conda create -n lead-finder python=3.11 -c conda-forge -y
# conda activate lead-finder

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env with APIFY_TOKEN
echo "APIFY_TOKEN=apify_api_XXXXXXXXXXXX" > .env

# 5. Run the Streamlit UI
streamlit run app.py
requirements.txt (Minimal Suggestion)
textapify-client
python-dotenv
pydantic
streamlit
requests
langgraph
phonenumbers
rapidfuzz
Streamlit UI Usage

Open http://localhost:8501 (Streamlit will show the URL).
Enter Product and Location (e.g., Rice, Dubai).
Click "Find Buyer" — wait (Apify runs can take 10–90s depending on actors and counts).
Review table and JSON; download CSV/JSON for CRM import.

Troubleshooting & Common Fixes

ApifyApiError: User was not found or authentication token is not valid
→ Ensure APIFY_TOKEN is set in .env and loaded (token starts with apify_api_...).
Input is not valid: Field input.limit must be string
→ Some Apify actors require string-typed fields: limit = str(10).
Input is not valid: Field input.limit must equal allowed values
→ Use allowed values (e.g., "10", "20", "30", "40", "50", "100") or map requested values to nearest allowed.
AttributeError: 'CompanyInfo' object has no attribute 'procurement_contacts'
→ Normalize field names across code. Add a helper as_dict() in the UI to handle Pydantic objects/dicts.
Circular import (partially initialized module)
→ Build graph lazily: expose build_graph() in core.graph and call it at runtime.
Slow runs / Apify rate-limits
→ Cache results, lower maxCrawledPlacesPerSearch, or upgrade Apify plan / use proxies.
LinkedIn scraping returns no email
→ Many profiles hide email; use company domain + email-finder services (Hunter, ZeroBounce) as fallback.

Testing, Deployment & Scaling Notes
Testing

Unit-test each agent by mocking Apify responses.
Use fixtures under tests/fixtures/ with sample profile JSON.
CI (GitHub Actions): mock network calls in tests.

Deployment Options

Demo: Streamlit Cloud, Heroku (containerized).
Production:

Backend: FastAPI + worker pool (Celery/RQ).
DB: Postgres/Mongo for leads, Redis for caching.
Deploy workers to AWS ECS / GCP Cloud Run with autoscaling.



Scaling

Submit jobs asynchronously (UI enqueues job, worker executes Apify runs).
Batch and parallelize profile scraping; implement rate limiting and backoff.
Cache results and avoid repeated calls for same company.

Security, Costs & Ethics

API keys: Store in .env, never commit. Use secrets manager in production.
Costs: Apify actors and email verification APIs cost money. Start with free tiers and monitor usage.
Privacy & ToS: Respect terms of service for sources (LinkedIn) and robots.txt. Use data ethically.
GDPR: If storing personal data for EU residents, ensure lawful basis, retention policies, and rights management.

Future Ideas & Roadmap

Add confidence scoring & human-in-the-loop review (approve/reject).
Integrate email verification APIs to improve lead quality.
Add regional trade data (Panjiva, Trademap) for importer-level accuracy.
Build an exporter dashboard with analytics (conversions, contact success rate).
Integrate with CRMs (HubSpot, Salesforce) to auto-sync validated leads.

Example Files & Useful Snippets
LangGraph build_graph() Minimal Pattern
pythondef build_graph():
    from core.schema import BuyerState
    from core.node import company_scraper_agent, linkedin_contact_agent, validator_agent, output_agent
    graph = StateGraph(BuyerState)
    # add nodes & edges...
    return graph.compile()
Normalizing Function (in UI)
pythondef as_dict(obj):
    if isinstance(obj, dict): return obj
    if hasattr(obj, "dict"): return obj.dict()
    if hasattr(obj, "__dict__"): return vars(obj)
    return {"value": str(obj)}
Example-Run (Expected Timeline)

Submit query → company scraper (5–15s) → SERP & LinkedIn search (10–60s per company) → LinkedIn profile actor (20–90s depending on count) → validation & output.
Typical demo run (5 companies): ~30–90 seconds depending on Apify actor performance.

License & Credits
MIT License © 2025 — use, adapt, and contribute.
Built by you (Lead Finder Agent) — powered by LangGraph, Apify, Pydantic, and Streamlit.
If you want, I can:

Add badges (Python, Streamlit, LangGraph, Apify) at the top,
Include placeholder screenshots (drop them into /assets/ and I’ll update the README), or
Generate a short demo GIF snippet instructions to make the README even more attractive.
    
