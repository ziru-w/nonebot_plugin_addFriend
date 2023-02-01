# nonebot_plugin_addFriend
## 一个基于NoneBot2的插件，用于处理被请求加QQ好友和QQ群的请求


A plug-in based on nonebot2, which is used to process the request to add QQ friends and QQ groups

## 如果版本更新请按模板手动配置config.json文件中的新增项和键名更改项，如果不介意原来配置初始化，可以删掉重新生成。修改config.json 时，如果使用vscode的话推荐使用prettier插件格式化，自带的也行

下载方法:

    pip install nonebot_plugin_addFriend

1.该插件运行后会检查配置文件是否存在，并生成默认配置，也可手动复制内容创建文件，创建路径为插件目录，文件名为config.json,其中.json为后缀名，表征文件类型，请不要创建为config.json.json文件，

2.可自行设置是否同意自动加好友，命令为/更改自动同意群聊 1、/更改自动同意好友 0、/更改自动同意 1 1   1是同意,0是不同意

同时，也可以重置当时间段好友请求的数量 /重置好友请求 数量（不写默认重置日被请求加好友、群次数为零，后缀数字则会重置为该数值），

3.该插件会检查添加好友、群的请求，同意自动添加则自动，上限默认为两小时五个，下次收到请求时会检查时间不是时间段会重置被请求加好友、群次数，并向插件指定qq号发送提示，

4.不同意则保存记录等待命令/同意加 qq号或群号，/拒绝加 qq号或群号，/查看加 查看数量（可不填，默认为配置中的最大值）

5./添加请求接收者 /删除请求接收者 此二者用来添加好友请求处理人，默认配置为前2个超管。

6./更改最大加好友数量 数量（正整数） 

/更改查看加返回数量 数量 （非负整数，<120） 

/更改加好友时间单位 时/分/天 (刷新时间间隔单位，你说哪里修改数量，忘加上了，去配置里手动修改就好)  

7./重载配置 重新载入配置文件数据 用于直接修改文件后的重载问题 

8./设置bot私聊转发

9.黑名单群聊与警告群聊、黑名单群名与警告群名，一个直接拒绝、一个不自动同意，含黑名单、警告词或群号时生效，可以同时转发拉人头兼职群群聊发起者给配置过的好友，一般是该群管理员（自己配置qq号，因为只发给好友，临时会话太危险），暂无机器人接口、请于本插件目录下config.json文件中手动配置

10.验证消息，需要验证消息在添加者验证消息中方验证通过，默认空字符，表示皆通过。手动配置

11./清理请求表 清理请求表中已添加过的好友信息

12./加好友帮助 返回各命令，忘了命令是哪个就康康。



配置项结构
{
  "agreeAutoApprove": { "friend": 1, "group": 0 },
  "numControl": {"maxNum":5,"time":2,"unit":"h"},
  "maxViewNum":20,
  "recipientList": [],
  "forwardSet":0,
  "blackDict":{"friend":{"text":[],"id":[]},"group":{"text":[],"id":[]},"forward":{}},
  "warnDict":{"friend":{"text":[],"id":[]},"group":{"text":[],"id":[]},"forward":{}},
  "allowAddFriednText":[],
  "botName": "我",
  "friend_msg": {
      "notice_msg": "请求添加好友,验证消息为",
      "welcome_msg": "我未知的的朋友啊，很高兴你添加我为qq好友哦！\n同时，如果有疑问，可以发送/help哦"
  },
  "group_msg": {
      "notice_msg": "发送群邀请,验证消息为",
      "welcome_msg": "我亲爱的的朋友啊，很高兴你邀请我哦！"
  },
  "statusDict":{
      "blackDict":{"friend":{"status":"拉黑QQ,已拒绝,仅作提示"},"group":{"status":"拉黑群聊,已拒绝,仅作提示"}},
      "warnDict":{"friend":{"status":"警告QQ,手动同意,是否同意"},"group":{"status":"警告群聊,手动同意,是否同意"}}
  }
}