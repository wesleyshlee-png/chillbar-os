"""
qibar_project/menu_viewer.py
憩Bay餐酒館 (Chill Bar) - 官方實體菜單相冊 (修復上一頁/下一頁翻頁與多維度瀏覽)
"""

import streamlit as st
import os
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

MENU_PAGES = [
    {
        "id": "cover",
        "title": "🌟 憩Bay Chill Bar 官方品牌封面",
        "tab_name": "🌟 官方封面",
        "file": "menu_cover.jpg",
        "desc": "憩Bay Chill Bar 霓虹品牌視覺封面 • 冷氣開放 • 可帶外食 • 入店享用 (四國語言標示)"
    },
    {
        "id": "p1",
        "title": "🥜 第 1 頁：經典秘製滷下酒菜 & 主食與分享料理",
        "tab_name": "🥜 1. 滷味 & 主食",
        "file": "menu_p1.jpg",
        "desc": "秘製滷花生 ($90)、滷毛豆 ($80)、花生+毛豆雙拼 ($150)、滷甜不辣 ($75) ｜ 肉醬/青醬義大利麵 ($200)、紐澳良烤雞翅 ($230)、烤一夜干午仔魚 ($300)"
    },
    {
        "id": "p2",
        "title": "🧃 第 2 頁：無酒精特調飲品 & 微醺下酒炸物",
        "tab_name": "🧃 2. 無酒精 & 炸物",
        "file": "menu_p2.jpg",
        "desc": "有機野莓洛神檸檬冰茶 ($120/$160)、有機爽身檸檬冰茶 ($120/$160)、椰子氣泡水 ($120)、可樂/雪碧 ($80)、蘇打水 ($80) ｜ 香脆薯條 ($100)、香酥雞塊 ($120)"
    },
    {
        "id": "p3",
        "title": "🍱 第 3 頁：精選套餐 & 超值加價購升級專區",
        "tab_name": "🍱 3. 精選套餐 & 加購",
        "file": "menu_p3.jpg",
        "desc": "義大利麵+大杯無酒精飲 ($200)、義大利麵+微醺調酒 ($410)、一夜干+炸物雙拼+18天生啤大*2 ($980) ｜ +$60 滷味 / +$80 炸物 / +$195 烤雞翅"
    },
    {
        "id": "p4",
        "title": "🍸 第 4 頁：特色調酒、風味茶酒與生啤酒",
        "tab_name": "🍸 4. 特色調酒 & 生啤",
        "file": "menu_p4.jpg",
        "desc": "泰式奶茶酒 8% ($300)、紅心芭樂梅 8% ($250)、芭樂梅茶酒 8% ($290)、柚香梅沙瓦 ($260)、伯爵覆盆子 8% ($290)、梅脾氣 ($260)、野莓洛神 4% ($220)、Mojito冰茶 4% ($220)、雷檸紫蘇/荔枝/草莓 ｜ 18天生啤 ($250/$320)、朝日生啤 ($250/$320)、Highball/Lime ($200)"
    },
    {
        "id": "p5",
        "title": "🍾 第 5 頁：敲敲瓶身感受微醺！精釀啤酒與韓式燒啤",
        "tab_name": "🍾 5. 敲敲瓶裝 & 燒啤",
        "file": "menu_p5.jpg",
        "desc": "朝日瓶裝 ($160)、布希啤酒 ($210)、歸剛ㄟ零糖啤酒 ($220)、小滿冬瓜茶啤酒 ($220)、立秋東方美人茶啤酒 ($220)、貓頭鷹蘋果氣泡酒 ($220)、燒酒Somaek ($220)、美韓轟炸機組合 ($390)"
    }
]


