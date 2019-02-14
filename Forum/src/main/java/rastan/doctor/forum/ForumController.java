package rastan.doctor.forum;


import org.apache.http.HttpHeaders;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
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


    @GetMapping("/forum/add")
    public HashMap AddForum(@RequestHeader("Id") String Id,@RequestHeader("Token")String Token){


            repository.insert(new Forum("amin","amin","asd","amin","amin"));
            return Forum.AddForum(Id,Token,"","","","","");

    }

}
