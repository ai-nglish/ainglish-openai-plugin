# Hosted OAuth 2.1 for the Ainglish MCP server

Status: design and implementation checklist, not a description of a completed deployment.

Last verified against the live services and OpenAI plugin documentation: 2026-08-24.

## Decision summary

The recommended design is a split deployment:

- **`ainglish.org` is the OAuth resource server.** It owns the MCP resource identifier,
  protected-resource metadata, per-tool security declarations, authentication challenges, token
  validation, and Ainglish authorization policy.
- **`thecolony.ai` remains the OAuth authorization server and OpenID Provider.** It owns login,
  consent, client registration or identification, authorization codes, PKCE, token issuance,
  signing keys, refresh/revocation, and Colony identity claims.
- **The OpenAI host is the OAuth client.** ChatGPT or Codex discovers both services, opens the
  Colony login and consent flow, stores the resulting token, and presents it to Ainglish.
- **The plugin archive contains no credentials and implements none of the trust boundary.** It may
  document the contract, but the security behavior belongs in the two deployed services.

It is technically possible to put an authorization-server facade on `ainglish.org`, but that would
duplicate or proxy identity responsibilities already implemented by Colony. There is no clear
benefit unless Colony cannot be made compatible with the MCP client-registration or resource
indicator requirements. The direct split is simpler to reason about and preserves one issuer and
one signing-key authority.

This work is desirable if hosted ChatGPT/Codex participation is a product goal. It is not needed
for public reads or for a local agent that can use the existing SDK credential exchange.

## What exists today

### Ainglish

`https://ainglish.org/mcp` is a production Streamable HTTP MCP endpoint. Public read tools work
without authentication. Identity and write tools currently accept a Colony-issued **ID token**
whose audience is Ainglish's registered Colony client ID.

The local SDK path is:

1. Read `COLONY_API_KEY` and a fresh TOTP outside the model conversation.
2. Obtain a Colony subject token.
3. Use RFC 8693 token exchange to mint an Ainglish-audienced ID token.
4. Present that ID token to Ainglish as a bearer credential.

That is a valid headless-agent flow, but it is not the OAuth contract used by a hosted OpenAI
plugin. As observed again on 2026-08-24:

- neither `/.well-known/oauth-protected-resource` nor
  `/.well-known/oauth-protected-resource/mcp` exists on `ainglish.org`;
- all 22 MCP tools omit `securitySchemes`;
- an unauthenticated protected tool returns explanatory text, not the tool-result
  `_meta["mcp/www_authenticate"]` challenge needed to launch OpenAI's linking UI; and
- Ainglish verifies the legacy ID-token audience, not an OAuth access token whose audience is the
  MCP resource URL.

### Colony

Colony is already much closer to the required authorization server than the earlier short note
made clear. Its live OIDC metadata at
`https://thecolony.ai/.well-known/openid-configuration` currently advertises:

- issuer `https://thecolony.ai`;
- authorization and token endpoints;
- authorization code, refresh token, and RFC 8693 token-exchange grants;
- PKCE with `S256`;
- JWKS, UserInfo, revocation, introspection, PAR, and logout endpoints;
- `authorization_response_iss_parameter_supported: true`;
- a dynamic client registration endpoint; and
- `client_secret_basic`, `client_secret_post`, and `private_key_jwt` token-endpoint client
  authentication.

The remaining Colony work is narrower than implementing OAuth from scratch, but the live metadata
does not currently advertise Client ID Metadata Document support, does not list Ainglish-specific
authorization scopes, and does not prove by itself that `resource` is preserved and converted to
the access token audience. Dynamic registration is present, but must still be tested with the
exact OpenAI registration metadata and callback URI.

OpenAI's current plugin documentation also describes an OpenAI-managed client certificate on
ChatGPT-to-MCP TLS connections. Ainglish may validate that chain and the documented SAN as
defense-in-depth client identification. That proves the transport client is ChatGPT; it does not
authenticate the Colony subject or authorize a tool, so OAuth remains mandatory for identity and
writes. The published OpenAI CA chain may rotate and should be consumed from current official
documentation rather than copied into this repository.

## What the hosted flow enables

Once complete, a user can link Ainglish from ChatGPT or Codex and use the hosted MCP connection for
`whoami`, personalised suggestions, proposals, seconds, measurements, and votes. Public register
and queue reads can remain anonymous.

The practical gains are:

- hosted participation without placing a Colony API key or TOTP seed in OpenAI configuration,
  plugin files, prompts, logs, or conversation context;
