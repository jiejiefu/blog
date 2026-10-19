/* Engineering Console — genact-style activity generator (no dependencies).
   Reads its config from <script data-cfg> (data/home.yaml → shared.console).
   Stops itself when: reduced-motion, tab hidden, or console scrolled off-screen.

   ⚠️ 刻意寫成 ES5（var / function），與 assets/js/share-link.js 同一款。
      assets/js/mermaid-init.js 是 ESM，但那個必須是 module 才能 import
      importmap 裡的 mermaid；console 不需要 ESM，沒有理由升級語法。 */
(function () {
    'use strict';
    var root = document.querySelector('[data-console]');
    if (!root) return;

    var cfg;
    try {
        cfg = JSON.parse(root.querySelector('[data-cfg]').textContent);
    } catch (e) {
        return;
    }

    var log = root.querySelector('[data-log]');
    var clock = root.querySelector('[data-clock]');
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function pad(n) {
        return ('0' + n).slice(-2);
    }
    function now() {
        var d = new Date();
        return pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
    }
    function r(a, b) {
        return a + Math.random() * (b - a);
    }
    function ri(a, b) {
        return Math.floor(r(a, b + 1));
    }
    function pick(a) {
        return a[ri(0, a.length - 1)];
    }
    /* 線性插值百分位（與 numpy 預設的 method='linear' 一致）。
       只有帶 levels 的 metric 會用到，序列固定所以一輪算一次。 */
    function percentile(sorted, p) {
        var k = (sorted.length - 1) * p / 100;
        var f = Math.floor(k), c = Math.min(f + 1, sorted.length - 1);
        return sorted[f] + (sorted[c] - sorted[f]) * (k - f);
    }
    function hex(n) {
        var s = '';
        while (n--) s += ri(0, 15).toString(16);
        return s;
    }

    /* 範本裡的 {placeholder} 由這裡產生；未知的 placeholder 原樣保留。
       要新增 placeholder 就改 subs，data/home.yaml 那邊不用動。
       ⚠️ 值域不是裝飾：{f3} 是 0–0.12，拿它寫「score 超過 0.85」會永遠不成立；
          {pct} 是 1–99，拿它寫 psi=0.{pct} 會出現 0.99 這種不現實的漂移值。
          所以異常分數 / PSI / 緩衝量 / 結束碼各有一個專屬 placeholder。 */
    var subs = {
        ms: function () { return ri(2, 64); },
        pct: function () { return ri(1, 99); },
        f2: function () { return r(0, 1).toFixed(2); },
        f3: function () { return r(0, 0.12).toFixed(3); },
        /* 0.86 起跳：這串只用來描述「超過 0.85 門檻」，
           若允許 0.72 就會出現 score=0.823 exceeds threshold 0.85 這種自相矛盾的句子 */
        score: function () { return r(0.86, 0.99).toFixed(3); },
        psi: function () { return r(0.12, 0.41).toFixed(2); },
        buf: function () { return ri(1200, 4980); },
        code: function () { return pick([1, 2, 125, 126, 127, 134, 137, 139, 143]); },
        hex: function () { return hex(8); },
        n: function () { return ri(100, 9999); },
        h: function () { return ri(120, 2400); },
        node: function () { return 'edge-' + pad(ri(1, 12)); },
        temp: function () { return ri(38, 71); },
        khz: function () { return pick([12.8, 25.6, 51.2]); },
        ver: function () { return 'v' + ri(1, 3) + '.' + ri(0, 9) + '.' + ri(0, 20); }
    };
    function fill(t) {
        return t.replace(/\{(\w+)\}/g, function (m, k) {
            return subs[k] ? subs[k]() : m;
        });
    }

    /* ---------- 日誌 ---------- */
    var max = cfg.max || 14;

    /* 等級加權：先依 weights 抽等級，再從該等級的桶子裡抽一則。
       直接對整個 stream 均勻抽樣的話，新增的 err 訊息會把錯誤率拉高到 ~19%，
       console 看起來像壞掉。權重缺漏的等級直接不參與（總和自動重新歸一），
       沒有 weights 或 stream 全空時退回原本的均勻抽樣。 */
    var buckets = null;
    (function () {
        var w = cfg.weights;
        if (!w || !cfg.stream || !cfg.stream.length) return;
        var byLv = {};
        cfg.stream.forEach(function (s) {
            (byLv[s.lv] = byLv[s.lv] || []).push(s);
        });
        var levels = [], total = 0;
        Object.keys(byLv).forEach(function (lv) {
            var weight = w[lv] || 0;
            if (weight <= 0) return;
            total += weight;
            levels.push({ upto: total, items: byLv[lv] });
        });
        if (levels.length) buckets = { levels: levels, total: total };
    })();

    function pickEvent() {
        if (!buckets) return pick(cfg.stream);
        var x = Math.random() * buckets.total;
        for (var i = 0; i < buckets.levels.length; i++) {
            if (x < buckets.levels[i].upto) return pick(buckets.levels[i].items);
        }
        return pick(cfg.stream);
    }

    function addLine(lv, text) {
        var p = document.createElement('p');
        p.className = 'lab-log lab-log--' + lv;
        var t = document.createElement('span');
        t.className = 'lab-log__t';
        t.textContent = now();
        var l = document.createElement('span');
        l.className = 'lab-log__lv';
        l.textContent = lv.toUpperCase();
        var m = document.createElement('span');
        m.className = 'lab-log__msg';
        m.textContent = text;
        p.appendChild(t);
        p.appendChild(l);
        p.appendChild(m);
        log.appendChild(p);
        while (log.children.length > max) log.removeChild(log.firstChild);
        return m;
    }

    /* genact 招牌：進度條任務，跨多個 tick 逐步推進 */
    var running = [];

    function bar(pct) {
        var w = 18, f = Math.round(w * pct / 100);
        return '[' + new Array(f + 1).join('█') + new Array(w - f + 1).join('░') + '] ' +
            (pct < 10 ? '  ' : pct < 100 ? ' ' : '') + pct + '%';
    }

    function startTask() {
        var name = fill(pick(cfg.tasks));
        running.push({ name: name, pct: 0, el: addLine('info', name + ' ' + bar(0)) });
    }

    function advanceTasks() {
        for (var i = running.length - 1; i >= 0; i--) {
            var t = running[i];
            t.pct = Math.min(100, t.pct + ri(4, 22));
            /* 這行可能已經被捲出視窗（DOM 被移除），
               parentNode 為 null 就不能再寫 textContent，否則 throw */
            if (!t.el.parentNode) {
                running.splice(i, 1);
                continue;
            }
            t.el.textContent = t.name + ' ' + bar(t.pct);
            if (t.pct >= 100) {
                t.el.parentNode.className = 'lab-log lab-log--ok';
                t.el.parentNode.children[1].textContent = 'OK';
                running.splice(i, 1);
            }
        }
    }

    function tick() {
        advanceTasks();
        if (running.length < 2 && Math.random() < 0.22) {
            startTask();
            return;
        }
        var s = pickEvent();
        addLine(s.lv, fill(s.t));
    }

    /* ---------- 指標（數值 + 24 格長條） ----------
       資料流是「右進左出」：series 游標往前走一格，hist.push 新值、hist.shift 舊值，
       bars[23] 永遠是最新。因為每一格拿到的都是隔壁上一輪的值，
       24 根同時 transition: height 就會讓整條波形往左流動一格。

       ⚠️ 這裡刻意不是每 tick 重新抽隨機數。白雜訊的相鄰兩點互不相關，
          24 根一起亂變只會像雜訊，看不出時序。 */
    var metrics = [];
    [].forEach.call(root.querySelectorAll('[data-metric]'), function (el) {
        var def = null;
        cfg.metrics.forEach(function (m) {
            if (m.id === el.getAttribute('data-metric')) def = m;
        });
        if (!def) return;
        var bars = el.querySelectorAll('.lab-metric__bars i');
        var n = bars.length;
        var series = def.series;
        var hist = [];

        if (series && series.length) {
            /* 先把 24 格填成「以 series[0] 結尾」的前 24 步 —— 這樣最右邊那根
               剛好等於伺服器端渲染的初始值（partial 取 index .series 0），
               沒有 JS 與有 JS 的畫面一致。開場就是有起伏的波形，不會從平線長出來。 */
            var cur = 0;
            var N = series.length;
            for (var i = 0; i < n; i++) {
                hist.push(series[(cur - (n - 1) + i + N * 2) % N]);
            }
        } else {
            for (var j = 0; j < n; j++) hist.push(def.base);
        }

        /* 染色門檻：有 levels 且序列存在時，把 series 排序後各算一次百分位。
           序列固定、只算一次，不必進 tick；沒有 levels 就保持單色。 */
        var warnV = null, errV = null;
        if (def.levels && series && series.length) {
            var sorted = series.slice().sort(function (a, b) { return a - b; });
            warnV = percentile(sorted, def.levels.warn);
            errV = percentile(sorted, def.levels.err);
        }

        metrics.push({
            def: def,
            val: el.querySelector('[data-val]'),
            bars: bars,
            hist: hist,
            series: series,
            warnV: warnV,
            errV: errV,
            cur: series && series.length ? 0 : 0
        });
    });

    function height(v, d) {
        var lo, hi;
        if (d.domain && d.domain.length === 2) {
            lo = d.domain[0];
            hi = d.domain[1];
        } else {
            /* 沒有 domain 的舊資料：沿用原本的動態範圍 */
            lo = d.base - d.jitter * 1.5;
            hi = d.base + d.jitter * 3;
        }
        return Math.max(8, Math.min(100, ((v - lo) / (hi - lo)) * 100));
    }

    function paint(m) {
        for (var i = 0; i < m.bars.length; i++) {
            m.bars[i].style.height = height(m.hist[i], m.def) + '%';
        }
        /* 三色分級：只在帶 levels 的 metric 生效（其他 metric warnV/errV 為 null）。
           依「該格的值」上色，所以紅色長條往左移動時仍保持紅色，滑出視野才消失。 */
        if (m.warnV === null) return;
        for (var j = 0; j < m.bars.length; j++) {
            m.bars[j].className = tier(m.hist[j], m);
        }
        /* 讀數與最右邊那根同源，顏色跟著最新一筆走 */
        m.val.className = tier(m.hist[m.hist.length - 1], m);
    }

    function tier(v, m) {
        if (v >= m.errV) return 'is-err';
        if (v >= m.warnV) return 'is-warn';
        return '';
    }

    /* 立刻畫一次：CSS 的 nth-child 只是「沒有 JS 時的靜態輪廓」，
       若不先畫，第一輪 stepMetrics 會讓 24 根同時從假輪廓變形過去。 */
    metrics.forEach(paint);

    function stepMetrics() {
        metrics.forEach(function (m) {
            var d = m.def;
            var v;
            if (m.series && m.series.length) {
                m.cur = (m.cur + 1) % m.series.length;
                v = m.series[m.cur];
            } else {
                /* 沒有 series 時的退路：維持舊的白雜訊行為 */
                v = d.base + r(-d.jitter, d.jitter);
                if (Math.random() < 0.06) v += d.jitter * 2.2;
                v = Math.max(0, v);
            }
            m.hist.push(v);
            m.hist.shift();
            /* 讀數與最右邊那根同源，不再另外抽一個數字 */
            m.val.textContent = v.toFixed(d.digits || 0);
            paint(m);
        });
    }

    /* ---------- 排程（可見時才跑） ----------
       首頁不是 SPA，切走分頁就整份 stop()；捲出視窗靠 IntersectionObserver。 */
    var timer = null, mTimer = null, cTimer = null, onScreen = true;

    function loop() {
        timer = setTimeout(function () {
            tick();
            loop();
        }, ri(140, 560));
    }

    function start() {
        if (timer || reduce) return;
        loop();
        mTimer = setInterval(stepMetrics, 900);
        cTimer = setInterval(function () {
            clock.textContent = now();
        }, 1000);
        clock.textContent = now();
    }

    function stop() {
        clearTimeout(timer);
        clearInterval(mTimer);
        clearInterval(cTimer);
        timer = mTimer = cTimer = null;
    }

    function sync() {
        (onScreen && !document.hidden) ? start() : stop();
    }

    /* 使用者要求減少動態效果時：不排程，但時鐘仍顯示當下時間。
       沒有 JS 時時鐘顯示的是伺服器端渲染的建置時間，不是壞掉。 */
    if (reduce) {
        clock.textContent = now();
        return;
    }

    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
            onScreen = es[0].isIntersecting;
            sync();
        }).observe(root);
    }
    document.addEventListener('visibilitychange', sync);
    sync();
})();