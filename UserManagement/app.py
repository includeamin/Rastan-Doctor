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
import hashlib, binascii
import logging
from flask_cors import CORS
from DB import usersDb, codesDb ,temp_users , messagedb
from smtplib import SMTP_SSL
import hashlib, uuid

app = Flask(__name__)
cors = CORS(app)


def Result(state, description):
    return json.dumps({
        "State": state,
        "Description": description
    })


def dumps(data):
    return json.dumps(data, indent=4, sort_keys=True, default=str)


# ---------------------- database collections --------------------------
class VerificationsCodePhoneNumber:
    def __init__(self, phonenumber, code):
        self.User_PhoneNumber = phonenumber
        self.User_Code = code
        self.IsUsed = False
        self.GenerateTime = datetime.datetime.now()


class VerificationsCodeEmail:
    def __init__(self, email, code):
        self.User_Email = email
        self.User_Code = code
        self.IsUsed = False
        self.GenerateTime = datetime.datetime.now()







class User():
    def __init__(self, phonenumber=None, username=None, email=None, password=None, ip=None , isactive=False,
                 fname=None,
                 lname =None,
                 ):
        self.UserName = username
        self.Email = email
        self.Fname = fname
        self.Lname = lname
        self.Birthday = None
        self.gender = None
        self.province = None
        self.city = None
        self.address = None
        self.alias = None
        self.time = None
        self.PassWord = password
        self.Ip = ip
        self.PhoneNumber = phonenumber
        self.Create_at = datetime.datetime.now()
        self.Update_at = datetime.datetime.now()
        self.Inventory = ""
        self.IsActive = isactive
        self.EndSession=datetime.datetime.now()
        self.StartSession = datetime.datetime.now()
        self.Message={}
        self.Status = "INPROGRESS" #CONFIRM #NOTCONFIRM
        self.Profile = "1.png"



    @staticmethod
    def sign_up_by_phonenumber(phonenumber,fname=None,lname=None):
        try:
            user = usersDb.find_one({"PhoneNumber":phonenumber})
            if user is not None:
                if user["IsActive"] == True:
                    return Result(False, "UAE")

            if fname is None:
                fname = User.GenUniqUserName()
            if lname is None:
                lname = fname
            usersDb.delete_one({"PhoneNumber":phonenumber})
            usersDb.insert_one(User(phonenumber,fname,lname).__dict__)
            User.SendVerificationCode(phonenumber)
            return Result(False,"CS") # code sent
        except Exception as ex:
            return Result(False,ex.args)

    @staticmethod
    def set_online_session(username):
        pass
    @staticmethod
    def int_by_phonenumber(phonenumber, username, ip ,oldusername=None):
        return User.InsertUserToDb(phonenumber, username, ip,oldusername=oldusername)
    @staticmethod
    def init_by_email(username, email, password, ip , oldusername=None):
        try:
            return User.add_user_email(email=email, username=username, password=password, ip=ip,oldusername=oldusername)
        except Exception as ex:
            return Result(False, ex.args)
    @staticmethod
    def init_as_gust(ip):
        return User.init_gust(ip)
    @staticmethod
    def add_message_user_message():
        try:
            pass
        except Exception as ex:
            return Result(False,ex.args)
    @staticmethod
    def init_gust(ip):
        try:
            username = User.GenUniqUserName()
            password = User.GenUniqUserName()
            email = User.GenUniqUserName()
            temp = User(username=username,email=email,ip=ip,password=password,isactive=True)
            id=usersDb.insert_one(temp.__dict__)
            token = User.GenerateUserToken_email(str(id.inserted_id), email)
            out = {"UserName":str(username),"Token":token,"Id":str(id.inserted_id)}
            return Result(True,json.dumps(out))
        except Exception as ex:
            return Result(False,ex.args)
    @staticmethod
    def SendVerificationCode(phoneNumber):
        try:
            Code = User.codeGen()
            logging.warning(Code)
            # first should code send by sms
            state = User.sendSms(phonenumber=phoneNumber, code=Code)

            logging.warning("code sent")

            User_Code = VerificationsCodePhoneNumber(phoneNumber, Code)
            # mongodb = pymongo.MongoClient(app.config["MogoDbUrl"])
            # database = mongodb[app.config['UsersDb']]
            # CodeCollection = database[app.config["Code"]]
            samecode = codesDb.find_one({"User_PhoneNumber": phoneNumber})
            if samecode is not None:
                codesDb.delete_one({"_id": samecode["_id"]})
            codesDb.insert_one(User_Code.__dict__)
            return (True, "Code inserted")
        except Exception as ex:
            return (False, ex.args)

    @staticmethod
    def SendVerificationCode_email(email):

        Code = User.codeGen()
        logging.warning(Code)
        out = User.send_email(email, Code)
        logging.warning(out)
        User_Code = VerificationsCodeEmail(email, Code)
        codesDb.delete_one({"User_Email": email})
        codesDb.insert_one(User_Code.__dict__)
        return Result(True, "CSE")  # code send to email

    @staticmethod
    def sendSms(phonenumber, code):
        logging.warning("try to send sms")
        try:
            # else:
            logging.warning("send sms code")
            headers = {
                "Content-Type": "application/json",
                "x-sms-ir-secure-token": app.config["SmsToken"]
            }
            body = {
                "Code": code,
                "MobileNumber": phonenumber

            }
            resp = requests.post('https://RestfulSms.com/api/VerificationCode', data=json.dumps(body),
                                 headers=headers).content

            logging.warning(resp)
            if json.loads(resp.decode("utf-8"))["IsSuccessful"] == True:
                return Result(True, "sendt")
            else:
                logging.warning("Hier")
                User.GetTokenOfSms(phonenumber, code)
                return Result(False, json.loads(resp.decode("utf-8"))["Message"])

        except Exception as ex:
            User.GetTokenOfSms(phonenumber, code)
            logging.warning(ex.args)

    @staticmethod
    def codeGen():
        return randint(1000, 9999)

    @staticmethod
    def GetTokenOfSms(phonenumber, code):
        content = requests.post("https://RestfulSms.com/api/Token", {
            "UserApiKey": "79da5cbe8f60d6cf8ac66983",
            "SecretKey": "I9F31A9BjRyi"
        }).content

        content = json.loads(content.decode("utf-8"))
        logging.warning("sms send at second request")
        if content["IsSuccessful"] == True:
            app.config["SmsToken"] = content["TokenKey"]
            logging.warning("new token get")
        headers = {
            "Content-Type": "application/json",
            "x-sms-ir-secure-token": app.config["SmsToken"]
        }
        body = {
            "Code": code,
            "MobileNumber": phonenumber

        }
        resp = requests.post('https://RestfulSms.com/api/VerificationCode', data=json.dumps(body),
                             headers=headers).content
        logging.warning(resp)

    @staticmethod
    def active_phonenumber_code(phonenumber,code):
        try:
            codeindb = codesDb.find_one({"User_PhoneNumber":phonenumber})

            if codeindb is None:
                return Result(False,"CNF") # code not found
            if codeindb["IsUsed"]:
                return Result(False,"CU") # code used
            if codeindb["Code"]== int(code):
                codesDb.update_one({"_id":codeindb["_id"]},{"$set":{"IsUsed":True}})
                usersDb.update_one({"PhoneNumber":phonenumber},{"$set":{"IsActive":True}})
                temp = usersDb.find_one({"PhoneNumber":phonenumber})
                token = User.GenerateUserToken(temp["_id"], phonenumber)
                return Result(True,dumps({"Token":token,
                                          "_id":temp["_id"]}))

        except Exception as ex:
            return Result(False,ex.args)

    @staticmethod
    def ActiveUserAccount(phonenumber, code,OldUserName=None):
        try:
            userCollection = usersDb
            CodeCollection = codesDb
            logging.warning(code)
            query = CodeCollection.find({"User_PhoneNumber": phonenumber})
            if query[0]["IsUsed"]:
                return Result(False, "This code has been expired")
            if query.count() > 0:

                if query[0]["User_Code"] == int(code):
                    newValue = {"$set": {"IsActive": True}}
                    temp_users.update_one({"PhoneNumber": phonenumber}, newValue)
                    userintemp =  temp_users.find_one({"PhoneNumber":phonenumber})
                    userCollection.update_one({"UserName": OldUserName}, {"$set":
                                                                              {"PhoneNumber": phonenumber,
                                                                               "UserName":userintemp["UserName"],
                                                                                 "IsActive":True,
                                                                                 "Email":"",
                                                                                 "PassWord":"",
                                                                                 "Ip":userintemp["Ip"],
                                                                                 "Update_at": datetime.datetime.now(),
                                                                                 "StartSession": datetime.datetime.now()
                                                                                                 }})
                    temp_users.find_one_and_delete({"PhoneNumber":phonenumber})
                    #userCollection.update_one({"UserName":OldUserName},{})
                    newCodeValue = {"$set": {"IsUsed": True}}
                    CodeCollection.update_one({"User_PhoneNumber": phonenumber}, newCodeValue)


                    temp = userCollection.find_one({"PhoneNumber": phonenumber})
                    token = User.GenerateUserToken(temp["_id"], phonenumber)
                    return Result(True, token)
                else:
                    return Result(False, "Wrong Code")

            else:
                return Result(False, "user not register yet")
        except Exception as ex:
            return Result(False, ex.args)

    @staticmethod
    def ActiveUserAccount_email(email, code ,oldUserName=None):
        try:
            query = codesDb.find_one({"User_Email": email})
            if query is None:
                return Result(False, "CNE")  # code not exist
            if query["IsUsed"]:
                return Result(False, "Code has been expired")
            if oldUserName is None:
                return Result(False,"OLDUSERNAME")
            if query["User_Code"] == int(code):

                #newValue = {"$set": {"IsActive": True}}
                #usersDb.update_one({"Email": email}, newValue)
                newCodeValue = {"$set": {"IsUsed": True}}
                codesDb.update_one({"User_Email": email}, newCodeValue)
                temp = usersDb.find_one({"UserName": oldUserName})

                user_in_temp = temp_users.find_one({"Email":email})

                usersDb.update_one({"UserName":oldUserName},{"$set":{"Email":user_in_temp["Email"],
                                                                     "UserName": user_in_temp["UserName"],
                                                                     "Ip":user_in_temp["Ip"],
                                                                     "PassWord":user_in_temp["PassWord"],
                                                                     "IsActive":True,
                                                                     "PhoneNumber":"",
                                                                     "Update_at":datetime.datetime.now(),
                                                                     "StartSession":datetime.datetime.now(),
                                                                     }})
                temp_users.find_one_and_delete({"Email":email})
                token = User.GenerateUserToken_email(temp["_id"], email)


                return Result(True, token)
            else:
                return Result(False, "WC")  # wrong code

        except Exception as ex:
            return Result(False, ex.args)

    @staticmethod
    def InternalTokenDesign(requestKey):
        hash_object = hashlib.sha256(requestKey)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    @staticmethod
    def GenerateUserToken(userid, phonenumber):
        token = User.InternalTokenDesign(str.encode(userid.__str__()))

        requesttoken = User.InternalTokenDesign(b"SETAUTHTOKEN")

        content = requests.post(app.config["RoleService"] + "authentication/addtoken/",
                                {"User_Id": userid, "Auth_Token": token,
                                 "Key": requesttoken, "PhoneNumber": phonenumber
                                 }).content

        logging.warning(content)

        if json.loads(content.decode("utf-8"))["State"] is True:
            return token
        else:
            return json.loads(content.decode("utf-8"))["Description"]

    @staticmethod
    def GenerateUserToken_email(userid, emil):
        token = User.InternalTokenDesign(str.encode(userid.__str__()))

        requesttoken = User.InternalTokenDesign(b"SETAUTHTOKEN")

        content = requests.post(app.config["RoleService"] + "authentication/addtoken/email",
                                {"User_Id": userid, "Auth_Token": token,
                                 "Key": requesttoken, "Email": emil
                                 }).content

        logging.warning(content)

        if json.loads(content.decode("utf-8"))["State"] is True:
            return token
        else:
            return json.loads(content.decode("utf-8"))["Description"]

