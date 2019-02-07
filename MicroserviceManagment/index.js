const express = require('express')
const app = express()
var fs = require("fs")
var bodyParser = require('body-parser')
const fetch = require('node-fetch');
var parser = bodyParser.urlencoded({ extended: false })
var mongodbClient = require('mongodb').MongoClient;
var MongoDbUrl = 'Default'
var token = 'Default'
var ServiceDb = "Default"


var roleServiceUrl = "Default"
port = 3020

class ServiceInfo {
  
    constructor(name,url,port,description ){
        this.name= name
        this.url = url
        this.port = port
        this.description = description
       
    }

}

function InitializeService(){
 
  configs = JSON.parse(fs.readFileSync("./confiqure.json","utf8"))
  roleServiceUrl = configs["RoleService"]
  MongoDbUrl = configs["MongoDbUrl"]
  //load configs from database
  mongodbClient.connect(MongoDbUrl,{ useNewUrlParser: true },(err,db)=>{
   if(err) throw err;
   var dbo = db.db("InitializeDb")
   
   dbo.collection("Config").findOne({},(err,result)=>{
     if (err) throw err 
     token = result["OwnerToken"]
   })

  })
  //----------------Connect to microservices database ---------
  mongodbClient.connect(MongoDbUrl,{ useNewUrlParser: true },(err,db)=>{
    if(err) throw err;
    var dbo = db.db("Rastan_Words_MicroserviceManagement")
    
   ServiceDb = dbo
 
   })


  //-------- add service information in to server management database -----------



  //-------------- check role service availability ----------------

  //fetch(roleServiceUrl,{ useNewUrlParser: true })
  //.then(res => res.text())
  //.then(body => {console.log(body)
    //console.log("Role Service availability : Ok")
   //});
   
//------------ checking  report availability ---------------------
  

}

app.get('/',(req,res)=>{
    res.send("<div>Hello</div>  <div>This is Micromanagement service</div><div>Written by inlcudeamin</div>")
    res.end()
})
app.get('/ServicesInfo',parser,(req,res)=>{
    // should query to database and get all saved microservices
    try {
        ServiceDb.collection("Services").find({}).toArray(function(err, result) {
            if (err) throw err;
            
            res.send(result)
          });
    } catch (error) {
        console.log(error)
    }
  
})
app.post("/SetNewService",parser,(req,res)=>{

    try {
        var ServiceName = req.body["ServiceName"]
        var Url = req.body["Url"]
        var Port = req.body["Port"]
        var Description = req.body["Description"]
        var Service = new ServiceInfo(ServiceName,Url,Port,Description)
        ServiceDb.collection("Services").insertOne(Service,(err,res)=>{
            if(err) throw err
            console.log("New Service added")
            
        })
        res.send("Service added")
    } catch (error) {
        console.log(`insertation faild ${error}`)
        
    }   
    
    res.end()
    //require token  later should be update code
})

app.get("/Service/GetByName",(req,res)=>{
    try {
        var ServiceName = req.query["ServiceName"]
        ServiceDb.collection("Services").find({"name":ServiceName}).toArray(function(err, result) {
            if (err) throw err;
            
            res.send(result)
          });
    } catch (error) {
        console.log(error)
    }
})

//TODO: get all service that publisher  panel need to have access



app.listen(port,"0.0.0.0",()=>{
    console.log("loading configures")
    InitializeService()
        
    console.log(`The MicroservicesManagement now is running on port : ${port}!`)
})




