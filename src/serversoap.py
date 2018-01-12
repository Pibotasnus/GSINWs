#!/usr/bin/env python
"""
@author: Pibotasnus
"""


""" Imports """

import socket
import select
import os
import sys
import getopt
import json
import ConfigParser
import websocket
import time
from gc import collect
from zeep import Client as cl
from threading import Thread
from datetime import datetime

BASE_URL = 'http://10.42.0.34:8181'
ORIGINATOR = 'admin:admin'
CLIENTS = []

class FuncThread(Thread):
    """ Redefining the thread class """
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        Thread.__init__(self)

    def run(self):
        self._target(*self._args)

INFO_BS = ['temp', 'light', 'clim']
LOC = ['GM', 'GP', 'GEI']
ROOMS = {'GM':4, 'GP':3, 'GEI':5}

def on_message(ws, message):
    """ Recv msg """
    print message
    global CLIENTS
    if "Clients" in message:
        configExt = ConfigParser.ConfigParser()
        configExt.read("Config/EXT.cfg")
        if "dont" not in message:
            CLIENTS = json.loads(message.split(":")[1])
        test = '{"TempExt": "'+configExt.get('Config', 'temp', 1)+'"}'
        on_send(ws, test)
        for i in CLIENTS:
            to_send = json.loads(test)
            loc, room = i.split("_")
            print loc, room
            if loc in LOC:
                for j in INFO_BS:
                    print j
                    print BASE_URL+"/~/"\
                        +loc+"-cse/mn-name/"+j+"_"+room+"/DATA/la"
                    result = requestHandler(BASE_URL+"/~/"\
                        +loc+"-cse/mn-name/"+j+"_"+room+"/DATA/la", "admin:admin", "retrieve", "", "")
                    print result
                    if j == "temp":
                        pattern = "name=&quot;Temp&quot; val=&quot;"
                        indx = result.find(pattern)+len(pattern)
                        value = result[indx: result.find("&quot;" , indx)]
                        to_send['TempInt'+i] = value
                    if j == "light":
                        pattern = "name=&quot;State&quot; val=&quot;"
                        indx = result.find(pattern)+len(pattern)
                        value = result[indx: result.find("&quot;" , indx)]
                        to_send['Light'+i] = value
                    if j == "clim":
                        pattern = "name=&quot;Temp&quot; val=&quot;"
                        indx = result.find(pattern)+len(pattern)
                        value = result[indx: result.find("&quot;" , indx)]
                        to_send['Radiator'+i] = value
            on_send(ws, json.dumps(to_send))

def on_send(ws, msg):
    """ Send msg """
    ws.send(msg)

def on_error(ws, error):
    """ If error occured """
    print(error)


def on_close(ws):
    """ Closing com """
    ws.close()
    print("### closed ###")


def on_open(ws):
    """ Opening com """
    def run(*args):
        ws.send("SET SRC :serversoap")
        time.sleep(1)

    Thread(target=run).start()

host = "ws://localhost:9090"
ws = websocket.WebSocketApp(host,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close)

def comInit(client):
    client.send("Identify yourself")
    if client.recv(1024).strip() == "letmein":
        return True
    return False

