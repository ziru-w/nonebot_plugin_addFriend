# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 16:49
# @Author  : wk
# @Email   :  1515945392@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
import datetime
import os
import re
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot,  MessageEvent,RequestEvent,FriendRequestEvent,GroupRequestEvent
from nonebot.message import event_preprocessor
from os.path import dirname

FriendAdd = on_command("重置好友请求")
dir = dirname(__file__) + "/"
path=dir+'num.txt'
max=6

@event_preprocessor
async def _(bot: Bot, event: RequestEvent):
    if not isinstance(event,FriendRequestEvent) and not isinstance(event,GroupRequestEvent):
        return
    uid = str(event.user_id)
    await bot.send_private_msg(user_id=1515945392, message=uid+'发送好友请求,验证消息为'+event.comment)
    num,now,old=read_data()
    if num>max and now.day-old.day==0:
        await bot.send_private_msg(user_id=1515945392, message=uid+'发送好友请求,但已日增5人,验证消息为'+event.comment)
    else:
        await event.approve(bot)
        if now.day-old.day!=0:
            num=0
        else:
            num+=1
        with open(path,'w',encoding='utf-8') as fp:
            fp.write(str(num)+','+str(now))    
        await bot.send_private_msg(user_id=1515945392, message=uid+'添加成功')

@FriendAdd.handle()
async def _(bot: Bot, event: MessageEvent):
    if event.user_id!=1515945392:
        await FriendAdd.finish('无权限')
    num,now,old=read_data()
    if num<max and now.day-old.day==0:
        await FriendAdd.send(message='未日增5人,人数为'+str(num)+'上次添加时间'+str(now))
    if '为' in event.get_plaintext():
        plaintext=re.findall('[0-9]',event.get_plaintext())
        if len(plaintext)==0:
            num='0'
        else:
            num=plaintext[0]
    else:
        num='0'
    with open(path,'w',encoding='utf-8') as fp:
        fp.write(num+','+str(now))
    await FriendAdd.finish('重置成功')



def read_data():
    global num,now,old
    if not os.path.exists(path):
        now = datetime.datetime.now()
        with open(path, "w", encoding="utf-8") as fp:
            fp.write('1'+','+str(now))
    with open(path,'r',encoding='utf-8') as fp:
        data_list=fp.read().split(',')
        if len(data_list)<2:
            now = datetime.datetime.now()
            data_list=['1',str(now)]
    num=int(data_list[0])
    old=datetime.datetime.strptime(data_list[1], "%Y-%m-%d %H:%M:%S.%f")
    now = datetime.datetime.now()
    return num,now,old