<div align="center">

# 🍸 憩Bay餐酒館 (Chill Bar)
### 現代全方位智慧餐飲營運大腦與數位吧檯系統 (Smart Bistro & Lounge OS)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![UI Style: Macaron Soft Pink](https://img.shields.io/badge/UI_Style-Macaron_Pastel-FF6B8B.svg)](#)

*全套收錄官方 45+ 款真實特色調酒、精釀啤酒、套餐、滷味與炸物，整合 POS 點餐、菜單相冊、VIP CRM、夜場排班、席位預約與財務 P&L 分析！*

---

</div>

## 📖 專案簡介 (About Project)

**「憩Bay餐酒館 (Chill Bar)」** 是一套專為現代餐酒館、微醺酒吧與特色 Bistro 量身打造的**全方位智慧餐飲管理系統**。
系統以法式馬卡龍輕奢粉調 (Macaron Pastel) 為視覺核心，搭配黑金色調霓虹招牌品牌形象，徹底解決餐酒館在夜場營業時面臨的 **「配方扣庫存、常客風味記憶、跨夜排班打卡、包廂低消檢核與即時利潤損益」** 等核心痛點。

---

## 🌟 7 大核心管理模組 (Key Features)

### 1. 🍸 吧檯點餐 POS (配方扣庫存 & 即時改價) — `orders.py`
- **45+ 款官方真實菜單一鍵點餐**：分類支援特色調酒、生啤酒、敲敲瓶裝精釀、精選套餐、經典秘製滷味、主食烤物與無酒精飲品。
- **BOM 配方級自動扣庫存**：點一杯調酒自動扣減對應琴酒、蘭姆酒、果汁糖漿與冰塊原料水位。
- **即時手動改價抽屜**：吧檯隨時調整現場單杯售價與成本，實時試算單品毛利與毛利率。

### 2. 📖 官方實體菜單相冊 (MENU 6頁全收錄) — `menu_viewer.py`
- **高清原圖 100% 收錄**：包含官方品牌封面與 5 頁完整高清實體菜單圖片。
- **3 種流暢瀏覽模式**：
  - 📸 **翻頁相冊 (Flip Album)**：上一頁/下一頁流暢切換與快捷頁籤跳轉。
  - 🖼️ **全頁畫廊 (Gallery Grid)**：6 頁雙欄並列平鋪，一眼對照。
  - 📋 **結構化價格表 (Price List)**：品項關鍵字即時搜尋與毛利速查。

### 3. 👥 VIP 常客偏好與寄酒 CRM — `crm.py`
- **👑 VIP 會員等級與消費追蹤**：黑卡 VIP (Black Card)、金卡 VIP 與銀卡名冊，累積消費額與到店次數。
- **🎯 個人專屬風味五角雷達圖 (Taste Profile Radar)**：量化常客之【甜度、酸度、酒感厚度、苦甜藥草、泥煤木質】偏好。
- **🍾 吧檯寄酒管理 (Bottle Keeping)**：即時追蹤寄放剩餘 ml 數，支援現場單次取酒（45ml）一鍵扣減。
- **📝 客製化接待備註**：記錄顧客特定偏好（如：不吃香菜、週五固定席位、冰塊少三顆）。

### 4. ⏰ 調酒師排班與夜場打卡 — `attendance.py`
- **🕒 夜場專用打卡鐘**：專為 18:00 ~ 03:00 跨夜營業設計，支援一鍵簽到與簽退結算工時。
- **💰 兼職時薪 + 夜間加給 + 酒水抽成即時試算**：
  - 兼職基本時薪：`NT$ 220 / hr`
  - 23:00 後夜間津貼：`+$50 / hr`
  - 酒水出單業績抽成：`1% ~ 3%`
- **📅 每週夜場輪值排班表**：主調 (Head Bartender)、副調、吧廚與外場服務排班清冊。

### 5. 🪑 席位預約與包廂低消檢核 — `reservations.py`
- **🗺️ 全店 4 大席位分區狀態圖**：
  - 🍸 **吧檯席 (01 ~ 06)**：免低消，近距離欣賞調酒師演出。
  - 🥂 **高腳桌區 (A ~ D)**：好友聚會小酌，低消 `NT$ 500 / 人`。
  - 👑 **沙發 VIP 包廂**：6~10 人隱密奢華聚會，自動檢核 **包廂低消 `NT$ 6,000`** 與預收定金。
  - 🌿 **戶外露天雅席**：微風夜酌，低消 `NT$ 350 / 人`。
- **📋 一鍵報到入座**：貴賓到店點擊報到，無縫連動 POS 點餐出單。

