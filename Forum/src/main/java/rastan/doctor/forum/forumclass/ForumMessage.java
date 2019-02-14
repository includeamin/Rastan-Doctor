package rastan.doctor.forum.forumclass;

import java.time.LocalDateTime;
import java.util.HashMap;

public class ForumMessage {

    public String Title;
    public String Message;
    public LocalDateTime Create_at;
    public LocalDateTime Update_at;
    public boolean IsAccepted;
    public String AccepterId;
    public LocalDateTime Accept_at;
    public ForumMessage(String Title,String Message){
        this.Title=Title;
        this.Message=Message;
        this.Create_at = LocalDateTime.now();
        this.Update_at = LocalDateTime.now();
        this.IsAccepted = false;
        this.AccepterId = "";
        this.Accept_at = null;


    }
    public static HashMap Add_Message_to_Forum(String UserId,String Title,String Message){
        return null;
    }

}
