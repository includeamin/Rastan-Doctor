import pymongo
import json
import requests






configs = ""
with open("./Config.json") as f:
      configs = json.load(f)

Temp_GetDatabaseService = requests.get(
          configs["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=DbService").content
Temp_DatabaseService = json.loads(Temp_GetDatabaseService.decode("utf-8"))
mongodb = pymongo.MongoClient(Temp_DatabaseService[0]["url"])
database = mongodb[configs["UsersManagementDb"]]
usersDb = database[configs["UsersDb"]]
codesDb = database[configs["CodesDb"]]
temp_users = database[configs["TempUserDb"]]
messagedb = database[configs["MessageDb"]]