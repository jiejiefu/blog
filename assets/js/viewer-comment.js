(function () {
    'use strict';

    function readQuotes(root) {
        var node = root.querySelector('script[type="application/json"]');
        if (!node) return null;
        try {
            return JSON.parse(node.textContent || node.innerHTML);
        } catch (e) {
            return null;
        }
    }

    function setText(root, selector, value) {
        var el = root.querySelector(selector);
        if (el) el.textContent = value;
    }

    function currentQuote(root) {
        var el = root.querySelector('[data-vc-quote]');
        if (!el) return '';
        return (el.textContent || '').replace(/^[\u201C\u201D\s]+|[\u201C\u201D\s]+$/g, '');
    }

    function render(root, item) {
        setText(root, '[data-vc-handle]', '@' + item.handle);
        setText(root, '[data-vc-quote]', '\u201C' + item.text + '\u201D');
        setText(root, '[data-vc-credit]', '\u2014 ' + item.who + (item.episode ? ' \u00B7 ' + item.episode : ''));
    }

    function pick(list, current) {
        if (!list || !list.length) return null;
        if (list.length === 1) return list[0];
        var item;
        var guard = 0;
        do {
            item = list[Math.floor(Math.random() * list.length)];
            guard += 1;
        } while (item.text === current && guard < 12);
        return item;
    }

    function init(root) {
        var list = readQuotes(root);
        if (!list || !list.length) return;

        var initial = currentQuote(root);
        var item = pick(list, initial);
        if (item && item.text !== initial) render(root, item);

        // 初次自動抽換不應該被螢幕閱讀器朗讀；
        // 等這一輪結束後才掛上 aria-live，之後按鈕造成的變更才會播報。
        var quoteEl = root.querySelector('[data-vc-quote]');
        if (quoteEl) {
            window.setTimeout(function () {
                quoteEl.setAttribute('aria-live', 'polite');
            }, 0);
        }

        var button = root.querySelector('[data-vc-reroll]');
        if (!button) return;
        button.addEventListener('click', function () {
            var next = pick(list, currentQuote(root));
            if (next) render(root, next);
        });
    }

    function start() {
        var blocks = document.querySelectorAll('[data-viewer-comment]');
        for (var i = 0; i < blocks.length; i++) {
            init(blocks[i]);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
