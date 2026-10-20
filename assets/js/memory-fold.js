(function () {
    "use strict";

    var blocks = document.querySelectorAll("details.memory");
    if (!blocks.length) return;

    var opened = null;

    function openAll() {
        if (opened !== null) return;
        opened = [];
        for (var i = 0; i < blocks.length; i++) {
            if (!blocks[i].open) {
                opened.push(blocks[i]);
                blocks[i].open = true;
            }
        }
    }

    function restore() {
        if (opened === null) return;
        for (var i = 0; i < opened.length; i++) {
            opened[i].open = false;
        }
        opened = null;
    }

    window.addEventListener("beforeprint", openAll);
    window.addEventListener("afterprint", restore);

    if (!window.matchMedia) return;

    var mql = window.matchMedia("print");
    var onChange = function (event) {
        if (event.matches) {
            openAll();
        } else {
            restore();
        }
    };

    if (mql.addEventListener) {
        mql.addEventListener("change", onChange);
    } else if (mql.addListener) {
        mql.addListener(onChange);
    }

    if (mql.matches) openAll();
})();
