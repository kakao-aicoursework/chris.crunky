import openai
import os
from datetime import datetime

import pynecone as pc
from pynecone.base import Base


openai.api_key = os.environ["OPENAI_API_KEY"]


def answer_text_using_chatgpt(text) -> str:
    # 나중에 사용자가 선택한 옵션에 대해 여러 기법을 적용할 수 있도록 구성해보기
    # # fewshot 예제를 만들고
    # def build_fewshot(src_lang, trg_lang):
    #     src_examples = parallel_example[src_lang]
    #     trg_examples = parallel_example[trg_lang]
    #
    #     fewshot_messages = []
    #
    #     for src_text, trg_text in zip(src_examples, trg_examples):
    #         fewshot_messages.append({"role": "user", "content": src_text})
    #         fewshot_messages.append({"role": "assistant", "content": trg_text})
    #
    #     return fewshot_messages

    # system instruction 만들기
    system_instruction = f"assistant는 친절한 선생님이다. 학생들이 이해하기 쉽게 다양한 예시를 통해 설명한다."

    messages = [{"role": "system", "content": system_instruction},
                # *fewshot_messages,
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

    text: str = ""
    messages: list[Message] = []

    @pc.var
    def output(self) -> str:
        if not self.text.strip():
            return "Answers will appear here."

        answer = answer_text_using_chatgpt(self.text)
        return answer

    def post(self):
        self.messages = [
            Message(
                question=self.text,
                answer=self.output,
                created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
            )
        ] + self.messages


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


def message(message):
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


def output():
    return pc.box(
        pc.box(
            smallcaps(
                "Answer",
                color="#aeaeaf",
                background_color="white",
                padding_x="0.1rem",
            ),
            position="absolute",
            top="-0.5rem",
        ),
        pc.text(State.output),
        padding="1rem",
        border="1px solid #eaeaef",
        margin_top="1rem",
        border_radius="8px",
        position="relative",
    )


def index():
    """The main view."""
    return pc.container(
        header(),
        pc.input(
            placeholder="Text to question",
            on_blur=State.set_text,
            margin_top="1rem",
            border_color="#eaeaef"
        ),
        # 나중에 사용자가 좋은 답변을 위해 뭔가를 선택할 수 있도록 만들기?
        # pc.select(
        #     list(parallel_example.keys()),
        #     value=State.src_lang,
        #     placeholder="Select a language",
        #     on_change=State.set_src_lang,
        #     margin_top="1rem",
        # ),
        # pc.select(
        #     list(parallel_example.keys()),
        #     value=State.trg_lang,
        #     placeholder="Select a language",
        #     on_change=State.set_trg_lang,
        #     margin_top="1rem",
        # ),
        output(),
        pc.button("Ask", on_click=State.post, margin_top="1rem"),
        pc.vstack(
            pc.foreach(State.messages, message),
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
