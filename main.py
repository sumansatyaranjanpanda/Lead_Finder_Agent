# app.py
"""
Streamlit UI for Buyer Finder Agent (LangGraph).
Run:
    streamlit run app.py

Expectations:
- Your project exposes `compiled_graph` and `BuyerState`:
    from core.graph import compiled_graph
    from core.schema import BuyerState
- APIFY_TOKEN and other env vars are set in your environment or .env.
- compiled_graph.invoke(...) may return None (and mutate input) or return a result.
This app normalizes both cases and displays a table + JSON + download buttons.
"""

import json
import io
import traceback
from datetime import datetime
from typing import Any

import streamlit as st

# Attempt to import project modules; if they fail, show error in UI
try:
    from core.graph import compiled_graph  # compiled LangGraph graph
    from core.schema import BuyerState      # pydantic model or similar
    _import_error = None
except Exception:
    compiled_graph = None
    BuyerState = None
    _import_error = traceback.format_exc()

# Attempt to import pydantic BaseModel for safe detection
try:
    from pydantic import BaseModel
except Exception:
    BaseModel = None

st.set_page_config(page_title="Buyer Finder — Agent UI", layout="wide")
st.title("Buyer Finder — Agentic AI (LangGraph) 🌐")
st.markdown(
    "Enter product and target location, run the pipeline, and get structured buyer leads "
    "(companies + procurement contacts)."
)

