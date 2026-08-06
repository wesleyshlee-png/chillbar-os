"""
qibar_project/crm.py
憩Bay餐酒館 (Chill Bar) - VIP 常客檔案、風味偏好雷達、寄酒管理與熟客招待 CRM 系統
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3

try:
    from db import get_connection
except ImportError:
    def get_connection():
        return sqlite3.connect("qibar.db", check_same_thread=False)


def init_crm_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. VIP 客戶主檔
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,
            membership_tier TEXT DEFAULT 'Silver',
            total_spent REAL DEFAULT 0,
            visits_count INTEGER DEFAULT 1,
            favorite_cocktail TEXT DEFAULT '招牌特調 Negroni',
            favorite_seat TEXT DEFAULT '吧檯席 01',
            notes TEXT,
            taste_sweet REAL DEFAULT 3,
            taste_sour REAL DEFAULT 4,
            taste_alcohol REAL DEFAULT 4,
            taste_bitter REAL DEFAULT 2,
            taste_peat REAL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    # 2. 寄酒管理 (Bottle Keeping)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bottle_keeping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT,
            bottle_name TEXT NOT NULL,
            total_volume_ml REAL NOT NULL DEFAULT 700.0,
            remaining_volume_ml REAL NOT NULL DEFAULT 700.0,
            opened_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            status TEXT DEFAULT 'KEEPING',
            created_at TEXT NOT NULL
        )
    """)

    # 寫入初始常客範例
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seed_vips = [
            ("Wesley Lee", "0912-345-678", "Black Card VIP", 58400.0, 18, "泰式奶茶酒8%", "吧檯席 01", "週五夜間固定到店，喜歡高酒精厚實調酒，不吃香菜", 2.5, 4.0, 5.0, 3.5, 4.5, now_str),
            ("Jennifer Lin", "0922-111-222", "Gold VIP", 32500.0, 12, "白桃茉莉茶酒8%", "沙發 VIP 包廂", "喜歡清爽花果茶香，生日月份送招牌炸物", 4.5, 4.0, 3.0, 1.5, 1.0, now_str),
            ("Michael Chen", "0933-888-999", "Gold VIP", 28900.0, 9, "野火雞101波本威士忌", "高腳桌 A", "威士忌純飲愛好者，有寄放 1 瓶波本威士忌", 1.5, 2.0, 4.5, 4.0, 4.8, now_str),
            ("Emily Wang", "0955-666-777", "Silver", 14200.0, 5, "紅心芭樂梅8%", "吧檯席 03", "喜歡拍照打卡，推薦季節性特調", 4.0, 4.5, 2.5, 2.0, 1.0, now_str),
            ("David Wu", "0966-333-444", "Silver", 9800.0, 3, "朝日Asahi生啤", "戶外露天席", "下班小酌，固定點炸物雙拼", 2.0, 1.5, 3.0, 2.5, 1.5, now_str),
        ]
        for v in seed_vips:
            cursor.execute("""
                INSERT INTO customers (name, phone, membership_tier, total_spent, visits_count, favorite_cocktail, favorite_seat, notes, taste_sweet, taste_sour, taste_alcohol, taste_bitter, taste_peat, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, v)

    # 寫入初始寄酒範例
    cursor.execute("SELECT COUNT(*) FROM bottle_keeping")
    if cursor.fetchone()[0] == 0:
        now_dt = datetime.now()
        seed_bottles = [
            ("Michael Chen", "0933-888-999", "野火雞101波本威士忌 (Wild Turkey 1000ml)", 1000.0, 650.0, (now_dt - timedelta(days=15)).strftime("%Y-%m-%d"), (now_dt + timedelta(days=75)).strftime("%Y-%m-%d"), "KEEPING", now_dt.strftime("%Y-%m-%d %H:%M:%S")),
            ("Wesley Lee", "0912-345-678", "龐貝藍鑽琴酒 (Bombay Sapphire 750ml)", 750.0, 420.0, (now_dt - timedelta(days=20)).strftime("%Y-%m-%d"), (now_dt + timedelta(days=70)).strftime("%Y-%m-%d"), "KEEPING", now_dt.strftime("%Y-%m-%d %H:%M:%S")),
            ("Jennifer Lin", "0922-111-222", "波爾多莊園紅葡萄酒 (Bordeaux Rouge 750ml)", 750.0, 350.0, (now_dt - timedelta(days=5)).strftime("%Y-%m-%d"), (now_dt + timedelta(days=25)).strftime("%Y-%m-%d"), "KEEPING", now_dt.strftime("%Y-%m-%d %H:%M:%S")),
        ]
        for b in seed_bottles:
            cursor.execute("""
                INSERT INTO bottle_keeping (customer_name, phone, bottle_name, total_volume_ml, remaining_volume_ml, opened_date, expiry_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, b)

    conn.commit()
    conn.close()


def add_customer(name: str, phone: str, tier: str, fav_drink: str, fav_seat: str, notes: str, sweet: float, sour: float, alcohol: float, bitter: float, peat: float):
    init_crm_tables()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO customers (name, phone, membership_tier, total_spent, visits_count, favorite_cocktail, favorite_seat, notes, taste_sweet, taste_sour, taste_alcohol, taste_bitter, taste_peat, created_at)
        VALUES (?, ?, ?, 0, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, tier, fav_drink, fav_seat, notes, sweet, sour, alcohol, bitter, peat, now_str))
    conn.commit()
    conn.close()


