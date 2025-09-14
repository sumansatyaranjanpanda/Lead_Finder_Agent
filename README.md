🚀 Lead Finder Agent — Buyer Discovery (LangGraph + Apify + Streamlit)
AI-powered Buyer Discovery workflow that automatically finds importers, wholesalers, and distributors for any product + location and returns validated leads (company + procurement contacts) as JSON/CSV.Built with LangGraph (multi-agent orchestration), Apify scrapers (Google Places, Google SERP, LinkedIn Profile Scraper), Pydantic schemas, and a Streamlit UI for running & exporting results.
Problem: Exporters and manufacturers spend huge manual effort finding reliable buyers in target markets.Solution: Automate discovery, enrichment, and validation of B2B leads so sales teams get production-ready contacts fast.

🔖 Table of Contents

High-Level Architecture & Flow (Visual)  
Deep Explanation — Each Component  
Data Model / Schema (Example)  
How It Works — Step-by-Step Run  
Install & Run (Copy-Paste)  
Streamlit UI Usage  
Troubleshooting & Common Fixes  
Testing, Deployment & Scaling Notes  
Security, Costs & Ethics  
Future Ideas & Roadmap  
Example Files & Useful Snippets  
License & Credits


High-Level Architecture & Flow (Visual)
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

Deep Explanation — Each Component

Entry (Streamlit UI)Accepts product and location, a run label, and optional parameters (max companies).Builds an initial BuyerState and invokes the LangGraph pipeline.Shows progress, preview table, JSON, CSV downloads and allows re-runs.

Company Scraper AgentGoal: produce a clean list of candidate companies (company_name, website, phone, partial address).Preferred sources:  

Apify Google Places / Google Maps actor – good for local importers/distributors.  
Apify Alibaba / IndiaMART / Trade portal actors – supplier listings.  
Apify Google Search actor with domain filters (e.g., site:tradeindia.com) if portal scrapers miss targets.Output: list of CompanyInfo (Pydantic) or plain dicts.


LinkedIn Discovery (Google SERP)Query pattern:Procurement Manager {company_name} {location} site:linkedin.com/in/Use Apify Google SERP Scraper to fetch candidate LinkedIn profile URLs.Filter results: keep those whose title or description mentions the company name (or use fuzzy matching).

LinkedIn Profile ScraperFeed found LinkedIn profile URLs into dev_fusion/Linkedin-Profile-Scraper (Apify actor).Actor returns structured profile items: fullName, headline, linkedinUrl, companyName, email (sometimes), location, etc.

Validator AgentMVP logic: keep leads with company.email OR any procurement contact with email OR linkedin.Production improvements:  

Email format validation (EmailStr), deliverability checks (ZeroBounce/Hunter), phone normalization (phonenumbers), fuzzy deduplication (rapidfuzz).  
Confidence scoring combining website, email, phone, procurement contact presence.


Output Formatter AgentStandardize final schema and return JSON/CSV.Optionally persist to DB (Postgres/Mongo) or push to CRM (HubSpot/Salesforce).


Data Model / Schema (Example)
Use Pydantic to validate & serialize:
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List

class ProcurementContact(BaseModel):
    name: Optional[str]
    designation: Optional[str]
    email: Optional[EmailStr]
    linkedin: Optional[HttpUrl]

class CompanyInfo(BaseModel):
    company_name: str
    website: Optional[HttpUrl]
    email: Optional[EmailStr]
    phone: Optional[str]
    procurement_contacts: List[ProcurementContact] = []

class BuyerState(BaseModel):
    location: str
    product: str
    companies: List[CompanyInfo] = []

Example final JSON (single company):
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
linkedin_contact_agent:For each company, run Apify Google SERP scraper with Procurement Manager {company} {location} site:linkedin.com/in/.Filter SERP results for best matches.Pass top profile URLs to Apify LinkedIn Profile Scraper → get structured contacts.  
validator_agent: filter leads with at least one usable contact (email or linkedin).  
output_agent: format & return the result.


Streamlit receives final state and shows preview table, JSON output, and CSV/JSON downloads.

Install & Run (Copy-Paste)
Assumes repo Lead_Finder_Agent with core/ modules (graph, node, schema), app.py (Streamlit), and requirements.txt.
# 1. Clone the repo
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
apify-client
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

ApifyApiError: User was not found or authentication token is not valid→ Ensure APIFY_TOKEN is set in .env and loaded (token starts with apify_api_...).

Input is not valid: Field input.limit must be string→ Some Apify actors require string-typed fields: limit = str(10).

Input is not valid: Field input.limit must equal allowed values→ Use allowed values (e.g., "10", "20", "30", "40", "50", "100") or map requested values to nearest allowed.

AttributeError: 'CompanyInfo' object has no attribute 'procurement_contacts'→ Normalize field names across code. Add a helper as_dict() in the UI to handle Pydantic objects/dicts.

Circular import (partially initialized module)→ Build graph lazily: expose build_graph() in core.graph and call it at runtime.

Slow runs / Apify rate-limits→ Cache results, lower maxCrawledPlacesPerSearch, or upgrade Apify plan / use proxies.

LinkedIn scraping returns no email→ Many profiles hide email; use company domain + email-finder services (Hunter, ZeroBounce) as fallback.


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
Privacy & ToS: Respect terms of service for sources (LinkedIn) and robots.txt. Use data
