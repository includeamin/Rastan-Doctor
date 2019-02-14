package rastan.doctor.forum.forumclass;

import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ForumRepository extends MongoRepository<Forum,ObjectId> {
}
