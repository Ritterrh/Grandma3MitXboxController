# Nzbget

[Nzbget](http://nzbget.com/) is a usenet downloader, written in C++ and designed with performance in mind to achieve maximum download speed by using very little system resources.

## Source

- Portainer template id: 406
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/nzbget/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/nzbget/configmkdir -p /srv/lsio/nzbget/downloads
