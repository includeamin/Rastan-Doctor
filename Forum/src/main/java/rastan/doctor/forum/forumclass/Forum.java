package rastan.doctor.forum.forumclass;


import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.web.bind.annotation.RequestHeader;
import rastan.doctor.forum.tools.Authentication;
import rastan.doctor.forum.tools.Header;
import rastan.doctor.forum.tools.Result;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

//@Document(collection = "Forum")
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

    public  Forum(String Title, String Description, String OwnerId, String OwnerUserName, String ForumIcon){

        this.Title = Title;
        this.Description = Description;
        this.OwerId = OwnerId;
        this.OwnerUserName = OwnerUserName;
        this.ForumIcon = ForumIcon;
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
                                   String userId,
                                   String UserName,
                                   String icon){
        if(!Authentication.IsAuth(Id,Token)){
            return Result.Response(false,"AD");
        }

        return Result.Response(true,Id);
    }

}