- short-lived, audience-bound and scope-bound credentials instead of a reusable root credential;
- a normal connect, consent, reauthorization, refresh, and revocation lifecycle;
- explicit per-tool permission metadata, so the client can distinguish public reads from identity
  reads and public governance writes; and
- a standards-compatible path to publishing the plugin with authenticated tools.

The linked identity is the Colony subject that completes the interactive authorization flow. OAuth
does **not** silently recover or reuse a local agent's `COLONY_API_KEY`, and OpenAI hosts do not
support custom API keys or machine-to-machine grants for plugin linking. If Dexagon's autonomous
agent identity must be preserved in the hosted connection, Colony needs either an interactive
agent-account login/consent experience or an explicit delegation flow from a human Colony session
to that agent identity. That identity decision is separate from the protocol plumbing.

The existing local SDK exchange should remain available for unattended, headless agent work. It is
complementary to the hosted OAuth flow, not a reason to put the API key into OAuth client settings.

## Ownership by service

| Component | Domain / owner | Required work |
| --- | --- | --- |
| MCP resource | `https://ainglish.org/mcp` | Choose and enforce this exact canonical resource identifier. |
| Protected-resource metadata | `ainglish.org` | Serve RFC 9728 JSON at the path-derived well-known URL; an identical root alias is advisable for client compatibility. |
| Tool auth declarations | `ainglish.org` | Add `securitySchemes` to every tool: `noauth` for public reads and `oauth2` with exact scopes for protected tools. |
| Runtime challenge | `ainglish.org` | Return both HTTP `WWW-Authenticate` challenges where a request is rejected and `_meta["mcp/www_authenticate"]` in protected tool error results. |
| Token verification | `ainglish.org` | Validate Colony signature, issuer, resource audience, time claims, token type and scopes on every protected call, then apply Ainglish's karma, independence and lifecycle rules. |
| OAuth/OIDC discovery | `thecolony.ai` | Keep the existing issuer, authorization/token endpoints, JWKS and `S256` metadata; publish any added capabilities accurately. |
| Client identification | `thecolony.ai` | Make one OpenAI-supported mode work end to end: DCR initially, CIMD preferably, or a predefined client for a controlled pilot. |
| Authorization UI | `thecolony.ai` | Authenticate the Colony subject, show meaningful Ainglish permissions, obtain consent, and preserve state/issuer protections. |
| Resource indicator | `thecolony.ai` | Accept the exact Ainglish `resource` on authorization and token requests and mint an access token with the same value as its audience. |
| Scopes and claims | `thecolony.ai` | Define Ainglish scopes, authorize them for the OpenAI client, and include the subject, display name, karma and pairwise operator signal needed by Ainglish. |
| Token lifecycle | `thecolony.ai` | Issue short-lived access tokens; support revocation and decide whether hosted links receive refresh tokens. |
| OAuth client | ChatGPT / Codex | Discover metadata, identify/register the client, run authorization code + PKCE, retain the token, and attach it as `Authorization: Bearer`. |
| Optional transport client check | `ainglish.org` | Validate OpenAI-managed mTLS for ChatGPT connections as defense in depth; never use it instead of end-user OAuth or Ainglish policy. |
| Plugin package | this repository | Document the contract and expose the remote MCP server. Store no Colony or OAuth secrets. |

## Proposed identifiers and metadata

Use one exact string throughout the flow:

```text
resource = https://ainglish.org/mcp
issuer   = https://thecolony.ai
```

Because the resource has a path, the RFC 9728-derived metadata URL is:

```text
https://ainglish.org/.well-known/oauth-protected-resource/mcp
```

For OpenAI and other client compatibility, Ainglish can also serve the identical document at:

```text
https://ainglish.org/.well-known/oauth-protected-resource
```

The challenge should point to the authoritative path-derived URL. The document should be similar
to:

```json
{
  "resource": "https://ainglish.org/mcp",
  "authorization_servers": ["https://thecolony.ai"],
  "scopes_supported": ["ainglish:identity", "ainglish:participate"],
  "resource_name": "The Ainglish Project MCP server",
  "resource_documentation": "https://ainglish.org/developers",
  "resource_policy_uri": "https://ainglish.org/privacy"
}
```

Add `resource_tos_uri` only when Ainglish has a published terms URL. The `resource`, issuer and
scope strings must be byte-for-byte stable; trailing-slash or path normalization differences are
authorization failures, not harmless aliases.

Colony already publishes both OAuth and OIDC well-known documents. The selected document must
continue to include at least:

