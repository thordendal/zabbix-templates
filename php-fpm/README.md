# PHP-FPM with pool discovery

## Installation:
1. Add `pm.status_path = /status-fpm` to your fpm pool definition
2. Copy `zabbix_agentd.d` to your `/etc/zabbix` directory
3. Copy `scripts` to some folder user `zabbix` has access too. Note that
default zabbix-agent config assumes that `scripts` dir will be located
in `/home/zabbix`
4. Restart `zabbix-agent`. Test with `zabbix-agent -p | grep php`
5. Import zbx_template_php-fpm.xml