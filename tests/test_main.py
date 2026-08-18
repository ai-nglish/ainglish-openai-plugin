"""Dispatcher unit tests — offline: the client is monkeypatched, no network is touched."""

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "participate_main",
    Path(__file__).resolve().parent.parent / "skills" / "ainglish-participate" / "main.py",
)
main = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(main)


def run(request, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(request) if isinstance(request, dict) else request))
    code = main.main()
    out = capsys.readouterr().out.strip()
    return code, json.loads(out)


def test_action_map_exposes_semantic_methods_and_hides_transport():
    assert "proposal" in main.ACTIONS
    assert "suggestions" in main.ACTIONS
    assert "second" in main.ACTIONS
    assert "get" not in main.ACTIONS
    assert "post" not in main.ACTIONS


def test_unknown_action_is_a_typed_error(monkeypatch, capsys):
    code, resp = run({"action": "definitely_not_a_method"}, monkeypatch, capsys)
    assert code == 1
    assert resp["status"] == "error"
    assert resp["error"]["code"] == "UNKNOWN_ACTION"
    # the error names the valid actions so the caller can self-correct
    assert "proposal" in resp["error"]["message"]


def test_invalid_json_is_a_typed_error(monkeypatch, capsys):
    code, resp = run("{not json", monkeypatch, capsys)
    assert code == 1
    assert resp["error"]["code"] == "INVALID_JSON"


def test_empty_input_is_a_typed_error(monkeypatch, capsys):
    code, resp = run("", monkeypatch, capsys)
    assert code == 1
    assert resp["error"]["code"] == "EMPTY_INPUT"


def test_dispatch_calls_the_named_method_with_kwargs(monkeypatch, capsys):
    calls = {}

    class FakeClient:
        def __init__(self, base_url="https://ainglish.org"):
            calls["base_url"] = base_url

        def proposal(self, slug):
            calls["slug"] = slug
            return {"slug": slug, "stage": "proposed"}

    monkeypatch.setattr(main, "AinglishClient", FakeClient)
    code, resp = run({"action": "proposal", "slug": "some-row"}, monkeypatch, capsys)
    assert code == 0
    assert resp == {"status": "ok", "result": {"slug": "some-row", "stage": "proposed"}}
    assert calls == {"base_url": "https://ainglish.org", "slug": "some-row"}


def test_wrong_kwargs_surface_as_invalid_args(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, base_url=""):
            pass

        def proposal(self, slug):  # noqa: ARG002
            return {}

    monkeypatch.setattr(main, "AinglishClient", FakeClient)
    code, resp = run({"action": "proposal", "nope": "x"}, monkeypatch, capsys)
    assert code == 1
    assert resp["error"]["code"] == "INVALID_ARGS"


def test_sdk_errors_become_envelopes_never_tracebacks(monkeypatch, capsys):
    class Boom(Exception):
        code = "rejected"

    class FakeClient:
        def __init__(self, base_url=""):
            pass

        def second(self, slug):
            raise Boom("the register said no")

    monkeypatch.setattr(main, "AinglishClient", FakeClient)
    code, resp = run({"action": "second", "slug": "row"}, monkeypatch, capsys)
    assert code == 1
    assert resp["error"] == {"code": "rejected", "message": "the register said no"}
