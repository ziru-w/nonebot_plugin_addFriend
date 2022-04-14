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
from time import sleep
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot,  MessageEvent, MessageSegment,RequestEvent, GroupDecreaseNoticeEvent,FriendRequestEvent,GroupRequestEvent
from nonebot.typing import T_State
from nonebot.message import event_preprocessor
from os.path import dirname
from nonebot import get_driver
superuser=list(get_driver().config.superusers)[0]
FriendAdd = on_command("重置好友请求")
dir = dirname(__file__) + "/"
path=dir+'num.txt'
max=4

@event_preprocessor
async def _(bot: Bot, event: RequestEvent):
    if isinstance(event,FriendRequestEvent):
        notice_msg='请求添加好友,验证消息为'
        welcome_msg='我未知的的朋友啊，很高兴你添加我为qq好友哦！\n同时，如果有疑问，可以发送/help哦，包括添加课表的方式哦'
    elif isinstance(event,GroupRequestEvent):
        if event.sub_type!='invite':
            print(event.sub_type)
            return
        print(event.sub_type)
        notice_msg='发送群邀请,验证消息为'
        welcome_msg='我未知的的朋友啊，很高兴你邀请我哦！'
    else:
        return
    uid = str(event.user_id)
    await bot.send_private_msg(user_id=superuser, message=uid+notice_msg+event.comment)
    num,now,old=read_data()
    if num>max and (now.date()-old.date()).days==0:
        await bot.send_private_msg(user_id=superuser, message=uid+notice_msg+event.comment+'但已日增5人')
    else:
        await event.approve(bot)
        if now.day-old.day!=0:
            num=0
        else:
            num+=1
        with open(path,'w',encoding='utf-8') as fp:
            fp.write(str(num)+','+str(now))    
        await bot.send_private_msg(user_id=superuser, message=uid+'添加成功')
        
        sleep(1.5)
        await bot.send_private_msg(user_id=event.user_id, message=welcome_msg)

        
@FriendAdd.handle()
async def _(bot: Bot, event: MessageEvent):
    if event.user_id!=superuser:
        await FriendAdd.finish('无权限')
    num,now,old=read_data()
    if num<max and (now.date()-old.date()).days==0:
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
