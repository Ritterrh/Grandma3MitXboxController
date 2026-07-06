# Syncthing (container)

[Syncthing](https://syncthing.net) replaces proprietary sync and cloud services with something open, trustworthy and decentralized. Your data is your data alone and you deserve to choose where it is stored, if it is shared with some third party and how it's transmitted over the Internet.

## Source

- Portainer template id: 576
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/syncthing/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/syncthing/configmkdir -p /srv/lsio/syncthing/data1mkdir -p /srv/lsio/syncthing/data2