#todo: when user register with sms , first user insert to temp_user and next when active account
    @staticmethod
    def InsertUserToDb(phonenumber, username, ip , oldusername=None):
        #Temp_User = User(phonenumber=phonenumber, username=username, ip=ip)
       # userCollection = usersDb
        userCollection = temp_users
        existUser = usersDb.find_one({"PhoneNumber": phonenumber})
        if existUser is not None:
            return Result(False, "User with this phone number exist")
        else:
            ex = usersDb.find_one({"UserName":oldusername})
            if ex is None:
                return Result(False,"IUN")#invalid username
            if usersDb.find_one({"UserName":username}) is not None:
                return Result(False,"UAE")#username already exist
            #userCollection.update_one({"UserName":oldusername},{"$set":{"PhoneNumber":phonenumber,
             #                                                           "UserName":username,
              #                                                          "IsActive":False,
               #                                                         "Email":"",
                #                                                        "PassWord":"",
                 #                                                       "Ip":ip
                  #                                                      }})
            userCollection.find_one_and_delete({"PhoneNumber":phonenumber})
            userCollection.insert_one(User(phonenumber,username,"","",ip).__dict__)
            #userCollection.insert_one(Temp_User.__dict__)
            User.SendVerificationCode(phonenumber)

            return Result(True, "User added and code sent")

    @staticmethod
    def add_user_email(username, password, email, ip,oldusername=None):
        #sign up with old username mechanisem
        try:

            hashed_password = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
            #Temp_User = User(email=email, username=username, ip=ip, password=hashed_password)
            exist_username = usersDb.find_one({"UserName": username})
            if exist_username is not None:
                return Result(False, "UNEX")  # username exist
            exist_email = usersDb.find_one({"Email": email})
            if exist_email is not None:
                return Result(False, "EEX")  # email exist
            oldusernameExist = usersDb.find_one({"UserName":oldusername})
            if oldusernameExist is None:
                return  Result(False,"IOUN")#invalid old username


            #usersDb.update_one({"UserName":oldusername},{"$set":{"UserName":username,"Email":email,
                                                               #  "PassWord":hashed_password,"Ip":ip,
                                                               #  "IsActive":True,
                                                              #   "PhoneNumber":""
                                                               #  }})
            temp_users.find_one_and_delete({"Email": email})
            temp_users.insert_one(User("",username,email,hashed_password,ip).__dict__)

            #usersDb.insert_one(Temp_User.__dict__)
            result = User.SendVerificationCode_email(email)
            return result
        except Exception as ex:
            return Result(False, ex)
    @staticmethod
    def GenUniqUserName():
        try:
            isUniqe = False
            uniqUserName = ""
            while isUniqe is False :
               base = "کاربرمهمان" + str(randint(1,99999))
               temp=usersDb.find_one({"UserName": base})
               if temp is None:
                  isUniqe = True
                  uniqUserName = base

            return uniqUserName


        except Exception as ex:
            return Result(False,ex.args)
    @staticmethod
    def send_email(email, code):
        try:
            server = SMTP_SSL("smtp.gmail.com", 465)
            server.ehlo()
            server.login("info.jinekagame@gmail.com", "mohsen1374")
            server.sendmail("info.jinekagame@gmail.com", email, str(code))
            return Result(True, "ACSM")  # activation code sned to email

        except Exception as ex:
            return Result(False, ex.args)

    @staticmethod
    def check_username_exist(username):
        try:
            temp = usersDb.find_one({"UserName": username})
            if temp is None:
                return Result(False, "UNE")  # username exist
            return Result(True, "UNNE")  # username not exist
        except Exception as ex:
            return Result(False, ex.args)

    @staticmethod
    def login_phone(phonenumber):
        userCollection = usersDb
        Temp_User = userCollection.find_one({"PhoneNumber": phonenumber})
        if Temp_User is None:
            return Result(False, "user with this phone number not sign up")
        logging.warning(Temp_User["_id"])
        isLoggedin = Authentication.CheckUserLogin(Temp_User["_id"])
        if isLoggedin:
            return Result(False, "user loggedin in another device")

        if Temp_User is None:
            return Result(False, "User with this phonenumber not exist")
        else:

            status = User.SendVerificationCode(phoneNumber=phonenumber)
            if status[0]:
                return Result(True, "Verifivation code has been send")
            else:
                return Result(False, "Some thing wrong in code send")

    @staticmethod
    def login_email(username , password):
        try:
            temp = usersDb.find_one({"UserName":username})
            isLoggedin = Authentication.CheckUserLogin(temp["_id"])
            if isLoggedin:
                return Result(False, "AUL")#another user loggen in
            if temp is None:
                return Result(False,"UNF")#user not found
            dbpass= temp["PassWord"]
            hashed_password = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
            if dbpass == hashed_password:
                token = User.GenerateUserToken_email(temp["_id"], temp["Email"])
                return Result(True,token)
            else:
                return Result(False,"WP")#wrong password
        except Exception as ex:
            return Result(False,ex.args)
    @staticmethod
    def reset_password_by_mail():
        try:
            pass
        except Exception as ex:
            return Result(False,ex.args)
    @staticmethod
    def logout(headers):
        request_token = User.InternalTokenDesign(b"LOGOUTUSER")
        content = requests.post(app.config["RoleService"]+"authentication/logout/",
                                {"Token":request_token,
                                 "User_Id":headers["Id"]}).content
        content = json.loads(content.decode("utf-8"))
        if content["State"] is True:
            return content
        else:
            logging.warning(content["Description"])
            return content