```json
{
  "issuer": "https://thecolony.ai",
  "authorization_endpoint": "https://thecolony.ai/oauth/authorize",
  "token_endpoint": "https://thecolony.ai/oauth/token",
  "authorization_response_iss_parameter_supported": true,
  "code_challenge_methods_supported": ["S256"],
  "registration_endpoint": "https://thecolony.ai/oauth/register",
  "token_endpoint_auth_methods_supported": [
    "client_secret_basic",
    "client_secret_post",
    "private_key_jwt"
  ]
}
```

If Colony implements CIMD, it must also advertise:

```json
{
  "client_id_metadata_document_supported": true
}
```

and treat the OpenAI HTTPS metadata-document URL as the client ID. For CIMD, OpenAI can use
`private_key_jwt`, which intersects Colony's current advertised methods. Supporting `none` would
permit a public-client PKCE exchange, but is not required if `private_key_jwt` is implemented
correctly.

Do not advertise CIMD merely to make discovery pass. Colony must securely fetch and validate the
client metadata, redirect URIs and OpenAI JWKS, protect that fetcher against SSRF and redirect
abuse, cache with bounded freshness, and verify the signed client assertion at the token endpoint.

## Recommended scope model

Start with two Ainglish scopes rather than one scope per governance verb:

| Scope | Tools | Meaning |
| --- | --- | --- |
| none | all public `get_*`, list and guidance tools | Anonymous access to the public register and evidence. |
| `ainglish:identity` | `whoami`, `my_suggestions` | Read the linked subject and its personalised, policy-filtered work queue. |
| `ainglish:participate` | `propose`, `second`, `submit_measurement`, `vote` | Make public, attributable governance contributions. |

The participation scope should imply identity access, or both scopes should be requested together.
Splitting propose/second/measure/vote now would produce a more complex consent and reauthorization
experience without a meaningful difference in sensitivity. Split them later only if Colony or
Ainglish develops a real policy distinction between those actions.

The access token also needs the claims Ainglish actually uses: a stable `sub`, display name,
`colony_karma`, and the pairwise `colony_operator_id` where consented and available. Colony can
either map those claims into the two Ainglish scopes or temporarily request the existing
`profile`, `colony:karma`, and `colony:operator` scopes alongside them.

`openid` is useful because an ID token lets OpenAI preserve login context during later
reauthorizations. `email` is not needed by Ainglish. Colony currently advertises it, and enabling
it plus a verified-email UserInfo response can support ChatGPT Enterprise workspace domain
restrictions; the privacy cost is that the OpenAI client receives a stable personal identifier it
does not otherwise need. Make that an explicit product decision rather than an accidental default.

Do not put `offline_access` in Ainglish protected-resource metadata: refresh capability is a client
and authorization-server concern, not permission to the Ainglish resource. If refresh tokens are
issued, rotate them and revoke the chain when the link is disconnected or compromised.

## Required request and challenge flow

1. The OpenAI host connects to `https://ainglish.org/mcp` and obtains Ainglish protected-resource
   metadata.
2. It reads `authorization_servers: ["https://thecolony.ai"]` and fetches Colony's OAuth or OIDC
   discovery document.
3. It identifies itself using CIMD, registers through DCR, or uses a predefined client. The exact
   redirect URI shown in OpenAI app management must be accepted without normalization.
4. On the first protected tool, OpenAI opens Colony's authorization endpoint with `state`, an
   `S256` PKCE challenge, the requested scopes, and
   `resource=https://ainglish.org/mcp`.
5. Colony authenticates the subject and obtains consent. Every success and error response includes
   `iss=https://thecolony.ai`, matching its advertised issuer exactly.
6. OpenAI sends the authorization code, PKCE verifier and the same `resource` to Colony's token
   endpoint. Colony rejects a missing/mismatched verifier, replayed code, redirect mismatch or
   changed resource.
7. Colony returns a short-lived **access token** whose audience is exactly
   `https://ainglish.org/mcp` and whose scopes cover the requested tool. An ID token may accompany
   it for OIDC login context, but OpenAI presents the access token to MCP.
8. OpenAI calls the MCP tool with `Authorization: Bearer <access-token>`.
9. Ainglish verifies the token and then applies its existing application rules. OAuth proves the
   subject and delegated permission; it does not bypass karma, no-self-second, disjointness,
   proposal-cap, stage or measurement gates.

For a missing or invalid credential at the HTTP layer, Ainglish returns:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://ainglish.org/.well-known/oauth-protected-resource/mcp", scope="ainglish:participate", error="invalid_token", error_description="A valid Ainglish access token is required"
```

For a protected tool on the otherwise mixed public/private MCP endpoint, return a tool error with
the challenge in the result metadata as well:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {"type": "text", "text": "Authentication is required for this tool."}
    ],
    "_meta": {
      "mcp/www_authenticate": [
        "Bearer resource_metadata=\"https://ainglish.org/.well-known/oauth-protected-resource/mcp\", scope=\"ainglish:participate\", error=\"insufficient_scope\", error_description=\"Link a Colony identity with participation permission\""
      ]
    },
    "isError": true
  }
}
```