def render_menu_viewer_page():
    st.markdown("## 📖 憩Bay 官方完整實體菜單相冊 (Official Menu Book)")
    st.caption("點擊下方【快捷翻頁按鈕】或【上一頁 / 下一頁】，即可流暢翻閱全套 6 頁高清官方菜單！")

    # 1. 確保 session_state 存在
    if "menu_page_idx" not in st.session_state:
        st.session_state.menu_page_idx = 0

    total_pages = len(MENU_PAGES)

    # 2. 瀏覽模式選擇
    view_mode = st.radio(
        "選擇瀏覽模式：",
        ["📸 模式 A：流暢翻頁相冊 (Flip Album)", "🖼️ 模式 B：全頁畫廊平鋪 (Gallery Grid)", "📋 模式 C：結構化品項定價清單 (Price List)"],
        horizontal=True
    )

    st.markdown("---")

    # ==========================================
    # 模式 A：翻頁相冊檢視 (保證 100% 翻頁正常)
    # ==========================================
    if view_mode == "📸 模式 A：流暢翻頁相冊 (Flip Album)":
        # 🌟 快速頁次快捷跳轉列 (Quick Jump Pills)
        st.markdown("##### 📌 快速跳頁選擇：")
        pill_cols = st.columns(total_pages)
        for i, p_info in enumerate(MENU_PAGES):
            with pill_cols[i]:
                is_active = (st.session_state.menu_page_idx == i)
                btn_label = f"👉 {p_info['tab_name']}" if is_active else p_info['tab_name']
                btn_type = "primary" if is_active else "secondary"
                if st.button(btn_label, key=f"quick_pill_{i}", type=btn_type, use_container_width=True):
                    st.session_state.menu_page_idx = i
                    st.rerun()

        st.markdown("---")

        # 當前頁面資料
        cur_idx = st.session_state.menu_page_idx
        cur_page = MENU_PAGES[cur_idx]
        img_path = os.path.join(ASSETS_DIR, cur_page["file"])

        # 頂部導航指示列
        nav_c1, nav_c2, nav_c3 = st.columns([1.2, 2.5, 1.2])
        with nav_c1:
            if cur_idx > 0:
                if st.button(f"⬅️ 上一頁 ({MENU_PAGES[cur_idx-1]['tab_name']})", key="btn_top_prev", use_container_width=True):
                    st.session_state.menu_page_idx = cur_idx - 1
                    st.rerun()
            else:
                st.button("⬅️ 已是第一頁", disabled=True, use_container_width=True)

        with nav_c2:
            st.markdown(f"<div style='text-align:center; font-weight:900; font-size:16px; color:#E11D48; padding-top:6px;'>📖 第 {cur_idx + 1} / {total_pages} 頁：{cur_page['title']}</div>", unsafe_allow_html=True)

        with nav_c3:
            if cur_idx < total_pages - 1:
                if st.button(f"下一頁 ➡️ ({MENU_PAGES[cur_idx+1]['tab_name']})", key="btn_top_next", type="primary", use_container_width=True):
                    st.session_state.menu_page_idx = cur_idx + 1
                    st.rerun()
            else:
                st.button("下一頁 ➡️ (已是末頁)", disabled=True, use_container_width=True)

        st.info(f"💡 **本頁說明**：{cur_page['desc']}")

        # 顯示菜單大圖
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, use_container_width=True, caption=cur_page["title"])
        else:
            st.error(f"找不到菜單圖片：{img_path}")

        # 底部翻頁按鈕列
        b_prev, b_space, b_next = st.columns([1.5, 2, 1.5])
        with b_prev:
            if cur_idx > 0:
                if st.button("⬅️ 返回上一頁", key="btn_bot_prev", use_container_width=True):
                    st.session_state.menu_page_idx = cur_idx - 1
                    st.rerun()
        with b_next:
            if cur_idx < total_pages - 1:
                if st.button("翻至下一頁 ➡️", key="btn_bot_next", type="primary", use_container_width=True):
                    st.session_state.menu_page_idx = cur_idx + 1
                    st.rerun()

    # ==========================================
    # 模式 B：全頁畫廊平鋪
    # ==========================================
    elif view_mode == "🖼️ 模式 B：全頁畫廊平鋪 (Gallery Grid)":
        st.markdown("### 🖼️ 憩Bay 官方完整菜單 6 頁平鋪總覽")
        for i in range(0, total_pages, 2):
            g1, g2 = st.columns(2)
            p1 = MENU_PAGES[i]
            with g1:
                st.markdown(f"#### {p1['title']}")
                st.caption(p1["desc"])
                img1_path = os.path.join(ASSETS_DIR, p1["file"])
                if os.path.exists(img1_path):
                    st.image(Image.open(img1_path), use_container_width=True)

            if i + 1 < total_pages:
                p2 = MENU_PAGES[i + 1]
                with g2:
                    st.markdown(f"#### {p2['title']}")
                    st.caption(p2["desc"])
                    img2_path = os.path.join(ASSETS_DIR, p2["file"])
                    if os.path.exists(img2_path):
                        st.image(Image.open(img2_path), use_container_width=True)

    # ==========================================
    # 模式 C：結構化品項定價清單
    # ==========================================
    else:
        st.markdown("### 📋 憩Bay 官方菜單品項與毛利速查表")
        from db import get_connection
        conn = get_connection()
        import pandas as pd
        df = pd.read_sql_query("SELECT category AS 菜單分類, name AS 品項名稱, selling_price AS 現場售價, cost_price AS 原物料成本 FROM menu_items ORDER BY id ASC", conn)
        conn.close()

        df["單品獲利"] = df["現場售價"] - df["原物料成本"]
        df["毛利率"] = (df["單品獲利"] / df["現場售價"] * 100).round(1)

        search_kw = st.text_input("🔍 搜尋品項關鍵字：", placeholder="例：奶茶酒、一夜干、烤雞翅、生啤、薯條")
        if search_kw:
            df = df[df["品項名稱"].str.contains(search_kw) | df["菜單分類"].str.contains(search_kw)]

        st.dataframe(
            df.style.format({
                "現場售價": "NT$ {:,.0f}",
                "原物料成本": "NT$ {:,.0f}",
                "單品獲利": "NT$ {:,.0f}",
                "毛利率": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )
