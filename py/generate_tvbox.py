# -*- coding: utf-8 -*-
"""
TVBox JSON 生成器
将源文件夹中 81 个 Python Spider + 7 个 txt 直链文件
转换为 TVBox 标准 JSON 格式

TVBox JSON 标准格式:
{
  "name": "站点名",
  "url": "站点URL",
  "api": "api地址",
  "playUrl": "播放器URL前缀",
  "categories": ["分类1", "分类2", ...],
  "filters": {...}  // 可选
}
"""
import re, os, json, sys

PY = r'D:\Program Files\QClaw\v0.2.37.630\resources\python\python.exe'
SRC = r'C:\Users\Administrator\Desktop\源'
OUT = r'C:\Users\Administrator\Desktop\TVBox源'
TEMP = r'C:\Users\Administrator\Desktop\源\generate_tvbox.py'

# Ensure output dir
os.makedirs(OUT, exist_ok=True)

# ==================== 辅助函数 ====================
def read_file(fp):
    for enc in ('utf-8', 'gbk', 'utf-16', 'latin-1'):
        try:
            with open(fp, 'r', encoding=enc, errors='ignore') as f:
                return f.read()
        except:
            pass
    return ''

def extract_spider_name(content):
    """从 Spider 类提取站点名称"""
    # 优先找 getName 返回值
    m = re.search(r"def getName\(self\):\s*return\s*['\"]([^'\"]+)['\"]", content)
    if m:
        return m.group(1)
    # 找类名
    m = re.search(r'class\s+Spider\s*\([^)]+\)\s*:', content)
    if m:
        return content[max(0, m.start()-200):m.start()].split('\n')[-1].strip()
    return ''

def extract_home_content_classes(content):
    """从 homeContent 中提取分类列表"""
    classes = []
    # 找 homeContent 方法
    idx = content.find('def homeContent')
    if idx < 0:
        return []
    chunk = content[idx:idx+2000]
    # 匹配各种字典格式
    for m in re.finditer(r"['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]", chunk):
        name = m.group(2)
        tid = m.group(1)
        if name and tid and len(name) < 30 and len(tid) < 20:
            classes.append({'type_id': tid, 'type_name': name})
    # 去掉明显不是分类的
    filtered = [c for c in classes if c['type_name'] not in ('国产自拍','国产传媒','探花系列','最新','热门','推荐')]
    return filtered[:20]  # 最多20个分类

def extract_api_info(content, filename):
    """从 spider 内容提取 URL/API 信息"""
    info = {
        'name': extract_spider_name(content) or filename.replace('.py',''),
        'url': '',
        'api': '',
        'playUrl': '',
        'categories': [],
        'type': '3'  # 影视
    }
    
    # 找 HOST/RELEASE/BASE_URL 等常量
    for const in ['RELEASE', 'HOST', 'HOME', 'BASE_URL', 'SITE_URL']:
        m = re.search(r'%s\s*=\s*[\'"](https?://[^\'"]+)[\'"]' % const, content)
        if m and not info['url']:
            info['url'] = m.group(1)
    
    # 找 __init__ 中的 URL 设置
    init_idx = content.find('def __init__')
    if init_idx > 0:
        init_chunk = content[init_idx:init_idx+500]
        m = re.search(r'[\'"](https?://[^\'"]+)[\'"]', init_chunk)
        if m and not info['url']:
            info['url'] = m.group(1)
    
    if not info['url']:
        info['url'] = 'https://example.com'
    
    # 分类
    cats = extract_home_content_classes(content)
    if cats:
        info['categories'] = [c['type_name'] for c in cats]
    
    return info

# ==================== 处理 Spider 文件 ====================
def process_spider(fp, filename):
    content = read_file(fp)
    if not content or 'def playerContent' not in content:
        return None
    
    info = extract_api_info(content, filename)
    info['name'] = info['name'] or filename.replace('.py','')
    
    return info

