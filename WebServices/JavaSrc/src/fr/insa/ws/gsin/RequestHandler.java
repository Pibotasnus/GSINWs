package fr.insa.ws.gsin;

import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.math.BigInteger;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.net.ssl.HttpsURLConnection;
import org.apache.commons.io.IOUtils;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.eclipse.om2m.commons.resource.AE;
import org.eclipse.om2m.commons.resource.CSEBase;
import org.eclipse.om2m.commons.resource.ChildResourceRef;
import org.eclipse.om2m.commons.resource.Container;
import org.eclipse.om2m.commons.resource.ContentInstance;
import org.eclipse.om2m.commons.resource.RemoteCSE;
import org.json.JSONException;
import org.json.JSONObject;

import fr.insat.om2m.tp2.client.Client;
import fr.insat.om2m.tp2.client.Response;
import fr.insat.om2m.tp2.mapper.Mapper;
import fr.insat.om2m.tp2.mapper.MapperInterface;
import obix.Obj;
import obix.io.ObixDecoder;

public class RequestHandler {
	
	String url = "";
	String url_base = "";
	String originator = "";
	String toDelete = "";
	Boolean flag = true;
	MapperInterface mapper = new Mapper();
	
//	public static void main(String[] args) throws Exception {
//		String xml = "<m2m:cin xmlns:m2m='http://www.onem2m.org/xml/protocols'><cnf>message</cnf><con><obj><str name='appId' val='MY_SENSOR'/><str name='category' val='temperature '/> <int name='data' val='27'/><int name='unit' val='celsius'/></obj></con></m2m:cin>";
//		RequestHandler http = new RequestHandler();
//
//		System.out.println("Testing 1 - Send Http GET request");
//		String rs = http.sendRequest("http://127.0.0.1:8181/~/mn-cse/mn-name/Hello_Gei_1/DATA", "admin:admin", "create", xml, "4");
//		System.out.println(rs);
//	}
	
	private String discovery(CSEBase rs, String url) throws IOException{
		Client cli = new Client();
		Response reponse = new Response();
		String result = "";
		if(rs!=null)
		for (int i =0; i<rs.getChildResource().size();i++){
			if(flag && (BigInteger.valueOf(16).compareTo(rs.getChildResource().get(i).getType()) == 0) && !(rs.getChildResource().get(i).getResourceName().equals("in-name"))){
				reponse = cli.retrieve(url.split(this.toDelete)[0]+rs.getChildResource().get(i).getResourceName()+"?rcn=5", originator);
				result += reponse.getRepresentation();
				CSEBase base = (CSEBase) this.mapper.unmarshal(reponse.getRepresentation());
				result += discovery(base, url.split(this.toDelete)[0]+rs.getChildResource().get(i).getResourceName());
			}
			if(BigInteger.valueOf(2).compareTo(rs.getChildResource().get(i).getType()) == 0){
//				if(!toDelete.equals("mn-cse")){
					reponse = cli.retrieve(url+"/"+rs.getChildResource().get(i).getValue().split("/")[2], originator);
					result += reponse.getRepresentation();
//				}
//				else{
//					reponse = cli.retrieve(url+rs.getChildResource().get(i).getValue().split("/")[2], originator);
//					result += reponse.getRepresentation();
//				}
			}
		}
		return result;
	}
	
	public String getDecider(String type, String constraints, String value) throws JSONException{
		JSONObject json_obj = new JSONObject(constraints);
		if(type.equals("lux")){
			System.out.println(type);
			int x = json_obj.getInt("lux_min");
			int y = json_obj.getInt("lux_ext");
			int z = Integer.parseInt(value);
			if(z<x){
				if(y<x){
					return "on light";
				}
				else{
					return "open curtain\noff light";
				}
			}
		}
		else{
			if(type.equals("temp")){
				int w = json_obj.getInt("temp_min");
				int x = json_obj.getInt("temp_max");
				int y = json_obj.getInt("temp_ext");
				int z = Integer.parseInt(value);
				if(y>=w && y<=x)
					return "open window";
				else
					if(z>x)
						return x+" clim";
					else
						return w+" clim";
			}
		}
		return "ok";
	}

	public String sendRequest(String url, String origine, String operation, String operation_content, String type) throws Exception {
		this.url_base = url;
		this.originator = origine;
		this.toDelete = url.split("/")[4];
		Response rs = new Response();
		String result = "";
		Client cli = new Client();
		if(operation.equals("retrieve") || operation.equals(""))	{
			rs = cli.retrieve(url, origine);
			result += rs.getRepresentation();
		}
		else{
			if(operation.equals("discover")){
				rs = cli.retrieve(url+"?rcn=5", origine);
				CSEBase base = (CSEBase) this.mapper.unmarshal(rs.getRepresentation());
				result += rs.getRepresentation();
				result += discovery(base, url);
			}
			else{
				if(operation.equals("create") || operation == "u"){
					rs = cli.create(url, operation_content, origine, type);
					result += rs.getRepresentation();
				}
				else{
	//				con.setRequestMethod("PUT");
				}	
			}
		}
		
		return result;

	}
	
}
