# Plex

[Plex](https://plex.tv) organizes video, music and photos from personal media libraries and streams them to smart TVs, streaming boxes and mobile devices. This container is packaged as a standalone Plex Media Server. Straightforward design and bulk actions mean getting things done faster.

## Source

- Portainer template id: 463
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/plex/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/plex/configmkdir -p /srv/lsio/plex/tvmkdir -p /srv/lsio/plex/movies
