# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 16:49
# @Author  : wziru
# @File    : __init__.py.py
# @Software: PyCharm

from datetime import datetime
import json

import re
from asyncio import sleep
from os.path import dirname,exists
from typing import Union
from nonebot import on_command,on_request,on_notice,require
from nonebot.adapters.onebot.v11 import Bot,  MessageEvent,PrivateMessageEvent,GroupMessageEvent, MessageSegment,RequestEvent,GroupRequestEvent, FriendRequestEvent,NoticeEvent,GroupDecreaseNoticeEvent,GroupIncreaseNoticeEvent
from nonebot.message import event_preprocessor
from nonebot import get_driver
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.adapters import Message
from .configUtil import config,requestorDict,basedir,numPath,configPath,requestorPath,writeData,blackLogPath
from .utils import getReferIdList,read_data,sendMsg,getExist,parseMsg,isNormalAdd,writeLog,filterFriend,parseTime
# try:
#     scheduler = require('nonebot_plugin_apscheduler').scheduler
# except:
#     import nonebot_plugin_apscheduler 
#     scheduler = nonebot_plugin_apscheduler.scheduler

#初始化完毕，num文件单独初始化
parseRequest = on_request(priority=1, block=True)
# @event_preprocessor
@parseRequest.handle()
async def _(bot: Bot, event: RequestEvent):
    num,now,old=read_data(numPath)
    time=str(now)
    if isinstance(event,FriendRequestEvent):
        notice_msg=config["friend_msg"]["notice_msg"]
        welcome_msg=config["friend_msg"]["welcome_msg"]
        id = str(event.user_id)
        autoType='friend'
        agreeAutoApprove=config['agreeAutoApprove'][autoType]
        addInfo=await bot.get_stranger_info(user_id=int(id),no_cache=True)
        msg=id+notice_msg+event.comment+'\n时间:{}'.format(time)
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
        await sleep(0.5)
        addInfo=await bot.get_group_info(group_id=int(id),no_cache=True)
        print(autoType,addInfo,agreeAutoApprove)
        msg='群号'+id+'，'+event.get_user_id()+notice_msg+event.comment+'\n时间:{}'.format(time)
        if addInfo["member_count"]!=0:
            status='\n或因群人数少,已经添加成功'
            await sendMsg(bot,config['recipientList'],msg+status,0)
            await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)
            return
    else:
        return
    agreeAutoApprove,status=isNormalAdd(config,autoType,addInfo,agreeAutoApprove)
    if agreeAutoApprove==-1:
        await event.reject(bot)
        await sendMsg(bot,config['recipientList'],msg+status,0)  #黑名单警告，转发给设定的人
        forwardId=config["blackDict"]["forward"].get(id)
        if forwardId!=None and autoType=="group":
            friendList=await getReferIdList(bot,'user_id')
            if forwardId in friendList:
                await bot.send_private_msg(user_id=forwardId,message=msg+status)
            else:
                del config["blackDict"]["forward"][id]
            writeLog(blackLogPath,msg+status+'\n')
        return
    if not filterFriend(event.comment,autoType,config['allowAddFriednText']): #验证信息
        status='\n未通过验证消息,已拒绝'
        await sendMsg(bot,config['recipientList'],msg+status,0)#不记录
        await event.reject(bot)
        return
    num=parseTime(config['numControl'],num,old,now)
    if agreeAutoApprove==0 or num==-1:
        if num==-1:
            status='\n此时日增{}人,未能再自动添加'.format(config['numControl']['maxNum'])
        else:
            status='\n未允许自动添加'
        requestorDict[autoType][id]={'flag':event.flag,'comment':event.comment,"notice_msg":notice_msg,'staus':status,'requestorId':event.user_id,'time':time}
        writeData(requestorPath,requestorDict)
        await sendMsg(bot,config['recipientList'],msg+status,0)
    else:  
        #既自动添加又条件合适
        with open(numPath,'w',encoding='utf-8') as fp:
            fp.write(str(num)+','+str(now))  
        await event.approve(bot)
        await sendMsg(bot,config['recipientList'],msg+status,0)
        #等待腾讯服务器更新
        await sleep(1.5)
        await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)



