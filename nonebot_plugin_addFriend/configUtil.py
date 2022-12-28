


from os.path import dirname,exists
from nonebot import get_driver
import json

basedir = dirname(__file__)
numPath=basedir+'/num.txt'
configPath=basedir+'/config.json'
requestorPath=basedir+'/requestor.json'
max=5
blackLogPath=basedir+'/.json'
def readData(path,content={}):
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
configModel={
    "agreeAutoApprove": { "friend": 1, "group": 0 },
    "numControl": {"maxNum":5,"time":2,"unit":'h'},
    "maxViewNum":20,
    "recipientList": recipientList[:2],
    "groupMemberNumNoticeList":[],
    "forwardSet":0,
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
        "blackDict":{"friend":{"status":"拉黑Q类,已拒绝,仅作提示"},"group":{"status":"拉黑群类,已拒绝,仅作提示"}},
        "warnDict":{"friend":{"status":"警告Q类,手动同意,是否同意"},"group":{"status":"警告群类,手动同意,是否同意"}}
    }
}
config=readData(configPath,configModel)
requestorDict=readData(requestorPath,{"friend":{},"group":{}})
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


