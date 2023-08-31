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
from .configUtil import check_dict_key_bot_id, config,requestorDict,basedir,configPath,requestorDictPath,writeData,blackLogPath,numDict,numDictPath
from .utils import getReferIdList,sendMsg,getExist,parseMsg,isNormalAdd,writeLog,filterFriend,parseTime,writeTime
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
    check_dict_key_bot_id(config,requestorDict,numDict,bot)
    now=datetime.now()
    time=str(now)
    if isinstance(event,FriendRequestEvent):
        notice_msg=config[bot.self_id]["friend_msg"]["notice_msg"]
        welcome_msg=config[bot.self_id]["friend_msg"]["welcome_msg"]
        id = str(event.user_id)
        autoType='friend'
        agreeAutoApprove=config[bot.self_id]['agreeAutoApprove'][autoType]
        addInfo=await bot.get_stranger_info(user_id=int(id),no_cache=True)
        msg=id+notice_msg+event.comment+'\n时间:{}'.format(time)
    elif isinstance(event,GroupRequestEvent):
        if event.sub_type!='invite':
            print(event.sub_type)
            return
        print(event.sub_type)
        notice_msg=config[bot.self_id]["group_msg"]["notice_msg"]
        welcome_msg=config[bot.self_id]["group_msg"]["welcome_msg"]
        id = str(event.group_id)
        autoType='group'
        agreeAutoApprove=config[bot.self_id]['agreeAutoApprove'][autoType]
        await sleep(0.5)
        addInfo=await bot.get_group_info(group_id=int(id),no_cache=True)
        print(autoType,addInfo,agreeAutoApprove)
        msg='群号'+id+'，'+event.get_user_id()+notice_msg+event.comment+'\n时间:{}'.format(time)
        if addInfo["member_count"]!=0:
            status='\n或因群人数少,已经添加成功'
            await sendMsg(bot,config[bot.self_id]['recipientList'],msg+status,0)
            await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)
            return
    else:
        return
    # num,now,old=read_data(numPath,autoType)
    agreeAutoApprove,status=isNormalAdd(config[bot.self_id],autoType,addInfo,agreeAutoApprove) #正常添加判断，过滤无意义添加，类似xx通知群
    if agreeAutoApprove==-1: #黑名单结果
        await event.reject(bot)
        await sendMsg(bot,config[bot.self_id]['recipientList'],msg+status,0)  #黑名单警告，转发给设定的人
        forwardId=config[bot.self_id]["blackDict"]["forward"].get(id)
        if forwardId!=None and autoType=="group":
            friendList=await getReferIdList(bot,'user_id')
            if forwardId in friendList:
                await bot.send_private_msg(user_id=forwardId,message=msg+status)
            else:
                del config[bot.self_id]["blackDict"]["forward"][id]
            writeLog(blackLogPath,msg+status+'\n')
        return
    if not filterFriend(event.comment,autoType,config[bot.self_id]['allowAddFriednText']): #验证信息
        status='\n未通过验证消息,已拒绝'
        await sendMsg(bot,config[bot.self_id]['recipientList'],msg+status,0)#不记录
        await event.reject(bot)
        return
    num=parseTime(config[bot.self_id]['numControl'],numDict[bot.self_id][autoType],now)
    if agreeAutoApprove==0 or num==-1:
        if num==-1:
            status='\n此时增满{}人,未能再自动添加'.format(config[bot.self_id]['numControl']['maxNum'])
        else:
            status='\n未允许自动添加'
        requestorDict[bot.self_id][autoType][id]={'flag':event.flag,'comment':event.comment,"notice_msg":notice_msg,'staus':status,'requestorId':event.user_id,'time':time}
        writeData(requestorDictPath,requestorDict)
        await sendMsg(bot,config[bot.self_id]['recipientList'],msg+status,0)
    else:  
        #既自动添加又条件合适
        writeTime(numDictPath,numDict)
        await event.approve(bot)
        await sendMsg(bot,config[bot.self_id]['recipientList'],msg+status,0)
        #等待腾讯服务器更新
        await sleep(1.5)
        await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)



