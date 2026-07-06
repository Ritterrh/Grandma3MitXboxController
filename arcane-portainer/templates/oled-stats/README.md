# System Stats OLED display

A quick way to display system stats on a 128x64 I2C OLED display.

## Source

- Portainer template id: 579
- Portainer type: 1
- Compose source: https://raw.githubusercontent.com/Ritterrh/Grandma3MitXboxController/refs/heads/main/arcane-portainer/templates/oled-stats/compose.yaml
- Maintainer: https://github.com/novaspirit/pi-hosted/

## Notes

Template created by Pi-Hosted SeriesCheck our Github page: https://github.com/pi-hosted/pi-hostedOfficial Webpage: https://www.the-diy-life.com/Official Docker Documentation: https://github.com/mklements/OLED_Stats_DockerRun this command first to enable is2 communication! \nsudo raspi-config nonint do_i2c 0\nsudo /DietPi/dietpi/func/dietpi-set_hardware i2c enable || sudo /boot/dietpi/func/dietpi-set_hardware i2c enable\n
