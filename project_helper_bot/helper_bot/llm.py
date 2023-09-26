import os

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

PROMPTS_DIR = os.path.join(os.getcwd(), 'assets/prompt_templates')


class Llm:
    def __init__(self):
        llm_openai = ChatOpenAI(temperature=0.8, model="gpt-3.5-turbo")

        self.main_chain = LLMChain(
            llm=llm_openai,
            prompt=ChatPromptTemplate.from_template(
                template=self.read_prompt_template(os.path.join(PROMPTS_DIR, 'main-template.txt'))
            ),
            verbose=True,
        )

        self.search_value_check_chain = LLMChain(
            llm=llm_openai,
            prompt=ChatPromptTemplate.from_template(
                template=self.read_prompt_template(os.path.join(PROMPTS_DIR, 'search-value-check-template.txt'))
            ),
            verbose=True,
        )

    def read_prompt_template(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            prompt_template = f.read()

        return prompt_template
