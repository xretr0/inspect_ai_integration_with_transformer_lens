from dataclasses import dataclass
from typing import TypedDict

import numpy as np
from pydantic import BaseModel
from test_helpers.utils import (
    skip_if_no_anthropic,
    skip_if_no_google,
    skip_if_no_mistral,
    skip_if_no_openai,
    skip_if_no_vertex,
)

from inspect_ai import Task, eval
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.log._log import EvalLog
from inspect_ai.model import ChatMessageTool
from inspect_ai.model._model import Model, get_model
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import ToolFunction, tool
from inspect_ai.tool._tool import Tool


@tool
def mean():
    async def execute(numbers: list[float]) -> float:
        """Take the mean of a set of numbers.

        Args:
          numbers: A list of integers to take the mean of

        Returns:
          The mean of the numbers
        """
        return np.mean(numbers).item()

    return execute


class Point(TypedDict):
    x: int
    y: int


@tool
def offset():
    async def execute(point: Point, offset: int) -> str:
        """
        Offset a point by the specified offset value

        Args:
          point: Point to offset
          offset: Offset value

        Returns:
          A Point with the x and y values offset
        """
        return str(Point(x=point["x"] + offset, y=point["y"] + offset))

    return execute


@dataclass
class PointDataclass:
    x: int
    y: int


@tool
def offset_dataclass():
    async def execute(point: PointDataclass, offset: int):
        """
        Offset a point by the specified offset value

        Args:
          point: Point to offset
          offset: Offset value

        Returns:
          A Point with the x and y values offset
        """
        return str(PointDataclass(x=point.x + offset, y=point.y + offset))

    return execute


class Word(BaseModel):
    type: str
    word: str


@tool
def extract_words():
    async def execute(extracted: list[Word]):
        """
        Accepts the extracted nouns and adjectives from a sentence

        Args:
          extracted: A list of Word objects each with a type and word.

        Returns:
          The words and their types in a list
        """
        return ", ".join([f"{x.word}: {x.type}" for x in extracted])

    return execute


@tool
def sound_check():
    async def execute(sound: str, extra: str = "stuff"):
        """
        Accepts the extracted nouns and adjectives from a sentence

        Args:
          sound: The sound to check
          extra: Optional extra stuff


        Returns:
          The sound that was passed to check.
        """
        return f"{sound} ({extra})"

    return execute


@tool
def computer_action():
    async def execute(
        action: str,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
    ) -> str:
        """Take an action using a computer.

        Args:
          action: Action to take.
          text: Text related to the action
          coordinate: Coordinate related to the action.

        Returns:
          The sound that was passed to check.
        """
        return action

    return execute


def check_point(model: str | Model, tool: Tool, function_name: str) -> None:
    task = Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="Start with the point x=10, y=10 then offset it by 5.",
                )
            ]
        ),
        solver=[
            use_tools([tool], tool_choice=ToolFunction(function_name)),
            generate(),
        ],
    )

    log = eval(task, model=model)[0]
    verify_tool_call(log, "15")


def check_typed_dict(model: str | Model) -> None:
    check_point(model, offset(), "offset")


def check_dataclass(model: str | Model) -> None:
    check_point(model, offset_dataclass(), "offset_dataclass")


def check_list_of_numbers(model: str | Model) -> None:
    task = Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="Take the mean of the following numbers: 5, 10, 15",
                    target="10",
                )
            ]
        ),
        solver=[
            use_tools([mean()], tool_choice=ToolFunction("mean")),
            generate(),
        ],
    )

    log = eval(task, model=model)[0]
    verify_tool_call(log, "10")


def check_list_of_objects(model: str | Model) -> None:
    # grok sometimes doesn't get this one (just says 'I have extracted, how would you like to proceed')
    if isinstance(model, str) and "grok" in model:
        return

    task = Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="Extract the nouns and adjectives from the following sentence.\nSentence:\nThe quick brown fox jumped over the lazy dog."
                )
            ]
        ),
        solver=[
            use_tools([extract_words()], tool_choice=ToolFunction("extract_words")),
            generate(),
        ],
    )

    log = eval(task, model=model)[0]
    verify_tool_call(log, "quick")


def check_optional_args(model: str | Model) -> None:
    task = Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="Please call the sound_check tool with single argument 'boo' and report its output."
                )
            ]
        ),
        solver=[
            use_tools([sound_check()], tool_choice=ToolFunction("sound_check")),
            generate(),
        ],
    )

    log = eval(task, model=model)[0]
    verify_tool_call(log, "stuff")


def check_none_default_arg(model: str | Model) -> None:
    task = Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="Please call the computer_action function with the action='click' argument."
                )
            ]
        ),
        solver=[
            use_tools([computer_action()], tool_choice=ToolFunction("computer_action")),
            generate(),
        ],
    )

    log = eval(task, model=model)[0]
    verify_tool_call(log, "click")


def check_tool_types(model: str | Model):
    if "google" not in str(model):
        check_typed_dict(model)
        check_dataclass(model)
    check_list_of_numbers(model)
    check_list_of_objects(model)
    check_optional_args(model)
    check_none_default_arg(model)


@skip_if_no_openai
def test_openai_tool_types() -> None:
    check_tool_types("openai/gpt-4o")


@skip_if_no_openai
def test_openai_responses_tool_types() -> None:
    check_tool_types(get_model("openai/gpt-4o-mini", responses_api=True))


@skip_if_no_anthropic
def test_anthropoic_tool_types() -> None:
    check_tool_types("anthropic/claude-3-5-sonnet-20240620")


@skip_if_no_google
def test_google_tool_types() -> None:
    check_tool_types("google/gemini-1.5-pro")


@skip_if_no_vertex
def test_vertex_tool_types():
    check_tool_types("vertex/gemini-1.5-flash")


@skip_if_no_mistral
def test_mistral_tool_types() -> None:
    check_tool_types("mistral/mistral-large-latest")


# grok and groq tool calling are extremely unreliable and
# consequently cause failed tests that are red herrings. don't
# exercise these for now.

# @skip_if_no_grok
# def test_grok_tool_types() -> None:
#     check_tool_types("grok/grok-3-mini")


# @skip_if_no_groq
# def test_groq_tool_types() -> None:
#     check_tool_types("groq/mixtral-8x7b-32768")


def verify_tool_call(log: EvalLog, includes: str):
    assert log.samples
    tool_message = log.samples[0].messages[-2]
    assert isinstance(tool_message, ChatMessageTool)
    assert includes.lower() in log.samples[0].output.completion.lower()
