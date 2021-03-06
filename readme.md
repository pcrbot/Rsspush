# Rsspush

##### 更新日志
1.27 修复因为多个cqhttp实现连接到一个HoshinoBot而导致的无法推送的Bug

1.22 更新文字转图片的方法，使之更容易受控

> 引用自[本人HoshinoBot](https://github.com/AkiraXie/HoshinoBot/blob/master/hoshino/util.py)

1.19 现在支持以图片的形式推送订阅

### 简介

利用peewee和feedparser实现的rss推送插件，适用于HoshinoBot。

目前支持绝大多数的RSS源,同时也支持直接添加RSSHUB的**路由**作为订阅。

**路由可参考[RSSHUB文档](https://docs.rsshub.app/)；由于直播类路由的特性，需要在开播时才能订阅。**



### 安装方法

- 1.在modules目录下执行 `git clone https://github.com/pcrbot/Rsspush.git`
- 2.在`__bot__.py`的`module`中添加`Rsspush`
- 3.(可选)修改`data.py`中的`BASE_URL`为你的Rsshub地址
- 4.开启`rss`服务

### 使用方法

[]内为可选参数

| 功能                                                         | 指令                                  |
| ------------------------------------------------------------ | ------------------------------------- |
| 添加订阅，可以添加订阅名和RSS地址，当添加参数-r或者--rsshub之后，仅需添加rsshub的路由即可 | 添加订阅 name url/route [-r/--rsshub] |
| 取消订阅，可以根据要取消订阅的name来删除指定订阅             | 删除订阅 name                         |
| 查看本群订阅，可以查看本群存储的订阅                         | 查看本群订阅                          |
| 查订阅 ，可以查看指定订阅的当前状态,添加参数-l或者--limit后可以指定记录条数 | 查订阅 name [-l/--limit limit]        |
