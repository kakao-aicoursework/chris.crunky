import logging

import openai
import os
from datetime import datetime

import pynecone as pc
from pynecone.base import Base


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s ',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("helper_bot")
openai.api_key = os.environ["OPENAI_API_KEY"]


async def answer_text_using_chatgpt(text) -> str:
    logger.info("openai api call")

    # system instruction 만들기
    system_instruction = f"assistant는 친절한 선생님이다. 학생들이 이해하기 쉽게 다양한 예시를 통해 설명한다."

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": text},
    ]

    # API 호출
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    answer = response['choices'][0]['message']['content']

    # Return
    return answer


class Message(Base):
    question: str
    answer: str
    created_at: str


class State(pc.State):
    """The app state."""
    messages: list[Message] = []
    is_loading: bool = False

    async def handle_submit(self, form_data):
        self.is_loading = True
        yield
        question = form_data['question']

        response_message = await answer_text_using_chatgpt(question)

        self.messages = [
            Message(
                question=question,
                answer=response_message,
                created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
            )
        ] + self.messages

        self.is_loading = False
        yield pc.set_value("question", "")


# Define views.
def header():
    """Basic instructions to get started."""
    return pc.box(
        pc.text("Helper bot 🤖", font_size="2rem"),
        pc.text(
            "Ask me!",
            margin_top="0.5rem",
            color="#666",
        ),
    )


def down_arrow():
    return pc.vstack(
        pc.icon(
            tag="arrow_down",
            color="#666",
        )
    )


def text_box(text):
    return pc.text(
        text,
        background_color="#fff",
        padding="1rem",
        border_radius="8px",
    )


def message_box(message):
    return pc.box(
        pc.vstack(
            text_box(message.question),
            down_arrow(),
            text_box(message.answer),
            pc.box(
                pc.text(message.created_at),
                display="flex",
                font_size="0.8rem",
                color="#666",
            ),
            spacing="0.3rem",
            align_items="left",
        ),
        background_color="#f5f5f5",
        padding="1rem",
        border_radius="8px",
    )


def smallcaps(text, **kwargs):
    return pc.text(
        text,
        font_size="0.7rem",
        font_weight="bold",
        text_transform="uppercase",
        letter_spacing="0.05rem",
        **kwargs,
    )


def index():
    """The main view."""
    return pc.container(
        header(),
        pc.form(
            pc.input(
                id="question",
                placeholder="Text to question",
                margin_top="1rem",
                border_color="#eaeaef",
            ),
            pc.button("Ask", type_="submit", margin_top="1rem"),
            on_submit=State.handle_submit,
        ),
        pc.cond(
            State.is_loading,
            pc.spinner(
                color="lightgreen",
                thickness=5,
                speed="1.5s",
                size="xl",
                margin_top="1rem",
            ),
        ),
        pc.vstack(
            pc.foreach(State.messages, message_box),
            margin_top="2rem",
            spacing="1rem",
            align_items="left"
        ),
        padding="2rem",
        max_width="600px"
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="HelperBot")
app.compile()
