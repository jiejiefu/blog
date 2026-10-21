(function () {
    'use strict';

    var figures = document.querySelectorAll('[data-post-video]');
    if (!figures.length) {
        return;
    }

    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');

    function init(figure) {
        var media = figure.querySelector('.post-video__media');
        var toggle = figure.querySelector('.post-video__toggle');
        if (!media) {
            return;
        }

        var autoAllowed = !(reduceMotion && reduceMotion.matches);
        var userPaused = false;
        var offscreen = false;
        var pageVisible = !document.hidden;

        function paint() {
            var paused = media.paused;
            if (toggle) {
                toggle.hidden = !paused;
                toggle.setAttribute('aria-label', paused ? '播放影片' : '暫停影片');
                var label = toggle.querySelector('.post-video__sr');
                if (label) {
                    label.textContent = paused ? '播放影片' : '暫停影片';
                }
            }
            figure.classList.toggle('is-paused', paused);
            figure.classList.toggle('is-playing', !paused);
        }

        function play(isAuto) {
            if (isAuto && !autoAllowed) {
                paint();
                return;
            }
            userPaused = false;
            var promise = media.play();
            if (promise && promise.catch) {
                promise.catch(paint);
            }
        }

        function togglePlay() {
            if (media.paused) {
                autoAllowed = true;
                play(false);
            } else {
                userPaused = true;
                media.pause();
            }
        }

        media.addEventListener('play', paint);
        media.addEventListener('pause', paint);
        media.addEventListener('click', togglePlay);
        media.addEventListener('keydown', function (event) {
            if (event.key === ' ' || event.key === 'Enter') {
                event.preventDefault();
                togglePlay();
            }
        });

        if (toggle) {
            toggle.addEventListener('click', togglePlay);
        }

        document.addEventListener('visibilitychange', function () {
            pageVisible = !document.hidden;
            if (!pageVisible) {
                media.pause();
            } else if (!userPaused && !offscreen) {
                play(true);
            }
        });

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function (entries) {
                offscreen = !entries[0].isIntersecting;
                if (offscreen) {
                    media.pause();
                } else if (!userPaused && pageVisible) {
                    play(true);
                }
            }, { threshold: 0.25 });
            observer.observe(figure);
        }

        function start() {
            if (offscreen || !pageVisible) {
                paint();
                return;
            }
            play(true);
        }

        if (media.readyState >= 2) {
            start();
        } else {
            media.addEventListener('loadeddata', start, { once: true });
        }

        paint();
    }

    for (var i = 0; i < figures.length; i++) {
        init(figures[i]);
    }
})();
