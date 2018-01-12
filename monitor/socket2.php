#!/usr/bin/env php
<?php
	require_once('./websockets.php');

	class Server extends WebSocketServer {
	  //protected $maxBufferSize = 1048576; //1MB... overkill for an echo server, but potentially plausible for other applications.
	  protected $us = array();
	  protected $available = array();
	  protected $size = 0;
	  protected $flag = False;
	  protected function process ($user, $message) {
	    echo $message."\n";
	    if (strpos($message, 'SET SRC :') !== false) {
		    $clienspli = explode(":", $message);
			 if (strpos($clienspli[1],'serversoap') === FALSE){
			 	array_push($this->available, $clienspli[1]);
				if(!$this->flag){
					$this->flag = True;
				}
				else{
					$this->size++;
				}
			}
			else{
				$this->send($user,"Clients:".json_encode($this->available));
			}
			
		    $this->us[$clienspli[1]] = $user;
	    }
		print_r($this->available);
	    foreach($this->us as $key => $val){
		$clien = $key;
		echo $clien."\n";
		echo $this->size." === ";
		echo sizeof($this->available)."\n";
		    if (strpos($clien,'serversoap') !== FALSE){
				if(sizeof($this->available) !== $this->size && !empty($this->available)){
					echo "ok";
					$this->send($val,"Clients:".json_encode($this->available));
					$this->size++;
					$this->flag = False;
				}
			}
			else{
				if($val !== $user && $val !== $this->us['serversoap'])
					$this->send($val, $message);
			}
		}	    
	    // foreach($this->users as $i){
		//if($i!=$user)
		//	$this->send($i,$message);
	    //}
	  }
	  
	  protected function connected ($user) {
		// array_push($this->us,$user);
	  }
	  
	  protected function closed ($user) {
	    // Do nothing: This is where cleanup would go, in case the user had any sort of
	    // open files or other objects associated with them.  This runs after the socket 
	    // has been closed, so there is no need to clean up the socket itself here.
		foreach($this->us as $key => $val){
			if($user === $val){
				foreach($this->available as $k => $b){
					if($b === $key){
						$this->available[$k] = "";
						$this->size--;
						$this->send($this->us['serversoap'],"Clients:".json_encode($this->available));
					}
				}
				unset($this->us[$key]);
			}
		}
	  }
	}

	$server = new Server("localhost","9090");

	try {
	  $server->run();
	}
	catch (Exception $e) {
	  $server->stdout($e->getMessage());
	}
?>
