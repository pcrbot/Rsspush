import asyncio
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from nonebot.argparse import ArgumentParser
from nonebot import CommandSession
from hoshino import Service
from hoshino.util import pic2b64
from .aiohttpx import head
from .data import Rss, Rssdata, BASE_URL
sv = Service('rss', enable_on_default=False)

fontpath1 = os.path.join(os.path.dirname(__file__),'simsun.ttc')
fontpath2 = os.path.join(os.path.dirname(__file__),'simhei.ttf')


def getsize(text: str, fontsize: int) -> Tuple[int]:
    lines = text.split('\n')
    width = max([len(line) for line in lines])
    return width*fontsize, len(lines)*(fontsize+3)+4


def sumsize(a, b, c, d) -> Tuple[int]:
    return max(a, c), b+d


def info2pic(info: dict) -> str:
    title = f"标题: {info['标题']}"
    text = f"正文:\n{info['正文']}\n时间: {info['时间']}" 
    textsize = getsize(text, 18)
    titlesize = getsize(title, 22)
    base = Image.new('RGB', sumsize(*textsize, *titlesize), (255, 255, 255))
    draw = ImageDraw.Draw(base)
    font1 = ImageFont.truetype(fontpath1, 18)
    font2 = ImageFont.truetype(fontpath2, 22)
    draw.text((0, 0), title, font=font2, fill=(0,0,0))
    draw.text((0, titlesize[1]), text, font=font1, fill=(0,0,0))
    return pic2b64(base)
def infos2pic(infos:List[dict])->str:
    texts=[]
    for info in infos:
       text= f"标题: {info['标题']}\n时间: {info['时间']}\n======"
       texts.append(text)
    texts='\n'.join(texts)
    base = Image.new('RGB', getsize(texts,20), (255, 255, 255))
    draw = ImageDraw.Draw(base)
    font1 = ImageFont.truetype(fontpath1, 20)
    draw.text((0, 0), texts, font=font1, fill=(0,0,0))
    return pic2b64(base)
@sv.on_command('添加订阅', aliases=('addrss', '增加订阅'), shell_like=True)
async def addrss(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('name')
    parser.add_argument('url')
    parser.add_argument('-r', '--rsshub', action='store_true')
    args = parser.parse_args(session.argv)
    name = args.name
    url = BASE_URL+args.url if args.rsshub else args.url
    try:
        stats = await head(url, timeout=5, allow_redirects=True)
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.error(type(e))
        session.finish('请求路由失败,请稍后再试')
    if stats.status_code != 200:
        session.finish('请求路由失败,请检查路由状态')
    rss = Rss(url)
    if not await rss.has_entries:
        session.finish('暂不支持该RSS')
    try:
        Rssdata.replace(url=rss.url, name=name, group=session.event.group_id, date=await rss.last_update).execute()
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.error(type(e))
        session.finish('添加订阅失败')
    session.finish(f'添加订阅{name}成功')


@sv.on_command('删除订阅', aliases=('delrss', '取消订阅'))
async def delrss(session: CommandSession):
    try:
        name = session.current_arg_text.strip()
    except:
        return

    try:
        Rssdata.delete().where(Rssdata.name == name, Rssdata.group ==
                               session.event.group_id).execute()
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.error(type(e))
        session.finish('删除订阅失败')
    session.finish(f'删除订阅{name}成功')


@sv.scheduled_job('interval', minutes=3, jitter=20)
async def push_rss():
    bot = sv.bot
    glist = await sv.get_enable_groups()
    for gid in glist.keys():
        res = Rssdata.select(Rssdata.url, Rssdata.name,
                             Rssdata.date).where(Rssdata.group == gid)
        for r in res:
            rss = Rss(r.url)
            if not (await rss.has_entries):
                continue
            if (lstdate := await rss.last_update) != r.date:
                try:
                    await asyncio.sleep(0.5)
                    newinfo = await rss.get_new_entry_info()
                    msg = [f'订阅 {r.name} 更新啦！']
                    msg.append(f'[CQ:image,file={info2pic(newinfo)}]')
                    msg.append(f'链接: {newinfo["链接"]}')
                    Rssdata.update(date=lstdate).where(
                        Rssdata.group == gid, Rssdata.name == r.name, Rssdata.url == r.url).execute()
                    await bot.send_group_msg(message='\n'.join(msg), group_id=gid)
                except Exception as e:
                    sv.logger.exception(e)
                    sv.logger.error(f'{type(e)} occured when pushing rss')


@sv.on_command('订阅列表', aliases=('查看本群订阅'))
async def lookrsslist(session: CommandSession):
    try:
        res = Rssdata.select(Rssdata.url, Rssdata.name).where(Rssdata.group ==
                                                              session.event.group_id)
        msg = ['本群订阅如下:']
        for r in res:
            msg.append(f'订阅标题:{r.name}\n订阅链接:{await Rss(r.url).link}\n=====')
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.error(type(e))
        session.finish('查询订阅列表失败')
    session.finish('\n'.join(msg))


@sv.on_command('看订阅', aliases=('查订阅', '查看订阅'), shell_like=True)
async def lookrss(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('name')
    parser.add_argument('-l', '--limit', default=5, type=int)
    args = parser.parse_args(session.argv)
    limit = args.limit
    name = args.name
    try:
        res = Rssdata.select(Rssdata.url).where(Rssdata.name == name, Rssdata.group ==
                                                session.event.group_id)
        r = res[0]
        rss = Rss(r.url, limit)
        infos = await rss.get_all_entry_info()
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.error(type(e))
        session.finish(f'查订阅{name}失败')
    msg = [f'{name}的最近记录:']
    msg.append(f'[CQ:image,file={infos2pic(infos)}]')
    msg.append('详情可看: '+await rss.link)
    session.finish('\n'.join(msg))
