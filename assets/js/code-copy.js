/* 程式碼區塊複製按鈕（GitHub 風格，右上角）
 *
 * 由 layouts/partials/extend_head.html 在 .IsPage 載入（defer）。
 * 結構：
 *   <div class="highlight"><pre class="chroma"><code>…</code></pre></div>
 * 按鈕插進 .highlight（position: relative），沒有 .highlight 時插進 <pre>。
 * 樣式在 assets/css/extended/code-copy.css。
 *
 * ⚠️ 不要同時開 config.yaml 的 ShowCodeCopyButtons，PaperMod 內建的腳本
 *    會再插一顆文字按鈕（.copy-code），兩顆會疊在一起。
 */
(function () {
    "use strict";

    var labels = window.codeCopyLabels || { copy: "Copy code", copied: "Copied!" };
    var ICON_COPY =
        '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
        '<path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"/>' +
        '<path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"/>' +
        "</svg>";
    var ICON_CHECK =
        '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
        '<path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/>' +
        "</svg>";

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

    function setState(btn, copied) {
        btn.innerHTML = copied ? ICON_CHECK : ICON_COPY;
        btn.classList.toggle("is-copied", copied);
        var label = copied ? labels.copied : labels.copy;
        btn.setAttribute("aria-label", label);
        btn.title = label;
    }

    document.querySelectorAll(".post-content pre > code").forEach(function (code) {
        var pre = code.parentElement;
        var host = pre.closest(".highlight") || pre;
        if (host.querySelector(":scope > .code-copy")) return;

        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "code-copy";
        btn.innerHTML = ICON_COPY;
        btn.setAttribute("aria-label", labels.copy);
        btn.title = labels.copy;

        var timer = 0;
        btn.addEventListener("click", function () {
            writeToClipboard(code.textContent).then(function (ok) {
                if (ok === false) return;
                setState(btn, true);
                clearTimeout(timer);
                timer = setTimeout(function () {
                    setState(btn, false);
                }, 2000);
            });
        });

        host.appendChild(btn);
    });
})();
