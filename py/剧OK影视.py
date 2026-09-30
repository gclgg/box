# -*- coding: utf-8 -*-
"""
剧OK (juok3.top) 爬虫
支持影视仓/蜂蜜TVBox 等APP
主页: https://juok3.top
API:  /api/filter  /api/detail  /api/search
"""
import sys
import re
import json
from urllib.parse import quote

sys.path.append('..')
try:
    from base.spider import Spider
except ImportError:
    class Spider:
        def fetch(self, url, headers=None, **kw):
            import urllib.request
            req = urllib.request.Request(url, headers=headers or {})
            resp = urllib.request.urlopen(req, timeout=15)
            return type('R', (), {'text': resp.read().decode('utf-8')})()

HOST = "https://juok3.top"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 分类配置: type_id -> (catId, type参数, 中文名)
CLASS_MAP = {
    "movie":   (1, None, "电影"),
    "tv":      (2, None, "电视剧"),
    "variety": (3, None, "综艺"),
    "anime":   (4, None, "动漫"),
    "short":   (2, "短剧", "短剧"),  # type=短剧, catId=2
}

# 解析线路 (拼接URL)
PARSE_APIS = [
    {"name": "默认接口", "url": "https://jx.xmflv.com/?url="},
    {"name": "拾光", "url": "https://98.rf.gd/8/?s=jx&i="},
    {"name": "请你", "url": "https://a.wkvip.net/?url="},
    {"name": "欣赏", "url": "https://www.8090g.cn/?url="},
    {"name": "极速", "url": "https://jx.2s0.cn/player/?url="},
    {"name": "super", "url": "https://super.playr.top/?url="},
    {"name": "fongmi", "url": "https://json.fongmi.cc/web?url="},
    {"name": "7解析", "url": "https://www.8090g.cn/jiexi/?url="},
    {"name": "M3U8", "url": "https://jx.m3u8.tv/jx/jx.php?url="},
    {"name": "Jn1", "url": "https://yparse.jn1.cc/index.php?url="},
    {"name": "CK", "url": "https://www.ckplayer.vip/jiexi/?url="},
    {"name": "PlayerJY", "url": "https://jx.playerjy.com/?url="},
    {"name": "冰豆", "url": "https://bd.jx.cn/?url="},
    {"name": "剖元", "url": "https://www.pouyun.com/?url="},
    {"name": "七哥", "url": "https://jx.nnxv.cn/tv.php?url="},
    {"name": "PlayM3U8", "url": "https://www.playm3u8.cn/jiexi.php?url="},
    {"name": "夜幕", "url": "https://www.yemu.xyz/?url="},
    {"name": "盘古", "url": "https://www.pangujiexi.com/jiexi/?url="},
    {"name": "Yparse", "url": "https://jx.yparse.com/index.php?url="},
    {"name": "爱豆", "url": "https://jx.aidouer.net/?url="},
    {"name": "YT", "url": "https://jx.yangtu.top/?url="},
]

# 平台名称映射
PLATFORM_NAMES = {
    "qiyi": "爱奇艺", "iqiyi": "爱奇艺",
    "imgo": "芒果TV", "mgtv": "芒果TV",
    "qq": "腾讯视频", "v.qq": "腾讯视频",
    "youku": "优酷",
    "leshi": "乐视", "le": "乐视",
    "sohu": "搜狐",
    "bilibili": "B站",
    "1905": "1905",
    "pptv": "PPTV",
    "xigua": "西瓜",
    "douyin": "抖音",
    "kuaishou": "快手",
}

# 搜索缓存
_search_cache = {}


def _cover(raw):
    if not raw:
        return ""
    if raw.startswith("//"):
        return "https:" + raw
    return raw


def _year(pubdate):
    if pubdate and len(str(pubdate)) >= 4:
        return str(pubdate)[:4]
    return ""


def _platform_name(site):
    return PLATFORM_NAMES.get(site, site)