# ==================== 处理 TXT 直链文件 ====================
def process_txt(fp, filename):
    """将 txt 直链文件转换为 TVBox JSON 格式（直播源格式）"""
    content = read_file(fp)
    if not content:
        return None
    
    lines = content.split('\n')
    groups = []
    current_group = None
    total_urls = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 解析 genre 行
        if '#genre' in line.lower() or line.startswith('#'):
            genre = line.lstrip('#').replace('#genre','').strip().rstrip(',').strip()
            if genre:
                if current_group:
                    groups.append(current_group)
                current_group = {'name': genre, 'urls': []}
        elif ',' in line:
            parts = line.split(',', 1)
            name = parts[0].strip()
            url = parts[1].strip()
            
            # 检查是否是有效 URL
            if url.startswith('http') or url.startswith('rtmp') or url.startswith('rtsp'):
                if not current_group:
                    current_group = {'name': '未分类', 'urls': []}
                current_group['urls'].append({'name': name, 'url': url})
                total_urls += 1
            elif name.startswith('http'):
                # 可能是 URL 在前
                pass
    
    if current_group:
        groups.append(current_group)
    
    if not groups or total_urls == 0:
        return None
    
    return {
        'name': filename.replace('.txt','').replace('.text',''),
        'type': '1',  # 直播
        'groups': groups,
        'raw_urls': total_urls
    }

# ==================== 主流程 ====================
print("=" * 60)
print("TVBox JSON 生成器")
print("=" * 60)

spider_results = []
txt_results = []
skipped = []

files = sorted(os.listdir(SRC))

for fn in files:
    if fn.endswith('.py'):
        fp = os.path.join(SRC, fn)
        result = process_spider(fp, fn)
        if result:
            spider_results.append(result)
            print("  [SPIDER] %s" % fn)
        else:
            skipped.append(fn)
    elif fn.endswith('.txt') or fn.endswith('.text'):
        fp = os.path.join(SRC, fn)
        result = process_txt(fp, fn)
        if result:
            txt_results.append(result)
            print("  [TXT]    %s (%d URLs, %d groups)" % (fn, result.get('raw_urls',0), len(result.get('groups',[]))))
        else:
            skipped.append(fn)

print()
print("Spider: %d, TXT: %d, Skipped: %d" % (len(spider_results), len(txt_results), len(skipped)))

# ==================== 生成输出文件 ====================

# 1. 完整合并 JSON（所有 spider + txt）
combined = {
    'spiders': spider_results,
    'live_sources': txt_results,
    'generated': 'TVBox JSON',
    'total_spiders': len(spider_results),
    'total_live': len(txt_results)
}

out_combined = os.path.join(OUT, 'combined.json')
with open(out_combined, 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)
print("\n合并文件: %s" % out_combined)

# 2. 逐个生成 spider JSON 文件
for info in spider_results:
    safe_name = re.sub(r'[<>:"/\\|?*\[\]（）()（）]', '_', info['name'])
    safe_name = safe_name.strip(' _')
    if not safe_name:
        safe_name = 'spider'
    fp_out = os.path.join(OUT, safe_name + '.json')
    
    # TVBox 标准 spider JSON 格式
    tvbox_spider = {
        'name': info['name'],
        'url': info['url'],
        'api': info['api'] or '',
        'playUrl': info['playUrl'] or '',
        'categories': info['categories'] if info['categories'] else ['电影', '电视剧', '综艺', '动漫'],
        'type': info.get('type', '3')
    }
    
    with open(fp_out, 'w', encoding='utf-8') as f:
        json.dump(tvbox_spider, f, ensure_ascii=False, indent=2)

print("Spider JSON 文件已生成到: %s" % OUT)

# 3. 生成 txt 文件的直播源 JSON
live_groups = {}
for info in txt_results:
    groups = info.get('groups', [])
    for g in groups:
        gname = g['name']
        if gname not in live_groups:
            live_groups[gname] = []
        live_groups[gname].extend(g['urls'])

