# 小助手 LINE Bot

一個以 Python 開發、部署於 Vercel 的 LINE Bot 專案，整合多項第三方 API，支援天氣、機票、運勢查詢等功能，展示多元 API 整合與訊息回傳處理能力。

## 📌 專案簡介

**小助手**是一個實驗性 LINE 聊天機器人，目標為整合實用資訊查詢功能。雖然功能彼此獨立，無強制關聯性，但能展示完整的 API 呼叫、資料處理與互動式回應呈現。

---

## ✅ 現有功能

* ✈️ **機票查詢**：

  * 整合 Travelpayouts API 查詢來自桃園機場（TPE）出發的最便宜機票。
  * 利用 Trip.com 網址拼接產生購票頁面連結。
  * 使用 pandas 處理 IATA 機場代碼與中文名稱對照表。

* 🌦️ **天氣查詢**：

  * 顯示當前地點 36 小時內天氣概況（整合政府開放資料 API）。

* 🔮 **今日運勢**：

  * 隨機抽籤，回傳每日小運勢建議。

---

## 🛠 使用技術

* 語言：Python
* 後端框架：Flask
* LINE Messaging API：v3 版本
* 部署平台：Vercel（本地開發使用 ngrok）
* 資料處理：pandas + CSV（airports.csv）

---

## 🚀 快速開始

### 環境變數（`.env`）設定

請於根目錄下建立 `.env` 檔案，填入以下資訊：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的Token
LINE_CHANNEL_SECRET=你的Secret
TRAVELPAYOUTS_API_TOKEN=你的API金鑰
```

### 本地端啟動

```bash
python app.py
```

搭配 [ngrok](https://ngrok.com/) 測試 LINE Webhook：

```bash
ngrok http 5000
```

---

## 📱 LINE 使用方式

🔗 加入好友使用：[LINE ID @083vqema](https://line.me/R/ti/p/@083vqema)

### 指令範例：

```text
輸入「天氣」：查詢 36 小時天氣預報
輸入「機票」：顯示多筆便宜機票選項，附上 Trip.com 比價連結
輸入「今日運勢」：隨機抽籤占卜今日小運
```

### 範例導覽

當使用者輸入「介紹」、「說明」、「guide」時，LINE Bot 回傳：

> 本喵學會找天氣、找機票、占卜\n其他還在學\n\n輸入「天氣」可以找36小時內天氣\n輸入「機票」可以找便宜機票\n輸入「今日運勢」本喵會占卜！

---

## 🔍 未來計畫

* ✅ 根據使用者回饋，考慮加入地震查詢等資訊性功能。
* ✅ 增強錯誤處理與輸入指令彈性。

---

## 🙌 聯絡方式
如對專案有任何建議或想法，歡迎聯絡 💬 http://www.linkedin.com/in/trista-tsai-mc