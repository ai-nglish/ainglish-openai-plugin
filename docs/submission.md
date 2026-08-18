# OpenAI submission readiness

Use the OpenAI **With MCP** submission path and include both skills in the same draft.

## Repository checks

- [x] `.codex-plugin/plugin.json` identifies the package and bundled components.
- [x] Both skills use portable Agent Skills frontmatter.
- [x] The production HTTPS MCP endpoint is bundled for local testing.
- [x] Listing artwork, privacy URL, source URL, and support metadata are present.
- [x] Offline unit and package tests pass.
- [ ] Server-side OAuth 2.1 is complete and tested as described in `authentication.md`.
- [ ] Every MCP tool has final safety annotations and confirmation behavior reviewed.
- [ ] A clean ChatGPT developer-mode connection passes public and authenticated smoke tests.

## Portal steps after OAuth is ready

1. Obtain Apps Management write access in the OpenAI organization that will own the listing.
2. Complete the required individual or business identity verification.
3. In the plugin submission portal, create a **With MCP** draft.
4. Submit `https://ainglish.org/mcp` directly and verify control of `ainglish.org`.
5. Configure OAuth using the service's discovery metadata and the exact redirect information shown
   by the portal.
6. Add `ainglish-participate` and `ainglish-write` to the same draft.
7. Test in a clean environment, address every automated scan result, and submit for review.

`.app.json` is intentionally absent from source control. It would contain a portal-created
connection identifier that does not exist until the MCP server is registered; inventing one would
make the source package look more complete while making it less reproducible.
