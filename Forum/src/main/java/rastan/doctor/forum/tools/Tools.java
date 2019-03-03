package rastan.doctor.forum.tools;

import java.io.File;
import java.nio.file.Paths;

public class Tools {

    public static String GetForumUploadsDir(String Id){
        String Target = Paths.get("./ForumData",Id,"Icon").toString();
        File file = new File(Target);
        file.mkdirs();
        System.out.println(Target);


        return Target;
    }
    public static String RandomeFileName(){
        return "";
    }
}
