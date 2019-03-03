import requests
from datetime import  datetime
import json


baseurl = "http://localhost:3032/"
def log(item,content):
    print("{0} - {1} - {2}".format(datetime.now(),item,content))






def signup(phonenumber):

    content =requests.post("{0}users/signup".format(baseurl),
                           json={"PhoneNumber":phonenumber,
                               "Fname":"test",
                               "Lname":"test"}
                           ).content
    log("SIGNUP",content)
def activation():
    pass
def logout():
    pass
def login():
    pass
def change_user_name():
    pass



def main():
    signup("09119518867")

if __name__ == '__main__':
    main()