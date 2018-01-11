package fr.insa.ws.gsin;

import java.math.BigInteger;
import java.util.Iterator;

import org.eclipse.om2m.commons.resource.AE;
import org.eclipse.om2m.commons.resource.Container;
import org.eclipse.om2m.commons.resource.ContentInstance;
import org.json.*;
import fr.insat.om2m.tp2.mapper.Mapper;
import fr.insat.om2m.tp2.mapper.MapperInterface;
import obix.*;
import obix.io.ObixEncoder;

public class MapperWs {
	MapperInterface mapper = new Mapper();
	enum obixDT{ Abstime, Bool, Contract, ContractRegistry, Date, Enum, Err, Feed, Int, IObj, List, Obj, Op, Real, Ref, Reltime, Status, Str, Time, Uri, Val};
//	public static void main(String[] args) throws JSONException{
//		MapperWs ws = new MapperWs();
//		String json = "{'ae':{'Name':'MY_SENSOR'}}";
//		System.out.println(ws.getXMLRep(json));
//	}
	
	private obixDT getobixDataType(String input){
		if(input.equals("str")) return MapperWs.obixDT.Str;
		if(input.equals("bool")) return MapperWs.obixDT.Bool;
		if(input.equals("int")) return MapperWs.obixDT.Int;
		if(input.equals("real")) return MapperWs.obixDT.Real;
		if(input.equals("time")) return MapperWs.obixDT.Time;
		if(input.equals("uri")) return MapperWs.obixDT.Uri;
		if(input.equals("obj")) return MapperWs.obixDT.Obj;
		if(input.equals("list")) return MapperWs.obixDT.List;
		return MapperWs.obixDT.Str;
	}
	
	public String getXMLRep(String json_rep) throws JSONException{
		JSONObject json_obj = new JSONObject(json_rep);
		int state = 0;
		String info = "";
		try{
			info = json_obj.getJSONObject("ae").toString();
			state = 1;
		}
		catch(JSONException e1){
			try{
				info = json_obj.getJSONObject("cnt").toString();
				state = 2;
			}
			catch(JSONException e2){
				try{
					info = json_obj.getJSONObject("cin").toString();
					state = 3;
				}
				catch(JSONException e3){
					return "Cannot Resolve your request";
				}
			}
		}
		switch(state){
			case 1: return createAe(info);
			case 2: return createCnt(info);
			case 3: return createCin(info);
		}
//		MapperInterface mapper = new Mapper();
//		return mapper.marshal(obj);
		return info;
	}
	private String createAe(String info){
		JSONObject json_obj = new JSONObject();
		try {
			json_obj = new JSONObject(info);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		AE ae = new AE();
		try {
			ae.setName(json_obj.getString("Name"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			ae.setAppID(json_obj.getString("AppID"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			ae.setAppName(json_obj.getString("AppName"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			ae.setRequestReachability(json_obj.getBoolean("RequestReachability"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			ae.setAEID(json_obj.getString("Aeid"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
//			e.printStackTrace();
		}
		try {
			ae.setLabel(json_obj.getString("Label"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return mapper.marshal(ae);
	}
	
	private Obj createObject(JSONObject data_obj) throws JSONException{
		Obj object = new Obj();
		Iterator<?> keys = data_obj.keys();
		while(keys.hasNext()) {
		    String key = (String)keys.next();
		    switch(getobixDataType(key)){
		    	case Str:{
		    		Str value = new Str(data_obj.getJSONObject(key).getString("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case Bool:{
		    		Bool value = new Bool(data_obj.getJSONObject(key).getBoolean("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case Int:{
		    		Int value = new Int(data_obj.getJSONObject(key).getInt("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case Real:{
		    		Real value = new Real(data_obj.getJSONObject(key).getDouble("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case Obj:{
		    		Obj value = createObject(data_obj.getJSONObject(key).getJSONObject("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case Time:{
		    		Time value = new Time(data_obj.getJSONObject(key).getString("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case Uri:{
		    		Uri value = new Uri(data_obj.getJSONObject(key).getString("val"));
		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
		    	case List:{
//		    		List value = new List(data_obj.getJSONObject(key).getJSONArray("val"));
//		    		object.add(data_obj.getJSONObject(key).getString("name"), value);
		    		break;
		    	}
			default:
				break;
		    }
		}
		return object;
	}
	
	private String createCin(String info) throws JSONException{
		JSONObject json_obj = new JSONObject(info);
		ContentInstance cin = new ContentInstance();
		cin.setContentInfo("message");
//		cin.setName(json_obj.getString("Name"));
		Obj object = createObject(json_obj.getJSONObject("obj"));
		String result = ObixEncoder.toString(object);
		cin.setContentSize(BigInteger.valueOf(result.length()));
		cin.setContent(result);
		return mapper.marshal(cin);
	}
	private String createCnt(String info) throws JSONException{
		JSONObject json_obj = new JSONObject(info);
		Container cnt = new Container();
		cnt.setName(json_obj.getString("Name"));
		return mapper.marshal(cnt);
	}
}