againReadConfig= on_command("重载配置",aliases={"更改自动同意","更改最大加数量","更改加时间","更改加时间单位","更改查看加返回数量"},priority=5,block=True,permission=SUPERUSER)
@againReadConfig.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    global config
    #下个版本把其他俩json也重载一下，不知道为啥这次就不想改
    with open(configPath,'r',encoding='utf-8') as fp:
        config=json.loads(fp.read())
    check_dict_key_bot_id(config,requestorDict,numDict,bot)
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    commandText=getExist('',text,argsText)
    print(argsText)
    if '群聊' in argsText:
        argsText=argsText.replace('群聊','').strip()
        autoType='group'
    elif '好友' in argsText:
        argsText=argsText.replace('好友','').strip()
        autoType='friend'
    else:
        autoType='all'
    if "更改自动同意" in commandText:
        print(1)
        if argsText.isdigit() and autoType!='all':
            if int(argsText)>0:
                config[bot.self_id]['agreeAutoApprove'][autoType]=1
            else:
                config[bot.self_id]['agreeAutoApprove'][autoType]=0
        elif autoType=='all':
            setList=argsText.split()
            i=0
            setKeyList=list(config[bot.self_id]['agreeAutoApprove'].keys())
            for set in setList[:2]:
                if set.isdigit():
                    if int(set)>0:
                        config[bot.self_id]['agreeAutoApprove'][setKeyList[i]]=1
                    else:
                        config[bot.self_id]['agreeAutoApprove'][setKeyList[i]]=0
                i+=1      
        else:
            await againReadConfig.finish('格式')
        resMsg='更改成功,为\n{}'.format(config[bot.self_id]['agreeAutoApprove'])

    elif "更改最大加数量" in commandText:
        print(2)
        if argsText.isdigit():
            maxNum=int(argsText)
            if maxNum>0:
                config[bot.self_id]['numControl'][autoType]['maxNum']=maxNum
            else:
                config[bot.self_id]['numControl'][autoType]['maxNum']=0
        resMsg='更改成功,为{}'.format(config[bot.self_id]['numControl'][autoType]['maxNum'])
    elif "更改最大加时间" in commandText:
        print(2)
        if argsText.isdigit():
            time=int(argsText)
            if time>0:
                config[bot.self_id]['numControl'][autoType]['time']=time
        resMsg='更改成功,为{}'.format(config[bot.self_id]['numControl'][autoType]['time'])
    elif "更改加时间单位" in commandText:
        print(argsText,1)
        if '时' in argsText:
            config[bot.self_id]['numControl'][autoType]['unit']='h'
        elif '分' in argsText:
            config[bot.self_id]['numControl'][autoType]['unit']='m'
        else:
            config[bot.self_id]['numControl'][autoType]['unit']='d'
        resMsg='更改成功,为{}'.format(config[bot.self_id]['numControl'][autoType]['unit'])
    elif "更改查看加返回数量" in commandText:
        print(3)
        if argsText.isdigit():
            maxViewNum=int(argsText)
            if maxViewNum>0 and maxViewNum<120:
                config[bot.self_id]['maxViewNum']=maxViewNum
        resMsg='更改成功,为\n{}'.format(config[bot.self_id]['maxViewNum'])
    else:
        print(4)
        resMsg='重载成功:\n{}'.format(config[bot.self_id])
    if '重载配置' not in commandText:
        writeData(configPath,config)
    resMsg=await parseMsg(commandText,resMsg)
    await againReadConfig.finish(resMsg)
    
        
