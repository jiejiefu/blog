(function () {
    "use strict";

    function parseTimestamp(value) {
        var parts = value.trim().split(":");
        var seconds = 0;
        for (var i = 0; i < parts.length; i++) {
            seconds = seconds * 60 + parseFloat(parts[i].replace(",", "."));
        }
        return isNaN(seconds) ? 0 : seconds;
    }

    function parseVtt(text) {
        var cues = [];
        var blocks = text.replace(/^\uFEFF/, "").replace(/\r\n?/g, "\n").split(/\n{2,}/);

        for (var i = 0; i < blocks.length; i++) {
            var lines = blocks[i].split("\n");
            var timingIndex = -1;
            for (var j = 0; j < lines.length; j++) {
                if (lines[j].indexOf("-->") !== -1) {
                    timingIndex = j;
                    break;
                }
            }
            if (timingIndex === -1) {
                continue;
            }

            var match = lines[timingIndex].match(/(\S+)\s*-->\s*(\S+)/);
            if (!match) {
                continue;
            }

            var cueText = lines.slice(timingIndex + 1).join(" ").trim();
            if (!cueText) {
                continue;
            }

            cues.push({
                start: parseTimestamp(match[1]),
                end: parseTimestamp(match[2]),
                text: cueText
            });
        }

        cues.sort(function (a, b) {
            return a.start - b.start;
        });
        return cues;
    }

    function findCue(cues, time) {
        var low = 0;
        var high = cues.length - 1;

        while (low <= high) {
            var mid = (low + high) >> 1;
            if (time < cues[mid].start) {
                high = mid - 1;
            } else if (time >= cues[mid].end) {
                low = mid + 1;
            } else {
                return mid;
            }
        }
        return -1;
    }

    function setup(audio) {
        var url = audio.getAttribute("data-audio-captions");
        var box = audio.parentNode.querySelector("[data-audio-cue]");
        if (!url || !box || typeof window.fetch !== "function") {
            return;
        }

        var cues = null;
        var current = -1;

        function render() {
            if (!cues) {
                return;
            }

            var active = findCue(cues, audio.currentTime);
            if (active === current) {
                return;
            }
            current = active;

            if (active < 0) {
                // Keep the previous line in gaps and after the last cue so the
                // article below does not jump. Only clear before the first cue.
                if (audio.currentTime < cues[0].start) {
                    box.hidden = true;
                    box.textContent = "";
                    current = -1;
                }
                return;
            }
            box.textContent = cues[active].text;
            box.hidden = false;
        }

        function clear() {
            current = -1;
            box.hidden = true;
            box.textContent = "";
        }

        window.fetch(url, { credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.text();
            })
            .then(function (text) {
                cues = parseVtt(text);
                if (!cues.length) {
                    return;
                }

                audio.addEventListener("play", render);
                audio.addEventListener("timeupdate", render);
                audio.addEventListener("seeking", render);
                audio.addEventListener("seeked", render);
                audio.addEventListener("ended", render);
                audio.addEventListener("emptied", clear);

                if (!audio.paused || audio.currentTime > 0) {
                    render();
                }
            })
            .catch(function () {
                // Keep the player usable; captions are progressive enhancement.
            });
    }

    function init() {
        var audios = document.querySelectorAll("audio[data-audio-captions]");
        for (var i = 0; i < audios.length; i++) {
            setup(audios[i]);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
