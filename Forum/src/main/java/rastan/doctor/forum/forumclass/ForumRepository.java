package rastan.doctor.forum.forumclass;

import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import rastan.doctor.forum.forumclass.Forum.*;

public interface ForumRepository extends MongoRepository<Forum,ObjectId> {
    @Query("{Title:'?0'}")
    Forum findByTitle(String title);

}
