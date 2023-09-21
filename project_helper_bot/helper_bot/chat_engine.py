import logging
import os.path

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import FileChatMessageHistory, ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
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
template = read_prompt_template(os.path.join(PROMPTS_DIR, 'template.txt'))

chain = LLMChain(
    llm=llm_openai,
    prompt=ChatPromptTemplate.from_template(
        template=template
    ),
    verbose=True,
)


def query_db(query: str, use_retriever: bool = False) -> list[str]:
    if use_retriever:
        docs = retriever.get_relevant_documents(query)
    else:
        docs = db.similarity_search(query)

    str_docs = [doc.page_content for doc in docs]
    return str_docs


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


async def chat(question, conversation_id: str = 'test') -> str:
    logger.info('new chat')

    history = load_conversation_history(conversation_id)

    context = dict(question=question)
    context['related_documents'] = query_db(question)
    context['chat_histories'] = get_chat_history(conversation_id)

    answer = chain.run(context)

    log_user_message(history, question)
    log_bot_message(history, answer)

    return answer
