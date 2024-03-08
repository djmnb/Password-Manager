from datetime import datetime
from random import random
import rsa

def getM(len:int):
    data=""
    i = 0
    while i<len:
        data+=str(int(random()*10))
        i+=1
    return data



def getrsakey():
    [pub,priv] = rsa.newkeys(1024)
    print(pub,priv)
    pub
    return [pub,priv]


def encrypt(data:str,key):
    return rsa.encrypt(data.encode("utf-8"),key)


def decrypt(data:str,key):
    return rsa.decrypt(data,key).decode("utf-8")


def timeok(date1,date2,limit:int):
    try:
        temp = int(date2 - date1)
        if temp <= limit:
            return True
    except Exception as e:
        pass
    return False

# [pub,pri] = getrsakey()
# data = encrypt("我爱你",pub)
# print(data)
# print(decrypt(data,pri))