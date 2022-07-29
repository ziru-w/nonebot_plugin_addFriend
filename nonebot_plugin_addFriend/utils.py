





from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot,  MessageSegment
import os
import datetime
from nonebot_plugin_txt2img import Txt2Img
async def parseMsg(commandText,resMsg,font_size = 32,isText=1):
    if len(resMsg)<=300 and isText==1:
       return resMsg
    else:
        title = commandText
        img = Txt2Img(font_size)
        pic = img.save(title, resMsg)
        return MessageSegment.image(pic)

async def getReferIdList(bot:Bot,idName='group_id',no_cache=True):
    if idName=='user_id':
        referInfoList=await bot.get_friend_list(no_cache=no_cache)
    else:
        idName='group_id'
        referInfoList=await bot.get_group_list(no_cache=no_cache)
    referIdList=[]
    for temp in referInfoList:
        referIdList.append(temp[idName])
    return referIdList

 
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


def commandStartList(n=1)->list:
    command_start=list(get_driver().config.command_start)
    if len(command_start)==0:
        command_start=['']
    else:
        command_start=command_start[:n]
    return command_start
    
def parseDifferentCommandStart(text):
    lenght=len(commandStartList()[0])
    if lenght==0:
        text='/'+text
    else:
        text='/'+text[lenght:]
    print(text)
    return text

def getExist(plainCommandtext:str,wholeMessageText:str,argsText:str):
    commandText=wholeMessageText.replace(argsText,'').strip()
    if plainCommandtext=='':
        return commandText
    else:
        return plainCommandtext in commandText
def getExist1(plainCommandtext:str,wholeMessageText:str,argsText:str):
    commandText=wholeMessageText.replace(argsText,'').strip()
    lenght1=len(commandText)
    lenght2=len(plainCommandtext)
    return commandText[lenght1-lenght2:]==plainCommandtext



 

def read_data(numPath):
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



def isNormalAdd(config,autoType,addInfo,agreeAutoApprove):
    blackDict=config["blackDict"][autoType]
    warnDict=config["warnDict"][autoType]
    statusDict=config["statusDict"]
    blackStatusDict=statusDict["blackDict"][autoType]
    warnStatusDict=statusDict["warnDict"][autoType]
    if autoType=="group":
        name=addInfo["group_name"]
        id=addInfo["group_id"]
    else:
        name=addInfo["nickname"]
        id=addInfo["user_id"]
    status=blackStatusDict["status"]+"\n其名"+name
    if id in blackDict["id"]:
        return -1,status
    for balckText in blackDict["text"]:
        if balckText in name:
            return -1,status
    status=warnStatusDict["status"]+"\n其名{}\n是否同意".format(name)
    if id in warnDict["id"]:
        return 0,status
    for warnText in warnDict["text"]:
        if warnText in name:
            return 0,status
    if agreeAutoApprove==1:
        status='{}添加成功'.format(id)
        return agreeAutoApprove,status+"\n其名"+name
    status="\n其名{}\n是否同意".format(name)
    return agreeAutoApprove,status


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

