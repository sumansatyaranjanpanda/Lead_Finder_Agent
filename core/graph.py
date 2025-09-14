from core.schema import BuyerState
from langgraph.graph import StateGraph, END
from core.node import company_scraper_agent,linkedin_contact_agent,validator_agent,output_agent


graph = StateGraph(BuyerState)

graph.add_node("company_scraper", company_scraper_agent)
graph.add_node("linkedin_agent", linkedin_contact_agent)
graph.add_node("validator", validator_agent)
graph.add_node("output", output_agent)

graph.set_entry_point("company_scraper")
graph.add_edge("company_scraper", "linkedin_agent")
graph.add_edge("linkedin_agent", "validator")
graph.add_edge("validator", "output")
graph.add_edge("output", END)

compiled_graph = graph.compile()