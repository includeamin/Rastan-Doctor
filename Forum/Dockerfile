FROM java:8

# preserve Java 8  from the maven install.
RUN mv /etc/alternatives/java /etc/alternatives/java8
RUN apt-get update -y && apt-get install maven -y

COPY . ./app

# Restore Java 8
EXPOSE 3000

RUN mv -f /etc/alternatives/java8 /etc/alternatives/java
RUN ls -l /usr/bin/java && java -version
#RUN ./mvnw package
#RUN java -jar target/demo-0.0.1-SNAPSHOT.jar
#RUN ./mvnw spring-boot:run
WORKDIR /app
CMD ["ls"]
RUN  mvn clean install
CMD ["mvn","spring-boot:run"]
#CMD ["java","-jar","target/demo-0.0.1-SNAPSHOT.jar"]



