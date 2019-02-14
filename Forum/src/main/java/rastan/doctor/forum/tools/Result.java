package rastan.doctor.forum.tools;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.jackson.JsonObjectDeserializer;

import java.util.HashMap;

public class Result extends HashMap<String,Object> {

    public static HashMap<String,Object> Response(boolean state,String description){
        HashMap<String,Object> temp = new HashMap<>();
        temp.put("State",state);
        temp.put("Description",description);
        return temp;
    }
}
