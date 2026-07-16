// 站点: 4KVM
// 版本: 1.0
// 兼容: 蜂蜜影视, 影视仓

var rule = {
    title: '4KVM影视',
    host: 'https://www.4kvm.top',
    url: '/filter?classify=fyclass&page=fypage',
    searchUrl: '/search?q=**&page=fypage',
    class_name: '电影&电视剧&动漫',
    class_url: '1&2&3',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.4kvm.top',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    },
    一级: 'div[data-vod-id];div[data-vod-id];h3.text-white&&Text;img&&data-src;.text-green-500,.text-yellow-400&&Text',
    二级: {
        title: 'h1.text-xl&&Text',
        img: 'img.w-full||img[src]&&src',
        desc: '.rounded-lg div.grid&&Text',
        content: '.rounded-lg div.grid&&Text',
        director: '导演\\s*([^主\\n]+)',
        actor: '主演\\s*([^剧\\n]+)',
        tabs: '[x-data*="episodeManager"] a[data-line]&&data-line',
        lists: '[x-data*="episodeManager"] a[data-episode]'
    },
    搜索: 'div[data-vod-id];div[data-vod-id];h3.text-white&&Text;img&&data-src;.text-green-500,.text-yellow-400&&Text'
};

// 首页分类 + 推荐
function home(filter) {
    var html = request(rule.host + '/');
    var classes = [
        { type_id: '1', type_name: '电影' },
        { type_id: '2', type_name: '电视剧' },
        { type_id: '3', type_name: '动漫' }
    ];
    
    var list = [];
    if (html) {
        var cards = pdfa(html, 'div[data-vod-id]');
        for (var i = 0; i < Math.min(cards.length, 20); i++) {
            var card = cards[i];
            var vod_id = getAttr(card, 'data-vod-id');
            if (!vod_id) {
                var a = pdfa(card, 'a.block[href^="/play/"]');
                if (a && a.length > 0) {
                    var href = getAttr(a[0], 'href');
                    vod_id = href.replace('/play/', '').trim();
                }
            }
            if (!vod_id) continue;
            
            var title = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
            if (!title) continue;
            
            var pic = pdfh(card, 'img&&data-src');
            if (pic && !pic.startsWith('data:')) {
                if (!pic.startsWith('http')) pic = 'https:' + pic;
            }
            
            var remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
            
            list.push({
                vod_id: vod_id,
                vod_name: title,
                vod_pic: pic,
                vod_remarks: remarks
            });
        }
    }
    
    return JSON.stringify({
        class: classes,
        list: list,
        filters: getFilters()
    });
}

// 首页推荐（简版）
function homeVod() {
    var result = JSON.parse(home(false));
    return JSON.stringify({ list: result.list || [] });
}

// 分类列表
function category(tid, pg, filter, extend) {
    var page = parseInt(pg) || 1;
    var url = rule.url.replace('fyclass', tid).replace('fypage', page);
    
    if (extend) {
        var params = [];
        for (var k in extend) {
            if (extend[k] && k !== 'classify') {
                params.push(k + '=' + encodeURIComponent(extend[k]));
            }
        }
        if (params.length > 0) {
            url += '&' + params.join('&');
        }
    }
    
    var html = request(url, { headers: rule.headers });
    var list = [];
    
    if (html) {
        var cards = pdfa(html, 'div[data-vod-id]');
        for (var i = 0; i < cards.length; i++) {
            var card = cards[i];
            var vod_id = getAttr(card, 'data-vod-id');
            if (!vod_id) {
                var a = pdfa(card, 'a.block[href^="/play/"]');
                if (a && a.length > 0) {
                    var href = getAttr(a[0], 'href');
                    vod_id = href.replace('/play/', '').trim();
                }
            }
            if (!vod_id) continue;
            
            var title = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
            if (!title) continue;
            
            var pic = pdfh(card, 'img&&data-src');
            if (pic && !pic.startsWith('data:')) {
                if (!pic.startsWith('http')) pic = 'https:' + pic;
            }
            
            var remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
            
            list.push({
                vod_id: vod_id,
                vod_name: title,
                vod_pic: pic,
                vod_remarks: remarks
            });
        }
    }
    
    // 计算总页数
    var pagecount = page;
    if (html) {
        var pageMatch = html.match(/共\s*(\d+)\s*页/);
        if (pageMatch) {
            pagecount = parseInt(pageMatch[1]);
        }
    }
    
    return JSON.stringify({
        list: list,
        page: page,
        pagecount: pagecount || 1,
        limit: 24,
        total: list.length * (pagecount || 1)
    });
}

