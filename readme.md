# rsspush

##### 更新

现在支持以图片的形式推送订阅

### 简介

利用peewee和feedparser实现的rss推送插件，适用于HoshinoBot V2

目前支持绝大多数的RSS源

### 安装方法

- 1.在modules目录下执行 `git clone https://github.com/pcrbot/Rsspush.git`
- 2.在`__bot__.py`的`module`中添加`Rsspush`
- 3.(可选)修改`data.py`中的`BASE_URL`为你的Rsshub地址
- 4.开启`rss`服务

### 使用方法

[]内为可选参数

| 功能                                                         | 指令                                  |
| ------------------------------------------------------------ | ------------------------------------- |
| 添加订阅，可以添加订阅名和RSS地址，添加参数-r或者--rsshub之后，可以添加rsshub的路由 | 添加订阅 name url/route [-r/--rsshub] |
| 取消订阅，可以根据要取消订阅的name来删除指定订阅             | 删除订阅 name                         |
| 查看本群订阅，可以查看本群存储的订阅                         | 查看本群订阅                          |
| 查订阅 ，可以查看指定订阅的当前状态,添加参数-l后可以指定记录条数 | 查订阅 name [-l/--limit limit]        |

