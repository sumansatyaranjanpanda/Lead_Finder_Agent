from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import GROQ_API_KEY, TAVILY_API_KEY


# LLM client
llm = ChatGroq(model="llama-3.3-70b-versatile")

# Tavily client
tavily = TavilySearchResults(max_results=5)