---
title: "Plotly 互動圖表煙霧測試"
date: 2026-10-19
draft: true
tags:
  - Plotly
  - Hugo
description: "驗證 Plotly shortcode、Basic/Full 動態載入與深色模式切換的煙霧測試頁，不是正式文章。"
---

這是一頁**煙霧測試**，用來確認 Plotly 整合的每一條路徑都通。正式文章不會出現這種頁面。
它刻意放成 `draft: true`（`hugo server` 看得到、`hugo --minify` 不會發佈）。

## 1. Basic bundle：折線圖

plotly shortcode 的 body 是一段 JSON，等同 Plotly 的 `newPlot(div, data, layout, config)`。

{{< plotly height="420" caption="圖 1：Basic bundle 的折線圖，預設透明背景。" >}}
{
  "data": [
    {
      "x": ["週一", "週二", "週三", "週四", "週五", "週六", "週日"],
      "y": [12, 18, 9, 22, 27, 15, 19],
      "type": "scatter",
      "mode": "lines+markers",
      "name": "吞吐量"
    }
  ],
  "layout": { "title": "一週吞吐量" }
}
{{< /plotly >}}

## 2. Basic bundle：長條圖（第二張圖，驗證 id 不撞號）

{{< plotly height="380" >}}
{
  "data": [
    {
      "x": ["Edge", "Cloud", "DB"],
      "y": [42, 27, 13],
      "type": "bar",
      "marker": { "color": ["#4f46e5", "#0ea5e9", "#14b8a6"] }
    }
  ],
  "layout": { "title": "各層延遲" }
}
{{< /plotly >}}

## 3. Full bundle：3D 散佈圖

Basic bundle 只含 scatter / bar / pie，3D 需要 `bundle="full"`。
這一頁只要有一張 full，整頁就載入 full 一次（full 是 basic 的超集）。

{{< plotly bundle="full" height="520" caption="圖 3：Full bundle 的 3D 散佈圖，用來確認 bundle 切換真的生效。" >}}
{
  "data": [
    {
      "x": [1, 2, 3, 4, 5, 6, 7, 8],
      "y": [4, 7, 3, 9, 5, 8, 2, 6],
      "z": [9, 2, 7, 4, 8, 1, 6, 3],
      "type": "scatter3d",
      "mode": "markers",
      "marker": { "size": 8, "color": "#4f46e5" }
    }
  ],
  "layout": { "title": "三維特徵分布" }
}
{{< /plotly >}}

## 4. 使用者 layout 覆蓋主題預設

`themeBase()` 只補沒有被指定的鍵；這裡明確指定 `paper_bgcolor` 與字色，
應該要蓋掉預設的透明背景。

{{< plotly height="360" >}}
{
  "data": [
    { "x": [1, 2, 3, 4], "y": [4, 3, 2, 1], "type": "scatter", "mode": "lines" }
  ],
  "layout": {
    "title": "自訂底色",
    "paper_bgcolor": "#f5f5f5",
    "plot_bgcolor": "#f5f5f5",
    "font": { "color": "#333333" }
  }
}
{{< /plotly >}}

## 手動測試清單

- 切換 light / dark，第 1、2、3 張圖的字色與格線要跟著換，第 4 張保持自訂色。
- 開發者工具 Network 面板：這一頁載入的是 `plotly.min.js`（full），其餘單張圖的頁面載 `plotly-basic.min.js`。
- 把 CDN 擋掉或離線：圖表位置應顯示「圖表載入失敗」，頁面其餘部分正常。
- 一般文章（沒有 shortcode）的 Network 面板不該出現 `plotly-init`。
