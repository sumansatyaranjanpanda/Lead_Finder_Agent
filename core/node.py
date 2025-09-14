from core.schema import BuyerState,CompanyInfo,ProcurementContact
import os
import requests
from langgraph.graph import StateGraph, END
from apify_client import ApifyClient

import os
from config.settings import APIFY_TOKEN
client = ApifyClient(APIFY_TOKEN)

def company_scraper_agent(state: BuyerState) -> BuyerState:
    """Scrape Google Places for companies via Apify"""
    print(f"[Company Scraper] Finding {state.product} suppliers in {state.location}...")

    query = f"{state.product} supplier {state.location}"
    run = client.actor("compass/crawler-google-places").call(
        run_input={
            "includeWebResults": False,
            "language": "en",
            "locationQuery": state.location,
            "maxCrawledPlacesPerSearch": 7,
            "searchStringsArray": [f"{state.product} supplier"],
            "scrapeContacts": False,
            "scrapePlaceDetailPage": False,
        }
    )

    companies = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        companies.append(CompanyInfo(
            company_name=item.get("title"),
            website=item.get("website"),
            email=None,   # Google Maps doesn’t return emails
            phone=item.get("phone"),
        ))

    state.companies = companies
    return state


def linkedin_contact_agent(state: BuyerState) -> BuyerState:
    """Find procurement managers via Google Search → enrich with LinkedIn Profile Scraper"""
    print("[LinkedIn Agent] Searching procurement managers...")

    enriched_list = []
    for company in state.companies:
        query = f"Procurement Manager {company.company_name} {state.location} site:linkedin.com/in/"
        search_run = client.actor("scraperlink/google-search-results-serp-scraper").call(
            run_input={"keyword": query, "limit": "10"}
        )

        # Collect LinkedIn profile URLs
        profile_urls = []
        for item in client.dataset(search_run["defaultDatasetId"]).iterate_items():
            for result in item.get("results", []):
                # if company.company_name.lower() in result.get("description", "").lower():
                profile_urls.append(result["url"])

        if not profile_urls:
            print(f"⚠️ No relevant LinkedIn profiles found for {company.company_name}")
            enriched_list.append(company)
            continue

        # Step 2: Scrape LinkedIn profiles for details
        profile_run = client.actor("dev_fusion/Linkedin-Profile-Scraper").call(
            run_input={"profileUrls": profile_urls[:2]}  # top 2 results
        )

        contacts = []
        for item in client.dataset(profile_run["defaultDatasetId"]).iterate_items():
            contact = ProcurementContact(
                name=item.get("fullName"),
                designation=item.get("headline"),
                email=item.get("email"),
                linkedin=item.get("linkedinUrl")
            )
            contacts.append(contact)

        enriched_company = company.copy(update={"procurement_contacts": contacts})
        enriched_list.append(enriched_company)

    state.companies = enriched_list
    return state





def validator_agent(state: BuyerState) -> BuyerState:
    """Validate leads - keep only those with at least one valid contact (email or LinkedIn)."""
    print("[Validator] Validating company emails and contacts...")
    print(state.companies)

    valid = []
    for c in state.companies:
        keep = False

        # Check company email
        if c.email:
            keep = True

        # Check procurement contacts (if any exist)
        if c.procurement_contacts:
            for contact in c.procurement_contacts:
                if contact.email or contact.linkedin:
                    keep = True
                    break  # no need to check further contacts

        if keep:
            valid.append(c)

    state.companies = valid
    return state



def output_agent(state: BuyerState) -> BuyerState:
    """Final output formatter - print structured JSON leads."""
    print("\n✅ Final Buyer Leads (Validated Schema):")
    for company in state.companies:
        print(company.dict())
    return state