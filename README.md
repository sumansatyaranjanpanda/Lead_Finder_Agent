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
