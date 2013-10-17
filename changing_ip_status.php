<?php 

	function turn_ip_state($ip_state){
		if($ip_state == 0) return 1;
		else return 0;
	}

	$json_data_string = file_get_contents("http://192.168.1.1:8080/.json");

	if($json_data_string != "Error"){
		$json_data = json_decode($json_data_string);

		$action = array(0=>"DROP", 1=>"ACCEPT");

		foreach($json_data as $ip => $ip_state){
			exec("sudo iptables -A FORWARD -s $ip -j $action[$ip_state]");
			exec("sudo iptables -D FORWARD -s $ip -j".$action[turn_ip_state($ip_state)]);
		}

		exec("sudo iptables-save > /etc/sysconfig/firewall-config");

		header("Location:http://192.168.1.1:8080/");
	}else echo "<h1> Error. There is no JSON data, try again.</h1>";

?>
