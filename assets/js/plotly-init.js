/* Plotly 互動圖表初始化（無相依，ES5）。

   為什麼不在 <head> 直接載 Plotly，而是這裡才動態注入：
   Full bundle 是 4.83 MB min / 1.48 MB gzip，Basic 是 1.20 MB min / 398 KB gzip。
   由 JS 依 data-plotly-bundle 決定要載哪一個，好處是
     1. 模板不用解析 .RawContent 猜 bundle；
     2. 同一頁只要有一張 full，全頁載一次 full（full 是 basic 的超集）；
     3. 非圖表頁面連這支 init 都不會被 extend_head.html 載入。

   ⚠️ 刻意寫成 ES5（var / function），與 assets/js/share-link.js、lab-console.js 同一款。
      assets/js/mermaid-init.js 是 ESM，但那是因為它必須 import importmap 裡的 mermaid。

   ⚠️ CDN 版本與 SRI 一起釘死。升版時兩個都要換，並重算 SRI：
      curl -s <url> | openssl dgst -sha384 -binary | openssl base64 -A */
(function () {
    'use strict';

    var CDN = 'https://cdn.jsdelivr.net/npm/';
    var BUNDLES = {
        basic: {
            file: 'plotly.js-basic-dist-min@4.1.2/plotly-basic.min.js',
            integrity: 'sha384-CQVnjjRLr7qiE0NRUOMECQiOsJiFOrqPu+WrTttl7hUk5w+7FaiJA+y3SVfjpksc'
        },
        full: {
            file: 'plotly.js-dist-min@4.1.2/plotly.min.js',
            integrity: 'sha384-hHv6D3tTUUBpp4tVv6t2Dc3oGuRhphmWOTKUR8jWyN0Pnon1g3iebKCNDNmKmxo8'
        }
    };

    var scripts = document.querySelectorAll('.plotly-chart__spec');
    if (!scripts.length) return;

    var charts = [];
    var needFull = false;
    var i;

    for (i = 0; i < scripts.length; i++) {
        var script = scripts[i];
        var figure = script.parentNode;
        var el = figure ? figure.querySelector('.plotly-chart') : null;
        if (!el) continue;

        var spec;
        try {
            spec = JSON.parse(script.textContent);
        } catch (e) {
            fail(el, '圖表設定 JSON 解析失敗。');
            continue;
        }

        var bundle = el.getAttribute('data-plotly-bundle') || 'basic';
        if (bundle === 'full') needFull = true;
        charts.push({ el: el, spec: spec || {}, rendered: false });
    }

    if (!charts.length) return;

    var themeQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

    function isDark() {
        var attr = document.documentElement.getAttribute('data-theme');
        if (attr === 'auto' && themeQuery) return themeQuery.matches;
        return attr === 'dark';
    }

    function cssVar(name, fallback) {
        var v = getComputedStyle(document.documentElement).getPropertyValue(name);
        v = (v || '').trim();
        return v || fallback;
    }

    function themeBase() {
        var fg = cssVar('--primary', '#111');
        var grid = isDark() ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.14)';
        return {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: fg },
            modebar: { bgcolor: 'rgba(0,0,0,0)', color: fg, activecolor: fg },
            xaxis: { gridcolor: grid, zerolinecolor: grid, linecolor: grid },
            yaxis: { gridcolor: grid, zerolinecolor: grid, linecolor: grid }
        };
    }

    /* 使用者的 layout 優先；主題預設只補沒被指定的鍵。 */
    function mergeLayout(user) {
        var base = themeBase();
        var out = {};
        var k;
        for (k in user) {
            if (Object.prototype.hasOwnProperty.call(user, k)) out[k] = user[k];
        }
        if (!out.paper_bgcolor) out.paper_bgcolor = base.paper_bgcolor;
        if (!out.plot_bgcolor) out.plot_bgcolor = base.plot_bgcolor;
        out.font = shallow(base.font, user.font);
        out.modebar = shallow(base.modebar, user.modebar);
        out.xaxis = shallow(base.xaxis, user.xaxis);
        out.yaxis = shallow(base.yaxis, user.yaxis);
        return out;
    }

    function shallow(base, extra) {
        var out = {};
        var k;
        for (k in base) if (Object.prototype.hasOwnProperty.call(base, k)) out[k] = base[k];
        for (k in extra) if (Object.prototype.hasOwnProperty.call(extra, k)) out[k] = extra[k];
        return out;
    }

    function configFor(user) {
        var out = { responsive: true, displaylogo: false };
        var k;
        for (k in user) if (Object.prototype.hasOwnProperty.call(user, k)) out[k] = user[k];
        return out;
    }

    function fail(el, message) {
        el.className = 'plotly-chart plotly-chart__error';
        el.textContent = message;
    }

    function failAll(message) {
        for (var n = 0; n < charts.length; n++) fail(charts[n].el, message);
    }

    /* 用參數收住 chart，避免 var + 非同步 callback 的閉包取到最後一張圖。 */
    function renderOne(chart) {
        var data = chart.spec.data || [];
        var layout = mergeLayout(chart.spec.layout || {});
        var config = configFor(chart.spec.config);

        /* Basic bundle 遇到不支援的 trace 型別會 throw，
           在 onPlotError 裡翻成「請改用 bundle="full"」，
           而不是把 Plotly 的內部訊息直接丟給讀者。 */
        try {
            var p = window.Plotly.newPlot(chart.el, data, layout, config);
            if (p && p.then) {
                p.then(function () { chart.rendered = true; }, onPlotError(chart));
            } else {
                chart.rendered = true;
            }
        } catch (e) {
            onPlotError(chart)(e);
        }
    }

    function renderAll() {
        for (var n = 0; n < charts.length; n++) renderOne(charts[n]);
    }

    function onPlotError(chart) {
        return function (e) {
            var msg = (e && e.message) || '';
            if (/trace type|is not a valid|not found/i.test(msg)) {
                fail(chart.el, '此圖表需要 bundle="full"（目前載入的是 Basic）。');
            } else {
                fail(chart.el, '圖表渲染失敗。');
            }
        };
    }

    function applyTheme() {
        var fg = cssVar('--primary', '#111');
        var grid = isDark() ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.14)';
        for (var n = 0; n < charts.length; n++) {
            var chart = charts[n];
            if (!chart.rendered || !chart.el.layout) continue;

            var update = { font: { color: fg } };
            if (chart.el.layout.title) update['title.font.color'] = fg;

            var keys = Object.keys(chart.el.layout);
            for (var a = 0; a < keys.length; a++) {
                if (/^[xy]axis\d*$/.test(keys[a])) {
                    update[keys[a] + '.gridcolor'] = grid;
                    update[keys[a] + '.zerolinecolor'] = grid;
                    update[keys[a] + '.linecolor'] = grid;
                }
            }
            try {
                window.Plotly.relayout(chart.el, update);
            } catch (e) {
                /* 換色失敗不影響閱讀，不往上拋。 */
            }
        }
    }

    function watchTheme() {
        if (window.MutationObserver) {
            new MutationObserver(applyTheme).observe(document.documentElement, {
                attributes: true,
                attributeFilter: ['data-theme']
            });
        }
        if (themeQuery) {
            var handler = function () { applyTheme(); };
            if (themeQuery.addEventListener) themeQuery.addEventListener('change', handler);
            else if (themeQuery.addListener) themeQuery.addListener(handler);
        }
    }

    function inject(name) {
        var bundle = BUNDLES[name];
        var s = document.createElement('script');
        s.src = CDN + bundle.file;
        s.integrity = bundle.integrity;
        s.crossOrigin = 'anonymous';
        s.async = true;
        s.onload = function () {
            if (window.Plotly) renderAll();
            else failAll('圖表載入失敗。');
        };
        s.onerror = function () {
            failAll('圖表載入失敗（無法連線至 CDN）。');
        };
        document.head.appendChild(s);
    }

    function start() {
        if (window.Plotly) {
            renderAll();
            return;
        }
        inject(needFull ? 'full' : 'basic');
    }

    watchTheme();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
