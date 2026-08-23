#!/usr/bin/env python3
"""Sync the bundled skill reference from Ainglish's canonical compiler."""

import argparse
import hashlib
import os
import pathlib
import re
import tempfile
import urllib.request

FORMAT = "ainglish.agent-reference.v1"
REFERENCE_PATH = "/api/v1/register/reference.md"
CANONICAL_PATH = "/api/v1/register.canonical"
MAX_REFERENCE_BYTES = 5_000_000
MAX_REGISTER_BYTES = 20_000_000
ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "skills" / "ainglish-write" / "reference.md"


def _fetch(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "ainglish-reference-sync/1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("response exceeds the bounded sync size")
        return data, {key.lower(): value for key, value in response.headers.items()}


def validate(reference, canonical, reference_headers, canonical_headers):
    """Validate the compiler identity and its binding to independently fetched register bytes."""
    try:
        text = reference.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("reference is not UTF-8") from error
    if not text.startswith("# The Ainglish register — agent reference\n\n"):
        raise ValueError("reference has an unexpected document identity")
    format_match = re.search(r"^> Format: `([^`]+)`$", text, re.MULTILINE)
    digest_match = re.search(r"^> Register SHA-256: `([0-9a-f]{64})`$", text, re.MULTILINE)
    version_match = re.search(r"^> Register version: `([0-9]+\.[0-9]+\.[0-9]+)`$", text, re.MULTILINE)
    if not format_match or format_match.group(1) != FORMAT:
        raise ValueError("reference compiler format is missing or unsupported")
    if not digest_match or not version_match:
        raise ValueError("reference lacks its register version or digest")
    digest = hashlib.sha256(canonical).hexdigest()
    claimed = digest_match.group(1)
    if claimed != digest:
        raise ValueError("reference digest does not match independently fetched canonical bytes")
    for label, headers in (("reference", reference_headers), ("canonical", canonical_headers)):
        header_digest = headers.get("x-register-digest")
        if header_digest is not None and header_digest != digest:
            raise ValueError("%s X-Register-Digest disagrees with the bytes" % label)
    header_format = reference_headers.get("x-ainglish-reference-format")
    if header_format is not None and header_format != FORMAT:
        raise ValueError("reference format header disagrees with the document")
    return {"format": FORMAT, "version": version_match.group(1), "register_digest": digest,
            "reference_sha256": hashlib.sha256(reference).hexdigest()}


def _replace(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sync reference.md from the register-identified canonical Markdown endpoint.")
    parser.add_argument("--base-url", default="https://ainglish.org")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true",
                        help="Verify that the local reference already equals the canonical bytes.")
    args = parser.parse_args(argv)
    base = args.base_url.rstrip("/")
    reference, reference_headers = _fetch(base + REFERENCE_PATH, MAX_REFERENCE_BYTES)
    canonical, canonical_headers = _fetch(base + CANONICAL_PATH, MAX_REGISTER_BYTES)
    receipt = validate(reference, canonical, reference_headers, canonical_headers)
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != reference:
            raise SystemExit("reference.md is stale for register %s" % receipt["register_digest"])
        print("reference.md is current: %(version)s %(register_digest)s" % receipt)
        return 0
    _replace(args.output, reference)
    print("wrote %s: %s %s" % (args.output, receipt["version"], receipt["register_digest"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
