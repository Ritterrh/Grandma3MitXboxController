# Sealskin

[Sealskin](https://github.com/selkies-project/sealskin/) is a self-hosted, client-server platform that enables users to run powerful, containerized desktop applications streamed directly to a web browser. It uses a browser extension to intercept user actions—such as clicking a link or downloading a file and redirects them to a secure, isolated application environment running on a remote server.

## Source

- Portainer template id: 527
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/sealskin/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/sealskin/configmkdir -p /srv/lsio/sealskin/storage
