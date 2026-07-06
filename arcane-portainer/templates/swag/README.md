# Swag

SWAG - Secure Web Application Gateway (formerly known as letsencrypt, no relation to Let's Encrypt™) sets up an Nginx webserver and reverse proxy with php support and a built-in certbot client that automates free SSL server certificate generation and renewal processes (Let's Encrypt and ZeroSSL). It also contains fail2ban for intrusion prevention.

## Source

- Portainer template id: 573
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/swag/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/swag/config
