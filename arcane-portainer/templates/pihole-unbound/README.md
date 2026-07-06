# Pi-Hole-Unbound

A Linux network-level advertisement and Internet tracker blocking application which acts as a DNS sinkhole. This version has Ubound software installed on it so you don't need to rely on external DNS providers. When the installation is complete, navigate to your.ip.goes.here:1010/admin. Follow the article <a href='https://medium.com/@niktrix/getting-rid-of-systemd-resolved-consuming-port-53-605f0234f32f'>here</a>

## Source

- Portainer template id: 451
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/pihole-unbound/compose.yaml
- Maintainer: https://github.com/novaspirit/pi-hosted/

## Notes

Template created by Pi-Hosted SeriesCheck our Github page: https://github.com/pi-hosted/pi-hostedOfficial Webpage: https://pi-hole.net/Official Docker Documentation: https://github.com/chriscrowe/docker-pihole-unbound/tree/master/one-containerPi-Hosted dedicated documentation: pi-hole.mdWhen the installation is complete, navigate to your.ip.goes.here:1010/admin. Follow the article here if you run into issues binding to port 53. For extra information on this container visit the mainteiner GitHub Page. You can add ports: 5335 to access Ubound externally; 22 to enable SSH; 67 to use DHCP Server. Add those ports in Show advanced options. if you run into issues binding to port 53. If you like to use Pi-Hole's built in DHCP-Server change the Network type to host and open advance options and scroll to Labels and add: NET_ADMIN with the value True. When you do so, specify a port is no more needed, navigate to your.ip.goes.here/admin.
