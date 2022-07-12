# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 16:49
# @Author  : wziru
# @File    : __init__.py.py
# @Software: PyCharm
import datetime
import json
import os
import re
from asyncio import sleep
from os.path import dirname,exists
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot,  MessageEvent, MessageSegment,RequestEvent, FriendRequestEvent,GroupRequestEvent
from nonebot.message import event_preprocessor
from nonebot import get_driver
from nonebot.permission import SUPERUSER
basedir = dirname(__file__)
numPath=basedir+'/num.txt'
configPath=basedir+'/config.json'
requestorPath=basedir+'/requestor.json'
max=5
if not exists(configPath):
    recipientList=list(get_driver().config.superusers)
    # recipients=str(recipients)[1:-1].replace(' ','').replace("'",'')
    config={
        "agreeAutoApprove": { "qq": 1, "group": 0 },
        "maxNum": 5,
        "maxViewNum":20,
        "recipientList": recipientList[:2],
        "botName": "我",
        "friend_msg": {
            "notice_msg": "请求添加好友,验证消息为",
            "welcome_msg": "我未知的的朋友啊，很高兴你添加我为qq好友哦！\n同时，如果有疑问，可以发送/help哦"
        },
        "group_msg": {
            "notice_msg": "发送群邀请,验证消息为",
            "welcome_msg": "我未知的的朋友啊，很高兴你邀请我哦！"
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
def commandStartList(n=1)->list:
    command_start=list(get_driver().config.command_start)[:n]
    return command_start
def parseDifferentCommandStart(text):
    if len(commandStartList())==0:
        lenght=0
    else:
        lenght=len(commandStartList()[0])
    if lenght==0:
        text='/'+text
    else:
        text='/'+text[lenght:]
    print(text)
    return text
#初始化完毕，num文件单独初始化
@event_preprocessor
async def _(bot: Bot, event: RequestEvent):
    max=config['maxNum']
    staus='但已日增{}人,未能再自动添加'.format(max)
    if isinstance(event,FriendRequestEvent):
        notice_msg=config["friend_msg"]["notice_msg"]
        welcome_msg=config["friend_msg"]["welcome_msg"]
        id = str(event.user_id)
        autoType='qq'
        agreeAutoApprove=config['agreeAutoApprove'][autoType]
    elif isinstance(event,GroupRequestEvent):
        if event.sub_type!='invite':
            print(event.sub_type)
            return
        print(event.sub_type)
        notice_msg=config["group_msg"]["notice_msg"]
        welcome_msg=config["group_msg"]["welcome_msg"]
        id = str(event.group_id)
        autoType='group'
        agreeAutoApprove=config['agreeAutoApprove'][autoType]
        groupList=await getFriendList(bot,1)
        # 没啥用，群列表还是没更新
        await sleep(1.5)
        if int(id) in groupList:
            staus='或因群人数少,已经添加成功'
            await sendMsg(bot,config['recipientList'],'群号'+id+'，'+event.get_user_id()+notice_msg+event.comment+'\n'+staus,0)
            await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)
            return
    else:
        return
    
    num,now,old=read_data()
    if agreeAutoApprove==0:
        staus='是否同意'
    if agreeAutoApprove==0 or (num>=max and (now.date()-old.date()).days==0):
        requestorDict[id]={'flag':event.flag,'comment':event.comment,"notice_msg":notice_msg,'requestorId':event.user_id}
        with open(requestorPath,'w',encoding='utf-8') as fp:
            json.dump(requestorDict,fp,ensure_ascii=False)
        await sendMsg(bot,config['recipientList'],id+notice_msg+event.comment+'\n'+staus,0)
    else:
        #既自动添加又条件合适
        staus='{}添加成功'.format(id)
        if (now.date()-old.date()).days!=0:
            num=0
        else:
            num+=1
        with open(numPath,'w',encoding='utf-8') as fp:
            fp.write(str(num)+','+str(now))  
        await event.approve(bot)
        await sendMsg(bot,config['recipientList'],id+notice_msg+event.comment+'\n'+staus,0)
        await sleep(1.5)
        await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)

async def getFriendList(bot:Bot,op=0):
    if op==0:
        idName='user_id'
        friendInfoList=await bot.get_friend_list()
    else:
        idName='group_id'
        friendInfoList=await bot.get_group_list()
    friend_list=[]
    for temp in friendInfoList:
        friend_list.append(temp[idName])
    return friend_list