if compiled_graph is None or BuyerState is None:
    st.error("Could not import project modules `core.graph` or `core.schema`.")
    st.code(_import_error or "No import trace available.", language="python")
    st.stop()

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.header("Run parameters")
    product = st.text_input("Product", value="Rice")
    location = st.text_input("Location", value="Dubai")
    # max_companies = st.selectbox(
    #     "Max companies to fetch (if scrapers support this)",
    #     options=[5, 10, 20, 50],
    #     index=0,
    # )
    run_label = st.text_input("Run label (optional)", value=f"run-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
    show_raw = st.checkbox("Show raw returned objects", value=False)

    run_button = st.button("Find Buyer")

# ---------------------------
# Helpers
# ---------------------------
def to_json_serializable(obj: Any) -> Any:
    """Convert pydantic models / complex objects into JSON-serializable structures."""
    # If it's already JSON-friendly
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [to_json_serializable(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_json_serializable(v) for k, v in obj.items()}
    # pydantic BaseModel
    try:
        if BaseModel and isinstance(obj, BaseModel):
            return to_json_serializable(obj.dict())
    except Exception:
        pass
    # Has dict() method
    if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        try:
            return to_json_serializable(obj.dict())
        except Exception:
            pass
    # If it's a simple object with __dict__
    if hasattr(obj, "__dict__"):
        return to_json_serializable(obj.__dict__)
    # Fallback
    return str(obj)

def as_dict(obj: Any) -> dict:
    """Return a plain dict for dicts, pydantic models, or objects with .dict()."""
    if isinstance(obj, dict):
        return obj
    try:
        if BaseModel and isinstance(obj, BaseModel):
            return obj.dict()
    except Exception:
        pass
    if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        try:
            return obj.dict()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        # object.__dict__ may contain non-serializable; convert recursively after
        return {k: getattr(obj, k) for k in vars(obj).keys()}
    return {"value": str(obj)}

# ---------------------------
# Run pipeline
# ---------------------------
if run_button:
    st.info(f"Running pipeline for **{product}** in **{location}** — label: {run_label}")

    # Prepare initial state
    try:
        # Prefer creating BuyerState if available (pydantic)
        try:
            initial_state = BuyerState(location=location, product=product)
            initial_payload = initial_state.dict()
            initial_state_obj = initial_state
        except Exception:
            initial_state = {"location": location, "product": product, "companies": []}
            initial_payload = initial_state
            initial_state_obj = initial_state
    except Exception as e:
        st.error("Failed to prepare initial state.")
        st.exception(e)
        st.stop()

    with st.expander("Initial payload (what will be passed to compiled_graph.invoke)"):
        st.json(to_json_serializable(initial_payload))

    # Invoke the compiled graph
    try:
        with st.spinner("Invoking LangGraph pipeline (this may take 10-90s depending on Apify runs)..."):
            result = compiled_graph.invoke(initial_payload)
    except Exception as e:
        st.error("Pipeline execution failed. See error below:")
        st.exception(e)
        st.stop()

    # Normalize result: compiled_graph.invoke may return None and mutate initial payload/object
    if result is None:
        final_candidate = initial_state_obj
    else:
        final_candidate = result

    # Convert to plain JSON-serializable structure
    final_state = to_json_serializable(final_candidate)

    # Sometimes the top-level is a dict with 'companies'
    companies = None
    if isinstance(final_state, dict) and "companies" in final_state:
        companies = final_state.get("companies")
    elif isinstance(final_state, list):
        # maybe returned companies list directly
        companies = final_state
    else:
        # maybe final_candidate was an object with attribute 'companies'
        try:
            attr_companies = getattr(final_candidate, "companies", None)
            if attr_companies is not None:
                companies = to_json_serializable(attr_companies)
        except Exception:
            companies = None

    if not companies:
        st.warning("No companies found in final output. Showing full final state below.")
        if show_raw:
            st.subheader("Raw Final State")
            st.json(final_state)
        else:
            st.write(final_state)
        st.stop()

    # Normalize each company into a plain dict (handles pydantic models)
    normalized_companies = [as_dict(c) for c in companies]

    # Accept multiple possible key names and normalize fields in each company
    normalized_list = []
    for comp in normalized_companies:
        comp_d = {k: v for k, v in comp.items()}  # shallow copy
        # Normalize procurement contacts key variants
        contacts = comp_d.get("procurement_contacts") or comp_d.get("procurements_contacts") or comp_d.get("contacts") or comp_d.get("procurement") or []
        # Normalize each contact to dict
        contacts_list = [as_dict(ct) for ct in contacts] if contacts else []
        comp_normal = {
            "company_name": comp_d.get("company_name") or comp_d.get("title") or comp_d.get("name") or "",
            "website": comp_d.get("website") or comp_d.get("companyWebsite") or comp_d.get("company_website"),
            "email": comp_d.get("email") or comp_d.get("company_email"),
            "phone": comp_d.get("phone") or comp_d.get("phoneNumber") or comp_d.get("telephone"),
            "procurement_contacts": contacts_list,
        }
        normalized_list.append(comp_normal)

    # Build a dataframe for quick preview (primary contact as columns)
    import pandas as pd

    rows = []
    for comp in normalized_list:
        primary = comp["procurement_contacts"][0] if comp["procurement_contacts"] else {}
        rows.append({
            "company_name": comp["company_name"],
            "website": comp["website"],
            "company_email": comp["email"],
            "phone": comp["phone"],
            "primary_contact_name": primary.get("name") if isinstance(primary, dict) else None,
            "primary_contact_role": primary.get("designation") if isinstance(primary, dict) else None,
            "primary_contact_email": primary.get("email") if isinstance(primary, dict) else None,
            "primary_contact_linkedin": primary.get("linkedin") if isinstance(primary, dict) else None,
        })

    df = pd.DataFrame(rows)
    st.subheader("Final Buyer Leads — Table Preview")
    st.dataframe(df)

    st.subheader("Final Buyer Leads — JSON")
    st.json(normalized_list if show_raw else to_json_serializable(normalized_list))

    # Downloads
    json_bytes = json.dumps(normalized_list, default=str, indent=2).encode("utf-8")
    st.download_button("Download JSON", data=json_bytes, file_name=f"buyer_leads_{run_label}.json", mime="application/json")

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download CSV", data=csv_buffer.getvalue().encode("utf-8"), file_name=f"buyer_leads_{run_label}.csv", mime="text/csv")

    st.success("Pipeline finished. Use the JSON / CSV downloads or review table above.")
