#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Zeep library for webservices """
from zeep import Client

TYPES = ['window', 'light', 'door', 'curtain', 'clim', 'lux', 'temp']
CAT = {'window':'Object', 'light':'Object', 'door':'Object', \
            'curtain':'Object', 'clim':'Object', 'lux':'Sensor', 'temp':'Sensor'}
LOC = ['EXT', 'GM', 'GP', 'GEI']
ROOMS = {'EXT':1, 'GM':4, 'GP':3, 'GEI':5}

def createresource(loc, typ, i, lab):
    to_add = "_"+str(i+1)
    print '[+] Creating '+typ+to_add+' in '+loc
    try:
        print lab
        if loc == 'EXT':
            if typ != 'lux' and typ != 'temp':
                return
        if typ in CAT:
            lab = CAT[typ]
        msg = "{'ae':{'Name':'"+typ+to_add+"', 'AppID':'"+typ+to_add+"',\
            'RequestReachability':false, 'AppName':'"+typ+to_add+"', \
            'Label':'"+lab+"'}}"
        print msg
        client = Client('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
        cntxml = client.service.getXMLRep(msg)
        cntxml = cntxml.split('\n', 1)[-1]

        client = Client('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
        client.service.sendRequest('http://10.42.0.34:8181/~/'+loc+'-cse', \
                                        'admin:admin', 'create', cntxml, "2")

        client = Client('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
        cnt1xml = client.service.getXMLRep("{'cnt':{'Name':'DESCRIPTOR'}}")

        cnt2xml = client.service.getXMLRep("{'cnt':{'Name': 'DATA'}}")

        client = Client('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
        client.service.sendRequest('http://10.42.0.34:8181/~/'\
                +loc+'-cse/mn-name/'+typ+to_add, 'admin:admin', \
                'create', cnt1xml, "3")

        client.service.sendRequest('http://10.42.0.34:8181/~/'\
                +loc+'-cse/mn-name/'+typ+to_add, 'admin:admin', \
                'create', cnt2xml, "3")
        lab.encode("utf-8", "ignore")
        print lab
        if (typ == 'lux') or (typ == 'temp') or ("Sensor" in lab):
            print 'http://10.42.0.34:8181/~/'\
                    +loc+'-cse/mn-name/'+typ+to_add+'/DATA'
            try:
                msg = "<m2m:sub xmlns:m2m='http://www.onem2m.org/xml/protocols'\
                    rn='SUB_MY_SENSOR'><nu>http://10.42.0.1/monitor/monitor.php</nu><nct>2</nct>\
                    </m2m:sub>"
                client = Client('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
                client.service.sendRequest('http://10.42.0.34:8181/~/'\
                        +loc+'-cse/mn-name/'+typ+to_add+'/DATA', \
                        'admin:admin', 'create', msg, "23")
            except Exception, e:
                print "Didn't work"+e
    except Exception, e:
        print e

def main():
    """ Main function to create resources """
    for loc in LOC:
        for typ in TYPES:
            for i in xrange(ROOMS[loc]):
                createresource(loc, typ, i, "")

__all__ = ["createresource", "TYPES", "CAT", "LOC", "ROOMS"]

if __name__ == '__main__':
    main()
