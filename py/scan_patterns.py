import re, os

src = r'C:\Users\Administrator\Desktop\源'
files = os.listdir(src)
files.sort()

results = []
for fn in files:
    fp = os.path.join(src, fn)
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        try:
            with open(fp, 'r', encoding='gbk', errors='ignore') as f:
                content = f.read()
        except:
            results.append((fn, 'ERROR', '', 0))
            continue
    
    size = os.path.getsize(fp)
    name = fn.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    
    # Check file type
    if fn.endswith('.txt') or fn.endswith('.text'):
        results.append((fn, 'TEXT', 'direct_url_catalog', size))
    elif 'def playerContent' in content:
        # Find the playerContent method
        idx = content.find('def playerContent')
        chunk = content[idx:idx+500]
        
        # Extract the key patterns
        has_base64 = 'base64' in chunk.lower()
        has_b64d = 'b64d' in chunk.lower() or '_b64d' in chunk or 'b64decode' in chunk.lower()
        has_m3u8_direct = '.m3u8' in chunk
        has_proxy = 'proxy' in chunk.lower() or 'header' in chunk
        
        # Try to find return url
        m_url = re.search(r"['\"]url['\"]:\s*(['\"]([^'\"]+)['\"]|[\w.]+\(|result\[)", chunk)
        
        results.append((fn, 'SPIDER', 'playerContent', size))
    elif 'def ' in content and ('def homeContent' in content or 'def categoryContent' in content):
        results.append((fn, 'SPIDER', 'no_playerContent', size))
    elif 'def ' in content:
        results.append((fn, 'SPIDER', 'minimal', size))
    else:
        results.append((fn, 'OTHER', content[:100], size))

# Write results
with open(r'C:\Users\Administrator\Desktop\源\analysis_results.txt', 'w', encoding='utf-8') as f:
    for fn, ftype, detail, size in results:
        f.write(f'{ftype}\t{detail}\t{size}\t{fn}\n')

print('Done. Found:')
from collections import Counter
cnt = Counter(x[1] for x in results)
for k, v in cnt.items():
    print(f'  {k}: {v}')