addFriend = on_command("同意加",aliases={'拒绝加','查看加'},priority=5,block=True)
@addFriend.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    check_dict_key_bot_id(config,requestorDict,numDict,bot)
    if event.get_user_id() not in config[bot.self_id]['recipientList']:
        await addFriend.finish('无权限')
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    commandText=getExist("",text,argsText)
    print(argsText)
    if '群' in argsText:
        autoType='group'
        argsText=argsText.replace("群聊","").replace("群","").strip()
    else:
        argsText=argsText.replace("好友","").strip()
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
            num=config[bot.self_id]['maxViewNum']
        requestorValueList=list(requestorDict[bot.self_id][autoType].items())[:num]
        requestorInfos=str(requestorValueList)
        print(autoType,requestorInfos)
        resMsg=await parseMsg(commandText,requestorInfos)
        print(resMsg)
        await addFriend.finish(resMsg)
    if argsText=='':
        await addFriend.finish('格式')
    # 预处理完毕，开始设置参数
    QQOrGroupId=argsText.split()[0]
    print(QQOrGroupId)
    if requestorDict[bot.self_id][autoType].get(QQOrGroupId)==None:
        await addFriend.finish('没有此请求')

    flag=requestorDict[bot.self_id][autoType][QQOrGroupId]['flag']
    notice_msg=requestorDict[bot.self_id][autoType][QQOrGroupId]['notice_msg']
    comment=requestorDict[bot.self_id][autoType][QQOrGroupId]['comment']
    requestorId=requestorDict[bot.self_id][autoType][QQOrGroupId]['requestorId']
    time=requestorDict[bot.self_id][autoType][QQOrGroupId]['time']
    # 参数设置完毕，开始处理请求
    try:
        if autoType=="group":
            resMsg='群号{}，邀请者{}'.format(QQOrGroupId,requestorId)+notice_msg+comment+'\n时间:{}\n'.format(time)
            msgType='group_msg'
            groupList=await getReferIdList(bot)
            
            if int(QQOrGroupId) in groupList:
                print(1)
                status='已经添加成功，勿复添加'
            else:
                print(2)
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
        del requestorDict[bot.self_id][autoType][QQOrGroupId]
        writeData(requestorDictPath,requestorDict)
    resMsg+=status
    # 数据更易完毕，开始用户交互，返回结果，发送欢迎
    await addFriend.send(resMsg)
    # await bot.send_private_msg(user_id=event.user_id, message=resMsg)
    # await sendMsg(bot,config[bot.self_id]['recipientList'],resMsg,0)
    if status=='添加成功':
        # 等待腾讯数据更新
        await sleep(1.5)
        welcome_msg=config[bot.self_id][msgType]['welcome_msg']
        await bot.send_private_msg(user_id=requestorId, message=welcome_msg)
   
# @scheduler.scheduled_job('interval', hour=1, id='check_outdate', timezone="Asia/Shanghai")
delRequestorDict = on_command("清理请求表",priority=5, block=True,permission=SUPERUSER)
@delRequestorDict.handle()
async def check_outdate(bot:Bot, event: MessageEvent):
    check_dict_key_bot_id(config,requestorDict,numDict,bot)
    delList=[]
    for requestorType in  requestorDict:
        if requestorType!='friend':
            ReferIdList=await getReferIdList(bot,'group_id')
        else:
            ReferIdList=await getReferIdList(bot,'user_id')
        requestorList=list(requestorDict[bot.self_id][requestorType])
        print(ReferIdList)
        for requestor in requestorList:
            if int(requestor) in ReferIdList:
                delList.append(requestor)
                del requestorDict[bot.self_id][requestorType][requestor]
    writeData(requestorDictPath,requestorDict)
    msg='已清理如下:\n'+str(delList)[1:-1].replace(', ','  ')
    await delRequestorDict.send(msg)
    

