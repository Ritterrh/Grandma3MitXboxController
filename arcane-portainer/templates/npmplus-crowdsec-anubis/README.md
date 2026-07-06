# NPMplus with CrowdSec and Anubis

Arcane template for NPMplus, CrowdSec AppSec, and Anubis bot protection.

## Anleitung Kurzfassung

1. In Arcane unter `Settings -> Templates` diese Registry eintragen:

   ```text
   https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/registry.json
   ```

2. Danach bei `Compose Projects -> Create a New Project -> Use Template` das Template `NPMplus with CrowdSec and Anubis` auswählen.
3. Vor dem Deployment die `.env` Werte anpassen:
   - `TZ`
   - `INITIAL_ADMIN_EMAIL`
   - `INITIAL_ADMIN_PASSWORD`
   - `COOKIE_SECRET`
4. Stack starten.
5. NPMplus-Startpasswort prüfen, falls du kein eigenes `INITIAL_ADMIN_PASSWORD` gesetzt hast:

   ```sh
   docker logs npmplus
   ```

6. CrowdSec-Bouncer-Key erzeugen:

   ```sh
   docker exec crowdsec cscli bouncers add npmplus -o raw
   ```

7. Datei öffnen:

   ```text
   /opt/npmplus/crowdsec/crowdsec.conf
   ```

8. Dort setzen:

   ```text
   ENABLED=true
   API_KEY=<key aus cscli>
   ```

9. NPMplus neu starten:

   ```sh
   docker restart npmplus
   ```

10. In der NPMplus UI beim gewünschten Proxy Host `Anubis` als Auth-Request-Provider auswählen.

## What This Deploys

- `npmplus`: ZoeyVid/NPMplus, running with `network_mode: host`.
- `crowdsec`: CrowdSec Security Engine with the `ZoeyVid/npmplus` collection and AppSec listener.
- `anubis`: Anubis auth-request helper for bot challenges.

The CrowdSec acquisition config and the Anubis bot policy are embedded in `compose.yaml` through Docker Compose configs, so Arcane only needs `compose.yaml` and `.env.example`.

## Before Deploying

1. Make sure ports `80/tcp`, `443/tcp`, `443/udp`, and the NPMplus UI port are free on the host.
2. Edit `.env.example` values in Arcane before deployment:
   - `TZ`
   - `INITIAL_ADMIN_EMAIL`
   - `INITIAL_ADMIN_PASSWORD`
   - `COOKIE_SECRET`
3. Keep `CROWDSEC_LAPI_PORT`, `CROWDSEC_APPSEC_PORT`, and `ANUBIS_PORT` bound to localhost unless you know why they need to be exposed.

## After First Start

Generate the NPMplus CrowdSec bouncer key:

```sh
docker exec crowdsec cscli bouncers add npmplus -o raw
```

Then edit:

```text
/opt/npmplus/crowdsec/crowdsec.conf
```

Set:

```text
ENABLED=true
API_KEY=<the key from cscli>
```

Restart NPMplus:

```sh
docker restart npmplus
```

## Enable Anubis in NPMplus

The template already sets:

```text
AUTH_REQUEST_ANUBIS_UPSTREAM=http://127.0.0.1:8923
```

In the NPMplus UI, choose Anubis as the auth-request provider for the proxy host you want to protect. The embedded Anubis policy returns `401` for challenges and `403` for denied requests, as expected by NPMplus.

## Sources

- NPMplus: https://github.com/ZoeyVid/NPMplus
- CrowdSec NPMplus guide: https://docs.crowdsec.net/docs/next/appsec/quickstart/npmplus/
- Anubis Docker docs: https://techarohq-anubis.mintlify.app/installation/docker