// 详情页
function detail(vod_id) {
    var url = rule.host + '/play/' + vod_id;
    var html = request(url, { headers: rule.headers });
    
    if (!html) {
        return JSON.stringify({ list: [] });
    }
    
    var vod_name = pdfh(html, 'h1.text-xl&&Text') || pdfh(html, 'h1&&Text') || pdfh(html, 'h2&&Text') || vod_id;
    
    var vod_pic = pdfh(html, 'img.w-full&&src') || pdfh(html, 'img[src]&&src') || '';
    if (vod_pic && !vod_pic.startsWith('data:')) {
        if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
    }
    
    var infoText = pdfh(html, '.rounded-lg div.grid&&Text') || '';
    
    var vod_director = '';
    var vod_actor = '';
    var vod_content = '';
    
    if (infoText) {
        var dirMatch = infoText.match(/导演\s*([^主\n]+)/);
        if (dirMatch) vod_director = dirMatch[1].trim();
        
        var actMatch = infoText.match(/主演\s*([^剧\n]+)/);
        if (actMatch) vod_actor = actMatch[1].trim();
        
        var descMatch = infoText.match(/剧情简介\s*(.+)/s) || infoText.match(/简介\s*(.+)/s);
        if (descMatch) vod_content = descMatch[1].trim();
    }
    
    // 解析分集
    var play_from_list = [];
    var play_url_list = [];
    
    var episodeManager = pdfh(html, '[x-data*="episodeManager"]');
    if (episodeManager) {
        // 提取线路名称
        var lineNames = [];
        var nameMatches = episodeManager.match(/lineName\s*:\s*'([^']+)'/g);
        if (nameMatches) {
            for (var i = 0; i < nameMatches.length; i++) {
                var m = nameMatches[i].match(/'([^']+)'/);
                if (m) lineNames.push(m[1]);
            }
        }
        
        // 提取分集链接
        var episodeLinks = pdfa(html, '[x-data*="episodeManager"] a[data-episode]');
        var lines_eps = {};
        
        for (var i = 0; i < episodeLinks.length; i++) {
            var a = episodeLinks[i];
            var line = getAttr(a, 'data-line') || '1';
            var ep = getAttr(a, 'data-episode');
            var href = getAttr(a, 'href');
            
            if (!href || !ep) continue;
            var full_url = href.startsWith('http') ? href : rule.host + href;
            
            if (!lines_eps[line]) lines_eps[line] = [];
            lines_eps[line].push({ ep: parseInt(ep), url: full_url });
        }
        
        var lineKeys = Object.keys(lines_eps).sort(function(a, b) { return parseInt(a) - parseInt(b); });
        for (var i = 0; i < lineKeys.length; i++) {
            var key = lineKeys[i];
            var eps = lines_eps[key];
            eps.sort(function(a, b) { return a.ep - b.ep; });
            
            var lineName = '线路' + key;
            if (lineNames && lineNames.length > 0) {
                var idx = parseInt(key) - 1;
                if (idx >= 0 && idx < lineNames.length) lineName = lineNames[idx];
            }
            
            var epStrs = [];
            for (var j = 0; j < eps.length; j++) {
                epStrs.push('第' + eps[j].ep + '集$' + eps[j].url);
            }
            
            play_from_list.push(lineName);
            play_url_list.push(epStrs.join('#'));
        }
    }
    
    // 无分集，直接播放
    if (play_url_list.length === 0) {
        play_from_list.push('播放');
        play_url_list.push('播放$' + vod_id);
    }
    
    var vod_play_from = play_from_list.join('$$$');
    var vod_play_url = play_url_list.join('$$$');
    
    var result = [{
        vod_id: vod_id,
        vod_name: vod_name,
        vod_pic: vod_pic,
        vod_content: vod_content,
        vod_actor: vod_actor,
        vod_director: vod_director,
        vod_area: '',
        vod_year: '',
        vod_play_from: vod_play_from,
        vod_play_url: vod_play_url
    }];
    
    return JSON.stringify({ list: result });
}

// 搜索
function search(wd, quick, pg) {
    var page = parseInt(pg) || 1;
    var url = rule.searchUrl.replace('**', encodeURIComponent(wd)).replace('fypage', page);
    var html = request(url, { headers: rule.headers });
    var list = [];
    
    if (html) {
        var cards = pdfa(html, 'div[data-vod-id]');
        
        // 如果没有 data-vod-id，降级处理
        if (cards.length === 0) {
            var links = pdfa(html, 'a.block[href^="/play/"]');
            for (var i = 0; i < Math.min(links.length, 30); i++) {
                var a = links[i];
                var href = getAttr(a, 'href');
                var vod_id = href.replace('/play/', '').trim();
                if (!vod_id) continue;
                
                var title = pdfh(a, 'h3&&Text') || href;
                if (!title) continue;
                
                var pic = pdfh(a, 'img&&data-src') || '';
                if (pic && !pic.startsWith('data:')) {
                    if (!pic.startsWith('http')) pic = 'https:' + pic;
                }
                
                list.push({
                    vod_id: vod_id,
                    vod_name: title,
                    vod_pic: pic,
                    vod_remarks: ''
                });
            }
        } else {
            for (var i = 0; i < Math.min(cards.length, 30); i++) {
                var card = cards[i];
                var vod_id = getAttr(card, 'data-vod-id');
                if (!vod_id) {
                    var a = pdfa(card, 'a.block[href^="/play/"]');
                    if (a && a.length > 0) {
                        var href = getAttr(a[0], 'href');
                        vod_id = href.replace('/play/', '').trim();
                    }
                }
                if (!vod_id) continue;
                
                var title = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
                if (!title) continue;
                
                var pic = pdfh(card, 'img&&data-src');
                if (pic && !pic.startsWith('data:')) {
                    if (!pic.startsWith('http')) pic = 'https:' + pic;
                }
                
                var remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
                
                list.push({
                    vod_id: vod_id,
                    vod_name: title,
                    vod_pic: pic,
                    vod_remarks: remarks
                });
            }
        }
    }
    
    return JSON.stringify({
        list: list,
        page: page,
        pagecount: 1
    });
}

// 播放
function play(flag, id, flags) {
    var url = id.startsWith('http') ? id : rule.host + '/play/' + id;
    return JSON.stringify({
        parse: 1,
        url: url,
        header: rule.headers
    });
}

// ================= 辅助函数 =================

// 获取元素属性
function getAttr(elem, attr) {
    if (typeof elem === 'string') {
        var match = elem.match(new RegExp(attr + '=["\']([^"\']*)["\']'));
        return match ? match[1] : '';
    }
    // 在 drpy 中，元素是字符串，所以上面的逻辑已经处理
    return '';
}

// 获取筛选（简化版）
function getFilters() {
    var filters = {};
    // 简化处理，返回空筛选
    return filters;
}