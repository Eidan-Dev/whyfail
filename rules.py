"""Turn raw pytest error lines into a plain-English explanation.

Each rule matches an exception message and returns an Explanation.
Rules are checked from the most specific message to the most generic one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple


@dataclass
class Explanation:
    title: str
    why: str
    fix: str


Rule = Tuple[re.Pattern, Callable[[re.Match], Explanation]]

ASSERT_COMPARE = re.compile(r"^assert (?P<left>.+?) (?P<op>==|!=|<=|>=|<|>|is|is not|in|not in) (?P<right>.+)$")


def _attribute_on_none(m: re.Match) -> Explanation:
    attr = m.group("attr")
    return Explanation(
        title=f"You read .{attr} on a value that is None",
        why="A function returned None where you expected an object.",
        fix="Check the return value on the failing path. A missing `return` statement is the usual cause.",
    )


def _module_missing(m: re.Match) -> Explanation:
    name = m.group("name")
    top = name.split(".")[0]
    return Explanation(
        title=f"The module '{name}' cannot be found",
        why="Python does not see this package in the environment running the tests.",
        fix=f"Activate your virtualenv, then run: pip install {top}",
    )


def _key_error(m: re.Match) -> Explanation:
    key = m.group("key")
    return Explanation(
        title=f"The key {key} does not exist",
        why="The dictionary has no entry for this key at that point in the code.",
        fix="Use .get(key, default) if the key is optional, or check that the data really contains it.",
    )


def _index_error(m: re.Match) -> Explanation:
    return Explanation(
        title="You are reading past the end of a list",
        why="The list is shorter than the index you asked for, often because it is empty.",
        fix="Check len(...) before indexing, or review the loop bounds (off-by-one errors are common).",
    )


def _zero_division(m: re.Match) -> Explanation:
    return Explanation(
        title="You divided by zero",
        why="The denominator is 0 in a case you did not handle.",
        fix="Guard the division (if denominator: ...) or handle the empty case explicitly.",
    )


def _file_not_found(m: re.Match) -> Explanation:
    path = m.group("path")
    return Explanation(
        title=f"The file {path} does not exist",
        why="The path is probably relative to a different working directory than you expect.",
        fix="Print os.getcwd() in the test, or build the path from Path(__file__).parent.",
    )


def _type_error(m: re.Match) -> Explanation:
    msg = m.group("msg")
    return Explanation(
        title="A value has the wrong type",
        why=f"Python received something it cannot use here: {msg}",
        fix="Print type(value) at the call site to see what is actually being passed.",
    )


RULES: List[Rule] = [
    (re.compile(r"ModuleNotFoundError: No module named '(?P<name>[^']+)'"), _module_missing),
    (re.compile(r"AttributeError: 'NoneType' object has no attribute '(?P<attr>[^']+)'"), _attribute_on_none),
    (re.compile(r"KeyError: (?P<key>.+)$"), _key_error),
    (re.compile(r"IndexError: (?P<msg>.*)$"), _index_error),
    (re.compile(r"ZeroDivisionError: (?P<msg>.*)$"), _zero_division),
    (re.compile(r"FileNotFoundError: .*'(?P<path>[^']+)'"), _file_not_found),
    (re.compile(r"TypeError: (?P<msg>.*)$"), _type_error),
]


def _explain_assert(line: str) -> Optional[Explanation]:
    m = ASSERT_COMPARE.match(line.strip())
    if not m:
        return None

    left, op, right = m.group("left"), m.group("op"), m.group("right")

    if op == "==":
        if left == "None":
            return Explanation(
                title=f"Expected {right}, but the function returned None",
                why="Nothing was returned on this path, so the value is None.",
                fix="Look for a code path that reaches the end of the function without a `return`.",
            )
        return Explanation(
            title=f"Got {left}, expected {right}",
            why="The computed value differs from the expected one.",
            fix="Print the intermediate values in the function, or check the expected value in the test.",
        )

    if op == "!=":
        return Explanation(
            title=f"Got {left}, which should not equal {right}",
            why="The value matches one you explicitly ruled out.",
            fix="Check the logic that produces this value.",
        )

    return Explanation(
        title=f"Condition failed: {left} {op} {right}",
        why="The comparison is false for the values produced by the code.",
        fix="Print both sides just before the assert to see their real values.",
    )


def explain(error_lines: List[str]) -> Explanation:
    """Return the most useful explanation for a list of pytest 'E' lines."""
    messages = [line.strip() for line in error_lines if line.strip()]

    # Exceptions first (most specific), searching from the bottom of the traceback.
    for line in reversed(messages):
        for pattern, build in RULES:
            match = pattern.search(line)
            if match:
                return build(match)

    # Then plain assertions written with `assert a == b`.
    for line in reversed(messages):
        if line.startswith("assert "):
            explanation = _explain_assert(line)
            if explanation:
                return explanation

    if any("AssertionError" in line or line.startswith("assert") for line in messages):
        return Explanation(
            title="An assertion failed",
            why="A condition you asserted is False for the current values.",
            fix="Compare the actual values shown in the traceback with what you expected.",
        )

    return Explanation(
        title="The test failed with an error whyfail does not recognize yet",
        why="The exception is not in the rule set. The raw message below is the best clue.",
        fix="Read the last line of the traceback, or open an issue to add a rule for it.",
    )
