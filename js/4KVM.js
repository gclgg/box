// 4KVM.js - 符合 drpy 规范

var rule = {
    title: '4KVM影视',
    host: 'https://www.4kvm.top',
    url: '/filter?classify=fyclass&page=fypage',
    searchUrl: '/search?q=**&page=fypage',
    class_name: '电影&电视剧&动漫',
    class_url: '1&2&3',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    timeout: 15,
    
    // 一级解析规则：列表页
    一级: 'div[data-vod-id];div[data-vod-id];h3.text-white&&Text;img&&data-src;.text-green-500,.text-yellow-400&&Text',
    
    // 二级解析规则：详情页
    二级: {
        title: 'h1.text-xl&&Text||h1&&Text',
        img: 'img.w-full&&src||img[src]&&src',
        desc: '.rounded-lg div.grid&&Text',
        content: '.rounded-lg div.grid&&Text',
        tabs: '[x-data*="episodeManager"] a[data-line]&&data-line',
        lists: '[x-data*="episodeManager"] a[data-episode]'
    },
    
    // 搜索解析规则
    搜索: 'div[data-vod-id];div[data-vod-id];h3.text-white&&Text;img&&data-src;.text-green-500,.text-yellow-400&&Text'
};

// 首页分类
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
            // 直接使用 pdfh 提取
            var vod_id = pdfh(card, 'a.block[href^="/play/"]&&href');
            if (vod_id) {
                vod_id = vod_id.replace('/play/', '').trim();
            } else {
                vod_id = pdfh(card, '&&data-vod-id');
            }
            if (!vod_id) continue;
            
            var vod_name = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
            if (!vod_name) continue;
            
            var vod_pic = pdfh(card, 'img&&data-src') || pdfh(card, 'img&&src');
            if (vod_pic && !vod_pic.startsWith('data:') && vod_pic) {
                if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
            }
            
            var vod_remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
            
            list.push({
                vod_id: vod_id,
                vod_name: vod_name,
                vod_pic: vod_pic,
                vod_remarks: vod_remarks
            });
        }
    }
    
    return JSON.stringify({
        class: classes,
        list: list
    });
}

// 首页推荐
function homeVod() {
    var html = request(rule.host + '/');
    var list = [];
    if (html) {
        var cards = pdfa(html, 'div[data-vod-id]');
        for (var i = 0; i < Math.min(cards.length, 20); i++) {
            var card = cards[i];
            var vod_id = pdfh(card, 'a.block[href^="/play/"]&&href');
            if (vod_id) {
                vod_id = vod_id.replace('/play/', '').trim();
            } else {
                vod_id = pdfh(card, '&&data-vod-id');
            }
            if (!vod_id) continue;
            
            var vod_name = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
            if (!vod_name) continue;
            
            var vod_pic = pdfh(card, 'img&&data-src') || pdfh(card, 'img&&src');
            if (vod_pic && !vod_pic.startsWith('data:') && vod_pic) {
                if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
            }
            
            var vod_remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
            
            list.push({
                vod_id: vod_id,
                vod_name: vod_name,
                vod_pic: vod_pic,
                vod_remarks: vod_remarks
            });
        }
    }
    return JSON.stringify({ list: list });
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
            var vod_id = pdfh(card, 'a.block[href^="/play/"]&&href');
            if (vod_id) {
                vod_id = vod_id.replace('/play/', '').trim();
            } else {
                vod_id = pdfh(card, '&&data-vod-id');
            }
            if (!vod_id) continue;
            
            var vod_name = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
            if (!vod_name) continue;
            
            var vod_pic = pdfh(card, 'img&&data-src') || pdfh(card, 'img&&src');
            if (vod_pic && !vod_pic.startsWith('data:') && vod_pic) {
                if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
            }
            
            var vod_remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
            
            list.push({
                vod_id: vod_id,
                vod_name: vod_name,
                vod_pic: vod_pic,
                vod_remarks: vod_remarks
            });
        }
    }
    
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
    if (vod_pic && !vod_pic.startsWith('data:') && vod_pic) {
        if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
    }
    
    // 提取信息
    var vod_director = '';
    var vod_actor = '';
    var vod_content = '';
    
    var infoText = pdfh(html, '.rounded-lg div.grid&&Text') || '';
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
    
    // 提取线路和分集
    var episodeLinks = pdfa(html, '[x-data*="episodeManager"] a[data-episode]');
    if (episodeLinks && episodeLinks.length > 0) {
        // 按线路分组
        var linesEps = {};
        for (var i = 0; i < episodeLinks.length; i++) {
            var link = episodeLinks[i];
            var line = pdfh(link, '&&data-line') || '1';
            var ep = pdfh(link, '&&data-episode');
            var href = pdfh(link, '&&href');
            if (!href || !ep) continue;
            var fullUrl = href.startsWith('http') ? href : rule.host + href;
            if (!linesEps[line]) linesEps[line] = [];
            linesEps[line].push({ ep: parseInt(ep), url: fullUrl });
        }
        
        var lineKeys = Object.keys(linesEps).sort(function(a, b) { return parseInt(a) - parseInt(b); });
        for (var i = 0; i < lineKeys.length; i++) {
            var key = lineKeys[i];
            var eps = linesEps[key];
            eps.sort(function(a, b) { return a.ep - b.ep; });
            
            var lineName = '线路' + key;
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
    
    var result = [{
        vod_id: vod_id,
        vod_name: vod_name,
        vod_pic: vod_pic,
        vod_content: vod_content,
        vod_actor: vod_actor,
        vod_director: vod_director,
        vod_area: '',
        vod_year: '',
        vod_play_from: play_from_list.join('$$$'),
        vod_play_url: play_url_list.join('$$$')
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
        if (cards && cards.length > 0) {
            for (var i = 0; i < Math.min(cards.length, 30); i++) {
                var card = cards[i];
                var vod_id = pdfh(card, 'a.block[href^="/play/"]&&href');
                if (vod_id) {
                    vod_id = vod_id.replace('/play/', '').trim();
                } else {
                    vod_id = pdfh(card, '&&data-vod-id');
                }
                if (!vod_id) continue;
                
                var vod_name = pdfh(card, 'h3.text-white&&Text') || pdfh(card, 'h3&&Text');
                if (!vod_name) continue;
                
                var vod_pic = pdfh(card, 'img&&data-src') || pdfh(card, 'img&&src');
                if (vod_pic && !vod_pic.startsWith('data:') && vod_pic) {
                    if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
                }
                
                var vod_remarks = pdfh(card, '.text-green-500&&Text') || pdfh(card, '.text-yellow-400&&Text') || '';
                
                list.push({
                    vod_id: vod_id,
                    vod_name: vod_name,
                    vod_pic: vod_pic,
                    vod_remarks: vod_remarks
                });
            }
        } else {
            // 降级处理
            var links = pdfa(html, 'a.block[href^="/play/"]');
            for (var i = 0; i < Math.min(links.length, 30); i++) {
                var a = links[i];
                var href = pdfh(a, '&&href');
                var vod_id = href.replace('/play/', '').trim();
                if (!vod_id) continue;
                var vod_name = pdfh(a, 'h3&&Text') || href;
                var vod_pic = pdfh(a, 'img&&data-src') || pdfh(a, 'img&&src') || '';
                if (vod_pic && !vod_pic.startsWith('data:') && vod_pic) {
                    if (!vod_pic.startsWith('http')) vod_pic = 'https:' + vod_pic;
                }
                list.push({
                    vod_id: vod_id,
                    vod_name: vod_name,
                    vod_pic: vod_pic,
                    vod_remarks: ''
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