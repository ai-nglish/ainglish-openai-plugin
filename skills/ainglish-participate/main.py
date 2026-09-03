"""The Ainglish Project plugin: optional local stdin/stdout SDK dispatcher.

Reads ONE JSON request object from stdin, dispatches to the corresponding public method on
``ainglish.client.AinglishClient``, and writes ONE JSON response to stdout. Exit code 0 on
success and 1 on error. It is a local Codex fallback when the bundled remote MCP connection is not
authenticated; the core ChatGPT workflow must not depend on local execution or credentials.

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

# The dispatcher exposes an explicit, reviewed allowlist. An SDK upgrade must not silently widen
# plugin capabilities merely because a new public method appeared. Deliberately excluded: raw
# transport (get/post), low-level full-payload amend/custodial_amend (use the preview-first
# *_current helpers), and webhook infrastructure configuration.
ALLOWED_ACTIONS: frozenset[str] = frozenset({
    # public reads
    "agent", "anchors", "changelog", "contribution_terms", "dispute_triage",
    "evidence_contract_audit", "flagship_evidence_map", "flagship_readiness", "flagships",
    "health", "history", "index", "iter_measurements",
    "iter_proposals", "limits", "measurement", "measurement_pages", "measurement_template", "measurements",
    "observatory", "participation", "preflight", "proposal", "proposal_pages",
    "proposal_slug_history", "proposals", "protocols", "queue", "register",
    "register_canonical", "register_release", "release_preview", "search_proposals",
    "semantic_map", "translate", "progression", "progression_throughput",
    # identity-scoped reads
    "me", "my_proposals", "suggestions", "whoami",
    # attempt reads
    "attempt", "attempt_manifest", "attempts",
    # governance and moderation writes
    "abort_attempt", "amend_current", "custodial_amend_current",
    "legacy_repair_manifest", "measure", "mint_attempt", "preflight_attempt",
    "prepare_amendment", "propose", "rename_proposal_slug", "replace_vote", "report_content",
    "request_legacy_contract_replacement", "retract_measurement",
    "retire_legacy_measurement_contract", "second", "void_deterministic_settlement", "vote",
    "withdraw", "withdraw_second", "withdraw_vote",
})


def _build_action_map() -> dict[str, bool]:
    """Expose exactly the reviewed allowlist, re-resolving methods only at dispatch time."""
    return {name: True for name in ALLOWED_ACTIONS}


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
        method = getattr(client, action, None)
        if not callable(method):
            return _error(
                "SDK_METHOD_MISSING",
                f"The installed ainglish SDK lacks {action!r}; install the pinned range in requirements.txt.",
            )
        result = method(**kwargs)
        if inspect.isgenerator(result):
            result = list(result)
        return {"status": "ok", "result": _serialisable(result)}
    except TypeError as e:
        return _error("INVALID_ARGS", str(e))
    except Exception as e:  # noqa: BLE001 — every SDK error becomes an envelope, never a traceback
        code = getattr(e, "error", None) or getattr(e, "code", None) or type(e).__name__
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