againReadConfig= on_command("重载配置",aliases={"更改自动同意","更改最大加好友数量","更改查看加返回数量","更改加好友时间单位"},priority=5,block=True,permission=SUPERUSER)
@againReadConfig.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    global config
    with open(configPath,'r',encoding='utf-8') as fp:
        config=json.loads(fp.read())
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text()
    commandText=getExist('',text,argsText)
    if "更改自动同意" in commandText:
        text=args.extract_plain_text()
        if '群聊' in argsText:
            argsText=argsText.replace('群聊','').strip()
            autoType='group'
        elif '好友' in argsText:
            argsText=argsText.replace('好友','').strip()
            autoType='friend'
        else:
            autoType='all'
        if argsText.isdigit() and autoType!='all':
            if int(argsText)>0:
                config['agreeAutoApprove'][autoType]=1
            else:
                config['agreeAutoApprove'][autoType]=0
        elif autoType=='all':
            setList=argsText.split()
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
            await againReadConfig.finish('格式')
        resMsg='更改成功,为\n{}'.format(config['agreeAutoApprove'])

    elif "更改最大加好友数量" in commandText:
        if argsText.isdigit():
            maxNum=int(argsText)
            if maxNum>0:
                config['numControl']['maxNum']=maxNum
            else:
                config['numControl']['maxNum']=0
        resMsg='更改成功,为{}'.format(config['numControl']['maxNum'])
    elif "更改加好友时间单位" in commandText:
        if '时' in argsText:
                config['numControl']['unit']='h'
        elif '分' in argsText:
            config['numControl']['unit']='m'
        else:
            config['numControl']['unit']='d'
        resMsg='更改成功,为{}'.format(config['numControl']['unit'])
    elif "更改查看加返回数量" in commandText:
        if argsText.isdigit():
            maxViewNum=int(argsText)
            if maxViewNum>0 and maxViewNum<120:
                config['maxViewNum']=maxViewNum
        resMsg='更改成功,为\n{}'.format(config['maxViewNum'])
    else:
        resMsg='重载成功:\n{}'.format(config)
    if '重载配置' not in commandText:
        writeData(configPath,config)
    resMsg=await parseMsg(commandText,resMsg)
    await againReadConfig.finish(resMsg)
    
        
addFriend = on_command("同意加",aliases={'拒绝加','查看加'},priority=5,block=True)
@addFriend.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    if event.get_user_id() not in config['recipientList']:
        await addFriend.finish('无权限')
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    commandText=getExist("",text,argsText)
    if '群' in commandText:
        autoType='group'
    else:
        autoType='friend'
    if "同意加" in commandText:
        approve=True
        status='添加成功'
    elif '拒绝' in commandText:
        approve=False
        status='拒绝成功'
    else:
        num=argsText
        if num.isdigit():
            num=int(num)
        else:
            num=config['maxViewNum']
        requestorValueList=list(requestorDict[autoType].values())[:num]
        requestorInfos=str(requestorValueList)
        resMsg=await parseMsg(commandText,requestorInfos)
        await againReadConfig.finish(resMsg)
    if argsText=='':
        await addFriend.finish('格式')
    # 预处理完毕，开始设置参数
    argsText=argsText.split()
    QQOrGroupId=argsText[0]
    if requestorDict[autoType].get(QQOrGroupId)==None:
        await addFriend.finish('没有此请求')

    flag=requestorDict[autoType][QQOrGroupId]['flag']
    notice_msg=requestorDict[autoType][QQOrGroupId]['notice_msg']
    comment=requestorDict[autoType][QQOrGroupId]['comment']
    requestorId=requestorDict[autoType][QQOrGroupId]['requestorId']
    time=requestorDict[autoType][QQOrGroupId]['time']
    # 参数设置完毕，开始处理请求
    try:
        if autoType=="group":
            resMsg='群号{}，邀请者{}'.format(QQOrGroupId,requestorId)+notice_msg+comment+'\n时间:{}\n'.format(time)
            msgType='group_msg'
            groupList=await getReferIdList(bot)
            if int(QQOrGroupId) in groupList:
                status='已经添加成功，勿复添加'
            else:
                await bot.set_group_add_request(flag=flag,approve=approve)
        else:
            resMsg=QQOrGroupId+notice_msg+comment+'\n{}\n'.format(time)
            msgType='friend_msg'
            friendList=await getReferIdList(bot,'user_id')
            if int(QQOrGroupId) in friendList:
                status='已经添加成功，勿复添加'
            else:
                if len(argsText)>=2 and argsText[1]!='' and approve==True:
                    remark=argsText[1]
                    # 备注似乎无用
                    await bot.set_friend_add_request(flag=flag,approve=approve,remark=remark)
                else:
                    await bot.set_friend_add_request(flag=flag,approve=approve)
    except:
        status='为何手动添加而后又删好友或退群又来这里同意？'
    finally:
        # 请求处理完毕，开始更易数据
        del requestorDict[autoType][QQOrGroupId]
        writeData(requestorPath,requestorDict)
    resMsg+=status
    # 数据更易完毕，开始用户交互，返回结果，发送欢迎
    await addFriend.send(resMsg)
    # await bot.send_private_msg(user_id=event.user_id, message=resMsg)
    # await sendMsg(bot,config['recipientList'],resMsg,0)
    if status=='添加成功':
        # 等待腾讯数据更新
        await sleep(1.5)
        welcome_msg=config[msgType]['welcome_msg']
        await bot.send_private_msg(user_id=requestorId, message=welcome_msg)
   