class Spider(Spider):

    def init(self, extend=""):
        pass

    def getName(self):
        return "剧OK"

    def isVideoFormat(self, url):
        return bool(re.search(r'\.(m3u8|mp4|flv|avi|mkv|rmvb|wmv|ts)$', url, re.IGNORECASE))

    def manualVideoCheck(self):
        return True

    def destroy(self):
        pass

    # ── 分类 ──────────────────────────────────────────────
    def homeContent(self, filter=False):
        classes = []
        for k, v in CLASS_MAP.items():
            classes.append({"type_id": k, "type_name": v[2]})
        return {"class": classes}

    def homeVideoContent(self):
        try:
            all_items = []
            # 从各分类各取一些凑首页推荐
            for cat_id, size in [(1, 12), (2, 10), (3, 6), (4, 6)]:
                try:
                    url = f"{HOST}/api/filter?catId={cat_id}&page=1&size={size}"
                    r = self.fetch(url, headers={"User-Agent": UA, "Accept": "application/json"})
                    data = json.loads(r.text)
                    for m in data.get("movies", []):
                        vid = f"detail:{cat_id}:{m.get('id', '')}"
                        all_items.append({
                            "vod_id": vid,
                            "vod_name": m.get("title", "").strip(),
                            "vod_pic": _cover(m.get("cdncover") or m.get("cover", "")),
                            "vod_year": _year(m.get("pubdate", "")),
                            "vod_remarks": m.get("upinfo") or f"{m.get('total','')}集",
                        })
                except Exception:
                    pass
            return {"list": all_items[:50]}
        except Exception:
            return {"list": []}

    # ── 分类列表 ──────────────────────────────────────────
    def categoryContent(self, tid, pg=1, filter=False, extend=None):
        try:
            pn = max(int(str(pg)), 1)
            info = CLASS_MAP.get(tid)
            if not info:
                return {"list": [], "page": pn, "pagecount": 1, "limit": 24, "total": 0}

            cat_id, type_name, _ = info
            params = [f"catId={cat_id}", f"page={pn}", "size=24"]
            if type_name:
                params.append(f"type={quote(type_name)}")
            url = f"{HOST}/api/filter?{'&'.join(params)}"

            r = self.fetch(url, headers={"User-Agent": UA, "Accept": "application/json"})
            data = json.loads(r.text)
            total = data.get("total", 0)
            pagecount = (total // 24) + (1 if total % 24 else 0) if total else 1

            items = []
            for m in data.get("movies", []):
                vid = f"detail:{cat_id}:{m.get('id', '')}"
                # 备注优先用upinfo(更新状态)，其次总集数，最后年份+地区
                remarks = m.get("upinfo", "") or (f"{m.get('total','')}集" if m.get('total') else "")
                if not remarks:
                    parts = []
                    y = _year(m.get("pubdate", ""))
                    if y:
                        parts.append(y)
                    if isinstance(m.get("area"), list) and m.get("area"):
                        parts.append(m["area"][0])
                    remarks = " ".join(parts)

                items.append({
                    "vod_id": vid,
                    "vod_name": m.get("title", "").strip(),
                    "vod_pic": _cover(m.get("cdncover") or m.get("cover", "")),
                    "vod_year": _year(m.get("pubdate", "")),
                    "vod_remarks": remarks,
                })

            return {
                "list": items,
                "page": pn,
                "pagecount": max(pagecount, pn),
                "limit": 24,
                "total": total,
            }
        except Exception as e:
            print(f"categoryContent error: {e}")
            return {"list": [], "page": pg, "pagecount": 1, "limit": 24, "total": 0}

    # ── 详情 ──────────────────────────────────────────────
    def detailContent(self, ids):
        try:
            vid = str(ids[0]) if ids else ""
            if not vid:
                return {"list": []}

            # 搜索结果直接播放
            if vid.startswith("search:"):
                return self._detail_search(vid)

            if not vid.startswith("detail:"):
                return {"list": []}

            parts = vid.split(":", 2)
            if len(parts) != 3:
                return {"list": []}

            cat_id, hash_id = parts[1], parts[2]
            if not cat_id or not hash_id:
                return {"list": []}

            # 调详情API
            detail_url = f"{HOST}/api/detail?cat={cat_id}&id={hash_id}"
            r = self.fetch(detail_url, headers={
                "User-Agent": UA,
                "Accept": "application/json",
                "Referer": HOST + "/",
            })
            data = json.loads(r.text)

            if data.get("errno") != 0 or not data.get("data"):
                return {"list": []}

            d = data["data"]
            title = d.get("title", "")
            cover = _cover(d.get("cdncover") or d.get("cover", ""))
            year = _year(d.get("pubdate", ""))
            area = ", ".join(d.get("area", [])) if isinstance(d.get("area"), list) else str(d.get("area", ""))
            type_name = ", ".join(d.get("moviecategory", [])) if isinstance(d.get("moviecategory"), list) else str(d.get("moviecategory", ""))
            director = ", ".join(d.get("director", [])) if isinstance(d.get("director"), list) else str(d.get("director", ""))
            actor = ", ".join(d.get("actor", [])) if isinstance(d.get("actor"), list) else str(d.get("actor", ""))
            content = d.get("description", "")
            total = d.get("total", 0)
            upinfo = d.get("upinfo", "")
            remarks = str(upinfo) if upinfo else (f"{total}集" if total else "")

            allepi = d.get("allepidetail", {})
            pld = d.get("playlinksdetail", {})

            # ── 有分集 (电视剧/综艺) ──
            if allepi:
                pf_list, pu_list = [], []
                for api in PARSE_APIS:
                    ep_list = []
                    for site, episodes in allepi.items():
                        for ep in episodes:
                            ep_url = ep.get("url", "")
                            ep_num = ep.get("playlink_num", ep.get("num", ""))
                            if not ep_url:
                                continue
                            parse_url = api["url"] + ep_url
                            ep_list.append(f"第{ep_num}集${parse_url}")
                    if ep_list:
                        pf_list.append(api["name"])
                        pu_list.append("#".join(ep_list))

            # ── 单集/电影 ──
            elif pld:
                pf_list, pu_list = [], []
                platforms = []
                for site, info in pld.items():
                    du = info.get("default_url", "")
                    if du:
                        platforms.append((site, du))
                if not platforms:
                    return {"list": []}
                for api in PARSE_APIS:
                    ep_list = []
                    for site, url in platforms:
                        parse_url = api["url"] + url
                        ep_list.append(f"{_platform_name(site)}${parse_url}")
                    if ep_list:
                        pf_list.append(api["name"])
                        pu_list.append("#".join(ep_list))
            else:
                return {"list": []}

            vod = {
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": cover,
                "vod_year": year,
                "vod_area": area,
                "vod_class": type_name,
                "vod_director": director,
                "vod_actor": actor,
                "vod_content": content,
                "vod_remarks": remarks,
                "vod_play_from": "$$$".join(pf_list),
                "vod_play_url": "$$$".join(pu_list),
            }
            return {"list": [vod]}
        except Exception as e:
            print(f"detailContent error: {e}")
            return {"list": []}

    def _detail_search(self, vid):
        """从搜索缓存恢复详情"""
        try:
            cached = _search_cache.get(vid, {})
            if not cached or not cached.get("vod_play_url"):
                return {"list": []}
            return {
                "list": [{
                    "vod_id": vid,
                    "vod_name": cached.get("vod_name", ""),
                    "vod_pic": cached.get("vod_pic", ""),
                    "vod_remarks": cached.get("vod_remarks", ""),
                    "vod_year": cached.get("vod_year", ""),
                    "vod_play_from": cached.get("vod_play_from", "播放"),
                    "vod_play_url": cached.get("vod_play_url", ""),
                }]
            }
        except Exception:
            return {"list": []}

    # ── 搜索 ──────────────────────────────────────────────
    def searchContent(self, key, quick=False, pg=1):
        try:
            pn = max(int(str(pg)), 1)
            # 尝试两个域名
            for host in [HOST, "https://juok1.top"]:
                try:
                    url = f"{host}/api/search?q={quote(key)}"
                    if pn > 1:
                        url += f"&page={pn}"
                    r = self.fetch(url, headers={
                        "User-Agent": UA,
                        "Accept": "application/json, text/plain, */*",
                        "Referer": host + "/",
                    })
                    if r.status_code == 200 or (hasattr(r, 'text') and '{"results"' in r.text):
                        data = json.loads(r.text)
                        items = self._extract_search_items(data)
                        return {"list": items, "page": pn}
                except Exception:
                    continue
            return {"list": [], "page": pn}
        except Exception as e:
            print(f"searchContent error: {e}")
            return {"list": [], "page": 1}

    def _extract_search_items(self, data):
        """从搜索结果提取影片"""
        global _search_cache
        items = []
        for item in data.get("results", []):
            if "vod_name" in item:
                vod_id = str(item.get("vod_id", ""))
                if not vod_id:
                    continue
                source_key = item.get("sourceKey", "")
                cache_key = f"search:{vod_id}:{source_key}"
                pic = item.get("vod_pic", "")
                if pic and pic.startswith("//"):
                    pic = "https:" + pic
                _search_cache[cache_key] = {
                    "vod_name": item.get("vod_name", "").strip(),
                    "vod_pic": pic,
                    "vod_remarks": item.get("vod_remarks", ""),
                    "vod_year": item.get("vod_year", ""),
                    "vod_play_url": item.get("vod_play_url", ""),
                    "vod_play_from": item.get("vod_play_from", ""),
                }
                items.append({
                    "vod_id": cache_key,
                    "vod_name": item.get("vod_name", "").strip(),
                    "vod_pic": pic,
                    "vod_remarks": item.get("vod_remarks", ""),
                    "vod_year": item.get("vod_year", ""),
                })
            elif "title" in item:
                cat_id = item.get("cat_id", "")
                en_id = item.get("en_id", "")
                if not cat_id or not en_id:
                    continue
                cache_key = f"search:{item.get('id','')}:{cat_id}"
                pic = item.get("cover", "")
                if pic and pic.startswith("//"):
                    pic = "https:" + pic
                _search_cache[cache_key] = {
                    "vod_name": item.get("title", "").replace("<b>", "").replace("</b>", "").strip(),
                    "vod_pic": pic,
                    "vod_remarks": item.get("cat_name", ""),
                    "vod_play_url": f"{HOST}/api/detail?cat={cat_id}&id={en_id}",
                    "vod_play_from": "详情获取",
                }
                items.append({
                    "vod_id": cache_key,
                    "vod_name": item.get("title", "").replace("<b>", "").replace("</b>", "").strip(),
                    "vod_pic": pic,
                    "vod_remarks": item.get("cat_name", ""),
                })
        return items

    # ── 播放 ──────────────────────────────────────────────
    def playerContent(self, flag, id, vipFlags=None):
        url = str(id) if id else str(flag)
        if not url:
            return {"url": "", "parse": 0}

        # 去掉名称前缀  第X集$URL
        if "$" in url:
            url = url.split("$", 1)[1]

        # 搜索缓存URL
        if url.startswith("search:"):
            try:
                cached = _search_cache.get(url, {})
                play_url = cached.get("vod_play_url", "")
                if not play_url:
                    return {"url": "", "parse": 0}
                fmt = 1 if self.isVideoFormat(play_url) else 0
                return {"url": play_url, "parse": fmt, "header": {"User-Agent": UA}}
            except Exception:
                return {"url": "", "parse": 0}

        # m3u8/mp4 直链
        if url.startswith("http") and self.isVideoFormat(url):
            return {"url": url, "parse": 0, "header": {"User-Agent": UA}}

        # 其他视频URL (需要解析)
        if url.startswith("http"):
            return {"url": url, "parse": 1, "header": {"User-Agent": UA}}

        return {"url": url, "parse": 1, "header": {"User-Agent": UA}}

    def localProxy(self, param):
        pass
