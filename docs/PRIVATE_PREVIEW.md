# Private Codespaces Preview

This repository includes a GitHub Codespaces configuration for viewing the Industrial AI Foundry UI without installing Docker locally.

## Start

1. Open the repository on GitHub.
2. Select **Code**.
3. Open the **Codespaces** tab.
4. Select **Create codespace** on the desired branch.
5. Wait until the workspace opens.
6. Open the **Ports** panel.
7. Open port **5173 – Industrial AI Foundry**.

The preview ports are configured as **private**.

## Services

| Port | Service |
| --- | --- |
| 5173 | Foundry Console |
| 8000 | FastAPI |
| 7474 | Neo4j Browser |
| 9001 | MinIO Console |

## Startup behavior

Codespaces automatically:

- creates `.env` from `.env.example` when needed;
- starts the Docker Compose stack;
- forwards the application ports;
- keeps the preview access scoped to the authenticated Codespaces user.

If services need to be restarted manually:

```bash
bash scripts/codespace-start.sh
```

To inspect status:

```bash
docker compose ps
```

To inspect logs:

```bash
docker compose logs -f api frontend
```
