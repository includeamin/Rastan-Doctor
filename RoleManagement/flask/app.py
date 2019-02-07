from bson import objectid
from flask import Flask, request, Response, flash, Request, send_from_directory, send_file
import json
import datetime
from random import randint
import requests
import json
# from flask_pymongo import PyMongo
import pymongo
import os
import logging

from bson.json_util import dumps
import hashlib, binascii
from bson import objectid
from flask_cors import CORS
from DB import roledb, userroledb, permissiondb, rolepermissiondb, authtokendb

app = Flask(__name__)
cors = CORS(app)


# --------------------Db Collections--------------------------

class Permissions():
    def __init__(self, name, description):
        self.Name = name
        self.Created_at = datetime.datetime.now()
        self.Updated_at = datetime.datetime.now()
        self.Description = description


class User_Role():
    def __init__(self, user_id, role_id):
        self.User_Id = user_id
        self.RoleId = role_id
        self.Created_at = datetime.datetime.now()
        self.Updated_at = datetime.datetime.now()


class Role_Permission():
    def __init__(self, rolesId, permissions_Id_list):
        self.RolesId = rolesId
        self.RolesPermissionsIds = permissions_Id_list
        self.Created_at = datetime.datetime.now()
        self.Updated_at = datetime.datetime.now()


class Role():
    def __init__(self, name, description):
        self.Name = name
        self.Description = description
        self.Created_at = datetime.datetime.now()
        self.Updated_at = datetime.datetime.now()


class AuthToken():
    def __init__(self, userid, token, phonenumber=None, email=None):
        self.UserId = userid
        self.Email = email
        self.Token = token
        self.PhoneNumber = phonenumber
        self.Created_at = datetime.datetime.now()
        self.Updated_at = datetime.datetime.now()


class AuthTokenMail():
    def __init__(self, userid, token, email):
        self.UserId = userid
        self.Email = email
        self.Token = token
        self.Created_at = datetime.datetime.now()
        self.Updated_at = datetime.datetime.now()


class ResultVal:
    def __init__(self, state, description):
        self.State = state
        self.Description = description


# -------------------functions-------------------------------------

def Result(state, description):
    return dumps(ResultVal(state, description).__dict__)


def combinetwolist(list1, list2):
    one = set(list1)
    two = set(list2)
    return list1 + list(two - one)


