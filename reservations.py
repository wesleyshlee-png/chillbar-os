"""
qibar_project/reservations.py
憩Bay餐酒館 (Chill Bar) - 席位預約、沙發 VIP 包廂低消檢核與報到點餐系統
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

try:
    from db import get_connection
except ImportError:
    def get_connection():
        return sqlite3.connect("qibar.db", check_same_thread=False)


def init_reservations_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 預約資料表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            party_size INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            table_type TEXT NOT NULL,
            min_spend REAL DEFAULT 0.0,
            deposit_amount REAL DEFAULT 0.0,
            special_requests TEXT,
            status TEXT DEFAULT 'CONFIRMED',
            created_at TEXT NOT NULL
        )
    """)

    # 寫入初始預約範例
    cursor.execute("SELECT COUNT(*) FROM reservations")
    if cursor.fetchone()[0] == 0:
        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d")
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        seed_bookings = [
            ("Wesley Lee", "0912-345-678", 2, date_str, "20:00", "吧檯席 01", 0.0, 0.0, "慶生夜酌，需要 2 份義麵套餐", "SEATED", now_str),
            ("Jennifer Lin", "0922-111-222", 6, date_str, "21:30", "沙發 VIP 包廂", 6000.0, 2000.0, "VIP 包廂低消 NT$6,000，已預收訂金 $2,000", "CONFIRMED", now_str),
            ("Michael Chen", "0933-888-999", 4, date_str, "22:00", "高腳桌 A", 2000.0, 500.0, "開波本威士忌純飲，加點炸物雙拼", "CONFIRMED", now_str),
            ("Emily Wang", "0955-666-777", 2, (now_dt + timedelta(days=1)).strftime("%Y-%m-%d"), "20:30", "吧檯席 03", 0.0, 0.0, "兩位品嚐特色調酒", "CONFIRMED", now_str),
        ]
        for b in seed_bookings:
            cursor.execute("""
                INSERT INTO reservations (guest_name, phone, party_size, booking_date, booking_time, table_type, min_spend, deposit_amount, special_requests, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, b)

    conn.commit()
    conn.close()


def add_reservation(name: str, phone: str, size: int, b_date: str, b_time: str, table: str, min_spend: float, deposit: float, notes: str):
    init_reservations_tables()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO reservations (guest_name, phone, party_size, booking_date, booking_time, table_type, min_spend, deposit_amount, special_requests, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?)
    """, (name, phone, size, b_date, b_time, table, min_spend, deposit, notes, now_str))
    conn.commit()
    conn.close()


