package rastan.doctor.forum;


import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import rastan.doctor.forum.tools.Result;

import java.util.HashMap;

@RestController
public class temp {
    @GetMapping("/amin")
    @ResponseBody
    public HashMap amin(){

        return Result.Response(false,"aminjamal");
    }
}