class Authentication():
    @staticmethod
    def InternalTokenDesign(requestKey):
        hash_object = hashlib.sha256(requestKey)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    @staticmethod
    def AuthCheck(phonenumber, token):
        request_token = Authentication.InternalTokenDesign(b"ISAUTH")
        logging.warning(app.config["RoleService"] + "isauth/")
        content = requests.get(
            app.config["RoleService"] + "isauth/" + str(request_token) + "/" + str(
                token) + "/" + phonenumber + "/").content
        logging.warning(content)
        content = json.loads(content.decode("utf-8"))
        if content["State"] is True:
            return True
        else:
            logging.warning(content["Description"])
            return False

    @staticmethod
    def Permission_Check(phonenumber, permission):
        try:
            content = requests.get(app.config["RoleService"] + "userpermission/check/" + str(phonenumber) + "/" +
                                   permission).content
            content = json.loads(content.decode("utf-8"))
            if content["State"] is True:
                return True
            else:
                return False
        except Exception as ex:
            logging.warning(ex)
            return False
    @staticmethod
    def Permission_Check_id(id, permission):
        try:
            content = requests.get(app.config["RoleService"] + "userpermission/check/id/" + str(id) + "/" +
                                   permission).content
            content = json.loads(content.decode("utf-8"))
            if content["State"] is True:
                return True
            else:
                return False
        except Exception as ex:
            logging.warning(ex)
            return False

    @staticmethod
    def ChechAuthPermission(headers, permission):
        phonenumber = headers["Phonenumber"]
        token = headers["Token"]
        if Authentication.AuthCheck(phonenumber, token) is True:
            if Authentication.Permission_Check(phonenumber, permission) is True:
                return Result(True, "accepted")
            else:
                return Result(False, "Permission denied")
        return Result(False, "Should loggin")

    @staticmethod
    def ChechAuthPermission_id(headers, permission):
        id = headers["Id"]
        token = headers["Token"]
        if Authentication.Check_AuthId(headers) is True:
            if Authentication.Permission_Check_id(id, permission) is True:
                return Result(True, "accepted")
            else:
                return Result(False, "Permission denied")
        return Result(False, "Should loggin")

    @staticmethod
    def Check_Auth(headers):
        phonenumber = headers["Phonenumber"]
        token = headers["Token"]

        if Authentication.AuthCheck(phonenumber, token) is True:
            return True
        else:
            return False
    @staticmethod
    def Check_AuthId(headers):
        id = headers["Id"]
        token = headers["Token"]
        request_token = Authentication.InternalTokenDesign(b"ISAUTH")
        logging.warning(app.config["RoleService"] + "isauth/")
        content = requests.get(
            app.config["RoleService"] + "isauth/" + str(request_token) + "/" + str(
                token) + "/" + id + "/id").content
        logging.warning(content)
        content = json.loads(content.decode("utf-8"))
        if content["State"] is True:
            return True
        else:
            logging.warning(content["Description"])
            return False


    @staticmethod
    def CheckUserLogin(userId):
        requesttoken = Authentication.InternalTokenDesign(b"CHECKUSERLOGIN")
        content = requests.post(app.config["RoleService"] + "authentication/checklogin/",
                                {"UserId": userId, "Token": requesttoken

                                 }).content
        logging.warning(content)
        if json.loads(content.decode("utf-8"))["State"] is True:
            return True
        else:
            return False


