


from os.path import dirname,exists
from nonebot import get_driver
import json

basedir = dirname(__file__)
numPath=basedir+'/num.txt'
configPath=basedir+'/config.json'
requestorPath=basedir+'/requestor.json'
max=5
if not exists(configPath):
    recipientList=list(get_driver().config.superusers)
    # recipients=str(recipients)[1:-1].replace(' ','').replace("'",'')
    config={
        "agreeAutoApprove": { "friend": 1, "group": 0 },
        "maxNum": 5,
        "maxViewNum":20,
        "recipientList": recipientList[:2],
        "groupNumNoticeList":[],
        "botName": "我",
        "friend_msg": {
            "notice_msg": "请求添加好友,验证消息为",
            "welcome_msg": "我未知的的朋友啊，很高兴你添加我为qq好友哦！\n同时，如果有疑问，可以发送/help哦"
        },
        "group_msg": {
            "notice_msg": "发送群邀请,验证消息为",
            "welcome_msg": "我亲爱的的朋友啊，很高兴你邀请我哦！"
        }
    }
    with open(configPath,'w',encoding='utf-8') as fp:
        json.dump(config,fp,ensure_ascii=False)
if not exists(requestorPath):
    requestorDict={}
    with open(requestorPath,'w',encoding='utf-8') as fp:
        json.dump(requestorDict,fp,ensure_ascii=False)
with open(configPath,'r',encoding='utf-8') as fp:
    config=json.loads(fp.read())
with open(requestorPath,'r',encoding='utf-8') as fp:
    requestorDict=json.loads(fp.read())