# 生成每个 txt 的独立直播源 JSON
for info in txt_results:
    safe_name = re.sub(r'[<>:"/\\|?*\[\]（）()（）]', '_', info['name'])
    safe_name = safe_name.strip(' _')
    fp_out = os.path.join(OUT, safe_name + '_live.json')
    
    tvbox_live = {
        'name': info['name'],
        'type': '1',
        'urls': []
    }
    
    for g in info.get('groups', []):
        for u in g['urls']:
            tvbox_live['urls'].append({'name': '[%s] %s' % (g['name'], u['name']), 'url': u['url']})
    
    with open(fp_out, 'w', encoding='utf-8') as f:
        json.dump(tvbox_live, f, ensure_ascii=False, indent=2)

print("直播源 JSON 文件已生成到: %s" % OUT)

# 4. 生成全量直播源合并文件
all_live = []
for gname, urls in live_groups.items():
    seen = set()
    for u in urls:
        key = u['url']
        if key not in seen:
            seen.add(key)
            all_live.append({'name': '[%s] %s' % (gname, u['name']), 'url': u['url']})

live_combined = {
    'name': '全量直播源',
    'type': '1',
    'urls': all_live,
    'total': len(all_live),
    'groups': list(live_groups.keys())
}

out_live = os.path.join(OUT, 'all_live.json')
with open(out_live, 'w', encoding='utf-8') as f:
    json.dump(live_combined, f, ensure_ascii=False, indent=2)
print("全量直播源: %s (%d URLs)" % (out_live, len(all_live)))

# 5. 生成 TVBox 的 "影视Spider" 格式 JSON（完整可导入格式）
# 标准 TVBox spider JSON（免嗅探直接用）
spider_json_list = []
for info in spider_results:
    spider_json_list.append({
        'name': info['name'],
        'url': info['url'],
        'api': info['api'] or '',
        'playUrl': info['playUrl'] or '',
        'categories': info['categories'] if info['categories'] else ['电影', '电视剧', '综艺', '动漫']
    })

out_spider_list = os.path.join(OUT, 'spider_list.json')
with open(out_spider_list, 'w', encoding='utf-8') as f:
    json.dump(spider_json_list, f, ensure_ascii=False, indent=2)
print("Spider列表: %s (%d)" % (out_spider_list, len(spider_json_list)))

# 6. 生成说明文件
readme = """# TVBox 影视源

## 文件说明

### 合并文件
- `combined.json` - 全部影视Spider + 直播源合并（含元数据）
- `spider_list.json` - 影视Spider列表（TVBox直接导入）
- `all_live.json` - 全部直播源合并

### 影视Spider (共 %d 个)
每个文件是一个站点，TVBox 可直接导入 JSON 或填写 URL+api

### 直播源 (共 %d 个txt文件)
每个 `_live.json` 是独立的直播源 TVBox 格式
- `all_live.json` - 全量合并直播源 (%d 条URL)

## TVBox 导入方式

### 方式1: 配置文件中添加
在 TVBox 配置文件中加入:
```json
"spider": {
  "default": {
    "name": "影视Spider",
    "url": "file:///storage/emulated/0/Download/spider_list.json",
    "api": "",
    "type": "3"
  }
}
```

### 方式2: 直播源导入
将 `_live.json` 或 `all_live.json` 导入 TVBox 直播源

### 方式3: 手动添加站点
在 TVBox 中手动添加:
- 名称: 任意
- URL: 填入各 spider JSON 中的 url 字段值
- API: 填入各 spider JSON 中的 api 字段值

## 分类
%s

## 生成时间
%s
""" % (
    len(spider_results),
    len(txt_results),
    len(all_live),
    ', '.join(spider_results[0].get('categories', ['电影'])[:5]) if spider_results else '',
    '自动生成'
)

readme_path = os.path.join(OUT, 'README.md')
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme)

print()
print("=" * 60)
print("生成完成!")
print("输出目录: %s" % OUT)
print("  Spider: %d 个" % len(spider_results))
print("  直播源: %d 个 (%d 条URL)" % (len(txt_results), len(all_live)))
print("=" * 60)
