# Ldap-auth

[Ldap-auth](https://github.com/nginxinc/nginx-ldap-auth) software is for authenticating users who request protected resources from servers proxied by nginx. It includes a daemon (ldap-auth) that communicates with an authentication server, and a webserver daemon that generates an authentication cookie based on the user’s credentials. The daemons are written in Python for use with a Lightweight Directory Access Protocol (LDAP) authentication server (OpenLDAP or Microsoft Windows Active Directory 2003 and 2012).

## Source

- Portainer template id: 296
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/ldap-auth/compose.yaml
- Maintainer: https://github.com/technorabilia/portainer-templates/

## Notes

Portainer App Templates by Technorabilia, based on data provided by LinuxServer.io.Ensure to create the following volume directories on the host file system, or modify the paths in the volume mapping section under the advanced options below, as needed.mkdir -p /srv/lsio/ldap-auth/config