def add_bottle_keep(customer_name: str, phone: str, bottle_name: str, total_ml: float, opened_date: str, keep_days: int = 90):
    init_crm_tables()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    opened_dt = datetime.strptime(opened_date, "%Y-%m-%d")
    expiry_dt = opened_dt + timedelta(days=keep_days)
    cursor.execute("""
        INSERT INTO bottle_keeping (customer_name, phone, bottle_name, total_volume_ml, remaining_volume_ml, opened_date, expiry_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'KEEPING', ?)
    """, (customer_name, phone, bottle_name, total_ml, total_ml, opened_date, expiry_dt.strftime("%Y-%m-%d"), now_str))
    conn.commit()
    conn.close()


def pour_kept_bottle(bottle_id: int, pour_ml: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT remaining_volume_ml FROM bottle_keeping WHERE id = ?", (bottle_id,))
    row = cursor.fetchone()
    if row:
        cur_vol = row[0]
        new_vol = max(0.0, cur_vol - pour_ml)
        status = "COMPLETED" if new_vol <= 0 else "KEEPING"
        cursor.execute("UPDATE bottle_keeping SET remaining_volume_ml = ?, status = ? WHERE id = ?", (new_vol, status, bottle_id))
    conn.commit()
    conn.close()


def render_taste_radar(sweet, sour, alcohol, bitter, peat, customer_name):
    categories = ['甜度 (Sweet)', '酸度 (Sour)', '酒精感 (Alcohol)', '苦甜/藥草 (Bitter)', '泥煤/木質 (Peat)']
    values = [sweet, sour, alcohol, bitter, peat]
    values.append(values[0])
    categories.append(categories[0])

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(255, 107, 139, 0.35)',
        line=dict(color='#FF4B72', width=3),
        marker=dict(size=8, color='#FF6B8B')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10, color='#64748B'), gridcolor='#E2E8F0'),
            angularaxis=dict(tickfont=dict(size=12, color='#0F172A', family='Outfit'), gridcolor='#E2E8F0')
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#FFFFFF',
        margin=dict(l=40, r=40, t=30, b=30),
        height=300
    )
    return fig


