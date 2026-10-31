/* YouTube 縮圖 facade：先顯示 images/maxresdefault.jpg，點擊後才載入 iframe。
 *
 * 由 layouts/shortcodes/youtube.html 輸出 .yt-lite，extend_head.html 只在
 * 頁面用到 youtube shortcode 時載入本檔（defer）。
 *
 * 兩種失敗都會保留縮圖：
 *   1. navigator.onLine === false（裝置離線）
 *   2. iframe 8 秒內沒有 load（連不到 YouTube／被擋）
 * 樣式在 assets/css/extended/youtube-lite.css。
 */
(function () {
    "use strict";

    var TIMEOUT_MS = 8000;

    function showFallback(el) {
        el.classList.remove("is-loading");
        el.removeAttribute("aria-busy");
        el.setAttribute("data-offline", "1");
        var note = el.querySelector(".yt-lite__note");
        if (note) note.textContent = el.getAttribute("data-yt-offline") || "";
    }

    function loadPlayer(el) {
        if (el.classList.contains("is-loading") || el.classList.contains("is-playing")) return;

        el.removeAttribute("data-offline");

        if (navigator.onLine === false) {
            showFallback(el);
            return;
        }

        var src = el.getAttribute("data-yt-src");
        if (!src) return;

        var iframe = document.createElement("iframe");
        iframe.className = "yt-lite__iframe";
        iframe.src = src;
        iframe.title = el.getAttribute("aria-label") || "YouTube video";
        iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share");
        iframe.setAttribute("allowfullscreen", "");
        iframe.setAttribute("frameborder", "0");

        var settled = false;
        var timer = 0;

        function fail() {
            if (settled) return;
            settled = true;
            clearTimeout(timer);
            if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
            showFallback(el);
        }

        iframe.addEventListener("load", function () {
            if (settled) return;
            settled = true;
            clearTimeout(timer);
            el.classList.remove("is-loading");
            el.classList.add("is-playing");
            el.removeAttribute("data-offline");
            el.removeAttribute("aria-busy");
            el.removeAttribute("role");
            el.removeAttribute("tabindex");
            iframe.classList.add("is-ready");
            iframe.focus();
        });

        el.classList.add("is-loading");
        el.setAttribute("aria-busy", "true");
        el.appendChild(iframe);
        timer = setTimeout(fail, TIMEOUT_MS);
    }

    document.querySelectorAll(".yt-lite").forEach(function (el) {
        var img = el.querySelector(".yt-lite__thumb");
        if (img) {
            img.addEventListener("error", function () {
                if (img.getAttribute("data-fallback")) return;
                img.setAttribute("data-fallback", "1");
                img.src = img.src.replace(/maxresdefault/, "hqdefault");
            });
        }

        el.addEventListener("click", function () {
            loadPlayer(el);
        });

        el.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
                e.preventDefault();
                loadPlayer(el);
            }
        });
    });

    window.addEventListener("online", function () {
        document.querySelectorAll(".yt-lite[data-offline]").forEach(function (el) {
            el.removeAttribute("data-offline");
        });
    });
})();
