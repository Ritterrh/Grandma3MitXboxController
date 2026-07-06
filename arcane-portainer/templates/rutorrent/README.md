# ruTorrent

Popular torrent client with a webui for ease of use.

## Source

- Portainer template id: 521
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/rutorrent/compose.yaml
- Maintainer: https://github.com/novaspirit/pi-hosted/

## Notes

Template created by Pi-Hosted SeriesCheck our Github page: https://github.com/pi-hosted/pi-hostedOfficial Webpage: https://github.com/Novik/ruTorrentOfficial Docker Documentation: https://github.com/crazy-max/docker-rtorrent-rutorrentFor ruTorrent basic auth, XMLRPC through nginx and WebDAV on completed downloads, you can populate .htpasswd files with the following command:\ndocker run --rm -it httpd:2.4-alpine htpasswd -Bbn   >> $(pwd)/passwd/webdav.htpasswd
