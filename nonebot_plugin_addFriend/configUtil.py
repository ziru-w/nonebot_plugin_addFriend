


from datetime import datetime
from os.path import dirname,exists
from nonebot import get_driver
import json
from nonebot.adapters.onebot.v11 import Bot
from .utils import writeTime
basedir = dirname(__file__)
# numDictPath=basedir+'/num.txt'
configPath=basedir+'/config.json'
requestorDictPath=basedir+'/requestor.json'
numDictPath=basedir+'/num.json'
max=6
blackLogPath=basedir+'/blackLog.txt'

def check_dict_key_bot_id(config:dict,requestorDict:dict,numDict:dict,bot: Bot):
    print(1)
    if config.get(bot.self_id)==None:
        config[bot.self_id]=configModel
        writeData(configPath,config)
    if requestorDict.get(bot.self_id)==None:
        requestorDict[bot.self_id]=requestorDictModel
        writeData(requestorDictPath,requestorDict)
    if numDict.get(bot.self_id)==None:
        numDict[bot.self_id]=numDictModel
        for type in numDict[bot.self_id].keys():
            numDict[bot.self_id][type]["time"]=datetime.strptime(numDict[bot.self_id][type]["time"], "%Y-%m-%d %H:%M:%S.%f")
        writeTime(numDictPath,numDict)
    # return True
def readData(path,content={},update=0)->dict:
    if not exists(path):
        with open(path,'w',encoding='utf-8') as fp:
            json.dump(content,fp,ensure_ascii=False)
    with open(path,'r',encoding='utf-8') as fp:
        data = json.loads(fp.read())
    return data
def writeData(path,content):
    with open(path,'w',encoding='utf-8') as fp:
        json.dump(content,fp,ensure_ascii=False)
# if not exists(configPath):
recipientList=list(get_driver().config.superusers)
# recipients=str(recipients)[1:-1].replace(' ','').replace("'",'')
# 可以在这里修改默认模板哦
configModel={
    "agreeAutoApprove": { "friend": 1, "group": 0 },
    "recipientList": recipientList[:2],
    "forwardSet":0,
    "numControl": {"useAlgorithm":0, "maxNum": 6, "time": 2, "unit": "h" ,"friend":{"maxNum": 6, "time": 2, "unit": "h" },"group":{"maxNum": 2, "time": 8, "unit": "h" }},
    "maxViewNum": 20,
    "blackDict":{"friend":{"text":[],"id":[]},"group":{"text":[],"id":[]},"forward":{}},#"群号":"管理员号，转发给其用来揪出在群里拉人头的人"
    "warnDict":{"friend":{"text":[],"id":[]},"group":{"text":[],"id":[]},"forward":{}},
    "allowAddFriednText":[],
    "botName": "我",
    "friend_msg": {
        "notice_msg": "请求添加好友,验证消息为",
        "welcome_msg": "我未知的的朋友啊，很高兴你添加我为qq好友哦！\n同时，如果有疑问，可以发送/help哦"
    },
    "group_msg": {
        "notice_msg": "发送群邀请,验证消息为",
        "welcome_msg": "我亲爱的的朋友啊，很高兴你邀请我哦！"
    },
    "statusDict":{
        "blackDict":{"friend":{"status":"拉黑QQ,已拒绝,仅作提示"},"group":{"status":"拉黑群聊,已拒绝,仅作提示"}},
        "warnDict":{"friend":{"status":"警告QQ,手动同意,是否同意"},"group":{"status":"警告群聊,手动同意,是否同意"}}
    }
}
requestorDictModel={"friend":{},"group":{}}
numDictModel={"friend":{"count":0,"time":str(datetime.now())},"group":{"count":0,"time":str(datetime.now())}}
config=readData(configPath)
requestorDict=readData(requestorDictPath)
numDict=readData(numDictPath)
# for type in numDict.keys():
#     numDict[type]["time"]=datetime.strptime(numDict[type]["time"], "%Y-%m-%d %H:%M:%S.%f")



# if not exists(requestorPath):
#     requestorDict={}
#     with open(requestorPath,'w',encoding='utf-8') as fp:
#         json.dump(requestorDict,fp,ensure_ascii=False)

# with open(requestorPath,'r',encoding='utf-8') as fp:
#     requestorDict=json.loads(fp.read())
# blackDictFriend=config["blackDict"]['friend']
# warnDictFriend=config["warnDict"]['friend']
# blackDictGroup=config["blackDict"]['group']
# warnDictGroup=config["warnDict"]['group']


# def updateData(path,content:dict={},update=0):
#     if update==0:
#         return content
#     else:
#         if content.get("numControl")==None:
#             content["numControl"]={"useAlgorithm":0, "maxNum": 5, "time": 2, "unit": "h" ,"friend":{"maxNum": 5, "time": 2, "unit": "h" },"group":{"maxNum": 2, "time": 8, "unit": "h" }}
#         else:
#             if list(content["numControl"].keys())==["maxNum", "time", "unit"]:
#                 content["numControl"].update({"useAlgorithm":0,"friend":{"maxNum": 5, "time": 2, "unit": "h" },"group":{"maxNum": 2, "time": 8, "unit": "h" }})
#             elif content.get("recipientList")!=[]:
#                 return content
#         if content.get("recipientList")==[]:
#             content["recipientList"]=recipientList[:2]
#         with open(path,'w',encoding='utf-8') as fp:
#             json.dump(content,fp,ensure_ascii=False)
#     return content
