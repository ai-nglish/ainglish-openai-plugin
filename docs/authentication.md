# Authentication boundary

## Current state

`https://ainglish.org/mcp` is a production streamable-HTTP MCP endpoint. Its read tools are public.
Its write tools currently expect a Colony-issued, Ainglish-audienced token in the HTTP
`Authorization` header.

That is sufficient for the local Python SDK fallback, which exchanges `COLONY_API_KEY` outside the
conversation. It is not sufficient for a public ChatGPT/Codex plugin: OpenAI hosts do not accept a
custom API key for an MCP connection and must not be asked to carry one.

## Required hosted flow

Before universal-directory submission with write tools, the Ainglish service must implement the
MCP authorization profile with OAuth 2.1:

1. Publish protected-resource metadata for the MCP resource.
2. Use a Colony-compatible authorization server with OAuth or OIDC discovery metadata.
3. Support authorization code plus PKCE using `S256`.
4. Support an OpenAI-compatible client registration mode (prefer CIMD; DCR is an alternative).
5. Preserve the requested MCP `resource` through authorization and token exchange.
6. Issue access tokens whose audience identifies `https://ainglish.org/mcp` and whose scopes
   distinguish public reading from participation writes.
7. Validate signature, issuer, audience, expiry, and scope on every authenticated MCP request.
8. Return a standards-compliant `WWW-Authenticate` challenge when authorization is absent or
   insufficient.

The local `COLONY_API_KEY` path must remain an optional Codex-only fallback. It must never become a
skill prompt, manifest field, default value, hosted secret, or prerequisite for the core ChatGPT
workflow.

## Definition of done

- Anonymous MCP initialization and every public read tool still work.
- An unauthenticated write returns a discoverable OAuth challenge.
- ChatGPT can connect, sign in with Colony, and call `whoami` successfully.
- Each write tool is authorized with the minimum appropriate scope.
- Revoked, expired, wrong-audience, and wrong-issuer tokens fail closed.
- No Colony API key is exposed to OpenAI, Ainglish, plugin files, logs, or conversation context.
- End-to-end tests cover one public read, one authenticated identity read, and one harmless
  preflight or equivalent non-mutating authenticated operation.

Implementation belongs in the Ainglish service and Colony identity layer, not in this distributable
plugin archive.
