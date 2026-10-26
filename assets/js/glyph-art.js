/* 首頁的兔子：把一張圖印成文字。
   ==========================================================================
   移植自 Hallmark "Terminal" 主題 demo（burrow）的 page.js，只留畫圖那一段。
   網格資料在 assets/js/glyph-art-data.js（window.ART），文字區塊的無 JS 版本在
   assets/glyph-art/hare.txt。

   與原版的差異（視覺結果不變）：
   1. 色票從 box 讀，不是 documentElement —— 8 階色是 scope 在 .lab-glyph 上的，
      不是全站變數。
   2. 已落定的格子按亮度分 8 桶，每幀只切 8 次字型，不是每次亮度變了就切。
   3. 只在 (hover:hover) and (pointer:fine) 的裝置接滑鼠熱點（手機拖曳會誤觸）。
   4. 分頁隱藏時取消 raf，回到前景再續。
   5. 只在進入視窗後才開始（hero 在首屏，所以通常立刻觸發）。

   ⚠️ 字型一定要等 document.fonts.load 完成才開始：用替代字型量到的字寬會讓
      整張圖的字重疊錯位。 */
(() => {
    const DATA = window.ART;
    if (!DATA) return;

    const DOT = `export EDITOR=nvim
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
alias gs='git status -sb' ll='ls -lah' v=nvim
setopt hist_ignore_dups share_history
bindkey -e
[user] name = you email = you@host
[pull] rebase = true
[init] defaultBranch = main
vim.opt.number = true vim.opt.relativenumber = true
vim.opt.expandtab = true vim.opt.shiftwidth = 2
set -g mouse on set -g base-index 1
Host pi HostName pi.local User pi
Host desk HostName desk.lan ForwardAgent yes
`.replace(/\s+/g, '');
    const NOISE = '!#$%&*+-./:;<=>?@[]^_{|}~0123456789abcdefghijklmnopqrstuvwxyz';
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

    const art = (box, H) => {
        const cv = box.querySelector('canvas');
        if (!cv) return;
        const ctx = cv.getContext('2d');
        const cs = getComputedStyle(box);
        const FALLBACK = ['#1d2a22', '#2d3f33', '#3f5a46', '#547659', '#6c946e', '#86b385', '#a3d2a0', '#c9f5c3'];
        const ramp = Array.from({ length: 8 }, (_, i) => cs.getPropertyValue(`--glyph-${i}`).trim() || FALLBACK[i]);
        const hot = cs.getPropertyValue('--glyph-hot').trim() || ramp[7];

        const cells = [];
        let k = 0;
        H.lv.forEach((row, y) => [...row].forEach((c, x) => {
            const v = +c;
            if (v) cells.push({ x, y, v, ch: DOT[k++ % DOT.length], at: 0, heat: 0 });
        }));
        const buckets = Array.from({ length: 9 }, () => []);
        cells.forEach((c) => buckets[c.v].push(c));
        const grid = new Map(cells.map((c) => [c.y * H.cols + c.x, c]));

        let cw = 0, ch = 0, ox = 0, oy = 0, fs = 0, w = 0, h = 0, t0 = 0, raf = 0, live = false;

        const size = () => {
            const r = box.getBoundingClientRect();
            if (!r.width || !r.height) return;
            const dpr = Math.min(devicePixelRatio || 1, 2);
            cw = Math.min(r.width / H.cols, r.height / (H.rows * H.ratio));
            ch = cw * H.ratio;
            fs = cw * 1.62;
            w = r.width; h = r.height;
            ox = r.width - cw * H.cols;
            oy = r.height - ch * H.rows;
            cv.width = Math.round(r.width * dpr);
            cv.height = Math.round(r.height * dpr);
            cv.style.width = r.width + 'px';
            cv.style.height = r.height + 'px';
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
        };

        /* 暗格字級只給 62%：這是浮雕感的來源，不是透明度。 */
        const setFont = (v) => {
            const s = (fw(v) * fs).toFixed(2);
            ctx.font = `${v > 6 ? 700 : 500} ${s}px "Martian Mono", monospace`;
        };
        const fw = (v) => 0.62 + 0.38 * Math.min(1, v / 6);

        const draw = (now) => {
            raf = 0;
            const t = now - t0;
            let busy = false;
            ctx.clearRect(0, 0, w, h);

            /* 1. 已落定、沒被加熱的格子：按亮度分桶，字型只切 8 次。 */
            for (let v = 1; v <= 8; v++) {
                const list = buckets[v];
                if (!list.length) continue;
                setFont(v);
                ctx.fillStyle = ramp[v - 1];
                for (const c of list) {
                    if (t < c.at + 260 || c.heat > 0.04) continue;
                    c.heat = 0;
                    ctx.fillText(c.ch, ox + c.x * cw + cw / 2, oy + c.y * ch + ch / 2);
                }
            }

            /* 2. 還沒到、正在落定、正在退熱的格子：逐格畫。 */
            for (const c of cells) {
                const px = ox + c.x * cw + cw / 2, py = oy + c.y * ch + ch / 2;
                if (t < c.at) { busy = true; continue; }
                if (t < c.at + 260) {
                    busy = true;
                    setFont(8);
                    ctx.fillStyle = ramp[Math.min(7, c.v + 1)];
                    ctx.fillText(NOISE[(Math.random() * NOISE.length) | 0], px, py);
                    continue;
                }
                if (c.heat > 0.04) {
                    busy = true;
                    setFont(8);
                    ctx.fillStyle = c.heat > 0.5 ? hot : ramp[Math.min(7, c.v + 2)];
                    ctx.fillText(c.heat > 0.25 ? NOISE[(Math.random() * NOISE.length) | 0] : c.ch, px, py);
                    c.heat *= 0.9;
                }
            }
            if (busy) raf = requestAnimationFrame(draw);
        };

        const kick = () => { if (live && !raf) raf = requestAnimationFrame(draw); };

        const start = () => {
            live = true;
            box.classList.add('is-live');
            size();
            /* 進場：逐列由上而下，帶一點抖動，約 1.5 秒。 */
            cells.forEach((c) => { c.at = still ? -1e6 : c.y * (1100 / H.rows) + Math.random() * 420; });
            t0 = performance.now();
            kick();
        };

        if ('ResizeObserver' in window) {
            new ResizeObserver(() => { if (live) { size(); kick(); } }).observe(box);
        } else {
            addEventListener('resize', () => { if (live) { size(); kick(); } });
        }

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                if (raf) cancelAnimationFrame(raf), raf = 0;
            } else if (live) kick();
        });

        if (!still && fine) {
            box.addEventListener('pointermove', (e) => {
                const r = cv.getBoundingClientRect();
                const gx = (e.clientX - r.left - ox) / cw, gy = (e.clientY - r.top - oy) / ch;
                const R = 7;
                for (let y = Math.floor(gy - R / 2); y <= gy + R / 2; y++) {
                    for (let x = Math.floor(gx - R); x <= gx + R; x++) {
                        const c = grid.get(y * H.cols + x);
                        if (!c) continue;
                        const d = Math.hypot((x - gx) / R, (y - gy) / (R / 2));
                        if (d < 1) c.heat = Math.max(c.heat, 1 - d);
                    }
                }
                kick();
            });
        }

        return start;
    };

    const boxes = document.querySelectorAll('[data-art]');
    if (!boxes.length) return;

    const fontReady = document.fonts
        ? document.fonts.load('500 12px "Martian Mono"')
        : Promise.resolve();

    boxes.forEach((box) => {
        const data = DATA[box.dataset.art];
        if (!data) return;
        const start = art(box, data);
        if (!start) return;
        const go = () => fontReady.then(start, start);
        if (still || !('IntersectionObserver' in window)) { go(); return; }
        new IntersectionObserver((es, o) => {
            if (es[0].isIntersecting) { o.disconnect(); go(); }
        }, { threshold: 0.2 }).observe(box);
    });
})();