def update_reservation_status(res_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reservations SET status = ? WHERE id = ?", (new_status, res_id))
    conn.commit()
    conn.close()


def render_reservations_page():
    init_reservations_tables()
    conn = get_connection()
    res_df = pd.read_sql_query("SELECT * FROM reservations ORDER BY booking_date ASC, booking_time ASC", conn)
    conn.close()

    st.markdown("## 🪑 憩Bay 席位預約、沙發 VIP 包廂低消與報到管理")
    st.caption("輕鬆控管全店 4 大席位區域（吧檯席、高腳桌、沙發 VIP 包廂與露天席），支援包廂低消檢核與定金記錄！")

    # 4 大預約指標卡
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_res = res_df[res_df["booking_date"] == today_str]
    today_seated = len(today_res[today_res["status"] == "SEATED"])
    today_confirmed = len(today_res[today_res["status"] == "CONFIRMED"])
    total_deposit = res_df["deposit_amount"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 今日預約組數", f"{len(today_res)} 組", delta="熱門夜場滿座")
    c2.metric("🟢 已報到入座", f"{today_seated} 組", delta="點餐出單中")
    c3.metric("⏳ 待到店確認", f"{today_confirmed} 組", delta="電話提醒就緒")
    c4.metric("💳 預收訂金總額", f"NT$ {total_deposit:,.0f}", delta="包廂低消保障")

    st.divider()

    tab_tables, tab_book_list, tab_new_book = st.tabs([
        "🗺️ 全店席位狀態圖 (Floor Map)",
        "📋 預約名冊與報到入座 (Bookings)",
        "➕ 現場/電話新增預約 (New Booking)"
    ])

    # ==========================================
    # Tab 1: 全店席位狀態圖
    # ==========================================
    with tab_tables:
        st.markdown("### 🗺️ 憩Bay 全店 4 大席位分區與低消規範")
        
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("""
            <div style="background:#FFFFFF; border:2px solid #FFB5C5; border-radius:18px; padding:18px; box-shadow:0 6px 18px rgba(255,107,139,0.12);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-size:16px; font-weight:900; color:#0F172A;">🍸 1. 吧檯席 (Bar Seats: 01 ~ 06)</h4>
                    <span style="font-size:11px; background:#ECFDF5; color:#047857; padding:2px 8px; border-radius:20px; font-weight:800;">免低消</span>
                </div>
                <p style="font-size:12px; color:#64748B; margin:8px 0 0 0;">共 6 席高腳吧檯席，可近距離欣賞調酒師特調演出！</p>
                <div style="display:flex; gap:8px; margin-top:12px;">
                    <span style="padding:6px 12px; background:#FFF0F3; color:#E11D48; border-radius:10px; font-weight:800; font-size:12px;">01 (入座中)</span>
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">02 (空席)</span>
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">03 (已預約)</span>
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">04 (空席)</span>
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">05 (空席)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            st.markdown("""
            <div style="background:#FFFFFF; border:2px solid #E2E8F0; border-radius:18px; padding:18px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-size:16px; font-weight:900; color:#0F172A;">🥂 2. 高腳桌區 (High Tables: A ~ D)</h4>
                    <span style="font-size:11px; background:#FEF3C7; color:#92400E; padding:2px 8px; border-radius:20px; font-weight:800;">低消 $500/人</span>
                </div>
                <p style="font-size:12px; color:#64748B; margin:8px 0 0 0;">適合 2~4 人好友聚會、品嚐炸物與生啤酒！</p>
                <div style="display:flex; gap:8px; margin-top:12px;">
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">高腳 A (已預約)</span>
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">高腳 B (空席)</span>
                    <span style="padding:6px 12px; background:#F8FAFC; color:#64748B; border-radius:10px; font-weight:800; font-size:12px;">高腳 C (空席)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with t2:
            st.markdown("""
            <div style="background:#FFFFFF; border:2px solid #FDE68A; border-radius:18px; padding:18px; box-shadow:0 6px 18px rgba(245,158,11,0.12);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-size:16px; font-weight:900; color:#92400E;">👑 3. 沙發 VIP 包廂 (VIP Lounge Booth)</h4>
                    <span style="font-size:11px; background:#FEF3C7; color:#92400E; padding:2px 8px; border-radius:20px; font-weight:800;">包廂低消 NT$ 6,000</span>
                </div>
                <p style="font-size:12px; color:#64748B; margin:8px 0 0 0;">可容納 6~10 人隱密聚會，享專屬調酒侍酒與大螢幕娛樂！</p>
                <div style="display:flex; gap:8px; margin-top:12px;">
                    <span style="padding:6px 12px; background:#FEF3C7; color:#92400E; border-radius:10px; font-weight:800; font-size:12px;">👑 VIP 沙發包廂 (21:30 預約)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            st.markdown("""
            <div style="background:#FFFFFF; border:2px solid #E2E8F0; border-radius:18px; padding:18px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-size:16px; font-weight:900; color:#0F172A;">🌿 4. 戶外露天雅席 (Patio Lounge)</h4>
                    <span style="font-size:11px; background:#ECFDF5; color:#047857; padding:2px 8px; border-radius:20px; font-weight:800;">低消 $350/人</span>
                </div>
                <p style="font-size:12px; color:#64748B; margin:8px 0 0 0;">微風吹拂、夜景相伴，適合輕鬆夜酌與精釀啤酒！</p>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # Tab 2: 預約名冊與報到
    # ==========================================
    with tab_book_list:
        st.markdown("### 📋 憩Bay 預約名冊清單")
        if not res_df.empty:
            for _, r in res_df.iterrows():
                is_seated = (r["status"] == "SEATED")
                card_bg = "#ECFDF5" if is_seated else "#FFFFFF"
                border_c = "#10B981" if is_seated else "#F1E5D8"

                r_col1, r_col2, r_col3 = st.columns([3, 1.5, 1.5])
                with r_col1:
                    st.markdown(f"""
                    <div style="background:{card_bg}; border:1.5px solid {border_c}; border-radius:14px; padding:12px;">
                        <h4 style="margin:0; font-size:15px; font-weight:900; color:#0F172A;">{r['guest_name']} ({r['party_size']} 位) ｜ {r['table_type']}</h4>
                        <p style="margin:4px 0; font-size:12px; color:#64748B;">預約時間：<b>{r['booking_date']} {r['booking_time']}</b> ｜ 電話：{r['phone']}</p>
                        <p style="margin:2px 0 0 0; font-size:11px; color:#E11D48;">特殊需求：{r['special_requests']} ｜ 預收訂金：NT$ {r['deposit_amount']:,.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with r_col2:
                    st.write("")
                    if r["status"] == "CONFIRMED":
                        if st.button("🟢 貴賓報到入座", key=f"seat_btn_{r['id']}", type="primary", use_container_width=True):
                            update_reservation_status(r["id"], "SEATED")
                            st.success(f"已為【{r['guest_name']}】完成報到入座！")
                            st.rerun()
                    else:
                        st.markdown("<p style='color:#059669; font-weight:800; font-size:13px; text-align:center; padding-top:10px;'>✅ 已入座消費中</p>", unsafe_allow_html=True)

                with r_col3:
                    st.write("")
                    if st.button("❌ 取消預約", key=f"cancel_btn_{r['id']}", use_container_width=True):
                        update_reservation_status(r["id"], "CANCELLED")
                        st.warning(f"已取消【{r['guest_name']}】的預約！")
                        st.rerun()
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        else:
            st.info("目前無預約紀錄。")

    # ==========================================
    # Tab 3: 新增預約
    # ==========================================
    with tab_new_book:
        st.markdown("### ➕ 現場 / 電話快速登記預約")
        with st.form("new_res_form", clear_on_submit=True):
            r1, r2 = st.columns(2)
            with r1:
                b_name = st.text_input("貴賓姓名 *", placeholder="例：陳先生 / Ken")
                b_phone = st.text_input("聯絡手機 *", placeholder="例：0912-345-678")
                b_size = st.number_input("預約人數 *", min_value=1, max_value=20, value=2)
            with r2:
                b_table = st.selectbox("指定席位區域 *", ["吧檯席 01", "吧檯席 02", "吧檯席 03", "高腳桌 A", "高腳桌 B", "沙發 VIP 包廂 (低消$6,000)", "戶外露天席"])
                b_date = st.date_input("預約日期", value=datetime.today())
                b_time = st.selectbox("預約到店時段", ["19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30", "00:00"])

            r3, r4 = st.columns(2)
            with r3:
                b_deposit = st.number_input("預收訂金金額 (NT$)", min_value=0.0, value=2000.0 if "VIP" in b_table else 0.0, step=500.0)
            with r4:
                b_notes = st.text_input("特殊需求與招待備註", placeholder="例：朋友慶生、自帶香檳開瓶、不加冰塊")

            min_spend_calc = 6000.0 if "VIP" in b_table else (b_size * 500.0 if "高腳" in b_table else 0.0)

            if st.form_submit_button("🚀 立即完成預約登記", use_container_width=True):
                if b_name.strip() and b_phone.strip():
                    add_reservation(b_name.strip(), b_phone.strip(), b_size, str(b_date), b_time, b_table, min_spend_calc, b_deposit, b_notes.strip())
                    st.success(f"🎉 成功為【{b_name}】預約【{b_table}】（時段：{b_date} {b_time}）！")
                    st.rerun()
                else:
                    st.error("請輸入貴賓姓名與電話！")
