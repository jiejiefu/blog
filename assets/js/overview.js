/* 內容總覽：篩選、排序、URL 同步
   ------------------------------------------------------------------
   沒有相依、沒有 setInterval。表格在沒有 JS 時已完整輸出；
   這裡只做 client-side 篩選與排序，並把狀態寫回 query string。 */

(() => {
    const table = document.getElementById("ov-table");
    if (!table) return;

    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);
    const search = document.getElementById("ov-search");
    const type = document.getElementById("ov-type");
    const year = document.getElementById("ov-year");
    const tag = document.getElementById("ov-tag");
    const reset = document.getElementById("ov-reset");
    const empty = document.getElementById("ov-empty");
    const countEl = document.getElementById("ov-count");
    const sortButtons = Array.from(table.querySelectorAll(".ov-sort"));
    const countTemplate = countEl ? countEl.dataset.countTemplate : "{n}";
    const lang = document.documentElement.lang || "en";
    const collator = new Intl.Collator(lang, { numeric: true, sensitivity: "base" });

    const state = {
        q: "",
        type: "all",
        year: "all",
        tag: "all",
        sort: "date",
        order: "desc",
    };

    function hasOption(select, value) {
        return Array.from(select.options).some((option) => option.value === value);
    }

    function readUrl() {
        const params = new URLSearchParams(window.location.search);
        state.q = params.get("q") || "";
        state.type = params.get("type") || "all";
        state.year = params.get("year") || "all";
        state.tag = params.get("tag") || "all";
        state.sort = params.get("sort") || "date";
        state.order = params.get("order") === "asc" ? "asc" : "desc";

        if (type && !hasOption(type, state.type)) state.type = "all";
        if (year && !hasOption(year, state.year)) state.year = "all";
        if (tag && !hasOption(tag, state.tag)) state.tag = "all";
        if (!["title", "type", "date"].includes(state.sort)) state.sort = "date";
    }

    function writeUrl() {
        const params = new URLSearchParams();
        if (state.q) params.set("q", state.q);
        if (state.type !== "all") params.set("type", state.type);
        if (state.year !== "all") params.set("year", state.year);
        if (state.tag !== "all") params.set("tag", state.tag);
        if (state.sort !== "date" || state.order !== "desc") {
            params.set("sort", state.sort);
            params.set("order", state.order);
        }

        const query = params.toString();
        const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;
        window.history.replaceState(null, "", url);
    }

    function sortRows() {
        const direction = state.order === "asc" ? 1 : -1;
        const key = state.sort;

        rows.sort((a, b) => {
            let left;
            let right;

            if (key === "title") {
                left = a.dataset.title || "";
                right = b.dataset.title || "";
                return collator.compare(left, right) * direction;
            }

            if (key === "type") {
                left = a.dataset.type || "";
                right = b.dataset.type || "";
                return collator.compare(left, right) * direction;
            }

            left = a.dataset.date || "";
            right = b.dataset.date || "";
            return (left < right ? -1 : left > right ? 1 : 0) * direction;
        });

        const fragment = document.createDocumentFragment();
        rows.forEach((row) => fragment.appendChild(row));
        tbody.appendChild(fragment);
    }

    function matches(row) {
        if (state.type !== "all" && row.dataset.type !== state.type) return false;
        if (state.year !== "all" && row.dataset.year !== state.year) return false;

        if (state.tag !== "all") {
            const tags = (row.dataset.tags || "").split("|");
            if (!tags.includes(state.tag)) return false;
        }

        if (state.q) {
            const haystack = row.dataset.search || "";
            if (!haystack.includes(state.q.toLowerCase())) return false;
        }

        return true;
    }

    function applyFilters() {
        let visible = 0;

        rows.forEach((row) => {
            const show = matches(row);
            row.hidden = !show;
            if (show) visible += 1;
        });

        if (empty) empty.hidden = visible !== 0;
        if (countEl) countEl.textContent = countTemplate.replace("{n}", String(visible));
    }

    function updateSortUi() {
        sortButtons.forEach((button) => {
            const th = button.closest("th");
            if (!th) return;
            if (button.dataset.sortKey === state.sort) {
                th.setAttribute("aria-sort", state.order === "asc" ? "ascending" : "descending");
            } else {
                th.setAttribute("aria-sort", "none");
            }
        });
    }

    function syncControls() {
        if (search) search.value = state.q;
        if (type) type.value = state.type;
        if (year) year.value = state.year;
        if (tag) tag.value = state.tag;
    }

    function refresh() {
        syncControls();
        sortRows();
        updateSortUi();
        applyFilters();
    }

    if (search) {
        search.addEventListener("input", () => {
            state.q = search.value.trim();
            applyFilters();
            writeUrl();
        });
    }

    [type, year, tag].forEach((select) => {
        if (!select) return;
        select.addEventListener("change", () => {
            state[select.id.replace("ov-", "")] = select.value;
            applyFilters();
            writeUrl();
        });
    });

    sortButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const key = button.dataset.sortKey;
            if (!key) return;

            if (state.sort === key) {
                state.order = state.order === "asc" ? "desc" : "asc";
            } else {
                state.sort = key;
                state.order = key === "date" ? "desc" : "asc";
            }

            sortRows();
            updateSortUi();
            applyFilters();
            writeUrl();
        });
    });

    if (reset) {
        reset.addEventListener("click", () => {
            state.q = "";
            state.type = "all";
            state.year = "all";
            state.tag = "all";
            state.sort = "date";
            state.order = "desc";
            refresh();
            writeUrl();
        });
    }

    window.addEventListener("popstate", () => {
        readUrl();
        refresh();
    });

    readUrl();
    refresh();
})();
