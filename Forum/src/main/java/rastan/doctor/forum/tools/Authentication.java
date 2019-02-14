package rastan.doctor.forum.tools;

import org.apache.commons.codec.binary.Hex;
import org.json.JSONException;
import org.json.JSONObject;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class Authentication {
    public static boolean IsAuth(String Id,String Token) {

        String hash = "e52d49edf9e16e8ffebc25f5599fc1aa251ff40c67b5103c351b5d1920e91127";
        String url = "http://89.32.251.131:3021/isauth/"+hash+"/"+Token+"/"+Id+"/id";
        RestTemplate client = new RestTemplate();
        String result = client.getForObject(url,String.class);
        System.out.println(result);
        try {

            JSONObject jsonObj = new JSONObject(result);

            return (boolean)jsonObj.get("State");


        } catch (JSONException e) {
            e.printStackTrace();
            return false;
        }

    }
}