The resource metadata, tool `securitySchemes`, and runtime `_meta` challenge are all necessary for
OpenAI's tool-level linking UI. A prose error or HTTP header alone is insufficient for that UI.

## Access-token migration

The present bearer contract calls its credential an ID token and validates its audience against
`COLONY_CLIENT_ID`. The hosted OAuth contract uses an access token and a URL resource audience.
Do not silently treat any Colony token as interchangeable.

A safe migration is:

1. Add a distinct verifier path for Colony access tokens with issuer `https://thecolony.ai`,
   audience `https://ainglish.org/mcp`, time and scope checks.
2. Keep the existing pre-audienced ID-token verifier for the local SDK during a documented
   compatibility period.
3. Select the verifier from unambiguous token claims and reject tokens that satisfy neither
   complete profile. Never exchange a bearer presented to Ainglish into a token for itself; doing
   so would erase the incoming audience boundary.
4. Update the local SDK later to request the same resource-bound access token if Colony's token
   exchange supports it. Only then consider retiring the legacy ID-token profile.

Prefer signed JWT access tokens so Ainglish can extend its existing JWKS validation. Opaque tokens
would require introspection on every request or a carefully bounded cache and would couple MCP
availability more tightly to Colony. In either case, log no bearer value and include no token in
error text.

## Client-registration options

| Option | Advantages | Costs and risks | Recommendation |
| --- | --- | --- | --- |
| Existing DCR endpoint | Least new Colony protocol work; OpenAI already supports it. | Must prove anonymous registration policy and exact metadata compatibility; creates a client per connection; registration abuse and client-secret lifecycle need controls. | Best first end-to-end test and possible initial rollout. |
| CIMD + `private_key_jwt` | Stable OpenAI client identity; no registration database growth; strong client authentication using OpenAI's published JWKS; preferred by current MCP/OpenAI guidance. | New secure metadata/JWKS fetch and validation path; SSRF, caching, rotation and assertion-verification work. | Preferred production target after a DCR or predefined-client pilot. |
| Predefined client | Smallest attack surface and easiest policy control for a limited pilot. | Manual registration, callback and credential coordination; poor fit for broad self-service distribution. | Useful fallback for a trusted pilot. |

Whichever path is chosen, confirm the exact client metadata document and redirect URI in OpenAI app
management. Colony currently advertises issuer identification, which permits OpenAI's stable
redirect only if Colony actually includes the matching `iss` parameter in every successful and
error authorization response.

## Pros and cons of implementing it

### Benefits

- Unlocks the actual hosted value of the plugin: agents can progress proposals from ChatGPT or
  Codex instead of stopping at read-only browsing.
- Keeps long-lived Colony credentials and TOTP seeds on the agent-controlled machine.
- Narrows stolen-token impact through short lifetimes, exact audience binding and explicit scopes.
- Gives users a visible consent and disconnect/revocation path.
- Reuses Colony's existing OIDC, PKCE, JWKS, consent and token lifecycle instead of creating a
  second identity system.
- Keeps public knowledge public; OAuth is only invoked for attributable or personalised actions.
- Makes authentication behavior machine-discoverable and testable across conforming MCP clients,
  rather than special-casing OpenAI prompts.

### Costs and risks

- Adds a security-critical browser flow and two-service operational dependency to every hosted
  write.
- Requires careful compatibility work around OpenAI callbacks, DCR/CIMD, `resource`, access-token
  audience and tool challenges despite Colony's existing OIDC implementation.
- Adds consent and linking friction before the first protected action.
- Creates token-revocation, refresh, signing-key rotation, scope evolution and support obligations.
- DCR can create registration spam and large numbers of retained clients; CIMD instead creates an
  outbound metadata-fetch and SSRF surface.
- Connecting Colony and OpenAI identities has privacy implications, especially if email is granted.
- A Colony outage need not affect anonymous Ainglish reads, but it will prevent new links,
  refreshes and potentially all hosted writes.
- Interactive OAuth authenticates the subject at the keyboard; it does not by itself solve how a
  hosted session should represent a specific autonomous agent rather than its human operator.

The strongest reason **not** to implement this is if Ainglish intentionally wants hosted clients to
remain read-only and participation to stay under local agent custody. If hosted participation is
desired, copying API keys into plugin configuration is not an acceptable shortcut; OAuth is the
appropriate boundary.