def render_crm_page():
    init_crm_tables()
    conn = get_connection()
    customers_df = pd.read_sql_query("SELECT * FROM customers ORDER BY total_spent DESC", conn)
    bottles_df = pd.read_sql_query("SELECT * FROM bottle_keeping WHERE status = 'KEEPING' ORDER BY expiry_date ASC", conn)
    conn.close()

    st.markdown("## 👥 憩Bay VIP 熟客 CRM、個人風味雷達與寄酒管理")
    st.caption("深度記錄常客風味酒單喜好、專屬入座席位、開瓶寄酒水位與生日招待關懷！")

    # 4 大 CRM 核心數據卡
    total_vips = len(customers_df)
    black_card_count = len(customers_df[customers_df["membership_tier"] == "Black Card VIP"])
    total_kept_bottles = len(bottles_df)
    avg_spent = customers_df["total_spent"].mean() if not customers_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 註冊熟客總數", f"{total_vips} 位", delta="活耀常客 86%")
    c2.metric("💳 黑卡/金卡 VIP", f"{black_card_count + len(customers_df[customers_df['membership_tier'] == 'Gold VIP'])} 位", delta=f"{black_card_count} 位頂級黑卡")
    c3.metric("🍾 吧檯保管寄酒", f"{total_kept_bottles} 支", delta="即將到期 1 支")
    c4.metric("💰 常客平均消費", f"NT$ {avg_spent:,.0f}", delta="客單貢獻度高")

    st.divider()

    tab_vips, tab_radar, tab_bottles, tab_add_cust = st.tabs([
        "👑 VIP 熟客名冊與喜好",
        "🎯 個人風味雷達 (Taste Radar)",
        "🍾 吧檯寄酒管理 (Bottle Keeping)",
        "➕ 新增熟客檔案 / 登記寄酒"
    ])

    # ==========================================
    # Tab 1: VIP 熟客名冊
    # ==========================================
    with tab_vips:
        st.markdown("### 📋 憩Bay 常客名冊與專屬備註")
        if not customers_df.empty:
            display_cust = customers_df[[
                "name", "phone", "membership_tier", "total_spent", "visits_count", "favorite_cocktail", "favorite_seat", "notes"
            ]].copy()
            display_cust.columns = [
                "顧客姓名", "聯絡電話", "會員等級", "累計消費額", "到店次數", "最愛酒款", "偏好席位", "調酒師備註 / 特殊偏好"
            ]
            st.dataframe(
                display_cust.style.format({
                    "累計消費額": "NT$ {:,.0f}",
                    "到店次數": "{:d} 次"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("尚無客戶資料。")

    # ==========================================
    # Tab 2: 個人風味雷達圖
    # ==========================================
    with tab_radar:
        st.markdown("### 🎯 熟客專屬風味偏好雷達圖 (Taste Profile Radar)")
        if not customers_df.empty:
            r_col1, r_col2 = st.columns([1.2, 1.8])
            with r_col1:
                selected_cust_name = st.selectbox("選擇熟客姓名：", customers_df["name"].tolist(), key="crm_radar_sel")
                cust_row = customers_df[customers_df["name"] == selected_cust_name].iloc[0]

                st.markdown(f"""
                <div style="background:#FFFFFF; border:1.5px solid #F1E5D8; border-radius:18px; padding:16px; margin-top:10px;">
                    <h3 style="margin:0; font-size:18px; font-weight:900; color:#0F172A;">{cust_row['name']}</h3>
                    <p style="margin:4px 0 10px 0; font-size:12px; font-weight:800; color:#FF4B72;">{cust_row['membership_tier']} ｜ 到店 {cust_row['visits_count']} 次</p>
                    <hr style="border:0; border-top:1px solid #F1E5D8; margin:10px 0;">
                    <p style="font-size:12px; color:#475569; margin:4px 0;"><b>🍸 偏好特調</b>：{cust_row['favorite_cocktail']}</p>
                    <p style="font-size:12px; color:#475569; margin:4px 0;"><b>🪑 專屬席位</b>：{cust_row['favorite_seat']}</p>
                    <p style="font-size:12px; color:#475569; margin:4px 0;"><b>📝 調酒師備註</b>：{cust_row['notes']}</p>
                </div>
                """, unsafe_allow_html=True)

            with r_col2:
                radar_fig = render_taste_radar(
                    cust_row["taste_sweet"],
                    cust_row["taste_sour"],
                    cust_row["taste_alcohol"],
                    cust_row["taste_bitter"],
                    cust_row["taste_peat"],
                    cust_row["name"]
                )
                st.plotly_chart(radar_fig, use_container_width=True)

    # ==========================================
    # Tab 3: 寄酒管理
    # ==========================================
    with tab_bottles:
        st.markdown("### 🍾 憩Bay 吧檯寄酒即時庫存與出酒記錄")
        if not bottles_df.empty:
            for _, b in bottles_df.iterrows():
                remain_pct = (b["remaining_volume_ml"] / b["total_volume_ml"] * 100)
                b_c1, b_c2, b_c3 = st.columns([2.5, 1.5, 1.5])
                with b_c1:
                    st.markdown(f"#### 🍾 {b['bottle_name']}")
                    st.caption(f"寄放人：**{b['customer_name']}** ({b['phone']}) ｜ 開瓶日期：{b['opened_date']} ｜ 到期日：{b['expiry_date']}")
                    st.progress(remain_pct / 100.0)
                    st.caption(f"剩餘水位：**{b['remaining_volume_ml']:.0f} ml** / {b['total_volume_ml']:.0f} ml ({remain_pct:.1f}%)")
                with b_c2:
                    pour_amount = st.number_input(f"取酒毫升 (ml)", min_value=10.0, max_value=float(b["remaining_volume_ml"]), value=45.0, step=15.0, key=f"pour_input_{b['id']}")
                with b_c3:
                    st.write("")
                    st.write("")
                    if st.button(f"🥃 出酒 {pour_amount:.0f}ml", key=f"pour_btn_{b['id']}", type="primary"):
                        pour_kept_bottle(b["id"], pour_amount)
                        st.success(f"已自【{b['customer_name']}】的寄酒中扣除 {pour_amount:.0f}ml！")
                        st.rerun()
                st.divider()
        else:
            st.info("目前無寄存中的酒品。")

    # ==========================================
    # Tab 4: 新增熟客與登記寄酒
    # ==========================================
    with tab_add_cust:
        st.markdown("### ➕ 新增熟客檔案與風味資料")
        with st.form("add_new_cust_form", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                n_name = st.text_input("顧客姓名 *", placeholder="例：林冠宇 (Alex)")
                n_phone = st.text_input("聯絡電話 *", placeholder="例：0912-345-678")
            with f2:
                n_tier = st.selectbox("會員等級", ["Silver", "Gold VIP", "Black Card VIP"])
                n_drink = st.text_input("偏好特調/飲品", value="泰式奶茶酒8%")
            with f3:
                n_seat = st.selectbox("偏好席位", ["吧檯席 01", "吧檯席 02", "高腳桌 A", "沙發 VIP 包廂", "戶外露天席"])
                n_notes = st.text_input("調酒師接待備註", placeholder="例：週五固定夜酌，冰塊少三顆")

            st.markdown("#### 🎯 設定顧客風味偏好（0~5 分）：")
            sc1, sc2, sc3, sc4, sc5 = st.columns(5)
            with sc1:
                sw = st.slider("甜度 (Sweet)", 0.0, 5.0, 3.0, 0.5)
            with sc2:
                so = st.slider("酸度 (Sour)", 0.0, 5.0, 4.0, 0.5)
            with sc3:
                al = st.slider("酒感 (Alcohol)", 0.0, 5.0, 4.0, 0.5)
            with sc4:
                bi = st.slider("苦甜 (Bitter)", 0.0, 5.0, 2.0, 0.5)
            with sc5:
                pe = st.slider("泥煤 (Peat)", 0.0, 5.0, 1.0, 0.5)

            if st.form_submit_button("💾 儲存熟客檔案並建立風味雷達", use_container_width=True):
                if n_name.strip():
                    add_customer(n_name.strip(), n_phone.strip(), n_tier, n_drink, n_seat, n_notes, sw, so, al, bi, pe)
                    st.success(f"🎉 成功建立【{n_name}】的 VIP 熟客檔案！")
                    st.rerun()
                else:
                    st.error("請輸入顧客姓名！")

        st.divider()
        st.markdown("### 🍾 登記全新寄酒 (Bottle Registration)")
        with st.form("add_new_bottle_form", clear_on_submit=True):
            b1, b2 = st.columns(2)
            with b1:
                b_owner = st.selectbox("選擇寄酒顧客：", customers_df["name"].tolist() if not customers_df.empty else ["現場貴賓"])
                b_phone = st.text_input("聯絡電話", placeholder="例：0912-345-678")
            with b2:
                b_name = st.text_input("寄放酒品名稱 *", placeholder="例：麥卡倫 12 年雙桶雪莉 (Macallan 12Y 700ml)")
                b_ml = st.number_input("原瓶容量 (ml) *", min_value=100.0, value=700.0, step=50.0)

            b_date = st.date_input("開瓶寄存日期", value=datetime.today())
            if st.form_submit_button("🍾 登記開瓶寄放並列印存根聯", use_container_width=True):
                if b_name.strip():
                    add_bottle_keep(b_owner, b_phone, b_name.strip(), b_ml, str(b_date))
                    st.success(f"🎉 成功為【{b_owner}】登記寄放【{b_name}】！")
                    st.rerun()
