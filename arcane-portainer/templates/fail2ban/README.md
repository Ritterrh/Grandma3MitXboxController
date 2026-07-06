# Fail2ban

[Fail2ban](http://www.fail2ban.org/) is a daemon to ban hosts that cause multiple authentication errors.

## Source

- Portainer template id: 149
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/fail2ban/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/fail2ban/configmkdir -p /srv/lsio/fail2ban/var/log:romkdir -p /srv/lsio/fail2ban/remotelogs/airsonic:romkdir -p /srv/lsio/fail2ban/remotelogs/apache2:romkdir -p /srv/lsio/fail2ban/remotelogs/authelia:romkdir -p /srv/lsio/fail2ban/remotelogs/emby:romkdir -p /srv/lsio/fail2ban/remotelogs/filebrowser:romkdir -p /srv/lsio/fail2ban/remotelogs/homeassistant:romkdir -p /srv/lsio/fail2ban/remotelogs/lighttpd:romkdir -p /srv/lsio/fail2ban/remotelogs/nextcloud:romkdir -p /srv/lsio/fail2ban/remotelogs/nginx:romkdir -p /srv/lsio/fail2ban/remotelogs/nzbget:romkdir -p /srv/lsio/fail2ban/remotelogs/overseerr:romkdir -p /srv/lsio/fail2ban/remotelogs/prowlarr:romkdir -p /srv/lsio/fail2ban/remotelogs/radarr:romkdir -p /srv/lsio/fail2ban/remotelogs/sabnzbd:romkdir -p /srv/lsio/fail2ban/remotelogs/sonarr:romkdir -p /srv/lsio/fail2ban/remotelogs/unificontroller:romkdir -p /srv/lsio/fail2ban/remotelogs/vaultwarden:ro
