<?php 
	// print_r($_POST["tosend"]);
	$host    = "10.42.0.1";
	$port    = 8088;
//	echo "Message To server :".$message;
	$socket = socket_create(AF_INET, SOCK_STREAM, 0) or die("Could not create socket\n");
	$result = socket_connect($socket, $host, $port) or die("Could not connect to server\n");  
	socket_read ($socket, 1024) or die("Could not read server response\n");
	$message = "letmein";
	socket_write($socket, $message, strlen($message)) or die("Could not send data to server\n");
	socket_read ($socket, 1024) or die("Could not read server response\n");
	$message = "admin";
	socket_write($socket, $message, strlen($message)) or die("Could not send data to server\n");
	$rep = socket_read ($socket, 1024) or die("Could not read server response\n");
	echo $rep;
	$message = json_encode($_POST["tosend"]);
	socket_write($socket, $message, strlen($message)) or die("Could not send data to server\n");
	// $rep = socket_read ($socket, 1024) or die("Could not read server response\n");
	// echo $rep;
	socket_close($socket);
?>
