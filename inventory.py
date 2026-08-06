"""
qibar_project/inventory.py
憩bar餐酒館 (QiBar) - 庫存管理與低庫存自動預警模組
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3

try:
    from db import get_connection
except ImportError:
    def get_connection():
        return sqlite3.connect("qibar.db", check_same_thread=False)


def init_inventory_table():
    """確保 inventory 資料表存在"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            current_stock REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL,
            safety_stock REAL NOT NULL DEFAULT 5,
            cost_price REAL NOT NULL DEFAULT 0,
            selling_price REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_inventory_df() -> pd.DataFrame:
    """載入庫存資料並回傳 DataFrame"""
    init_inventory_table()
    conn = get_connection()
    query = """
        SELECT id, name, category, current_stock, unit, 
               safety_stock, cost_price, selling_price, updated_at
        FROM inventory
        ORDER BY category ASC, name ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def add_or_update_item(name: str, category: str, stock: float, unit: str, 
                       safety_stock: float, cost: float, price: float, item_id: int = None):
    """新增或更新庫存品項"""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if item_id:
        cursor.execute("""
            UPDATE inventory
            SET name = ?, category = ?, current_stock = ?, unit = ?, 
                safety_stock = ?, cost_price = ?, selling_price = ?, updated_at = ?
            WHERE id = ?
        """, (name, category, stock, unit, safety_stock, cost, price, now_str, item_id))
    else:
        cursor.execute("""
            INSERT INTO inventory (name, category, current_stock, unit, safety_stock, cost_price, selling_price, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, stock, unit, safety_stock, cost, price, now_str))

    conn.commit()
    conn.close()


def adjust_stock_quantity(item_id: int, delta_quantity: float, reason: str = ""):
    """快速調整庫存數量"""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE inventory
        SET current_stock = MAX(0, current_stock + ?),
            updated_at = ?
        WHERE id = ?
    """, (delta_quantity, now_str, item_id))

    conn.commit()
    conn.close()


def delete_inventory_item(item_id: int):
    """刪除指定品項"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def render_stock_level_chart(df: pd.DataFrame):
    """繪製即時庫存與安全警戒線對比圖"""
    if df.empty:
        st.info("尚無庫存數據可供視覺化呈現。")
        return

    chart_df = df.copy()
    chart_df["is_alert"] = chart_df["current_stock"] <= chart_df["safety_stock"]
    chart_df["status_color"] = chart_df["is_alert"].apply(
        lambda x: "#F43F5E" if x else "#38BDF8"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=chart_df["name"],
        y=chart_df["current_stock"],
        name="當前庫存",
        marker_color=chart_df["status_color"],
        hovertemplate="<b>%{x}</b><br>當前庫存: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=chart_df["name"],
        y=chart_df["safety_stock"],
        name="安全庫存警戒線",
        mode="lines+markers",
        line=dict(color="#FFB703", width=2, dash="dot"),
        marker=dict(size=6, color="#FB8500"),
        hovertemplate="安全警戒線: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="🍸 即時庫存水位 vs 安全庫存監控圖",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="sans-serif"),
        xaxis=dict(gridcolor="#F1F5F9", tickangle=-45),
        yaxis=dict(gridcolor="#F1F5F9", title="數量"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=80),
        height=380
    )

    st.plotly_chart(fig, use_container_width=True)


def render_category_donut_chart(df: pd.DataFrame):
    """繪製分類庫存總價值分佈圓環圖"""
    if df.empty:
        return

    chart_df = df.copy()
    chart_df["total_value"] = chart_df["current_stock"] * chart_df["cost_price"]
    cat_summary = chart_df.groupby("category", as_index=False)["total_value"].sum()
    colors = ["#38BDF8", "#EC4899", "#8B5CF6", "#F59E0B", "#10B981", "#6366F1", "#F43F5E"]

    fig = px.pie(
        cat_summary,
        names="category",
        values="total_value",
        title="🍷 各品類庫存價值分佈 (成本計算法)",
        hole=0.5,
        color_discrete_sequence=colors
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0F172A"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=320
    )

    st.plotly_chart(fig, use_container_width=True)


