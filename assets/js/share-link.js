/* 分享連結：複製 data-share-text（含標題、永久連結、出處）到剪貼簿 */
(function () {
    "use strict";

    function legacyCopy(text) {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.top = "-1000px";
        document.body.appendChild(ta);
        ta.select();
        var ok = false;
        try {
            ok = document.execCommand("copy");
        } catch (e) {
            ok = false;
        }
        document.body.removeChild(ta);
        return ok;
    }

    function writeToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        }
        return Promise.resolve(legacyCopy(text));
    }

    document.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-share-copy]");
        if (!btn) return;

        var box = btn.closest("[data-share-text]");
        if (!box) return;

        var status = box.querySelector(".share-box__status");
        var label = btn.dataset.label || btn.textContent;
        var done = btn.dataset.done || label;

        writeToClipboard(box.dataset.shareText).then(function (ok) {
            if (ok === false) return;
            btn.textContent = done;
            if (status) status.textContent = done;
            window.setTimeout(function () {
                btn.textContent = label;
                if (status) status.textContent = "";
            }, 2000);
        });
    });
})();
