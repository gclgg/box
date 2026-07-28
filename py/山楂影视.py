# -*- coding: utf-8 -*-
# 本资源来源于互联网公开渠道，仅可用于个人学习爬虫技术。
# 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。
# junyouyun

import sys
import json
import time
import base64
import hashlib
import urllib3
from urllib.parse import quote
from base.spider import Spider
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')

class Spider(Spider):
    host, userid, episode_list = '', '', []
    
    # ---------- 加密与签名相关常量 ----------
    PUB_KEY_B64 = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCoYt0BP77U+DM08BiI/QbSRIfxijXo85BTPqIM1Ow8BNwhLETzRIZ+dEwdWDbydG/PspgBAfRpGaYVdJYtvaC2JnoO8+Ik6qMWojfEJxSFLa0Pb0A892tun4gsxoEMjcreZ+YGyaBxAfqX0BSMfdrOgIYaZQjYrw9TRLlUT31QoQIDAQAB"
    APP_SIGN_SHA1 = "09a8dc51639a31801af5f6418caebfabc695eb24"
    DEVICE_ID = "2d590b9842d064a1"
    
    # RSA 私钥（用于解密响应）
    PRIV_KEY_B64 = """MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCquQQ5r6+yJI8CDFkXRp8vUsdD45ov8EP12ooLs56ca2DQXaSNGS9910bAPVA9chkp0mKIvKqjAsHz5Tl9EeNPblarGEeJUIxpxZtiSqNTpvtiD/TjhpzuHYic7RAfQ/h7p/ypE8ymU42pYjsB5t26Mv6XgkLV+jzrSf73HlCuS0iMyLmt6zz3Mw9izM13EpB8iFLtfbbYymycKTx4RAmPQLwhNGex/AlUIYxXP4R2yyaa4W6mEtc6aME2QuzJFxPgP3HJ9NBx/LWVn4skxWjZ7zg+VRQRHnjyVaSLu3Z5gN5ITWCyE32qaHJa6WBahZj5jWhRyAG1bQ+xKJa8lBL5AgMBAAECggEAUwv9SjJ0PSwbhNuM2w23kcWquROWhYtTA91zGY4esehqB/IFgb2mpIh8Gje5OKqwIu/8jpd4SiOlRYdUF8sD0DfUYRZGdj2AkFNX6tBz8tVfo6wvbB6naA1lzzBij1L5JO3qsjS3cJFkb+kg2yP66AC2Z+0tpfk8eRhdtshAZwfcd1DEGt1uAvYL1eaUK9HRvpt9lPeGcHERDl2hBd4uyaF0K1O+zF9y59nYbTySWPxRZq3sFEE85xRMlstD7YZi7W2gKvMFRD4/FKmrZ3m7aKJRITtyKOyyPcYmepNv3Qv7kk59Pg38n2WWQ0Ra/bCH3E48YNCnQvZMpitkTfJhoQKBgQDbnROOYTP8OTJ6f/qhoGjxeO3x1VOaOp8l0x7b0SCfoqNGS0Cyiqj72BmJtPMPqSTjn6MmNzqbg1KOdhXyzNozs+i5ccW1M56j96mr5I/Z0FpE3oyIHNfDDBlf9M8YQqEF9oYxniYYft9oapO7cRQkHER6qpvnHTavwlv4m78CXwKBgQDHAjs2YlpKDdI1lcbZJCc7TwtH+Pd2bUki8YXafWNcPhITQHbOZjr310eK1QJC6GJncjkOqbX7yv3ivvTO35FZTQhuA1xEG1P00FG8bE0tHYPIwQHi9y0eA5cieMdo8E6XYria1mw/3fqSQEsfZyJlR32JQIoGAipM8iO1X2nZpwKBgDkMFIhnt5lNQk+P7wsNIDWZtDWdtJnboHuy29E+Abt2A/O+mI/IdRz2hau/1WO8DFkUnszOi+rZshhPlGP90rCbi1igtTrcrdjp/KkqNjPea5R4OwkgdOu1uOG0NheXNzzVTQaWjk7Opjn5dWa7eP/oV+GFb/oZHJuLYVizHGsBAoGADA7rjZEKDYCm4w5PPSr+oY5ZjaPdQrS+gLqHtMRyN82fBMGcMUdqfUfzEstzVqCEDeaS5HuOBlK3bXzKkppjUTjksN3NQmcxgBz7RuJ9DqXCLXDcb2cwuafYCYOt+YLOEEgwDVm+t2P44dG5e46hO+fICH/7nP+WlpD5buz4GfMCgYB57r3g/6hi9WUDnfc7ZAzWMqR0EhJVYKYy+KFEtdIPzhkkIHq5RASe88E9kzoGoZFdb3tIjvGZWcHerirrqWkMsuQtP/Qi0zjieid5tAPj+r4kbiCVTw0E0jnmPBzGInQi7lpeTTKnG1fbyS5lBS+WmHfIuzpECgCkxhaT+LJJkg=="""

    headers = {
        'User-Agent': "okhttp/4.12.0",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json;charset=UTF-8",
        'Cache-Control': "no-cache",
        'token': "",
        'deviceId': DEVICE_ID,
        'client': "app",
        'deviceType': "Android"
    }

    def getName(self):
        return "山楂影视"

    # ---------- RSA 加密 ----------
    def rsa_encrypt(self, data: str) -> str:
        key = RSA.import_key(base64.b64decode(self.PUB_KEY_B64))
        cipher = PKCS1_v1_5.new(key)
        encrypted = cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    # ---------- RSA 解密（支持分块） ----------
    def rsa_decrypt(self, encrypted_b64: str) -> str:
        key = RSA.import_key(base64.b64decode(self.PRIV_KEY_B64))
        cipher = PKCS1_v1_5.new(key)
        encrypted_bytes = base64.b64decode(encrypted_b64)
        block_size = 256
        decrypted_parts = []
        for i in range(0, len(encrypted_bytes), block_size):
            block = encrypted_bytes[i:i+block_size]
            decrypted_parts.append(cipher.decrypt(block, None))
        return b''.join(decrypted_parts).decode('utf-8')

    # ---------- 构建签名参数 ----------
    def build_params_string(self, episode_id="", episode_index="", vid="", player_id="", type_id="", user_id=""):
        return (f"episodeId{episode_id}"
                f"episodeIndex{episode_index}"
                f"id{vid}"
                f"playerId{player_id}"
                f"source0"
                f"typeId{type_id}"
                f"userId{user_id}")

    def generate_sign(self, timestamp: str, params_str: str, device_id: str) -> str:
        raw = f"SaltLSFBTimestamp{timestamp}Params{params_str}ClientappDeviceId{device_id}"
        b64 = base64.b64encode(raw.encode('utf-8')).decode('utf-8')
        md5 = hashlib.md5(b64.encode('utf-8')).hexdigest().upper()
        return md5

    def build_encrypted_headers(self, body_json: str, params_str: str) -> dict:
        timestamp = str(int(time.time()))
        encrypted_key = self.rsa_encrypt(body_json)
        snjm = self.rsa_encrypt("113")
        appsign = self.rsa_encrypt(self.APP_SIGN_SHA1)
        sign = self.generate_sign(timestamp, params_str, self.DEVICE_ID)

        headers = {
            "snjm": snjm,
            "appsign": appsign,
            "timestamp": timestamp,
            "sign": sign,
            "deviceId": self.DEVICE_ID,
            "token": self.headers.get('token', ''),
            "client": "app",
            "deviceType": "Android",
            "Content-Type": "application/json;charset=UTF-8",
            "Cache-Control": "no-cache",
            "User-Agent": "okhttp/4.12.0"
        }
        return headers, {"key": encrypted_key}

    def init(self, extend=''):
        self.headers['deviceId'] = self.DEVICE_ID
        self.host = 'http://qkys.qukanwh.com'
        try:
            response = self.fetch(f'{self.host}/api/v1/app/user/visitorInfo', headers=self.headers).json()
            self.userid = str(response.get('data', {}).get('id', ''))
            token = response.get('data', {}).get('token', '')
            self.headers['token'] = token
        except Exception:
            self.userid = ''
            self.headers['token'] = ''

    # ---------- 影视仓必须返回 filters，否则首页不渲染 ----------
    def homeContent(self, filter):
        try:
            response = self.post(f'{self.host}/api/v1/app/screen/screenType', headers=self.headers).json()
            data = response.get('data', []) or []
            classes = []
            for i in data:
                if isinstance(i, dict) and 'id' in i and 'name' in i:
                    classes.append({
                        'type_id': str(i['id']),
                        'type_name': str(i['name'])
                    })
            # 影视仓解析首页时，如果缺少 filters 字段会直接跳过该源
            return {'class': classes, 'filters': {}}
        except Exception:
            return {'class': [], 'filters': {}}

    # ---------- 串行请求 + 限制分类数，防止影视仓超时 ----------
    def homeVideoContent(self):
        try:
            response = self.post(
                f'{self.host}/api/v1/app/recommend/recommendList',
                headers=self.headers
            ).json()
            data = response.get('data', []) or []
            videos = []
            # 影视仓对首页加载时间敏感，只取前 3 个分类，每个 6 条，避免超时
            for item in (data[:3] if isinstance(data, list) else []):
                try:
                    if not isinstance(item, dict) or 'id' not in item:
                        continue
                    resp = self.post(
                        f'{self.host}/api/v1/app/recommend/recommendSubList',
                        data=json.dumps({
                            "condition": item['id'],
                            "pageNum": 1,
                            "pageSize": 6
                        }),
                        headers=self.headers
                    ).json()
                    records = resp.get('data', {}).get('records', []) or []
                    for video in records:
                        if not isinstance(video, dict):
                            continue
                        videos.append({
                            "vod_id": str(video.get('id', '')),
                            "vod_name": str(video.get('name', '')),
                            "vod_pic": str(video.get('cover', '')),
                            "vod_remarks": str(video.get('area', '') or video.get('remark', '') or '')
                        })
                except Exception:
                    continue
            return {'list': videos}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        payload = {
            "condition": {
                "classify": "",
                "region": "",
                "sreecnTypeEnum": "NEWEST",
                "typeId": tid,
                "year": ""
            },
            "pageNum": int(pg) if str(pg).isdigit() else 1,
            "pageSize": 40
        }
        try:
            response = self.post(
                f'{self.host}/api/v1/app/screen/screenMovie',
                data=json.dumps(payload),
                headers=self.headers
            ).json()
            videos = []
            for i in response.get('data', {}).get('records', []) or []:
                videos.append({
                    "vod_id": str(i.get('id', '')),
                    "vod_name": str(i.get('name', '')),
                    "vod_pic": str(i.get('cover', '')),
                    "vod_remarks": str(i.get('area', '')),
                    "vod_year": str(i.get('year', ''))
                })
            return {'list': videos, 'page': int(pg) if str(pg).isdigit() else 1}
        except Exception:
            return {'list': [], 'page': int(pg) if str(pg).isdigit() else 1}

    def searchContent(self, key, quick, pg='1'):
        payload = {
            "condition": {
                "value": key
            },
            "pageNum": int(pg) if str(pg).isdigit() else 1,
            "pageSize": 40
        }
        try:
            response = self.post(
                f'{self.host}/api/v1/app/search/searchMovie',
                data=json.dumps(payload),
                headers=self.headers
            ).json()
            videos = []
            for i in response.get('data', {}).get('records', []) or []:
                videos.append({
                    'vod_id': str(i.get('id', '')),
                    'vod_name': str(i.get('name', '')),
                    'vod_pic': str(i.get('cover', '')),
                    'vod_remarks': str(i.get('area', '')),
                    'vod_year': str(i.get('year', '')),
                    'vod_area': str(i.get('area', '')),
                    'vod_content': str(i.get('desc', ''))
                })
            return {'list': videos, 'page': int(pg) if str(pg).isdigit() else 1}
        except Exception:
            return {'list': [], 'page': int(pg) if str(pg).isdigit() else 1}

    def detailContent(self, ids):
        type_id = "M15"
        vid = ids[0]
        body = {
            "id": vid,
            "source": 0,
            "typeId": type_id,
            "userId": self.userid,
            "episodeId": "",
            "episodeIndex": "",
            "playerId": ""
        }
        body_json = json.dumps(body, separators=(',', ':'))
        params_str = self.build_params_string(
            episode_id="",
            episode_index="",
            vid=str(vid),
            player_id="",
            type_id=type_id,
            user_id=str(self.userid)
        )
        headers, payload = self.build_encrypted_headers(body_json, params_str)

        try:
            resp_raw = self.post(
                f'{self.host}/api/v1/app/play/movieDetails',
                data=json.dumps(payload),
                headers=headers
            ).json()
            encrypted_data = resp_raw.get('data')
            if not encrypted_data:
                return {'list': []}
            decrypted_json_str = self.rsa_decrypt(encrypted_data)
            data = json.loads(decrypted_json_str)
        except Exception:
            return {'list': []}

        currentplayerid = data.get('playerId', '')
        play_urls = []
        play_url = []
        show = []
        episode_list = data.get('episodeList', []) or []
        for i in episode_list:
            play_url.append(f"{i['episode']}${ids[0]}@{currentplayerid}@{i['id']}@episode")
        if play_url:
            play_urls.append('#'.join(play_url))
        
        moviePlayerList = data.get('moviePlayerList', []) or []
        for i2 in moviePlayerList:
            if i2.get('id') == currentplayerid:
                show.append(str(i2.get('moviePlayerName', '')))
        
        for j in moviePlayerList:
            playerid = j.get('id')
            episodeTotal = j.get('episodeTotal')
            if playerid == currentplayerid or episodeTotal is None:
                continue
            play_url = []
            for k in range(1, int(episodeTotal) + 1):
                play_url.append(f"第{k}集${k}@{playerid}@{ids[0]}@virtual")
            if play_url:
                play_urls.append('#'.join(play_url))
            name = j.get('moviePlayerName', '')
            if name and name not in show:
                show.append(str(name))

        try:
            payload_desc = {"id": ids[0], "typeId": type_id}
            response_desc = self.post(
                f'{self.host}/api/v1/app/play/movieDesc',
                data=json.dumps(payload_desc),
                headers=self.headers
            ).json()
            data2 = response_desc.get('data', {}) or {}
        except Exception:
            data2 = {}

        video = {
            'vod_id': str(data2.get('id', vid)),
            'vod_name': str(data2.get('name', '')),
            'vod_pic': str(data2.get('cover', '')),
            'vod_content': str(data2.get('introduce', '')),
            'vod_year': str(data2.get('year', '')),
            'vod_area': str(data2.get('area', '')),
            'vod_remarks': '',
            'vod_score': str(data2.get('score', '')),
            'type_name': str(data2.get('classify', '')),
            'vod_director': str(data2.get('director', '')),
            'vod_actor': str(data2.get('star', '')),
            'vod_play_from': '$$$'.join(show) if show else '山楂影视',
            'vod_play_url': '$$$'.join(play_urls) if play_urls else ''
        }
        return {'list': [video]}

    def playerContent(self, flag, id, vipflags):
        param, playerid, param2, param3 = id.split('@')
        if param3 == 'virtual':
            payload = {
                "episodeIndex": str(int(param) - 1),
                "id": int(param2),
                "playerId": playerid,
                "source": 0,
                "typeId": "M15",
                "userId": self.userid,
                "episodeId": ""
            }
        else:
            payload = {
                "episodeId": param2,
                "id": int(param),
                "playerId": playerid,
                "source": 0,
                "typeId": "M15",
                "userId": self.userid,
                "episodeIndex": ""
            }
        body_json = json.dumps(payload, separators=(',', ':'))
        params_str = self.build_params_string(
            episode_id=payload.get("episodeId", ""),
            episode_index=payload.get("episodeIndex", ""),
            vid=str(payload["id"]),
            player_id=payload["playerId"],
            type_id=payload["typeId"],
            user_id=str(payload["userId"])
        )
        headers, encrypted_payload = self.build_encrypted_headers(body_json, params_str)
        try:
            resp_raw = self.post(
                f'{self.host}/api/v1/app/play/movieDetails',
                data=json.dumps(encrypted_payload),
                headers=headers
            ).json()
            encrypted_data = resp_raw.get('data')
            if not encrypted_data:
                return {'jx': '0', 'parse': '0', 'url': '', 'header': {}}
            decrypted_json_str = self.rsa_decrypt(encrypted_data)
            data = json.loads(decrypted_json_str)
        except Exception:
            return {'jx': '0', 'parse': '0', 'url': '', 'header': {}}

        parse_url = data.get('url', '')
        playerid = data.get('playerId', '')

        try:
            resp_analysis = self.fetch(
                f"{self.host}/api/v1/app/play/analysisMovieUrl?playerUrl={quote(parse_url, safe='')}&playerId={playerid}",
                headers=self.headers
            ).json()
            url = resp_analysis.get('data', '')
        except Exception:
            url = ''

        return {
            'jx': '0',
            'parse': '0',
            'url': url,
            'header': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            }
        }

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def localProxy(self, param):
        pass