def render_inventory_page():
    """庫存管理主介面入口"""
    st.markdown("## 🍾 憩bar 庫存管理與預警監控")
    st.caption("即時掌控吧檯基酒、副料與食材水位，自動偵測斷貨危機。")

    df = get_inventory_df()

    categories = [
        "烈酒/基酒 (Spirits)", "葡萄酒/香檳 (Wine)", "精釀啤酒 (Beer)", 
        "香甜酒/利口酒 (Liqueur)", "糖漿/果汁/副料 (Mixers)", 
        "生鮮水果/食材 (Food)", "吧檯耗材 (Consumables)"
    ]
    units = ["瓶 (Btl)", "罐 (Can)", "毫升 (ml)", "公斤 (kg)", "克 (g)", "份 (Portion)", "包 (Pack)"]

    total_items = len(df)
    low_stock_df = df[df["current_stock"] <= df["safety_stock"]] if not df.empty else pd.DataFrame()
    low_stock_count = len(low_stock_df)
    healthy_count = total_items - low_stock_count
    total_asset_value = (df["current_stock"] * df["cost_price"]).sum() if not df.empty else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 總在庫品項", f"{total_items} 款")
    col2.metric("✅ 水位正常", f"{healthy_count} 款")
    col3.metric("⚠️ 低庫存警戒", f"{low_stock_count} 款", delta=f"-{low_stock_count}" if low_stock_count > 0 else "0", delta_color="inverse")
    col4.metric("💰 庫存總資產成本", f"NT$ {total_asset_value:,.0f}")

    st.divider()

    if low_stock_count > 0:
        st.error(f"🚨 **即時預警**：目前有 **{low_stock_count}** 項酒水/食材庫存已低於安全水位，請儘速採購補貨！")
        with st.expander("🔻 點擊查看需立即補貨之品項清單", expanded=True):
            alert_display_df = low_stock_df[["name", "category", "current_stock", "safety_stock", "unit", "cost_price"]].copy()
            alert_display_df.columns = ["品項名稱", "分類", "現有庫存", "安全警戒線", "單位", "進貨成本 (NT$)"]
            st.dataframe(alert_display_df, use_container_width=True, hide_index=True)
    else:
        st.success("✨ 目前吧檯與廚房所有品項庫存充足，無斷貨風險！")

    tab_overview, tab_adjust, tab_manage = st.tabs([
        "📊 庫存總覽與視覺化", 
        "⚡ 快速進出庫 / 耗損盤點", 
        "⚙️ 品項建檔與資料維護"
    ])

    with tab_overview:
        c1, c2 = st.columns([1.8, 1.2])
        with c1:
            render_stock_level_chart(df)
        with c2:
            render_category_donut_chart(df)

        st.markdown("### 📋 完整庫存清冊")
        
        f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1])
        with f_col1:
            search_query = st.text_input("🔍 搜尋品名", placeholder="輸入品項名稱關鍵字...", key="inv_search")
        with f_col2:
            selected_cat = st.selectbox("🗂️ 依分類篩選", ["全部分類"] + categories, key="inv_cat_filter")
        with f_col3:
            only_low_stock = st.checkbox("僅看低庫存", key="inv_only_low")

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["name"].str.contains(search_query, case=False, na=False)]
        if selected_cat != "全部分類":
            filtered_df = filtered_df[filtered_df["category"] == selected_cat]
        if only_low_stock:
            filtered_df = filtered_df[filtered_df["current_stock"] <= filtered_df["safety_stock"]]

        if not filtered_df.empty:
            display_table = filtered_df.copy()
            display_table["庫存總值 (成本)"] = display_table["current_stock"] * display_table["cost_price"]
            
            display_table = display_table[[
                "id", "name", "category", "current_stock", "safety_stock", 
                "unit", "cost_price", "selling_price", "庫存總值 (成本)", "updated_at"
            ]]
            display_table.columns = [
                "ID", "品項名稱", "品類", "當前庫存", "安全庫存", 
                "單位", "進價 (NT$)", "售價 (NT$)", "在庫成本總值", "最後更新時間"
            ]
            st.dataframe(
                display_table.style.format({
                    "進價 (NT$)": "{:,.1f}",
                    "售價 (NT$)": "{:,.1f}",
                    "在庫成本總值": "NT$ {:,.0f}"
                }),
                use_container_width=True,
                hide_index=True
            )

            csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 匯出當前清冊為 CSV",
                data=csv_data,
                file_name=f"QiBar_Inventory_{datetime.now().strftime("%Y%m%d_%H%M")}.csv",
                mime="text/csv"
            )
        else:
            st.info("無符合篩選條件的庫存資料。")

    with tab_adjust:
        st.markdown("### ⚡ 現場快速庫存增減 (進貨 / 報廢耗損 / 調酒消耗)")
        if df.empty:
            st.warning("目前尚無品項，請先至「品項建檔」新增酒水。")
        else:
            item_options = {f"[{row["category"]}] {row["name"]} (現有: {row["current_stock"]} {row["unit"]})": row["id"] for _, row in df.iterrows()}
            
            with st.form("stock_adjust_form", clear_on_submit=True):
                selected_label = st.selectbox("選擇要異動的品項", list(item_options.keys()))
                target_id = item_options[selected_label]
                
                col_a, col_b, col_c = st.columns([1, 1, 1.5])
                with col_a:
                    action_type = st.radio("異動類型", ["進貨入庫 (+)", "耗損/調酒消耗 (-)"], horizontal=True)
                with col_b:
                    adjust_qty = st.number_input("異動數量", min_value=0.1, step=1.0, value=1.0)
                with col_c:
                    adjust_reason = st.text_input("異動備註 / 原因", placeholder="例：廠商每週進貨、碎瓶破片、客訂開酒")

                submitted = st.form_submit_button("確認送出庫存異動", use_container_width=True)
                if submitted:
                    final_delta = adjust_qty if "進貨" in action_type else -adjust_qty
                    adjust_stock_quantity(target_id, final_delta, adjust_reason)
                    st.success(f"庫存異動成功！已更新品項 ID: {target_id}")
                    st.rerun()

    with tab_manage:
        st.markdown("### ➕ 新增庫存品項")
        with st.form("add_item_form", clear_on_submit=True):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                new_name = st.text_input("品項名稱 *", placeholder="例：Hendrick's 亨利爵士琴酒")
                new_cat = st.selectbox("品項類別 *", categories)
                new_unit = st.selectbox("計量單位 *", units)
                new_stock = st.number_input("初始庫存數量 *", min_value=0.0, step=1.0, value=10.0)
            with col_m2:
                new_safety = st.number_input("安全庫存警戒線 *", min_value=0.0, step=1.0, value=3.0, help="當庫存小於等於此數值時觸發預警")
                new_cost = st.number_input("每單位進貨成本 (NT$)", min_value=0.0, step=10.0, value=850.0)
                new_price = st.number_input("單品售價 / 單杯定價 (NT$)", min_value=0.0, step=10.0, value=350.0)

            btn_add = st.form_submit_button("✨ 建立新品項", use_container_width=True)
            if btn_add:
                if not new_name.strip():
                    st.error("請填寫品項名稱！")
                else:
                    try:
                        add_or_update_item(
                            name=new_name.strip(),
                            category=new_cat,
                            stock=new_stock,
                            unit=new_unit,
                            safety_stock=new_safety,
                            cost=new_cost,
                            price=new_price
                        )
                        st.success(f"成功新增品項：{new_name}！")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("該品項名稱已存在，請使用不同名稱或至下方編輯修改。")

        st.divider()

        if not df.empty:
            st.markdown("### ✏️ 編輯 / 刪除既有品項")
            edit_options = {f"[{row["id"]}] {row["name"]}": row["id"] for _, row in df.iterrows()}
            selected_edit_label = st.selectbox("選擇要維護的品項", list(edit_options.keys()))
            edit_item_id = edit_options[selected_edit_label]
            target_row = df[df["id"] == edit_item_id].iloc[0]

            with st.form("edit_item_form"):
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    e_name = st.text_input("品項名稱", value=target_row["name"])
                    e_cat_idx = categories.index(target_row["category"]) if target_row["category"] in categories else 0
                    e_cat = st.selectbox("品項類別", categories, index=e_cat_idx)
                    e_unit_idx = units.index(target_row["unit"]) if target_row["unit"] in units else 0
                    e_unit = st.selectbox("單位", units, index=e_unit_idx)
                    e_stock = st.number_input("當前庫存", min_value=0.0, value=float(target_row["current_stock"]))
                with e_col2:
                    e_safety = st.number_input("安全庫存警戒線", min_value=0.0, value=float(target_row["safety_stock"]))
                    e_cost = st.number_input("進貨成本 (NT$)", min_value=0.0, value=float(target_row["cost_price"]))
                    e_price = st.number_input("單品售價 (NT$)", min_value=0.0, value=float(target_row["selling_price"]))

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    btn_save_edit = st.form_submit_button("💾 儲存修改", use_container_width=True)
                with col_btn2:
                    btn_delete = st.form_submit_button("🗑️ 刪除此品項", use_container_width=True)

                if btn_save_edit:
                    add_or_update_item(e_name, e_cat, e_stock, e_unit, e_safety, e_cost, e_price, item_id=edit_item_id)
                    st.success("品項資料已更新！")
                    st.rerun()

                if btn_delete:
                    delete_inventory_item(edit_item_id)
                    st.warning(f"品項 {e_name} 已成功刪除！")
                    st.rerun()
