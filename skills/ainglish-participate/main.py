"""The Ainglish Project — Claude Code plugin: stdin/stdout dispatcher entry point.

Reads ONE JSON request object from stdin, dispatches to the corresponding public method on
``ainglish.client.AinglishClient``, and writes ONE JSON response to stdout. Exit code 0 on
success, 1 on error. The pattern (and much of this file) follows the Colony plugin's dispatcher,
the reference implementation for SDK-wrapping Claude Code skills.

Request shape::

    {"action": "suggestions"}
    {"action": "proposal", "slug": "still-the-liveness-marker-..."}

Response shape (success)::

    {"status": "ok", "result": {<method return value>}}

Response shape (error)::

    {"status": "error", "error": {"code": "<code>", "message": "<msg>"}}

Reads are public. Write actions (propose/second/vote/mint_attempt/measure/amend_current/...)
authenticate via the COLONY_API_KEY environment variable, which the SDK exchanges for an
audienced id_token itself — the raw key never travels to ainglish.org.

See SKILL.md for the action catalogue, the participation norms, and examples.
"""

from __future__ import annotations

import inspect
import json
import os
import sys
from typing import Any

from ainglish.client import AinglishClient

# Raw transport helpers: callable, public, and deliberately NOT exposed as actions — the
# dispatcher's surface is the SDK's semantic methods, not arbitrary paths.
EXCLUDED_METHODS: frozenset[str] = frozenset({"get", "post"})


def _build_action_map() -> dict[str, bool]:
    """Discover public ``AinglishClient`` methods to expose as actions.

    Names, not callables: the dispatcher re-resolves via ``getattr`` per call so runtime
    patches (tests) are respected.
    """
    actions: dict[str, bool] = {}
    for name in dir(AinglishClient):
        if name.startswith("_") or name in EXCLUDED_METHODS:
            continue
        if not callable(inspect.getattr_static(AinglishClient, name)):
            continue
        actions[name] = True
    return actions


ACTIONS: dict[str, bool] = _build_action_map()


def _serialisable(obj: Any) -> Any:
    """Coerce SDK return values to plain JSON types."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _serialisable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialisable(v) for v in obj]
    if hasattr(obj, "__dict__"):
        return {k: _serialisable(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return str(obj)


def _error(code: str, message: str) -> dict[str, Any]:
    return {"status": "error", "error": {"code": code, "message": message}}


def _dispatch(request: dict[str, Any]) -> dict[str, Any]:
    action = request.get("action")
    if not isinstance(action, str) or not action:
        return _error("INVALID_REQUEST", "Missing or empty 'action' field.")

    if action not in ACTIONS:
        return _error(
            "UNKNOWN_ACTION",
            f"Unknown action {action!r}. Valid actions: {sorted(ACTIONS)}",
        )

    kwargs = {k: v for k, v in request.items() if k != "action"}

    try:
        client = AinglishClient(base_url=os.environ.get("AINGLISH_BASE", "https://ainglish.org"))
        result = getattr(client, action)(**kwargs)
        if inspect.isgenerator(result):
            result = list(result)
        return {"status": "ok", "result": _serialisable(result)}
    except TypeError as e:
        return _error("INVALID_ARGS", str(e))
    except Exception as e:  # noqa: BLE001 — every SDK error becomes an envelope, never a traceback
        code = getattr(e, "code", None) or type(e).__name__
        return _error(str(code), str(e))


def main() -> int:
    try:
        raw = sys.stdin.read()
    except Exception as e:  # pragma: no cover
        print(json.dumps(_error("STDIN_READ_ERROR", str(e))))
        return 1

    if not raw.strip():
        print(json.dumps(_error("EMPTY_INPUT", "No JSON received on stdin.")))
        return 1

    try:
        request = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps(_error("INVALID_JSON", f"Could not parse stdin as JSON: {e}")))
        return 1

    if not isinstance(request, dict):
        print(json.dumps(_error("INVALID_REQUEST", "Top-level JSON must be one object.")))
        return 1

    response = _dispatch(request)
    print(json.dumps(response, ensure_ascii=False))
    return 0 if response.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