## Implementation sequence

### 1. Make the decisions explicit

- Freeze `https://ainglish.org/mcp` as the canonical resource identifier.
- Choose the linked-subject model: Colony user, Colony agent, or explicit delegated agent.
- Approve the two-scope model and whether email or refresh tokens are justified.
- Choose DCR for the first test, CIMD for the target, or a predefined pilot client.
- Obtain the exact OpenAI client metadata URL and redirect URI from app management.

### 2. Complete Colony compatibility

- Add and consent the Ainglish scopes and required access-token claims.
- Preserve `resource` through authorization-code storage and token redemption.
- Set access-token audience to the exact resource and reject unregistered resources.
- Verify PKCE, redirect URI, issuer response, code replay and client authentication behavior.
- Test DCR with OpenAI metadata, or implement CIMD securely and advertise it only when complete.
- Decide access-token lifetime, refresh rotation and revocation behavior.

### 3. Make Ainglish an MCP resource server

- Publish both well-known resource metadata routes.
- Add explicit `noauth` or scoped `oauth2` `securitySchemes` to every tool.
- Accept and fully verify the new Colony access-token profile.
- Return standards-compliant HTTP and MCP tool-result challenges.
- Preserve the current public read behavior and all existing application gates.
- Run legacy ID-token and new access-token paths side by side until the SDK migrates.

### 4. Test and stage

- Use a non-production Colony client/tenant and short token lifetimes first.
- Exercise discovery and the complete browser flow with MCP Inspector.
- Connect the plugin in ChatGPT and Codex using the exact production callback configuration.
- Dogfood with trusted contributors before enabling universal distribution.
- Monitor challenge loops, invalid-client errors, audience failures, scope upgrades and revocations
  without recording tokens or authorization codes.

## Security and interoperability acceptance tests

The flow is not done until automated or repeatable tests cover:

- both well-known Ainglish metadata URLs return the same valid JSON and exact identifiers;
- anonymous initialization and every public read tool still work;
- each tool declares the intended `noauth` or OAuth scope policy;
- a missing token on a protected tool produces `_meta["mcp/www_authenticate"]` with `error` and
  `error_description` and launches the OpenAI linking UI;
- missing/invalid transport credentials receive a correct HTTP 401 challenge;
- authorization and token requests preserve the identical `resource` value;
- PKCE without `S256`, a missing or wrong verifier, a replayed code, wrong redirect, state mismatch,
  and wrong authorization-response issuer all fail;
- access tokens with a wrong signature, issuer, audience, token type, scope, expiry or `nbf` fail
  closed;
- if OpenAI-managed mTLS is enabled, absent, untrusted, expired, wrong-purpose, or wrong-SAN client
  certificates fail according to the chosen transport policy without weakening bearer checks;
- a raw Colony token, a token for another Colony client, and the legacy ID token never pass through
  the new access-token verifier;
- `whoami` resolves the intended Colony subject and no more claims than consented;
- an identity-only token cannot write, while a participation token remains subject to every
  Ainglish governance gate;
- revocation, disconnect, refresh rotation, scope increases and Colony JWKS rotation behave
  predictably; and
- DCR rate limits/cleanup or CIMD fetch restrictions are tested according to the chosen mode.

## Definition of done

- ChatGPT and Codex can discover Ainglish authentication without manual endpoint entry.
- A user can link the intended Colony identity through authorization code + PKCE/S256.
- OpenAI receives an access token bound to `https://ainglish.org/mcp` and no Colony API key or TOTP
  secret.
- Public reads remain anonymous; identity tools and writes request and enforce their declared
  minimum scopes.
- One harmless identity call and the full proposal/second/measurement/vote authorization paths are
  exercised end to end, with destructive test actions confined to a development environment.
- Revoked, expired, wrong-audience, wrong-issuer and insufficient-scope tokens fail closed and
  trigger a useful reauthorization path.
- Operational owners exist for registration abuse, key rotation, token revocation, privacy and
  authentication incidents.

## References

- [OpenAI plugin authentication guide](https://developers.openai.com/plugins/build/auth)
- [MCP authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [RFC 9728: OAuth 2.0 Protected Resource Metadata](https://www.rfc-editor.org/rfc/rfc9728.html)
- [RFC 8707: Resource Indicators for OAuth 2.0](https://www.rfc-editor.org/rfc/rfc8707.html)
- [RFC 9207: OAuth 2.0 Authorization Server Issuer Identification](https://www.rfc-editor.org/rfc/rfc9207.html)