### 6. 📊 財務損益 P&L (8大看板大腦) — `financials.py`
- **🌊 金流損益瀑布圖 (Waterfall)**：營收 ➔ 銷貨成本 ➔ 毛利 ➔ OPEX 費用 ➔ 營業淨利。
- **🎯 主要成本率 (Prime Cost)**：食材原料 + 人事薪資佔比儀表盤（健康警戒線 < 60%）。
- **🍸 菜單工程 (Menu BCG Matrix)**：
  - ★ **明星品項 (Stars)**：高毛利、高銷量（如：泰式奶茶酒、美韓轟炸機）。
  - ◆ **金牛品項 (Cash Cows)**：高毛利、穩健成長（如：烤一夜干午仔魚）。
  - ● **主力引流 (Plowhorses)**：低毛利、高人氣（如：台啤18天生啤酒）。
- **🔥 時段坪效 (RevPASH) 空間熱力圖**：19:00 ~ 02:00 各時段每席位創收能力。
- **🛠️ 每日營業額對帳與手動修改**：歷史營業額校正與即時營運費用記帳。

### 7. 🍾 庫存水位與自動警戒 — `inventory.py`
- **原物料安全水位警示**：低於安全庫存即時跳出亮橘色警戒。
- **一鍵進貨盤點**：快速補貨與庫存現況匯總。

---

## 🏗️ 系統架構 (System Architecture)

```text
qibar_project/
├── app.py              # Streamlit 智慧營運大腦主進入點 (側邊欄品牌與模組路由)
├── db.py               # SQLite 資料庫核心與官方 45+ 款真實菜單種子資料
├── qibar.db            # SQLite 關聯式資料庫 (Menu, Orders, Inventory, CRM, Staff, Booking)
├── orders.py           # 吧檯點餐 POS、購物車結帳、即時改價抽屜與 BOM 扣庫存
├── menu_viewer.py      # 官方實體菜單相冊 (封面 + 5 頁大圖翻頁、畫廊與價格表)
├── crm.py              # VIP 客戶主檔、個人風味五角雷達圖、吧檯寄酒與取酒管理
├── attendance.py       # 夜場打卡鐘、每週輪值排班、時薪結算與夜間津貼抽成試算
├── reservations.py     # 4 大分區席位平面圖、線上電話預約、包廂低消 $6,000 檢核
├── financials.py       # 8 大財務看板、Waterfall、Prime Cost 量規、BCG 矩陣、RevPASH
├── inventory.py        # 原物料水位監控、安全庫存警告與進貨管理
├── styles.py           # 法式馬卡龍輕奢粉調 (Macaron Pastel) 客製化 CSS 樣式
├── preview.html        # 獨立輕量版前端預覽網頁 (免後端伺服器)
├── requirements.txt    # Python 依賴套件清單
├── Dockerfile          # Docker 容器化建置設定
├── docker-compose.yml  # Docker Compose 一鍵啟動設定
├── run.sh              # 本地一鍵啟動腳本
└── assets/             # 官方 LOGO 與高清菜單原圖
    ├── logo.jpg
    ├── menu_cover.jpg
    ├── menu_p1.jpg
    ├── menu_p2.jpg
    ├── menu_p3.jpg
    ├── menu_p4.jpg
    └── menu_p5.jpg
```

---

## 🚀 快速開始 (Quick Start)

### 1. 本地環境運行 (Local Setup)

```bash
# 1. 複製專案庫
git clone https://github.com/<your-username>/qibar_project.git
cd qibar_project

# 2. 建立並啟動 Python 虛擬環境
python3 -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows

# 3. 安裝依賴套件
pip install -r requirements.txt

# 4. 初始化資料庫並啟動系統
streamlit run app.py
```

瀏覽器打開 `http://localhost:8501` 即可開始體驗！

---

### 2. Docker 容器化運行 (Docker Setup)

```bash
# 一鍵構建並啟動容器
docker compose up -d --build

# 查看運行狀態
docker compose ps
```

---

## 🌐 雲端一鍵部署指南 (Deployment Options)

- **Streamlit Community Cloud** (推薦)：將此 Repo 推送至 GitHub 後，至 [share.streamlit.io](https://share.streamlit.io) 登入並選擇 `app.py` 即可免費一鍵發布！
- **Railway / Render / Fly.io**：直接連結 GitHub Repository，設定啟動命令 `streamlit run app.py --server.port $PORT`。
- **GCP Cloud Run / AWS ECS**：使用本專案內附之 `Dockerfile` 即可快速建置映像檔上雲。

---

## 📄 授權條款 (License)

本專案採用 **[MIT License](LICENSE)** 授權開源。歡迎自由修改、擴充與商業應用！