def door(url, action):
    if action == 'lock':
        action = True
    else:
        action = False
    client = cl('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
    config = ConfigParser.ConfigParser()
    config.read('Config/json_samples.cfg')
    config.set('cinDATA', 'state', action)
    cin = client.service.getXMLRep(config.get('cinDATA', 'door', 0))
    print requestHandler(url, ORIGINATOR, 'create', cin, "4")

def light(url, action):
    print "[!] Reaching "+url+" with intention "+action
    if action == 'on':
        action = True
    else:
        action = False
    client = cl('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
    config = ConfigParser.ConfigParser()
    config.read('Config/json_samples.cfg')
    config.set('cinDATA', 'state', action)
    cin = client.service.getXMLRep(config.get('cinDATA', 'light', 0))
    requestHandler(url, ORIGINATOR, 'create', cin, "4")
    
def window(url, action):
    if action == 'lock':
        action = True
    else:
        action = False
    client = cl('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
    config = ConfigParser.ConfigParser()
    config.read('Config/json_samples.cfg')
    config.set('cinDATA', 'state', action)
    cin = client.service.getXMLRep(config.get('cinDATA', 'window', 0))
    requestHandler(url, ORIGINATOR, 'create', cin, "4")

def curtain(url, action):
    if action == 'open':
        action = True
    else:
        action = False
    client = cl('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
    config = ConfigParser.ConfigParser()
    config.read('Config/json_samples.cfg')
    config.set('cinDATA', 'state', action)
    cin = client.service.getXMLRep(config.get('cinDATA', 'curtain', 0))
    requestHandler(url, ORIGINATOR, 'create', cin, "4")

def clim(url, action):
    client = cl('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
    config = ConfigParser.ConfigParser()
    config.read('Config/json_samples.cfg')
    config.set('cinDATA', 'temp', action)
    cin = client.service.getXMLRep(config.get('cinDATA', 'clim', 0))
    requestHandler(url, ORIGINATOR, 'create', cin, "4")

def requestHandler(url, originator, action, data, type):
    client = cl('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
    return client.service.sendRequest(url, originator, action, data, type)

def mapperWS(json_raw):
    client = cl('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
    return client.service.getXMLRep(json_raw)

def decider(category, constraints, value):
    client = cl('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
    return client.service.getDecider(category, constraints, value)

def interpreter(result, sur, type):
    try:
        AVAILABLE[result.split(' ')[-1]](BASE_URL +'/~'+ sur.replace(type, result.split(' ')[-1]).replace('SUB_MY_SENSOR', ''),\
                                        result.split(' ')[0])
    except:
        print 'Nothing to be done'

def logg(msg):
    with open("Logs/log-"+datetime.now().date(), "a") as log:
        log.write("\n"+datetime.now().time()+" "+ msg)

AVAILABLE = {
    'light'  : light,
    'window' : window,
    'door'   : door,
    'clim'   : clim,
    'curtain': curtain
}



def runWebSocketClient(ws):
    ws.run_forever()

class Server(object):
    """Server class"""
    def __init__(self, host,port):
        self.host = host
        self.port = port
        try:
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            print "[+] The Server has been successfully built."
        except:
            print "[-] The Server couldn't be build."
    def start(self):
        global ws
        try:
            ws.on_open = on_open
            t1 = FuncThread(runWebSocketClient, ws)
            t1.start()
            self.socket.bind((self.host,self.port))
            self.socket.listen(5)
            print "[+] The Server has been successfully started and is listening on port : "+str(self.port)+"."
        except:
            print "[-] The Server couldn't be started."
    def run(self):
        print "[+] The Server is running ..."
        master = 0
        opens  = []
        pseudo = {}
        client_location = 'in'
        c = 0
        configExt = ConfigParser.ConfigParser()
        configExt.read("Config/EXT.cfg")
        while 1:
            rlist, wlist, xlist = select.select([self.socket]+opens,[],[])
            for client in rlist:
                if client is self.socket:
                    try:
                        new_client, addr = self.socket.accept()
                        if comInit(new_client):
                            print "[+]  Connected successfully to the new client."
                            opens.append(new_client)
                            new_client.send("<SERVER>: Please give us your pseudo.\n")
                            pseudo[new_client] = new_client.recv(1024)
                            # print nick
                            new_client.send("<SERVER>: Welcome to our server.\n")
                        else :
                            new_client.send("NO !")
                            new_client.close()
                            print "[-] Failed to connect to the new client."
                    except:
                        print "[-] Except : Failed to connect to the new client."
                else:
                    msg = client.recv(2048)
                    try:
                        if msg == "" :
                            opens.remove(client)
                            client.close()
                            print "[-] "+pseudo[client]+" disconnected."
                            del pseudo[client]
                        else:
                            # print '[+] Got '+msg+ '\nFrom :'+pseudo[client]
                            if pseudo[client] == "monitor":
                                on_message(ws, "Clients dont")
                                sur = msg[msg.find("<sur>")+5:msg.find("</sur>")]
                                print '[!] sur: '+sur
                                location = sur.split('-')[0]
                                location = location.replace('/','')
                                print '[!] location: '+location
                                config = ConfigParser.ConfigParser()
                                obj_name = sur.split('/')[3]
                                print '[!] Object Name: '+obj_name
                                type = obj_name.split('_')[0]
                                if location is not "EXT":
                                    print '[!] We are in '+location
                                    config.read("Config/"+location+".cfg")
                                    if type == "lux":
                                        pattern = "name=&quot;Lux&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = msg[indx: msg.find("&quot;" , indx)]
                                        print '[!] Value of Lux: '+value
                                        constraints = "{'lux_min': "+config.get('Config', 'lux_min', 0)+", 'lux_ext':"+configExt.get('Config', 'lux', 1)+"}"
                                        print "[!] Constraints are "+str(constraints)
                                    if type == 'temp':
                                        pattern = "name=&quot;Temp&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = msg[indx: msg.find("&quot;" , indx)]
                                        print '[!] Value of temp: '+value
                                        constraints = "{'temp_min': "+config.get('Config', 'temp_min', 0)+", 'temp_max':"+config.get('Config', 'temp_max', 0)+", 'temp_ext':"+configExt.get('Config', 'temp', 1)+"}"
                                    result = decider(type, constraints, value)
                                    print '[!] Decision: '+result
                                    # logg(result+" in "+location+" for "+obj_name)
                                    result = result.split('\n')
                                    for op in result:
                                        interpreter(op, sur, type)
                                else:
                                    if type == "lux":
                                        pattern = "name=&quot;Lux&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = msg[indx: msg.find("&quot;" , indx)]
                                    if type == 'temp':
                                        pattern = "name=&quot;Temp&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = msg[indx: msg.find("&quot;" , indx)]
                                    config.set('Config', type, value)
                                    with open('Config/EXT.cfg', 'wb') as configfile:
                                        config.write(configfile)
                            if pseudo[client] == "admin":
                                location = msg
                                config = ConfigParser.ConfigParser()
                                obj_name = sur[3]
                                type = obj_name.split('_')[0]
                                if location is not "EXT":
                                    config.read("Config/"+location+".cfg")
                                    if type == "lux":
                                        pattern = "name=&quot;Lux&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = int(msg[indx: msg.find("&quot;" , indx)])
                                        constraints = "{'lux_min': "+config.get('Config', 'lux_min', 0)+", 'lux_ext':\
                                                        "+configExt.get('Config', 'lux', 1)+"}"
                                    if type == 'temp':
                                        pattern = "name=&quot;Temp&quot; val=&qusot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = int(msg[indx: msg.find("&quot;" , indx)])
                                        constraints = "{'temp_min': "+config.get('Config', 'temp_min', 0)+", 'temp_max':\
                                                         "+config.get('Config', 'temp_max', 0)+", 'temp_ext': "+configExt.get('Config', 'temp', 1)+"}"
                                    result = decider(type, constraints, value)
                                    logg(result+" in "+location+" for "+obj_name)
                                    interpreter(result, sur, type)
                                else:
                                    if type == "lux":
                                        pattern = "name=&quot;Lux&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = msg[indx: msg.find("&quot;" , indx)]
                                    if type == 'temp':
                                        pattern = "name=&quot;Temp&quot; val=&quot;"
                                        indx = msg.find(pattern)+len(pattern)
                                        value = msg[indx: msg.find("&quot;" , indx)]
                                    config.set('Config', type, value)
                                    with open('Config/EXT.cfg', 'wb') as configfile:
                                        config.write(configfile)
                    except:
                        print "[-] Something went wrong !"
            collect()

def main():
    """Main function"""
    length = len(sys.argv[1:])
    if not length:
        sys.exit(0)	
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:", ["host", "port"])
    except:
        sys.exit(0)
    for o, a in opts:
        if o in ("-p", "--port")  :
            port = int(a)
        elif o in ("-h", "--host")  :
            host = a
        else :
            sys.exit(0)
    ser = Server(host, port)
    ser.start()
    ser.run()

if __name__ == '__main__':
    main()
