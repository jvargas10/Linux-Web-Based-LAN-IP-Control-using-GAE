The following project is intended to control LAN IP's via a web based application using the following technologies:

	* Python (Google App Engine)
	* PHP
	* JSON
	* HTML
	* CSS
	* Memcache
	* RegExp

Initially was thought to use only Python but due to framework limitations (Google App Engine),
PHP is used to execute terminal commands. It is not possible in Google App Engine because of
sandbox principles.

Application Features:

	* Controls IP's in a Linux environment serving as Internet gateway.
		- Turn off Computer IP
		- Turn on Computer IP
	* Computer Management System
		- Create computer (assign name, ip, location, computer features, installed programs,etc)
		- Update computer 
		- Delete computer
	* Check Computer IP response.

Requirements and considerations: 
	
	* Linux Server as a gateway
	* SELINUX disabled
	* Granted permission to execute the following commands from php:
		- sudo iptables -A FORWARD ...
		- sudo iptables -D FORWARD ...
		- sudo iptables-save > /etc/sysconfig/firewall-config
		- ping ...

 
