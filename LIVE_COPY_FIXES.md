# TeamHealix live-copy fixes (not for the original Space)

Do not push these to MCP-1st-Birthday/TeamHealix.

Changes vs the November 2025 submission:
- Pin Python deps so a fresh Space build is reproducible.
- Install `gradio[mcp]==5.49.1` and launch with `mcp_server=True` so the
  MCP endpoint is `https://mackenzietechdocs-healixpath.hf.space/gradio_api/mcp/`.
- AI backend: the Anthropic client was removed. Generation uses open models through
  Hugging Face Inference Providers with each visitor's own token (Sign in with Hugging Face),
  so no API key or Space secret is needed. (The original model, `claude-3-haiku-20240307`, was retired on 20 April 2026.)
- Remove an unused `subprocess` import.

The TypeScript MCP server under `src/` is a local demo (no official MCP
transport) and `dist/` is gitignored, so a Gradio Space never ran it.
