# nonebot_plugin_addFriend
一个基于NoneBot2的插件，用于处理被请求加QQ好友和QQ群的请求


A plug-in based on nonebot2, which is used to process the request to add QQ friends and QQ groups


下载方法 pip install nonebot_plugin_addFriend

1.该插件运行后会检查配置文件是否存在，并生成默认配置，
2.可自行设置是否同意自动加好友，命令为/更改自动同意 1或0、/重置好友请求 数量（不写默认重置日被请求加好友、群次数为零，后缀数字则会重置为该数值），
3.该插件会检查添加好友、群的请求，同意自动添加则自动，上限默认为一日五个，下次收到请求时会检查时间不是一天会重置日被请求加好友、群次数，并向插件指定qq号发送提示，
4.不同意则保存记录等待命令/同意加 qq号，/拒绝加 qq号，/查看加。

配置项结构

{
  "agreeAutoApprove": 1,
  "maxNum": 5,
  "friend_msg": [
    "请求添加好友,验证消息为",
    "我未知的的朋友啊，很高兴你添加我为qq好友哦！\n同时，如果有疑问，可以发送/help哦"
  ],
  "group_msg": [
    "发送群邀请,验证消息为",
    "我未知的的朋友啊，很高兴你邀请我哦！"
  ],
  "botName": "我",
  "recipientList": [],
  "requestorDict": {}
}

