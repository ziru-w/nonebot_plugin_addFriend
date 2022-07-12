# nonebot_plugin_addFriend
一个基于NoneBot2的插件，用于处理被请求加QQ好友和QQ群的请求


A plug-in based on nonebot2, which is used to process the request to add QQ friends and QQ groups


下载方法 pip install nonebot_plugin_addFriend

1.该插件运行后会检查配置文件是否存在，并生成默认配置，也可手动复制内容创建文件，创建路径为插件目录，文件名为config.json,其中.json为后缀名，表征文件类型，请不要创建为config.json.json文件

2.可自行设置是否同意自动加好友，命令为/更改自动同意群聊 1或0、/更改自动同意好友 1或0、/更改自动同意 1或0 1或0

同时，也可以重置当日好友请求的数量 /重置好友请求 数量（不写默认重置日被请求加好友、群次数为零，后缀数字则会重置为该数值），

3.该插件会检查添加好友、群的请求，同意自动添加则自动，上限默认为一日五个，下次收到请求时会检查时间不是一天会重置日被请求加好友、群次数，并向插件指定qq号发送提示，

4.不同意则保存记录等待命令/同意加 qq号或群号，/拒绝加 qq号或群号，/查看加 查看数量（可不填，默认为配置中的最大值）

5./添加请求接收者 /删除请求接收者 此二者用来添加好友请求处理人，默认配置为前2个超管。

6./更改最大日加好友数量 数量（正整数） /更改查看加返回数量 数量 （非负整数，<120）  /重载配置 重新载入配置文件数据 用于直接修改文件后的重载问题

配置项结构

{
    "agreeAutoApprove": { "qq": 1, "group": 0 },
    "maxNum": 5,
    "maxViewNum":20,
    "recipientList": [],
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