againReadConfig= on_command("重载配置",aliases={"更改自动同意","更改最大日加好友数量","更改查看加返回数量"},permission=SUPERUSER)
@againReadConfig.handle()
async def _(bot: Bot, event: MessageEvent):
    global config
    with open(configPath,'r',encoding='utf-8') as fp:
        config=json.loads(fp.read())
    
    text=event.get_plaintext().strip()
    text=parseDifferentCommandStart(text)
    if "更改自动同意" in text:
        text=text[7:].strip()
        if '群聊' in text:
            text=text.replace('群聊','').strip()
            autoType='group'
        elif '好友' in text:
            text=text.replace('好友','').strip()
            autoType='qq'
        else:
            autoType='all'
        if text.isdigit() and autoType!='all':
            if int(text)>0:
                config['agreeAutoApprove'][autoType]=1
            else:
                config['agreeAutoApprove'][autoType]=0
        elif autoType=='all':
            setList=text.split()
            i=0
            setKeyList=list(config['agreeAutoApprove'].keys())
            for set in setList[:2]:
                if set.isdigit():
                    if int(set)>0:
                        config['agreeAutoApprove'][setKeyList[i]]=1
                    else:
                        config['agreeAutoApprove'][setKeyList[i]]=0
                i+=1      
        else:
            await reFriendReqNum.finish('格式')
        resMsg='更改成功,为{}'.format(config['agreeAutoApprove'])

    elif "更改最大日加好友数量" in text:
        text=text[11:].strip()
        if text.isdigit():
            maxNum=int(text)
            if int(text)>0:
                config['maxNum']=maxNum
        resMsg='更改成功,为{}'.format(config['maxNum'])
    elif "更改查看加返回数量" in text:
        text=text[10:].strip()
        if text.isdigit():
            maxViewNum=int(text)
            if maxViewNum>0 and maxViewNum<120:
                config['maxViewNum']=maxViewNum
        resMsg='更改成功,为{}'.format(config['maxViewNum'])
    else:
        resMsg='重载成功,为{}'.format(config)
        await againReadConfig.send(resMsg[:400])
        return
    with open(configPath,'w',encoding='utf-8') as fp:
        json.dump(config,fp,ensure_ascii=False)
    await againReadConfig.send(resMsg[:400])
    
        
addFriend = on_command("同意加",aliases={'拒绝加','查看加'})
@addFriend.handle()
async def _(bot: Bot, event: MessageEvent):
    if event.get_user_id() not in config['recipientList']:
        await addFriend.finish('无权限')
    text=event.get_plaintext().strip()
    text=parseDifferentCommandStart(text)
    op=text[1:3]
    if op=='同意':
        approve=True
        staus='添加成功'
    elif op=='拒绝':
        approve=False
        staus='拒绝成功'
    else:
        num=text[4:].strip()
        if num.isdigit():
            num=int(num)
        else:
            num=config['maxViewNum']
        requestorValueList=list(requestorDict.values())[:num]
        requestorInfos=str(requestorValueList)
        while True:
            await addFriend.send(requestorInfos[:400])
            requestorInfos=requestorInfos[400:]
            if requestorInfos=='':
                break
        return
    if text[4:]=='':
        await addFriend.finish('格式')
    # 预处理完毕，开始设置参数
    text=text[4:].replace(' ','').split()
    QQOrGroupId=text[0]
    if requestorDict.get(QQOrGroupId)==None:
        await addFriend.finish('没有此请求')

    flag=requestorDict[QQOrGroupId]['flag']
    notice_msg=requestorDict[QQOrGroupId]['notice_msg']
    comment=requestorDict[QQOrGroupId]['comment']
    requestorId=requestorDict[QQOrGroupId]['requestorId']
    # 参数设置完毕，开始处理请求
    if notice_msg==config['group_msg']['notice_msg']:
        resMsg='群号'+QQOrGroupId+'，'+requestorId+notice_msg+comment+'\n'
        msgType='group_msg'
        groupList=await getFriendList(bot,1)
        if QQOrGroupId in groupList:
            staus='已经添加成功，勿复添加'
        else:
            await bot.set_group_add_request(flag=flag,approve=approve)
    else:
        resMsg=QQOrGroupId+notice_msg+comment+'\n'
        msgType='friend_msg'
        friendList=await getFriendList(bot,0)
        if QQOrGroupId in friendList:
            staus='已经添加成功，勿复添加'
        else:
            if len(text)>=2 and text[1]!='' and approve==True:
                remark=text[1]
                await bot.set_friend_add_request(flag=flag,approve=approve,remark=remark)
            else:
                await bot.set_friend_add_request(flag=flag,approve=approve)
    # 请求处理完毕，开始更易数据
    del requestorDict[QQOrGroupId]
    with open(requestorPath,'w',encoding='utf-8') as fp:
        json.dump(requestorDict,fp,ensure_ascii=False)
    
    resMsg+=staus
    # 数据更易完毕，开始用户交互，返回结果，发送欢迎
    await bot.send_private_msg(user_id=event.user_id, message=resMsg)
    # await sendMsg(bot,config['recipientList'],resMsg,0)
    if staus=='添加成功':
        # 等待腾讯数据更新
        await sleep(1.5)
        welcome_msg=config[msgType]['welcome_msg']
        await bot.send_private_msg(user_id=requestorId, message=welcome_msg)
    
