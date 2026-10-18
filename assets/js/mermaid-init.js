/* Mermaid 流程圖初始化。
 *
 * ⚠️ 這個檔案是 assets/js/ 裡唯一的 ESM 檔（用了 import 與箭頭函式），
 *    其餘如 share-link.js 刻意維持 ES5。差異是刻意的，不要「修正」成 ES5 ——
 *    import 是 ESM 專屬語法，改成 ES5 就等於刪掉 mermaid 的載入方式。
 *
 * 為什麼用 importmap 而不是把 CDN 網址寫在這裡：
 *    網址集中在 layouts/partials/extend_footer.html 的 importmap 宣告，
 *    這份檔案只管初始化邏輯，換版號只需要改一個地方。
 *
 * 為什麼用 ESM（mermaid.esm.min.mjs）而不是 UMD（mermaid.min.js）：
 *    實測 ESM 靜態 import 圖約 183 KB gzip（約 26 個請求，HTTP/2 多路復用下
 *    延遲遠小於單檔）；UMD mermaid.min.js 是 1.57 MB gzip，貴 8.6 倍。
 */
import mermaid from "mermaid";

var ready = document.readyState;

mermaid.initialize({
    /* 不用 startOnLoad：它仰賴 document.currentScript 的載入語意，
       在 Hugo 這種 partial 注入的情況下行為不如顯式呼叫可預測。 */
    startOnLoad: false,
    /* strict 會轉義節點標籤裡的 HTML 並停用 mermaid 的 click 互動。
       部落格是唯讀內容，這是預設該有的安全層級。 */
    securityLevel: "strict",
    /* 深色模式不靠這裡。custom.css 用 CSS filter 做反相，
       零 JS、零重繪，切換主題時不會閃爍。 */
    theme: "default",
    /* ⚠️ 這個一定要開，否則同一頁的第 2 張圖之後全部會壞掉。
       mermaid.run() 內部是 new InitIDGenerator(deterministicIds, seed)，
       每張圖取 `mermaid-${gen.next()}` 當 SVG 的 id。
       deterministicIds 預設 false，此時 next() 回傳 Date.now()；
       而 run() 是用 await 在一個緊密迴圈裡跑完所有圖的，同一毫秒內
       很容易拿到相同的時間戳 → id 撞車 → mermaid 對到別張圖的節點，
       結果是後面的圖產生「沒有 viewBox / 沒有 max-width」的空 SVG，
       並且整頁的圖疊在一起、錯誤圖還會蓋到別的圖上面。
       開成 true 之後 next() 回傳 this.count++（0, 1, 2 …），
       同一個 run() 內保證不重複。 */
    deterministicIds: true
});

function render() {
    mermaid.run({ querySelector: ".mermaid" }).catch(function (err) {
        /* 語法寫錯的圖只會讓自己那張圖失敗（mermaid 會在該元素內插入錯誤提示），
           不會影響頁面其他部分，所以只記錄、不往上拋。 */
        console.error("[mermaid] render failed:", err);
    });
}

if (ready === "loading") {
    document.addEventListener("DOMContentLoaded", render);
} else {
    render();
}