def InitService(app):
    configs = ""
    with open("./Configures/Config.json") as f:
        configs = json.load(f)
    logging.warning("read congifs from file")
    app.config["MicroServiceManagementURl"] = configs["MicroServiceManagementURl"]

    Temp_GetDatabaseService = requests.get(
        app.config["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=DbService").content
    Temp_DatabaseService = json.loads(Temp_GetDatabaseService.decode("utf-8"))
    app.config["MogoDbUrl"] = Temp_DatabaseService[0]["url"]

    Temp_UserService = requests.get(
        app.config["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=UserManagement").content

    Temp_UserService = json.loads(Temp_UserService.decode("utf-8"))
    app.config["UserService"] = Temp_UserService[0]["url"]

    app.config["RoleDB"] = configs["RoleServiceDatabaseName"]
    app.config["PermissionDb"] = configs["PermissionDbName"]
    app.config["RolesPermissionDb"] = configs["RolesPermissionsDbName"]
    app.config["RoleCollection"] = configs["RoleCollection"]
    app.config["UserRole"] = configs["UserRole"]
    app.config["Auth_Token"] = configs["Auth_Token"]
    logging.warning("all configs are  set")
    logging.warning(
        app.config["MogoDbUrl"] + app.config["RoleDB"] + app.config["PermissionDb"] + app.config["RolesPermissionDb"])
    # app.run(debug=True, host="0.0.0.0", port=3001)


InitService(app)


def AddNewPermission(permissionName, description):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        permissionCol = database[app.config["PermissionDb"]]
        exist = permissionCol.find({"Name": permissionName})
        if exist.count() == 0:
            permissionCol.insert_one(Permissions((str(permissionName).upper()), description).__dict__)
            return Result(True, "Permission has been added")
        else:
            return Result(False, "same permission already exist")
    except Exception as ex:
        return Result(False, ex.args)


def AddNewRole(name, description):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        rolesCol = database[app.config["RoleCollection"]]
        exist = rolesCol.find({"Name": name})
        if exist.count() == 0:
            rolesCol.insert_one(Role(name, description).__dict__)
            return Result(True, "role name added")
        else:
            return Result(False, "same role name already exist")
    except Exception as ex:
        return Result(False, ex.args)


def DefineRolesPermission(RoleName, listofpermissions):
    try:
        permsionIdList = str(listofpermissions).split(',')

        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        rolesCol = database[app.config["RoleCollection"]]
        permissionCol = database[app.config["PermissionDb"]]
        rolesPermissionCol = database[app.config["RolesPermissionDb"]]

        role = rolesCol.find_one({"Name": RoleName})
        if role is not None:
            roleId = role["_id"]
            permissionIdList = []
            for per in permsionIdList:

                Temp_permision = permissionCol.find_one({"Name": per})
                if Temp_permision is None:
                    return Result(False,
                                  "one or some of permissions is not exist or invalid , check and re-request again")
                else:
                    permissionIdList.append(Temp_permision["_id"])

            Temp_RolesPermission = Role_Permission(roleId, permissionIdList)
            exist = rolesPermissionCol.find_one({"RolesId": roleId})

            if exist is not None:
                logging.warning(permissionIdList)
                oldperlist = list(exist["RolesPermissionsIds"])
                newlist = combinetwolist(oldperlist, permissionIdList)
                rolesPermissionCol.update_one({"RolesId": roleId}, {
                    "$set": {"RolesPermissionsIds": newlist, "Updated_at": datetime.datetime.now()}})
                return Result(False, "Same roles permission alreadey defined , but permissions are updated")
            else:
                rolesPermissionCol.insert_one(Temp_RolesPermission.__dict__)

            return Result(True, "new Role defined")
        else:
            return Result(False, "This Role Name not exist")

    except Exception as ex:
        logging.warning(ex)
        return Result(False, ex.args)




def RequestUserIdFromUsersService(phonenumber):
    token = InternalTokenDesign(b"GetUserID")
    resp_content = requests.get(app.config["UserService"] + "Service/GetUserId" + "/" + str(token) +
                                "/" + phonenumber).content

    if json.loads(resp_content.decode("utf-8"))["State"]:
        return json.loads(resp_content.decode("utf-8"))["Description"]
    else:
        return None
#/system/users/validid/<id>
def IsValidId(id):
    resp_content = requests.get(app.config["UserService"] + "/system/users/validid/"+id).content

    if json.loads(resp_content.decode("utf-8"))["State"]:
        return True
    else:
        return False


def InternalTokenDesign(requestKey):
    hash_object = hashlib.sha256(requestKey)
    hex_dig = hash_object.hexdigest()
    return hex_dig


def AddUserRolePermission(phonenumber, roleName):
    try:
        userId = RequestUserIdFromUsersService(phonenumber)
        if userId is None:
            return Result(False, "user with this phoneNumber not exist")
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        rolesCol = database[app.config["RoleCollection"]]
        userRoleCol = database[app.config["UserRole"]]
        role = rolesCol.find_one({"Name": roleName})
        if role is not None:
            roleid = role["_id"]
            exist = userRoleCol.find_one({"User_Id": userId})
            if exist is None:

                userRoleCol.insert_one(User_Role(userId, roleid).__dict__)
                return Result(True, "new Role added to " + phonenumber)
            else:
                userRoleCol.update_one({"User_Id": userId},
                                       {"$set": {"RoleId": roleid, "Updated_at": datetime.datetime.now()}})
                return Result(True, "new Role updated to " + phonenumber)
        else:
            return Result(False, "This role name not fount")

    except Exception as ex:
        return Result(False, ex.args)

def AddUserRolePermission_id(id, roleName):
    try:
        #check valid ip
        if not IsValidId(id):
            return Result(False,"IVID")#invalid id
        userId = id #RequestUserIdFromUsersService(phonenumber)
        if userId is None:
            return Result(False, "user with this phoneNumber not exist")
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        rolesCol = database[app.config["RoleCollection"]]
        userRoleCol = database[app.config["UserRole"]]
        role = rolesCol.find_one({"Name": roleName})
        if role is not None:
            roleid = role["_id"]
            exist = userRoleCol.find_one({"User_Id": userId})
            if exist is None:

                userRoleCol.insert_one(User_Role(userId, roleid).__dict__)
                return Result(True, "new Role added to " + id)
            else:
                userRoleCol.update_one({"User_Id": userId},
                                       {"$set": {"RoleId": roleid, "Updated_at": datetime.datetime.now()}})
                return Result(True, "new Role updated to " + id)
        else:
            return Result(False, "This role name not fount")

    except Exception as ex:
        return Result(False, ex.args)


def CheckPermission(phonenumber, permission):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        userId = RequestUserIdFromUsersService(phonenumber)
        userRoleCol = database[app.config["UserRole"]]
        rolesPermissionCol = database[app.config["RolesPermissionDb"]]
        permissionCol = database[app.config["PermissionDb"]]

        permission_exist = permissionCol.find_one({"Name": permission})
        if permission_exist is None:
            return Result(False, "this permission not exist")
        permission_id = permission_exist["_id"]

        user_has_role = userRoleCol.find_one({"User_Id": userId})
        if user_has_role is None:
            return Result(False, "user has no role !")
        users_rols_permissions = rolesPermissionCol.find_one({"RolesId": user_has_role["RoleId"]})
        if users_rols_permissions is None:
            return Result(False, "Role not found")
        permissionList = list(users_rols_permissions["RolesPermissionsIds"])
        if permissionList.__contains__(permission_id):
            return Result(True, "Permission Accepted")

        return Result(False, "permission Denied")
    except Exception as ex:
        return Result(False, ex.args)


def CheckPermission_id(userId, permission):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        # userId = RequestUserIdFromUsersService(phonenumber)
        userRoleCol = database[app.config["UserRole"]]
        rolesPermissionCol = database[app.config["RolesPermissionDb"]]
        permissionCol = database[app.config["PermissionDb"]]

        permission_exist = permissionCol.find_one({"Name": permission})
        if permission_exist is None:
            return Result(False, "this permission not exist")
        permission_id = permission_exist["_id"]

        user_has_role = userRoleCol.find_one({"User_Id": userId})
        if user_has_role is None:
            return Result(False, "user has no role !")
        users_rols_permissions = rolesPermissionCol.find_one({"RolesId": user_has_role["RoleId"]})
        if users_rols_permissions is None:
            return Result(False, "Role not found")
        permissionList = list(users_rols_permissions["RolesPermissionsIds"])
        if permissionList.__contains__(permission_id):
            return Result(True, "Permission Accepted")

        return Result(False, "permission Denied")
    except Exception as ex:
        return Result(False, ex.args)


def GenUserAuthToken():
    pass


def AddUsersTokenToAuthentications(userId, token, phonenumber=None):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        Auth_Token = database[app.config["Auth_Token"]]
        Auth_Token.delete_one({"UserId": userId})
        Auth_Token.insert_one(AuthToken(userId, token, phonenumber).__dict__)
        return Result(True, "Token Added ")

    except Exception as ex:

        return Result(False, ex.args)


def AddUsersTokenToAuthentications_email(userId, token, email=None):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        Auth_Token = database[app.config["Auth_Token"]]
        Auth_Token.delete_one({"UserId": userId})
        Auth_Token.insert_one(AuthTokenMail(userId, token, email).__dict__)
        return Result(True, "Token Added ")

    except Exception as ex:

        return Result(False, ex.args)


def CheckUserLogin(userId):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        Auth_Token = database[app.config["Auth_Token"]]
        temp = Auth_Token.find_one({"UserId": userId})
        if temp is not None:
            return Result(True, temp["Token"])
        else:
            return Result(False, "User not logged in")
    except Exception as ex:
        return Result(False, ex.args)


def LogOut(userid):
    try:
        mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
        database = mongodb[app.config['RoleDB']]
        Auth_Token = database[app.config["Auth_Token"]]
        Auth_Token.find_one_and_delete({"UserId": userid})
        return Result(True, "logged out")

    except Exception as ex:
        return Result(False, ex.args)


def AddPublisherRole(phonenumber):
    try:
        userid = RequestUserIdFromUsersService(phonenumber)
        publisherrole = roledb.find_one({"Name": "Publisher"})
        if publisherrole is None:
            return Result(False, "role not exist")

        roleid = publisherrole["_id"]

        userroledb.insert_one(User_Role(userid, roleid).__dict__)
        return Result(True, "publisher role add to user")

    except Exception as ex:
        return Result(False, ex.args)


# ------------------routes-----------------------------------------

@app.route('/')
def hello_world():
    return "<div> this is role manager and access contorl server </div> <div> written by amin jamal (includeamin)</div>"


@app.route("/permissions/add", methods=["POST"])
def AddPermission():
    form = request.form
    permissionName = form["PermissionName"]
    description = form["Description"]
    status = AddNewPermission(permissionName, description)
    return status


@app.route("/roles/add", methods=["POST"])
def AddRole():
    form = request.form
    name = form["RoleName"]
    description = form["Description"]
    status = AddNewRole(name, description)
    return status


@app.route("/rolepermission/define", methods=["POST"])
def Define_Role_Permission():
    form = request.form
    roleName = form["RoleName"]
    rawPermissions = form["Permissions"]
    status = DefineRolesPermission(RoleName=roleName, listofpermissions=rawPermissions)
    return status


@app.route("/userrolepermission/define", methods=["POST"])
def Add_User_Role_Permission():
    form = request.form
    phonenumber = form["PhoneNumber"]
    RoleName = form["RoleName"]
    status = AddUserRolePermission(phonenumber, RoleName)
    return status

@app.route("/userrolepermission/id/define", methods=["POST"])
def Add_User_Role_Permission_id():
    form = request.form
    id = form["Id"]
    RoleName = form["RoleName"]
    status = AddUserRolePermission_id(id, RoleName)
    return status


@app.route("/publisher/addrole/<token>/<phonenumber>")
def Add_Publisher_Role(token, phonenumber):
    inToken = InternalTokenDesign(b"ADDPUBLISHER")
    if inToken == token:
        status = AddPublisherRole(phonenumber=phonenumber)
        return status
    else:
        return Result(False, "Access Denied")


# ip secure
#@app.route("/userpermission/check/<phonenumber>/<permission>/")
#def Check_User_Permission(phonenumber, permission):
 #   status = CheckPermission(phonenumber, permission)
  #  return status


@app.route("/userpermission/check/id/<id>/<permission>/")
def Check_User_Permission(id, permission):
    status = CheckPermission_id(id, permission)
    return status


@app.route("/authentication/addtoken/", methods=["POST"])
def User_Authenticated():
    form = request.form
    try:
        key = InternalTokenDesign(b"SETAUTHTOKEN")

        requestKey = form["Key"]
        userId = form["User_Id"]
        token = form["Auth_Token"]
        phonenumber = form["PhoneNumber"]
        if key == requestKey:
            status = AddUsersTokenToAuthentications(userId, token, phonenumber)
            return status
        else:
            return Result(False, "Access Denied , internal request access denied")


    except Exception as ex:
        return Result(False, ex.args)


@app.route("/authentication/addtoken/email", methods=["POST"])
def User_Authenticated_mail():
    form = request.form
    try:
        key = InternalTokenDesign(b"SETAUTHTOKEN")
        requestKey = form["Key"]
        userId = form["User_Id"]
        token = form["Auth_Token"]
        email = form["Email"]
        if key == requestKey:
            status = AddUsersTokenToAuthentications_email(userId, token, email)
            return status
        else:
            return Result(False, "Access Denied , internal request access denied")


    except Exception as ex:
        return Result(False, ex.args)


@app.route("/authentication/checklogin/", methods=["POST"])
def Check_User_Login():
    form = request.form
    request_token = InternalTokenDesign(b"CHECKUSERLOGIN")
    token = form["Token"]
    userId = form["UserId"]
    if request_token == token:
        status = CheckUserLogin(userId)
        return status
    else:
        return Result(False, False)


@app.route("/authentication/logout/", methods=["POST"])
def User_Log_Out():
    form = request.form
    request_token = InternalTokenDesign(b"LOGOUTUSER")
    token = form["Token"]
    userId = form["User_Id"]
    if request_token == token:
        status = LogOut(userId)
        return status
    else:
        return Result(False, "internal request : access denied")


@app.route("/isauth/<token>/<user_token>/<phonenumber>/")
def Is_Auth(token, user_token, phonenumber):
    try:
        request_token = InternalTokenDesign(b"ISAUTH")
        logging.warning(request_token)
        logging.warning(token)
        if request_token == token:
            mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
            database = mongodb[app.config['RoleDB']]
            Auth_Token = database[app.config["Auth_Token"]]

            token_in_db = Auth_Token.find_one({"PhoneNumber": phonenumber})["Token"]

            if user_token == token_in_db:
                logging.warning("done")
                return Result(True, "access accept")
            else:
                logging.warning("hier")
                return Result(False, "Authentication faild")

        else:
            logging.warning("err")
            return Result(False, "Access denied , internal request access denied")
    except Exception as ex:
        return Result(False, ex.args)


@app.route("/isauth/<token>/<user_token>/<id>/id")
def Is_Auth_id(token, user_token, id):
    try:
        request_token = InternalTokenDesign(b"ISAUTH")
        logging.warning(request_token)
        logging.warning(token)
        if request_token == token:
            mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
            database = mongodb[app.config['RoleDB']]
            Auth_Token = database[app.config["Auth_Token"]]

            token_in_db = Auth_Token.find_one({"UserId": id})["Token"]

            if user_token == token_in_db:
                logging.warning("done")
                return Result(True, "access accept")
            else:
                logging.warning("hier")
                return Result(False, "Authentication faild")

        else:
            logging.warning("err")
            return Result(False, "Access denied , internal request access denied")
    except Exception as ex:
        return Result(False, ex.args)


if __name__ == '__main__':


    app.run(host="0.0.0.0", port=3021, debug=True)
