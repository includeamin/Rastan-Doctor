package rastan.doctor.forum;


import org.apache.http.HttpHeaders;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import rastan.doctor.forum.forumclass.Forum;
import rastan.doctor.forum.forumclass.ForumRepository;
import rastan.doctor.forum.tools.Authentication;
import rastan.doctor.forum.tools.Header;
import rastan.doctor.forum.tools.Result;

import java.io.File;
import java.util.HashMap;

@RestController
public class ForumController {

    @Autowired
    private ForumRepository repository;

    @GetMapping("/")
    public String Hello(){
        return "<div>" +
                "forum management microservice" +
                "</div>";
    }


    @PostMapping("/forum/add")
    public HashMap AddForum(@RequestHeader("Id") String Id, @RequestHeader("Token")String Token,
                            @RequestPart("Title") String Title ,
                            @RequestPart("Description") String Description,
                            @RequestPart("Icon")MultipartFile file


                            ){

            return Forum.AddForum(Id,Token,Title,Description,file,repository);

    }

}
