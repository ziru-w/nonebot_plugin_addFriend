# nonebot_plugin_addFriend
一个基于NoneBot2的插件，用于处理QQ好友和QQ群加入请求


A plugin based on NoneBot2 to process QQ friends and QQ group join requests


下载方法 pip install nonebot_plugin_addFriend


该插件会检查添加好友、群的请求，并自动添加，上限一日五个，下次收到请求时会检查时间不是一天会重置日添加好友、群友次数，并向插件指定qq号发送提示


发送命令 重置好友请求 可以重置日添加好友、群友次数重置为零，后缀数字则会重置为该数值。
 
 
注意，是次数，不是数量