reFriendReqNum = on_command("重置请求次数",block=True,priority=5,permission=SUPERUSER)
@reFriendReqNum.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    check_dict_key_bot_id(config,requestorDict,numDict,bot)
    # text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    if '群聊' in argsText:
        argsText=argsText.replace('群聊','').strip()
        autoType='group'
    elif '好友' in argsText:
        argsText=argsText.replace('好友','').strip()
        autoType='friend'
    else:
        autoType='all'
    max=config[bot.self_id]['numControl'][autoType]['maxNum']
    now=datetime.now()
    # num,now,old=read_data(numPath)
    if parseTime(config[bot.self_id]['numControl'][autoType],numDict[bot.self_id][autoType],now)!=-1:
        await reFriendReqNum.send(message='未增满{}人,人数为{}上次添加时间{}'.format(max,numDict[bot.self_id][autoType]['count'],now))
    argsText=argsText.replace('为','').strip()
    if argsText.isdigit():
        numDict[bot.self_id][autoType]['count']=int(argsText)
    else:
        numDict[bot.self_id][autoType]['count']=0
    numDict[bot.self_id][autoType]['time']=now
    writeTime(numDictPath,numDict)
    await reFriendReqNum.finish('重置成功,为{}'.format(numDict[bot.self_id][autoType]['count']))

addRecipient = on_command("添加请求接收者",aliases={"删除请求接收者"},block=True,priority=5,permission=SUPERUSER)
@addRecipient.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    check_dict_key_bot_id(config,requestorDict,numDict,bot)
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
            if recipient not in config[bot.self_id]['recipientList']:
                config[bot.self_id]['recipientList'].append(recipient)
        else:
            op='删除'
            if recipient in config[bot.self_id]['recipientList']:
                config[bot.self_id]['recipientList'].remove(recipient)
        writeData(configPath,config)
        await addRecipient.send(op+'{}成功'.format(recipient))
    else:
        await addRecipient.finish('不是{}的好友或者格式错误'.format(config[bot.self_id]['botName']))
   
friendHelp=on_command("加好友帮助",block=True,priority=5,permission=SUPERUSER)
@friendHelp.handle()
async def _(bot: Bot, event: MessageEvent):
    msg='重载配置\n更改自动同意,更改最大加数量,更改查看加返回数量,更改加时间,更改加时间单位(群聊、好友)\n同意加,拒绝加,查看加(群聊、好友)\n清理请求表\n重置请求次数(群聊、好友)\n添加请求接收者,删除请求接收者'
    await friendHelp.send(msg)



# agreeForward = on_command("设置bot私聊转发",block=True,priority=5,permission=SUPERUSER)
# @agreeForward.handle()
# async def _(bot: Bot, event: MessageEvent):
#     check_dict_key_bot_id(config,requestorDict,numDict,bot)
#     # forwardSet=config[bot.self_id]['forwardSet']
#     if config[bot.self_id]['forwardSet']==0:
#         config[bot.self_id]['forwardSet']=1
#         msg='开启成功哦'
#     else:
#         config[bot.self_id]['forwardSet']=0
#         msg='关闭成功哦'
#     writeData(configPath,config)
#     await agreeForward.send(msg)

# msgControl=[0,datetime.now(),1]
# @event_preprocessor
# async def sendPrivate(bot:Bot,event: PrivateMessageEvent):
#     check_dict_key_bot_id(config,requestorDict,numDict,bot)
#     if config[bot.self_id]['recipientList']==[] or config[bot.self_id]['forwardSet']==0:
#         return
#     if msgControl[2]==0: #
#         if (datetime.now()-msgControl[1]).seconds>20:
#             msgControl[2]=1
#         else:
#             return
#     msgControl[0]+=1
#     if msgControl[0]/((datetime.now()-msgControl[1]).seconds+1)>10:
#         msgControl[2]=0
#         msgControl[1]=datetime.now()
#         msgControl[0]=0
#     if event.get_user_id()!=config[bot.self_id]['recipientList'][0]:
#         plaintext=event.get_message()
#         await bot.send_private_msg(user_id=int(config[bot.self_id]['recipientList'][0]),message='叮~私聊消息\nqq:{}\n昵称:{}\n消息:{}'.format(event.user_id,event.sender.nickname,plaintext),auto_escape=False)