class Inventory():
    def __init__(self):
        self.Eye = []
        self.Hair = []
        self.Nose = []
        self.Cloth = []
        self.Glass = []
        self.Gune = []


# ----------functions-------------------------------------
def initialService(app):
    configs = ""
    with open("./Config.json") as f:
        configs = json.load(f)
    logging.warning("Loading configures")
    app.config["MicroServiceManagementURl"] = configs["MicroServiceManagementURl"]
    Temp_GetDatabaseService = requests.get(
        app.config["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=DbService").content
    Temp_DatabaseService = json.loads(Temp_GetDatabaseService.decode("utf-8"))
    Temp_RoleService = requests.get(
        app.config["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=" + configs[
            "RoleManagementService"]).content
    Temp_Role_Get = json.loads(Temp_RoleService.decode("utf-8"))
    logging.warning("gettin database url from Manager")
    app.config["RoleService"] = Temp_Role_Get[0]["url"]
    app.config["SmsToken"] = configs["SmsToken"]

    Temp_GameService =requests.get(
        app.config["MicroServiceManagementURl"] + "Service/GetByName?ServiceName=" + configs[
            "GameService"]).content

    app.config["GameService"] = json.loads(Temp_GameService.decode("utf-8"))[0]["url"]
    logging.warning("GameService:"+ app.config["GameService"])
    logging.warning("loading sms token" + app.config["SmsToken"])
    logging.warning("Database Url set")


initialService(app)


# ------------------- routes ------------------------------
@app.route("/")
def get():
    User.int_by_phonenumber("09119518867", "includeamin", request.remote_addr)
    return "<div>User service </div><div>developed by amin jamal (includeamin)</div><div>aminjamal10@gmail.com</div>"


@app.route("/users/signup",methods=["POST"])
def singup_phonenumber():
    try:
        form = request.json
        if form is None:
            return Result(False,"ContentType should be application/json")
        fname = form["Fname"]
        lname = form["Lname"]
        phonenumber = form["PhoneNumber"]
        return User.sign_up_by_phonenumber(phonenumber,fname,lname)
    except Exception as ex:
        return Result(False, ex.args)


@app.route("/users/account/activation/<phonenumber>/<code>")
def users_account_activation(phonenumber,code):
    pass



@app.route("/test",methods=["Post"])
def test():
    usersDb.delete_many({})


   #return dumps(json.loads("{\"UserName\": \"\\u06a9\\u0627\\u0631\\u0628\\u0631\\u0645\\u0647\\u0645\\u0627\\u06467767\", \"Token\": \"ed3caeecbc467b38d19b4e2f91d45e68ba2799fe5c4f947e232149bea444d51d\", \"Id\": \"5c4d6ba3fe2bed048d6869dd\"}"))
@app.route("/json",methods=["GET"])
def test_json_body():
    usersDb.update_many({},{"$set":{"Level":0}})
    return "ok"






if __name__ == '__main__':
   # User.sendSms("09119518867","1242")

    app.run(host="0.0.0.0", port=3032, debug=True)
