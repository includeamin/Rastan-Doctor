import pymongo
import json
import requests






configs = ""
with open("./Configures/Config.json") as f:
      configs = json.load(f)

Temp_GetDatabaseService = requests.get(
          configs["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=DbService").content
print( configs["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=DbService")
Temp_DatabaseService = json.loads(Temp_GetDatabaseService.decode("utf-8"))
mongodb = pymongo.MongoClient(Temp_DatabaseService[0]["url"])
database = mongodb[configs["RoleServiceDatabaseName"]]
roledb = database[configs["RoleCollection"]]
userroledb = database[configs["UserRole"]]
authtokendb = database[configs["Auth_Token"]]
permissiondb = database[configs["PermissionDbName"]]
rolepermissiondb = database[configs["RolesPermissionsDbName"]]