async def sendMsg(bot:Bot,recipientList,msg:str,op=0):
    if not isinstance(recipientList,list):
        if isinstance(recipientList,str) and recipientList.isdigit():
            recipientList=[recipientList]
        else:
            return
    for recipient in recipientList:
        recipient=int(recipient)
        if op==0:
            await bot.send_private_msg(user_id=recipient, message=msg)
        else:
            await bot.send_group_msg(group_id=recipient, message=msg)
    

reFriendReqNum = on_command("重置好友请求",permission=SUPERUSER)
@reFriendReqNum.handle()
async def _(bot: Bot, event: MessageEvent):
    text=event.get_plaintext().strip()
    text=parseDifferentCommandStart(text)
    max=config['maxNum']
    num,now,old=read_data()
    if num<max and (now.date()-old.date()).days==0:
        await reFriendReqNum.send(message='未日增{}人,人数为{}上次添加时间{}'.format(max,num,now))
    if '为' in text:
        plaintext=re.findall('[0-9]',text)
        if len(plaintext)==0:
            num='0'
        else:
            num=plaintext[0]
    else:
        num='0'
    with open(numPath,'w',encoding='utf-8') as fp:
        fp.write(num+','+str(now))
    await reFriendReqNum.finish('重置成功,为{}'.format(num))

addRecipient = on_command("添加请求接收者",aliases={"删除请求接收者"},permission=SUPERUSER)
@addRecipient.handle()
async def _(bot: Bot, event: MessageEvent):
    friend_tem=await bot.get_friend_list()
    friend_list=[]
    for a in friend_tem:
        friend_list.append(a['user_id'])
    print(friend_list)
    text=event.get_plaintext().strip()
    text=parseDifferentCommandStart(text)
    op=text[1:3]
    recipient=text[3:].replace('请求接收者','').replace(' ','')
    if recipient=='':
        await addRecipient.send('格式')
    if int(recipient) in friend_list:
        if op=='添加':
            if recipient not in config['recipientList']:
                config['recipientList'].append(recipient)
        else:
            if recipient in config['recipientList']:
                config['recipientList'].remove(recipient)
        with open(configPath,'w',encoding='utf-8') as fp:
            json.dump(config,fp,ensure_ascii=False)
        await addRecipient.send(op+'{}成功'.format(recipient))
    else:
        await addRecipient.finish('不是{}的好友或者格式错误'.format(config['botName']))
    

def read_data():
    global num,now,old
    if not os.path.exists(numPath):
        now = datetime.datetime.now()
        with open(numPath, "w", encoding="utf-8") as fp:
            fp.write('1'+','+str(now))
    with open(numPath,'r',encoding='utf-8') as fp:
        data_list=fp.read().split(',')
        if len(data_list)<2:
            now = datetime.datetime.now()
            data_list=['1',str(now)]
    num=int(data_list[0])
    old=datetime.datetime.strptime(data_list[1], "%Y-%m-%d %H:%M:%S.%f")
    now = datetime.datetime.now()
    return num,now,old




def parseTimeInterval(old='2022-06-21 20:57',now='',op='int'):
    if isinstance(old,str):
        old=datetime.datetime.strptime(old, "%Y-%m-%d %H:%M")
    if now=='':
        now=datetime.datetime.now()
    elif isinstance(now,str):
        now=datetime.datetime.strptime(now, "%Y-%m-%d %H:%M")
    symbol=1
    if now.date()<=old.date():
        temp=datetime.datetime.strptime(str(now.date()), "%Y-%m-%d")
        if (now-temp).seconds<(old-temp).seconds:
            temp=old
            old=now
            now=temp
            symbol=-1  
    interval=now-old
    days=interval.days
    seconds=interval.seconds
    if op=='int':
        return (days*3600*24+seconds)*symbol
    else:
        return {'days':days*3600*24*symbol,'seconds':seconds*symbol}
