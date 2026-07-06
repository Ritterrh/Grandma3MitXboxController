# tela

Self-hostable, markdown-native team wiki: Go + PostgreSQL backend, a React editor with live Yjs collaboration, full-text + optional semantic search, WebDAV sync, public/blog spaces, Slidev decks and PDF export. A built-in MCP server makes AI agents first-class editors, and Atlas can generate a cited wiki from your existing sources (git, Jira). After the stack is up, open the app on :8780 and complete /setup to create your admin account.

## Source

- Portainer template id: 587
- Portainer type: 3
- Compose source: https://raw.githubusercontent.com/lissy93/portainer-templates/HEAD/sources/stacks/tela.yml

## Notes

Three secrets are required and have no defaults: TELA_PG_PASSWORD, TELA_SHARE_SECRET and TELA_API_KEY_SECRET (generate each with openssl rand -hex 32). Keep them stable across redeploys — rotating TELA_API_KEY_SECRET invalidates every personal access token, and TELA_SHARE_SECRET invalidates outstanding share links. The app is served on port 8780; open it and complete /setup to create the first admin.
