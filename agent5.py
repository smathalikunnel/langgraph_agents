from dotenv import load_dotenv

_ = load_dotenv()
from langchain_community.tools.tavily_search import TavilySearchResults
tool = TavilySearchResults(max_results=1)
print(tool.invoke("who is playing in the euros today"))