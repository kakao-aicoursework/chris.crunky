import logging

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage

# 로깅 세팅
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s ',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("chat_engine")

# llm 세팅
llm_openai = ChatOpenAI(temperature=0.8)

system_message_prompt = SystemMessage(
    content='assistant는 안내를 위한 챗봇이다. 이해하기 쉬운 언어를 사용하고, 가능하면 step by step 형식으로 안내한다.'
)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    '''
    질문 : {question}
    답변 형식 : 문단을 보기 좋게 나눠서 만들어 줘
    답변 : 
    '''
)
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

# TODO: 상대 경로 사용할 수 있도록 수정하기
TextLoader('/Users/chris/llm-study/kakao-aicoursework/project1/project_helper_bot/data/kakao-sync.txt').load()

chain = LLMChain(llm=llm_openai, prompt=chat_prompt)


async def chat(question) -> str:
    logger.info('new chat')
    return chain.run(question=question)
