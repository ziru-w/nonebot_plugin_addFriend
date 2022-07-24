# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 16:49
# @Author  : wziru
# @File    : __init__.py.py
# @Software: PyCharm

import json

import re
from asyncio import sleep
from os.path import dirname,exists
from typing import Union
from nonebot import on_command,on_request,on_notice
from nonebot.adapters.onebot.v11 import Bot,  MessageEvent,PrivateMessageEvent,GroupMessageEvent, MessageSegment,RequestEvent,GroupRequestEvent, FriendRequestEvent,NoticeEvent,GroupDecreaseNoticeEvent,GroupIncreaseNoticeEvent
from nonebot.message import event_preprocessor
from nonebot import get_driver
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.adapters import Message
from .configUtil import config,requestorDict,basedir,numPath,configPath,requestorPath
from .utils import getReferIdList,read_data,sendMsg,getExist

#初始化完毕，num文件单独初始化
parseRequest = on_request(priority=1, block=True)
# @event_preprocessor
@parseRequest.handle()
async def _(bot: Bot, event: RequestEvent):
    max=config['maxNum']
    status='但已日增{}人,未能再自动添加'.format(max)
    if isinstance(event,FriendRequestEvent):
        notice_msg=config["friend_msg"]["notice_msg"]
        welcome_msg=config["friend_msg"]["welcome_msg"]
        id = str(event.user_id)
        autoType='friend'
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
        await sleep(0.5)
        groupList=await getReferIdList(bot)
        if int(id) in groupList:
            status='或因群人数少,已经添加成功'
            await sendMsg(bot,config['recipientList'],'群号'+id+'，'+event.get_user_id()+notice_msg+event.comment+'\n'+status,0)
            await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)
            return
    else:
        return
    
    num,now,old=read_data(numPath)
    time=str(now)
    if agreeAutoApprove==0:
        status='是否同意'
    if agreeAutoApprove==0 or (num>=max and (now.date()-old.date()).days==0):
        requestorDict[id]={'flag':event.flag,'comment':event.comment,"notice_msg":notice_msg,'requestorId':event.user_id,'time':time}
        with open(requestorPath,'w',encoding='utf-8') as fp:
            json.dump(requestorDict,fp,ensure_ascii=False)
        await sendMsg(bot,config['recipientList'],id+notice_msg+event.comment+'\n时间:{}\n{}'.format(time,status),0)
    else:
        #既自动添加又条件合适
        status='{}添加成功'.format(id)
        if (now.date()-old.date()).days!=0:
            num=0
        else:
            num+=1
        with open(numPath,'w',encoding='utf-8') as fp:
            fp.write(str(num)+','+str(now))  
        await event.approve(bot)
        await sendMsg(bot,config['recipientList'],id+notice_msg+event.comment+'\n时间:{}\n{}'.format(time,status),0)
        #等待腾讯服务器更新
        await sleep(1.5)
        await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)



againReadConfig= on_command("重载配置",aliases={"更改自动同意","更改最大日加好友数量","更改查看加返回数量"},block=True,permission=SUPERUSER)
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
            await reFriendReqNum.finish('格式')
        resMsg='更改成功,为{}'.format(config['agreeAutoApprove'])

    elif "更改最大日加好友数量" in commandText:
        if argsText.isdigit():
            maxNum=int(argsText)
            if maxNum>0:
                config['maxNum']=maxNum
            else:
                config['maxNum']=0
        resMsg='更改成功,为{}'.format(config['maxNum'])
    elif "更改查看加返回数量" in commandText:
        if argsText.isdigit():
            maxViewNum=int(argsText)
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
    
        
addFriend = on_command("同意加",aliases={'拒绝加','查看加'},block=True)
@addFriend.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    if event.get_user_id() not in config['recipientList']:
        await addFriend.finish('无权限')
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text()
    if getExist("同意加",text,argsText):
        approve=True
        status='添加成功'
    elif getExist('拒绝',text,argsText):
        approve=False
        status='拒绝成功'
    else:
        num=argsText
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
    if argsText=='':
        await addFriend.finish('格式')
    # 预处理完毕，开始设置参数
    argsText=argsText.split()
    QQOrGroupId=argsText[0]
    if requestorDict.get(QQOrGroupId)==None:
        await addFriend.finish('没有此请求')

    flag=requestorDict[QQOrGroupId]['flag']
    notice_msg=requestorDict[QQOrGroupId]['notice_msg']
    comment=requestorDict[QQOrGroupId]['comment']
    requestorId=requestorDict[QQOrGroupId]['requestorId']
    time=requestorDict[QQOrGroupId]['time']
    # 参数设置完毕，开始处理请求
    try:
        if notice_msg==config['group_msg']['notice_msg']:
            resMsg='群号{}，邀请者{}'.format(QQOrGroupId,requestorId)+notice_msg+comment+'\n时间:{}\n'.format(time)
            msgType='group_msg'
            groupList=await getReferIdList(bot)
            if QQOrGroupId in groupList:
                status='已经添加成功，勿复添加'
            else:
                await bot.set_group_add_request(flag=flag,approve=approve)
        else:
            resMsg=QQOrGroupId+notice_msg+comment+'\n{}\n'.format(time)
            msgType='friend_msg'
            friendList=await getReferIdList(bot,'user_id')
            if QQOrGroupId in friendList:
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
        del requestorDict[QQOrGroupId]
        with open(requestorPath,'w',encoding='utf-8') as fp:
            json.dump(requestorDict,fp,ensure_ascii=False)
    
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
   
    

