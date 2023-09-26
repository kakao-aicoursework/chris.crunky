import os

from langchain import GoogleSearchAPIWrapper
from langchain.tools import Tool

from .llm import Llm


class WebSearchClient:
    def __init__(self):
        search = GoogleSearchAPIWrapper(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            google_cse_id=os.getenv("GOOGLE_CSE_ID"),
        )

        self.search_tool = Tool(
            name="Google Search",
            description="Search Google for recent results.",
            func=search.run,
        )

        self.search_value_check_chain = Llm().search_value_check_chain

    def search(self, question):
        return self.search_tool.run(question)

    def search_value_check(self, question):
        return self.search_value_check_chain.run(question)
