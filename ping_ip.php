<?php
	$ip = $_GET['ip'];
	if($ip != null){
		exec("ping -c 1 -i 0.2 -W 1 $ip", $output, $retval);
		if (!$retval) echo "<h1>IP: $ip is responding.</h1>";
		else echo "<h1>IP: $ip is not responding. Verify that the computer is turned on.</h1>";
	}else echo "<h1>Enter an IP</h1>";
?>
