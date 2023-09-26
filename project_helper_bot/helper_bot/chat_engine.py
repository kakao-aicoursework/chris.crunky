import logging

from .history_repository import ChatHistoryRepository
from .kakao_api_document_repository import KakaoApiDocumentRepository
from .llm import Llm
from .web_search_client import WebSearchClient

# 로깅 세팅
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s ',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("chat_engine")

kakao_api_document_repository = KakaoApiDocumentRepository()
history_repository = ChatHistoryRepository(conversation_id='test')
web_search_client = WebSearchClient()
main_chain = Llm().main_chain


async def chat(question) -> str:
    logger.info('new chat')

    context = dict(question=question)
    context['related_web_search_results'] = web_search_client.search(question)

    has_value = web_search_client.search_value_check(context)
    if has_value == 'Y':
        context['search_results'] = context.pop('related_web_search_results')
    else:
        context.pop('related_web_search_results')
        context['search_results'] = ''

    context['related_documents'] = kakao_api_document_repository.query_db(question)
    context['chat_histories'] = history_repository.get_chat_history()

    answer = main_chain.run(context)

    history_repository.log_user_message(question)
    history_repository.log_bot_message(answer)

    return answer