reFriendReqNum = on_command("重置好友请求",block=True,permission=SUPERUSER)
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

addRecipient = on_command("添加请求接收者",aliases={"删除请求接收者"},block=True,permission=SUPERUSER)
@addRecipient.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    friend_list=await getReferIdList(bot,'user_id')
    # print(friend_list)
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
        with open(configPath,'w',encoding='utf-8') as fp:
            json.dump(config,fp,ensure_ascii=False)
        await addRecipient.send(op+'{}成功'.format(recipient))
    else:
        await addRecipient.finish('不是{}的好友或者格式错误'.format(config['botName']))
   

 

groupMemberNumNotice = on_notice(priority=10,block=True)
@groupMemberNumNotice.handle()
async def _(bot: Bot, event: Union[GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent]):
    print(type(event))
    gid=event.group_id
    uid=event.user_id     
    message=''
    if isinstance(event, GroupIncreaseNoticeEvent):        
        if gid in config["groupMemberNumNoticeList"]:
            message=MessageSegment.at(uid)+MessageSegment.text('\n又有新成员加入了，代表大家欢迎你哦')
    elif isinstance(event,GroupDecreaseNoticeEvent): 
        if gid in config["groupMemberNumNoticeList"]:
            message=MessageSegment.text('有人离开了群聊，这真是个伤心的故事')
            # return
    if message=='':
        return
    await bot.send(event,message)

addGroupNumNoticeList = on_command("设置群成员更易通知",block=True,permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER)
@addGroupNumNoticeList.handle()
async def _(bot: Bot, event: MessageEvent,args:Message=CommandArg()):
    msg=args.extract_plain_text().strip()
    groupList=await getReferIdList(bot)
    if msg!='' and (not msg.isdigit() or int(msg) not in groupList):
        msg='输入非法！空？非数字?非机器人群聊？'
        await addGroupNumNoticeList.finish(msg)
    if msg!='':
        gid=int(msg)
    elif isinstance(event,GroupMessageEvent):
        gid=event.group_id
    else:
        msg='输入非法！空？'
        await addGroupNumNoticeList.finish(msg)
    if gid not in config["groupMemberNumNoticeList"]:
        config["groupMemberNumNoticeList"].append(gid)
        msg+='开启成功哦'
    else:
        config["groupMemberNumNoticeList"].remove(gid)
        msg+='关闭成功哦'
    with open(configPath,'w',encoding='utf-8') as fp:
        json.dump(config,fp,ensure_ascii=False)
    await addGroupNumNoticeList.send(msg)

agreeForward = on_command("设置bot私聊转发",block=True,permission=SUPERUSER)
@agreeForward.handle()
async def _(bot: Bot, event: MessageEvent):
    # forwardSet=config['forwardSet']
    if config['forwardSet']==0:
        config['forwardSet']=1
        msg='开启成功哦'
    else:
        config['forwardSet']=0
        msg='关闭成功哦'
    with open(configPath,'w',encoding='utf-8') as fp:
        json.dump(config,fp,ensure_ascii=False)
    await agreeForward.send(msg)
@event_preprocessor
async def sendPrivate(bot:Bot,event: PrivateMessageEvent):
    if config['recipientList']==[] or config['forwardSet']==0:
        return
    if event.get_user_id()!=config['recipientList'][0]:
        plaintext=event.get_message()
        await bot.send_private_msg(user_id=int(config['recipientList'][0]),message='叮~私聊消息\nqq:{}\n昵称:{}\n消息:{}'.format(event.user_id,event.sender.nickname,plaintext),auto_escape=False)
