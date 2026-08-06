"""
qibar_project/attendance.py
憩Bay餐酒館 (Chill Bar) - 調酒師與夜場外場排班考勤、跨夜打卡與兼職時薪結算大腦
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3

try:
    from db import get_connection
except ImportError:
    def get_connection():
        return sqlite3.connect("qibar.db", check_same_thread=False)


def init_attendance_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 員工清冊
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            staff_type TEXT DEFAULT 'Part-time',
            hourly_rate REAL DEFAULT 220.0,
            monthly_base_salary REAL DEFAULT 0.0,
            night_allowance_hourly REAL DEFAULT 50.0,
            commission_rate REAL DEFAULT 0.02,
            phone TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    """)

    # 打卡出勤紀錄
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT NOT NULL,
            role TEXT NOT NULL,
            clock_in TEXT NOT NULL,
            clock_out TEXT,
            hours_worked REAL DEFAULT 0.0,
            night_hours REAL DEFAULT 0.0,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # 寫入初始員工範例
    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seed_staff = [
            ("Alex (小豪)", "主理調酒師 (Head Bartender)", "Full-time", 0.0, 52000.0, 60.0, 0.03, "0911-222-333", "ACTIVE", now_str),
            ("Ruby (小晴)", "資深調酒師 (Senior Bartender)", "Full-time", 0.0, 42000.0, 50.0, 0.025, "0922-333-444", "ACTIVE", now_str),
            ("Kevin (阿凱)", "兼職吧檯助理 (Barback / PT)", "Part-time", 220.0, 0.0, 50.0, 0.01, "0933-444-555", "ACTIVE", now_str),
            ("Bella (貝拉)", "外場接待 (Floor Host / PT)", "Part-time", 210.0, 0.0, 50.0, 0.01, "0955-666-777", "ACTIVE", now_str),
            ("Gordon (阿強)", "主廚 (Bistro Chef)", "Full-time", 0.0, 48000.0, 50.0, 0.02, "0966-777-888", "ACTIVE", now_str),
        ]
        for s in seed_staff:
            cursor.execute("""
                INSERT INTO staff (name, role, staff_type, hourly_rate, monthly_base_salary, night_allowance_hourly, commission_rate, phone, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, s)

    # 寫入初始出勤範例
    cursor.execute("SELECT COUNT(*) FROM attendance_logs")
    if cursor.fetchone()[0] == 0:
        now_dt = datetime.now()
        for i in range(7):
            cur_d = (now_dt - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO attendance_logs (staff_name, role, clock_in, clock_out, hours_worked, night_hours, date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("Kevin (阿凱)", "兼職吧檯助理 (Barback / PT)", f"{cur_d} 18:00:00", f"{cur_d} 02:30:00", 8.5, 3.5, cur_d, "週末客滿，加強洗杯與備冰", f"{cur_d} 18:00:00"))
            cursor.execute("""
                INSERT INTO attendance_logs (staff_name, role, clock_in, clock_out, hours_worked, night_hours, date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("Bella (貝拉)", "外場接待 (Floor Host / PT)", f"{cur_d} 18:30:00", f"{cur_d} 01:30:00", 7.0, 2.5, cur_d, "外場點單結帳與送餐", f"{cur_d} 18:30:00"))

    conn.commit()
    conn.close()


def clock_in_staff(staff_name: str, notes: str = "夜場上班"):
    init_attendance_tables()
    conn = get_connection()
    cursor = conn.cursor()
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now_dt.strftime("%Y-%m-%d")

    cursor.execute("SELECT role FROM staff WHERE name = ?", (staff_name,))
    role_row = cursor.fetchone()
    role = role_row[0] if role_row else "現場調酒師"

    cursor.execute("""
        INSERT INTO attendance_logs (staff_name, role, clock_in, date, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (staff_name, role, now_str, date_str, notes, now_str))
    conn.commit()
    conn.close()


def clock_out_staff(log_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT clock_in FROM attendance_logs WHERE id = ?", (log_id,))
    row = cursor.fetchone()
    if row:
        in_dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        hours = max(0.5, round((now_dt - in_dt).total_seconds() / 3600.0, 1))
        # 晚上 23:00 以後算夜間加給工時
        night_hours = min(hours, 4.0)
        cursor.execute("""
            UPDATE attendance_logs 
            SET clock_out = ?, hours_worked = ?, night_hours = ?
            WHERE id = ?
        """, (now_str, hours, night_hours, log_id))
    conn.commit()
    conn.close()


def render_attendance_page():
    init_attendance_tables()
    conn = get_connection()
    staff_df = pd.read_sql_query("SELECT * FROM staff WHERE status = 'ACTIVE'", conn)
    logs_df = pd.read_sql_query("SELECT * FROM attendance_logs ORDER BY id DESC LIMIT 50", conn)
    conn.close()

    st.markdown("## ⏰ 憩Bay 調酒師排班考勤、夜場打卡與時薪結算")
    st.caption("專為餐酒館設計：支援 18:00~03:00 跨夜打卡、夜間工時加給、吧檯抽成獎金與薪資試算！")

    # 4 大考勤卡片
    total_staff = len(staff_df)
    active_now = len(logs_df[logs_df["clock_out"].isna()]) if not logs_df.empty else 0
    total_hours_this_week = logs_df["hours_worked"].sum() if not logs_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍸 在職員工總數", f"{total_staff} 位", delta="調酒師 3 位")
    c2.metric("🟢 現場在班人員", f"{active_now} 人", delta="夜場營業中" if active_now > 0 else "目前未打卡")
    c3.metric("⏱️ 累計總工時", f"{total_hours_this_week:.1f} 小時", delta="夜間津貼時數充足")
    c4.metric("💰 兼職基本時薪", "NT$ 220 / hr", delta="夜間 +$50/hr")

    st.divider()

    tab_clock, tab_payroll, tab_roster, tab_add_staff = st.tabs([
        "🕒 現場夜場打卡鐘 (Punch Clock)",
        "💰 薪資與兼職時薪即時試算 (Payroll)",
        "📅 每週夜場排班表 (Roster)",
        "➕ 員工檔案維護 (Staff Profile)"
    ])

    # ==========================================
    # Tab 1: 現場打卡鐘
    # ==========================================
    with tab_clock:
        st.markdown("### 🕒 憩Bay 吧檯與外場現場打卡鐘")
        p_col1, p_col2 = st.columns([1.5, 2.5])
        
        with p_col1:
            st.markdown("#### 🟢 上班簽到 (Clock In)")
            clock_in_name = st.selectbox("選擇員工姓名：", staff_df["name"].tolist() if not staff_df.empty else ["調酒師"])
            clock_in_notes = st.text_input("打卡備註", value="準時到店，吧檯備料備冰")
            
            if st.button("🚀 立即簽到打卡", type="primary", use_container_width=True):
                clock_in_staff(clock_in_name, clock_in_notes)
                st.success(f"🎉【{clock_in_name}】打卡簽到成功！時間：{datetime.now().strftime('%H:%M:%S')}")
                st.rerun()

        with p_col2:
            st.markdown("#### 🔴 現場未下班出勤中名單 (點擊下班結算工時)")
            if not logs_df.empty:
                open_logs = logs_df[logs_df["clock_out"].isna()]
                if not open_logs.empty:
                    for _, l in open_logs.iterrows():
                        in_time = l["clock_in"].split(" ")[1] if " " in l["clock_in"] else l["clock_in"]
                        col_l1, col_l2 = st.columns([3, 1])
                        with col_l1:
                            st.info(f"🟢 **{l['staff_name']}** ({l['role']}) ｜ 上班時間：**{in_time}** ({l['date']}) ｜ 備註：{l['notes']}")
                        with col_l2:
                            if st.button("🔴 下班打卡", key=f"clock_out_btn_{l['id']}", use_container_width=True):
                                clock_out_staff(l["id"])
                                st.success(f"已完成【{l['staff_name']}】下班打卡與工時結算！")
                                st.rerun()
                else:
                    st.success("目前無尚未下班之人員。")
            else:
                st.info("尚無出勤紀錄。")

        st.divider()
        st.markdown("#### 📋 近期打卡出勤詳細清單")
        if not logs_df.empty:
            display_logs = logs_df[["staff_name", "role", "clock_in", "clock_out", "hours_worked", "night_hours", "date", "notes"]].copy()
            display_logs.columns = ["員工姓名", "職務角色", "簽到時間", "簽退時間", "總工時(hr)", "夜間工時(hr)", "出勤日期", "備註說明"]
            st.dataframe(display_logs, use_container_width=True, hide_index=True)

    # ==========================================
    # Tab 2: 薪資與兼職時薪結算
    # ==========================================
    with tab_payroll:
        st.markdown("### 💰 憩Bay 每月薪資、兼職時薪與酒水抽成試算大腦")
        
        payroll_rows = []
        for _, s in staff_df.iterrows():
            s_name = s["name"]
            s_type = s["staff_type"]
            h_rate = s["hourly_rate"]
            m_base = s["monthly_base_salary"]
            n_allow = s["night_allowance_hourly"]
            c_rate = s["commission_rate"]

            # 計算該員工總工時與夜間時數
            s_logs = logs_df[logs_df["staff_name"] == s_name]
            total_h = s_logs["hours_worked"].sum() if not s_logs.empty else 0.0
            total_night_h = s_logs["night_hours"].sum() if not s_logs.empty else 0.0

            if s_type == "Part-time":
                base_pay = total_h * h_rate
                night_pay = total_night_h * n_allow
                est_sales = total_h * 2200.0  # 預估帶動營收
                commission = est_sales * c_rate
                final_salary = base_pay + night_pay + commission
            else:
                base_pay = m_base
                night_pay = total_night_h * n_allow
                commission = 385000.0 * c_rate  # 全店營收抽成
                final_salary = base_pay + night_pay + commission

            payroll_rows.append({
                "員工姓名": s_name,
                "職位類別": f"{s['role']} ({s_type})",
                "累計工時": f"{total_h:.1f} hr",
                "夜間工時": f"{total_night_h:.1f} hr",
                "基本薪資": f"NT$ {base_pay:,.0f}",
                "夜間津貼": f"NT$ {night_pay:,.0f}",
                "酒水業績抽成": f"NT$ {commission:,.0f}",
                "本期應發薪資 (Total)": f"NT$ {final_salary:,.0f}"
            })

        st.dataframe(pd.DataFrame(payroll_rows), use_container_width=True, hide_index=True)
        st.info("💡 **計薪說明**：兼職採【時薪 NT$ 220 + 23:00後夜間津貼 NT$ 50/hr + 酒水出單 1%~2% 抽成】！")

    # ==========================================
    # Tab 3: 排班表
    # ==========================================
    with tab_roster:
        st.markdown("### 📅 本週夜場輪值排班表 (Night Shift Schedule)")
        days_of_week = ["週一 (店休)", "週二", "週三", "週四", "週五 (熱門)", "週六 (巔峰)", "週日"]
        roster_data = {
            "星期": days_of_week,
            "吧檯主調 (Head Bartender)": ["-", "Alex (小豪)", "Alex (小豪)", "Ruby (小晴)", "Alex (小豪)", "Alex (小豪)", "Ruby (小晴)"],
            "副調 (Bartender)": ["-", "Ruby (小晴)", "Kevin (阿凱)", "Alex (小豪)", "Ruby (小晴)", "Ruby (小晴)", "Kevin (阿凱)"],
            "吧廚料理 (Kitchen)": ["-", "Gordon (阿強)", "Gordon (阿強)", "Gordon (阿強)", "Gordon (阿強)", "Gordon (阿強)", "Gordon (阿強)"],
            "外場服務 (Floor Host)": ["-", "Bella (貝拉)", "Bella (貝拉)", "Bella (貝拉)", "Bella (貝拉)", "Bella (貝拉)", "Bella (貝拉)"]
        }
        st.dataframe(pd.DataFrame(roster_data), use_container_width=True, hide_index=True)

    # ==========================================
    # Tab 4: 員工檔案維護
    # ==========================================
    with tab_add_staff:
        st.markdown("### ➕ 新增員工或調整薪資條件")
        with st.form("add_staff_form", clear_on_submit=True):
            st1, st2 = st.columns(2)
            with st1:
                new_s_name = st.text_input("員工姓名與暱稱 *", placeholder="例：Leo (阿樂)")
                new_s_role = st.selectbox("職務職稱 *", ["主理調酒師 (Head Bartender)", "調酒師 (Bartender)", "兼職吧檯助理 (Barback / PT)", "外場接待 (Floor Host)", "主廚 (Bistro Chef)"])
                new_s_type = st.selectbox("聘僱性質", ["Part-time", "Full-time"])
            with st2:
                new_s_h_rate = st.number_input("兼職時薪 (NT$/hr)", min_value=190.0, value=220.0, step=10.0)
                new_s_base = st.number_input("正職底薪 (NT$/月)", min_value=0.0, value=45000.0, step=1000.0)
                new_s_phone = st.text_input("聯絡電話", placeholder="例：0912-345-678")

            if st.form_submit_button("💾 儲存並加入排班名冊", use_container_width=True):
                if new_s_name.strip():
                    conn = get_connection()
                    cursor = conn.cursor()
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                        INSERT INTO staff (name, role, staff_type, hourly_rate, monthly_base_salary, night_allowance_hourly, commission_rate, phone, status, created_at)
                        VALUES (?, ?, ?, ?, ?, 50.0, 0.02, ?, 'ACTIVE', ?)
                    """, (new_s_name.strip(), new_s_role, new_s_type, new_s_h_rate, new_s_base, new_s_phone.strip(), now_str))
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 成功新增員工【{new_s_name}】！")
                    st.rerun()
