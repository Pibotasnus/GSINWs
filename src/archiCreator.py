#!/usr/bin/env python

""" Zeep library for webservices """
from zeep import Client

TYPES = ['window', 'light', 'door', 'curtain', 'clim', 'lux', 'temp']
CAT = {'window':'Object', 'light':'Object', 'door':'Object', \
            'curtain':'Object', 'clim':'Object', 'lux':'Sensor', 'temp':'Sensor'}
LOC = ['EXT', 'GM', 'GP', 'GEI']
ROOMS = {'EXT':1, 'GM':4, 'GP':3, 'GEI':5}

def main():
    """ Main function to create resources """
    for l in LOC:
        for t in TYPES:
            for i in xrange(ROOMS[l]):
                to_add = "_"+str(i+1)
                if(l=='EXT' ):
                    if ((t!='lux' and t!='temp')):
                        continue
                print '[+] Creating '+t+to_add+' in '+l
                msg = "{'ae':{'Name':'"+t+to_add+"', 'AppID':'"+t+to_add+"',\
                    'RequestReachability':false, 'AppName':'"+t+to_add+"', \
                    'Label':'Category/"+t+" Location/"+l+to_add+" Type/"+CAT[t]+"'}}"
                client = Client('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
                cntxml = client.service.getXMLRep(msg)
                cntxml = cntxml.split('\n', 1)[-1]

                client = Client('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
                result = client.service.sendRequest('http://10.42.0.34:8181/~/'+l+'-cse', \
                                                'admin:admin', 'create', cntxml, "2")

                client = Client('http://localhost:8080/GSINWss/services/MapperWs?wsdl')
                cnt1xml = client.service.getXMLRep("{'cnt':{'Name':'DESCRIPTOR'}}")

                cnt2xml = client.service.getXMLRep("{'cnt':{'Name': 'DATA'}}")

                client = Client('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
                result = client.service.sendRequest('http://10.42.0.34:8181/~/'+l+'-cse/mn-name/'+t+'_'+str(i+1),'admin:admin', 'create', cnt1xml, "3")

                result = client.service.sendRequest('http://10.42.0.34:8181/~/'+l+'-cse/mn-name/'+t+'_'+str(i+1),'admin:admin', 'create', cnt2xml, "3")

                if(t=='lux' or t=='temp'):
                    msg = "<m2m:sub xmlns:m2m='http://www.onem2m.org/xml/protocols' rn='SUB_MY_SENSOR'><nu>http://10.42.0.1/monitor/monitor.php</nu><nct>2</nct></m2m:sub>"
                    client = Client('http://localhost:8080/GSINWss/services/RequestHandler?wsdl')
                    result = client.service.sendRequest('http://10.42.0.34:8181/~/'+l+'-cse/mn-name/'+t+'_'+str(i+1)+'/DATA','admin:admin', 'create', msg, "23")



if __name__ == '__main__':
    main()
