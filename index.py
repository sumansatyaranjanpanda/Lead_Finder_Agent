from apify_client import ApifyClient
import os
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.getenv("APIFY_TOKEN"))

def linkedin_contact_agent(profile_urls):
    """Call Apify LinkedIn Profile Scraper and return structured contacts"""
    run = client.actor("dev_fusion/Linkedin-Profile-Scraper").call(
        run_input={"profileUrls": profile_urls}
    )

    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append({
            "fullName": item.get("fullName"),
            "headline": item.get("headline"),
            "linkedinUrl": item.get("linkedinUrl"),
            "companyName": item.get("companyName"),
            "email": item.get("email"),
            "location": item.get("addressWithCountry")
        })

    return results


if __name__ == "__main__":
    test_profiles = [
        "https://www.linkedin.com/in/williamhgates",
        "http://www.linkedin.com/in/jeannie-wyrick-b4760710a"
    ]
    contacts = linkedin_contact_agent(test_profiles)
    print(contacts)
