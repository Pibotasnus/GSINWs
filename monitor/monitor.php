<?php
	$host    = "10.42.0.1";
	$port    = 8088;
	$content = file_get_contents('php://input');
	file_put_contents('test.txt', $content.PHP_EOL , FILE_APPEND | LOCK_EX);
	$socket = socket_create(AF_INET, SOCK_STREAM, 0) or die("Could not create socket\n");
	$result = socket_connect($socket, $host, $port) or die("Could not connect to server\n");  
	socket_read ($socket, 1024) or die("Could not read server response\n");
	$message = "letmein"; 
	socket_write($socket, $message, strlen($message)) or die("Could not send data to server\n");
	socket_read ($socket, 1024) or die("Could not read server response\n");
	$message = "monitor";
	socket_write($socket, $message, strlen($message)) or die("Could not send data to server\n");
	socket_read ($socket, 1024) or die("Could not read server response\n");
	socket_write($socket, $content, strlen($content)) or die("Could not send data to server\n");
	socket_close($socket);
?>