# @scheduler.scheduled_job('interval', hour=1, id='check_outdate', timezone="Asia/Shanghai")
delRequestorDict = on_command("清理请求表",priority=5, block=True,permission=SUPERUSER)
@delRequestorDict.handle()
async def check_outdate(bot:Bot, event: MessageEvent):
    delList=[]
    for requestorType in  requestorDict:
        if requestorType!='friend':
            ReferIdList=await getReferIdList(bot,'group_id')
        else:
            ReferIdList=await getReferIdList(bot,'user_id')
        requestorList=list(requestorDict[requestorType])
        for requestor in requestorList:
            if int(requestor) in ReferIdList:
                delList.append(requestor)
                del requestorDict[requestorType][requestor]
    writeData(requestorPath,requestorDict)
    msg='已清理如下:\n'+str(delList)[1:-1].replace(', ','  ')
    await delRequestorDict.send(msg)
    

reFriendReqNum = on_command("重置好友请求",block=True,priority=5,permission=SUPERUSER)
@reFriendReqNum.handle()
async def _(bot: Bot, event: MessageEvent):
    text=event.get_plaintext().strip()
    max=config['maxNum']
    num,now,old=read_data(numPath)
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

addRecipient = on_command("添加请求接收者",aliases={"删除请求接收者"},block=True,priority=5,permission=SUPERUSER)
@addRecipient.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    friend_list=await getReferIdList(bot,'user_id')
    print(friend_list)
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text()
    recipient=argsText
    if recipient=='':
        await addRecipient.send('格式')
    if int(recipient) in friend_list:
        if getExist('添加',text,argsText):
            op='添加'
            if recipient not in config['recipientList']:
                config['recipientList'].append(recipient)
        else:
            op='删除'
            if recipient in config['recipientList']:
                config['recipientList'].remove(recipient)
        writeData(configPath,config)
        await addRecipient.send(op+'{}成功'.format(recipient))
    else:
        await addRecipient.finish('不是{}的好友或者格式错误'.format(config['botName']))
   




agreeForward = on_command("设置bot私聊转发",block=True,priority=5,permission=SUPERUSER)
@agreeForward.handle()
async def _(bot: Bot, event: MessageEvent):
    # forwardSet=config['forwardSet']
    if config['forwardSet']==0:
        config['forwardSet']=1
        msg='开启成功哦'
    else:
        config['forwardSet']=0
        msg='关闭成功哦'
    writeData(configPath,config)
    await agreeForward.send(msg)

msgControl=[0,datetime.now(),1]
@event_preprocessor
async def sendPrivate(bot:Bot,event: PrivateMessageEvent):
    if config['recipientList']==[] or config['forwardSet']==0:
        return
    if msgControl[2]==0: #
        if (datetime.now()-msgControl[1]).seconds>20:
            msgControl[2]=1
        else:
            return
    msgControl[0]+=1
    if msgControl[0]/((datetime.now()-msgControl[1]).seconds+1)>10:
        msgControl[2]=0
        msgControl[1]=datetime.now()
        msgControl[0]=0
    if event.get_user_id()!=config['recipientList'][0]:
        plaintext=event.get_message()
        await bot.send_private_msg(user_id=int(config['recipientList'][0]),message='叮~私聊消息\nqq:{}\n昵称:{}\n消息:{}'.format(event.user_id,event.sender.nickname,plaintext),auto_escape=False)




friendHelp=on_command("加好友帮助",block=True,priority=5,permission=SUPERUSER)
@friendHelp.handle()
async def _(bot: Bot, event: MessageEvent):
    msg='重载配置,更改自动同意,更改最大加好友数量,更改查看加返回数量,更改加好友时间单位\n同意加,拒绝加,查看加(群、好友)\n清理请求表\n重置好友请求\n添加请求接收者,删除请求接收者'
    await friendHelp.send(msg)