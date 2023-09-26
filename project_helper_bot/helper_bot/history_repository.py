import os

from langchain.memory import FileChatMessageHistory, ConversationBufferMemory

HISTORY_DIR = os.path.join(os.getcwd(), "chat-histories")


class ChatHistoryRepository:
    def __init__(self, conversation_id: str):
        self.history = FileChatMessageHistory(os.path.join(HISTORY_DIR, f"{conversation_id}.json"))

    def log_user_message(self, user_message: str):
        self.history.add_user_message(user_message)

    def log_bot_message(self, bot_message: str):
        self.history.add_ai_message(bot_message)

    def get_chat_history(self):
        memory = ConversationBufferMemory(
            memory_key="chat_histories",
            input_key="user_message",
            chat_memory=self.history,
        )

        return memory.buffer
