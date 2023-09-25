import logging
import os.path

from langchain import LLMChain, GoogleSearchAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import FileChatMessageHistory, ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.tools import Tool
from langchain.vectorstores import Chroma

# 로깅 세팅
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s ',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("chat_engine")

# vector db 세팅
PERSIST_DIR = os.path.join(os.getcwd(), 'chroma-persist')
DOCUMENTS_DIR = os.path.join(os.getcwd(), 'assets/documents')

db = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=OpenAIEmbeddings(),
    collection_name='kakao-api-explain',
)
retriever = db.as_retriever()


def query_db(query: str, use_retriever: bool = False) -> list[str]:
    if use_retriever:
        docs = retriever.get_relevant_documents(query)
    else:
        docs = db.similarity_search(query)

    str_docs = [doc.page_content for doc in docs]
    return str_docs


def upload_embedding_from_file(file_path):
    document = TextLoader(file_path).load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(document)

    db.add_documents(
        documents=docs,
        embedding_function=OpenAIEmbeddings(),
        collection_name='kakao-api-explain',
    )
    logger.info('db upload success')


for dirpath, dirnames, filenames in os.walk(DOCUMENTS_DIR):
    for filename in filenames:
        if filename.endswith('.txt'):
            file_path = os.path.join(dirpath, filename)
            upload_embedding_from_file(file_path)


# llm 세팅
def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


llm_openai = ChatOpenAI(temperature=0.8, model="gpt-3.5-turbo")
PROMPTS_DIR = os.path.join(os.getcwd(), 'assets/prompt_templates')

main_chain = LLMChain(
    llm=llm_openai,
    prompt=ChatPromptTemplate.from_template(
        template=read_prompt_template(os.path.join(PROMPTS_DIR, 'main-template.txt'))
    ),
    verbose=True,
)

# memory 세팅
HISTORY_DIR = os.path.join(os.getcwd(), "chat-histories")


def load_conversation_history(conversation_id: str):
    return FileChatMessageHistory(os.path.join(HISTORY_DIR, f"{conversation_id}.json"))


def log_user_message(history: FileChatMessageHistory, user_message: str):
    history.add_user_message(user_message)


def log_bot_message(history: FileChatMessageHistory, bot_message: str):
    history.add_ai_message(bot_message)


def get_chat_history(conversation_id: str):
    history = load_conversation_history(conversation_id)
    memory = ConversationBufferMemory(
        memory_key="chat_histories",
        input_key="user_message",
        chat_memory=history,
    )

    return memory.buffer


# web search llm 세팅
search = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_cse_id=os.getenv("GOOGLE_CSE_ID"),
)

search_tool = Tool(
    name="Google Search",
    description="Search Google for recent results.",
    func=search.run,
)

search_value_check_chain = LLMChain(
    llm=llm_openai,
    prompt=ChatPromptTemplate.from_template(
        template=read_prompt_template(os.path.join(PROMPTS_DIR, 'search-value-check-template.txt'))
    ),
    verbose=True,
)


async def chat(question, conversation_id: str = 'test') -> str:
    logger.info('new chat')

    context = dict(question=question)
    context['related_web_search_results'] = search_tool.run(question)

    has_value = search_value_check_chain.run(context)
    if has_value == 'Y':
        context['search_results'] = context.pop('related_web_search_results')
    else:
        context.pop('related_web_search_results')
        context['search_results'] = ''

    context['related_documents'] = query_db(question)
    context['chat_histories'] = get_chat_history(conversation_id)

    answer = main_chain.run(context)

    history = load_conversation_history(conversation_id)
    log_user_message(history, question)
    log_bot_message(history, answer)

    return answer
