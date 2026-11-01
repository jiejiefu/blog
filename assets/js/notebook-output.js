/* Notebook 輸出操作：每顆 code cell 的三點選單，以及圖片上的複製／儲存。
 *
 * 由 layouts/partials/extend_head.html 在含 notebook shortcode 的頁面載入。
 * 文字輸出用 Clipboard API；HTML table 轉 TSV；圖片先轉 PNG 再寫入剪貼簿，
 * 瀏覽器不支援圖片剪貼簿時退回下載。
 */
(function () {
    "use strict";

    var labels = window.notebookOutputLabels || {
        copied: "Copied",
        copyFailed: "Copy failed",
        downloaded: "Downloaded"
    };

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

    function writeText(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text).then(function () {
                return true;
            }).catch(function () {
                return legacyCopy(text);
            });
        }
        return Promise.resolve(legacyCopy(text));
    }

    function tableToTSV(table) {
        var rows = [];
        Array.prototype.forEach.call(table.rows, function (row) {
            var cells = [];
            Array.prototype.forEach.call(row.cells, function (cell) {
                var value = cell.innerText || cell.textContent || "";
                cells.push(value.replace(/\r?\n/g, " ").trim());
            });
            rows.push(cells.join("\t"));
        });
        return rows.join("\n");
    }

    function outputText(host) {
        var parts = [];
        Array.prototype.forEach.call(host.querySelectorAll(".jp-output"), function (output) {
            var type = output.getAttribute("data-jp-output-type");
            if (type === "image") return;

            if (type === "html") {
                var table = output.querySelector(".jp-html-table table");
                if (table) {
                    parts.push(tableToTSV(table));
                    return;
                }
            }

            var text = output.querySelector(".jp-output-text");
            if (text) {
                parts.push((text.textContent || "").replace(/\s+$/, ""));
            }
        });
        return parts.filter(function (part) {
            return part.length > 0;
        }).join("\n");
    }

    function imagesIn(host) {
        return Array.prototype.slice.call(
            host.querySelectorAll(".jp-output-image img")
        );
    }

    function blobToPng(blob) {
        if (blob.type === "image/png") return Promise.resolve(blob);

        return new Promise(function (resolve, reject) {
            var image = new Image();
            var url = URL.createObjectURL(blob);
            image.onload = function () {
                var canvas = document.createElement("canvas");
                canvas.width = image.naturalWidth;
                canvas.height = image.naturalHeight;
                canvas.getContext("2d").drawImage(image, 0, 0);
                URL.revokeObjectURL(url);
                canvas.toBlob(function (png) {
                    if (png) resolve(png);
                    else reject(new Error("PNG conversion failed"));
                }, "image/png");
            };
            image.onerror = function () {
                URL.revokeObjectURL(url);
                reject(new Error("Image load failed"));
            };
            image.src = url;
        });
    }

    function withTimeout(promise, ms) {
        return new Promise(function (resolve, reject) {
            var timer = window.setTimeout(function () {
                reject(new Error("Operation timed out"));
            }, ms);
            promise.then(function (value) {
                window.clearTimeout(timer);
                resolve(value);
            }, function (error) {
                window.clearTimeout(timer);
                reject(error);
            });
        });
    }

    function copyImage(img) {
        if (!navigator.clipboard || !window.ClipboardItem || !window.isSecureContext) {
            return Promise.reject(new Error("Image clipboard unavailable"));
        }

        return fetch(img.currentSrc || img.src, { credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) throw new Error("Image fetch failed");
                return response.blob();
            })
            .then(blobToPng)
            .then(function (png) {
                return navigator.clipboard.write([
                    new ClipboardItem({ "image/png": png })
                ]);
            });
    }

    function downloadImage(img) {
        var url = img.currentSrc || img.src;
        var name = url.split("/").pop().split("?")[0] || "notebook-output.webp";
        try {
            name = decodeURIComponent(name);
        } catch (e) {
            /* keep the raw filename */
        }

        var link = document.createElement("a");
        link.href = url;
        link.download = name;
        link.style.display = "none";
        document.body.appendChild(link);
        link.click();
        link.remove();
    }

    function setMenuState(item, state, message) {
        var label = item.querySelector("[data-jp-copy-label]");
        if (!label) return;
        if (!item.dataset.jpOriginalLabel) {
            item.dataset.jpOriginalLabel = label.textContent;
        }
        item.classList.toggle("is-copied", state === "copied");
        item.classList.toggle("is-error", state === "error");
        label.textContent = message;
    }

    function resetMenuState(item) {
        if (!item || !item.dataset.jpOriginalLabel) return;
        var label = item.querySelector("[data-jp-copy-label]");
        if (label) label.textContent = item.dataset.jpOriginalLabel;
        item.classList.remove("is-copied", "is-error");
    }

    function setStatus(status, message) {
        if (status) status.textContent = message;
    }

    function closeMenu(host) {
        var toggle = host.querySelector(".jp-output-menu-toggle");
        var menu = host.querySelector(".jp-output-menu");
        if (!toggle || !menu) return;
        menu.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        resetMenuState(host.querySelector("[data-jp-copy-output]"));
    }

    function closeMenus(except) {
        Array.prototype.forEach.call(
            document.querySelectorAll("[data-jp-outputs]"),
            function (host) {
                if (host === except) return;
                var menu = host.querySelector(".jp-output-menu");
                if (menu && !menu.hidden) closeMenu(host);
            }
        );
    }

    function positionMenu(host) {
        var toggle = host.querySelector(".jp-output-menu-toggle");
        var menu = host.querySelector(".jp-output-menu");
        if (!toggle || !menu) return;

        menu.classList.remove("is-up");
        var rect = toggle.getBoundingClientRect();
        var menuHeight = menu.offsetHeight || 44;
        if (window.innerHeight - rect.bottom < menuHeight + 8) {
            menu.classList.add("is-up");
        }
    }

    function openMenu(host) {
        var toggle = host.querySelector(".jp-output-menu-toggle");
        var menu = host.querySelector(".jp-output-menu");
        var item = host.querySelector("[data-jp-copy-output]");
        if (!toggle || !menu || !item) return;

        closeMenus(host);
        resetMenuState(item);
        menu.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
        positionMenu(host);
        item.focus();
    }

    function copyCellOutput(host, item, status) {
        var text = outputText(host);
        var images = imagesIn(host);
        var job;

        if (text) {
            job = writeText(text).then(function (ok) {
                if (ok === false) throw new Error("Copy failed");
                return "copied";
            });
        } else if (images.length) {
            job = withTimeout(copyImage(images[0]), 3000).then(function () {
                return "copied";
            }).catch(function () {
                downloadImage(images[0]);
                return "downloaded";
            });
        } else {
            job = Promise.reject(new Error("Nothing to copy"));
        }

        job.then(function (result) {
            if (result === "downloaded") {
                setMenuState(item, "copied", labels.downloaded);
                setStatus(status, labels.downloaded);
            } else {
                setMenuState(item, "copied", labels.copied);
                setStatus(status, labels.copied);
            }
            window.setTimeout(function () {
                closeMenu(host);
            }, 900);
        }).catch(function () {
            setMenuState(item, "error", labels.copyFailed);
            setStatus(status, labels.copyFailed);
            window.setTimeout(function () {
                resetMenuState(item);
            }, 2000);
        });
    }

    function initOutputGroup(host) {
        var toggle = host.querySelector(".jp-output-menu-toggle");
        var menu = host.querySelector(".jp-output-menu");
        var item = host.querySelector("[data-jp-copy-output]");
        var status = host.querySelector("[data-jp-output-status]");
        if (!toggle || !menu || !item) return;

        toggle.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            if (menu.hidden) openMenu(host);
            else closeMenu(host);
        });

        item.addEventListener("click", function () {
            copyCellOutput(host, item, status);
        });

        menu.addEventListener("keydown", function (event) {
            if (event.key === "Tab") closeMenu(host);
        });
    }

    function initImageWrap(wrap) {
        var img = wrap.querySelector("img");
        var button = wrap.querySelector("[data-jp-copy-image]");
        if (!img || !button) return;

        var originalLabel = button.getAttribute("aria-label") || "";
        var originalTitle = button.getAttribute("title") || "";
        var originalHTML = button.innerHTML;
        var timer = 0;

        button.addEventListener("click", function () {
            button.disabled = true;
            withTimeout(copyImage(img), 3000).then(function () {
                showImageCopied(button, labels.copied);
            }).catch(function () {
                downloadImage(img);
                showImageCopied(button, labels.downloaded);
            }).then(function () {
                button.disabled = false;
            });
        });

        function showImageCopied(btn, message) {
            btn.classList.add("is-copied");
            btn.setAttribute("aria-label", message);
            btn.title = message;
            btn.innerHTML = ICON_CHECK;
            clearTimeout(timer);
            timer = window.setTimeout(function () {
                btn.classList.remove("is-copied");
                btn.setAttribute("aria-label", originalLabel);
                btn.title = originalTitle;
                btn.innerHTML = originalHTML;
            }, 2000);
        }
    }

    function init() {
        Array.prototype.forEach.call(
            document.querySelectorAll("[data-jp-outputs]"),
            initOutputGroup
        );
        Array.prototype.forEach.call(
            document.querySelectorAll(".jp-image-wrap"),
            initImageWrap
        );
    }

    document.addEventListener("click", function (event) {
        if (event.target.closest && event.target.closest("[data-jp-outputs]")) return;
        closeMenus();
    });

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") return;
        var open = document.querySelector(
            '.jp-output-menu-toggle[aria-expanded="true"]'
        );
        if (!open) return;
        closeMenus();
        open.focus();
    });

    window.addEventListener("resize", function () {
        closeMenus();
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
