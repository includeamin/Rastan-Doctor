package rastan.doctor.forum.forumclass;


import org.bson.types.ObjectId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.annotation.Id;
import org.springframework.data.domain.Example;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import org.springframework.data.mongodb.core.mapping.Field;
import org.springframework.data.mongodb.core.query.BasicQuery;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.multipart.MultipartFile;
import rastan.doctor.forum.tools.*;
import org.springframework.data.mongodb.core.*;

import javax.sound.midi.Track;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;

@Document(collection = "Forum")
public class Forum {
    @Id
    public ObjectId _id;
    @Indexed(unique = true)
    public String Title ;
    public String Description ;
    public int FollowrsCount ;
    public int MessageCount ;
    public List<ForumMessage> Messages;
    public List<FollowerList> FollowrList;
    public String OwerId;
    public String OwnerUserName;
    public String ForumIcon;
    public LocalDateTime Create_at;
    public LocalDateTime Update_at;
    public ForumStatus Status;

    public void set_id(ObjectId _id) {
        this._id = _id;
    }

    public String get_id() {
        return _id.toHexString();
    }

    public void setTitle(String title) {
        Title = title;
    }

    public String getTitle() {
        return Title;
    }

    public void setDescription(String description) {
        Description = description;
    }

    public String getDescription() {
        return Description;
    }

    public void setFollowrList(List<FollowerList> followrList) {
        FollowrList = followrList;
    }

    public int getMessageCount() {
        return MessageCount;
    }

    public void setFollowrsCount(int followrsCount) {
        FollowrsCount = followrsCount;
    }

    public void setMessageCount(int messageCount) {
        MessageCount = messageCount;
    }

    public void setForumIcon(String forumIcon) {
        ForumIcon = forumIcon;
    }

    public String getForumIcon() {
        return ForumIcon;
    }

    public void setMessages(List<ForumMessage> messages) {
        Messages = messages;
    }

    public String getOwerId() {
        return OwerId;
    }

    public void setOwerId(String owerId) {
        OwerId = owerId;
    }

    public String getOwnerUserName() {
        return OwnerUserName;
    }

    public void setOwnerUserName(String ownerUserName) {
        OwnerUserName = ownerUserName;
    }

    public int getFollowrsCount() {
        return FollowrsCount;
    }


    public  Forum(String Title, String Description, String OwnerId, String OwnerUserName  ){

        this.Title = Title;
        this.Description = Description;
        this.OwerId = OwnerId;
        this.OwnerUserName = OwnerUserName;
        this.FollowrList = new LinkedList<>();
        this.Messages = new LinkedList<>();
        this.FollowrsCount = 0;
        this.MessageCount = 0;
        this.Create_at = this.Update_at = LocalDateTime.now();
        //spater muss zu INPROGRESS wechseln
        this.Status = ForumStatus.CONFIRM;



    }
    public  Forum(ObjectId _id,String Title, String Description, String OwnerId, String OwnerUserName  ){
        this._id = _id;
        this.Title = Title;
        this.Description = Description;
        this.OwerId = OwnerId;
        this.OwnerUserName = OwnerUserName;
        this.FollowrList = new LinkedList<>();
        this.Messages = new LinkedList<>();
        this.FollowrsCount = 0;
        this.MessageCount = 0;
        this.Create_at = this.Update_at = LocalDateTime.now();
        //spater muss zu INPROGRESS wechseln
        this.Status = ForumStatus.CONFIRM;



    }

    public static HashMap AddForum(String Id,String Token,
                                   String title,
                                   String description,
                                   MultipartFile file
                        , ForumRepository repository){

        //if(!Authentication.IsAuth(Id,Token)){
        //  return Result.Response(false,"AD");
        // }


         HashMap UserData = Bridge.GetUserInformationById(Id);

         String OwUsername = "includemain";//UserData.get("UserName").toString();

         Forum forum = new Forum(title,description,Id,OwUsername);
        Forum exist = repository.findByTitle(title);
        if (exist!=null){
            System.out.println(exist.OwnerUserName);
            return Result.Response(true,"FAE");
        }







         repository.insert(forum);
         HashMap upload = UploadIcon(file,forum._id.toHexString());

         System.out.println(upload.toString());


        return Result.Response(true,Id);
    }

    public static HashMap UploadIcon(MultipartFile file ,String forumId){
        try {
            if( file.isEmpty()){
                return Result.Response(false,"FNF"); // file not found
            }
            byte[] bytes = file.getBytes();
            Path path = Paths.get(Tools.GetForumUploadsDir(forumId)+"/" + file.getOriginalFilename());
            System.out.println(path.toString());
            Files.write(path, bytes);
            return Result.Response(true,"FA"); // forum added

        }
        catch (Exception e){
            return Result.Response(false,e.getMessage());

        }
    }

}
