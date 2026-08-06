"""
qibar_project/orders.py
憩Bay餐酒館 (Chill Bar) - 官方真實菜單 POS 點餐、配方庫存自動扣減與即時修改系統
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3

try:
    from db import get_connection, init_db
except ImportError:
    def get_connection():
        return sqlite3.connect("qibar.db", check_same_thread=False)
    def init_db():
        pass


def load_official_menu() -> dict:
    """從資料庫讀取全套官方真實菜單"""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM menu_items ORDER BY id ASC", conn)
    conn.close()

    menu_dict = {}
    for _, r in df.iterrows():
        name = r["name"]
        price = float(r["selling_price"])
        cost = float(r["cost_price"])
        cat = r["category"]
        menu_dict[name] = {
            "price": price,
            "cost": cost,
            "category": cat
        }
    return menu_dict


def update_official_menu_item(old_name: str, new_name: str, new_cat: str, new_price: float, new_cost: float):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE menu_items 
        SET name = ?, category = ?, cost_price = ?, selling_price = ?, updated_at = ?
        WHERE name = ?
    """, (new_name, new_cat, new_cost, new_price, now_str, old_name))

    cursor.execute("""
        UPDATE order_items 
        SET item_name = ?, category = ?, unit_price = ?, unit_cost = ?
        WHERE item_name = ?
    """, (new_name, new_cat, new_price, new_cost, old_name))

    conn.commit()
    conn.close()


def add_official_menu_item(name: str, cat: str, price: float, cost: float):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT OR REPLACE INTO menu_items (name, category, cost_price, selling_price, monthly_sales, updated_at)
        VALUES (?, ?, ?, ?, 80, ?)
    """, (name, cat, cost, price, now_str))
    conn.commit()
    conn.close()


def delete_official_menu_item(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu_items WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def process_pos_checkout(cart_dict: dict, table_name: str, customer_name: str, payment_method: str, menu_dict: dict) -> tuple:
    conn = get_connection()
    cursor = conn.cursor()
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now_dt.strftime("%Y%m%d")

    cursor.execute("SELECT COUNT(*) FROM orders")
    seq = cursor.fetchone()[0] + 1
    order_no = f"ORD-{date_str}-{seq:04d}"

    total_amount = 0.0
    total_cogs = 0.0
    deducted_summary = []
    low_stock_alerts = []

    for item_name, qty in cart_dict.items():
        if qty <= 0 or item_name not in menu_dict:
            continue
        
        info = menu_dict[item_name]
        u_price = info["price"]
        u_cost = info.get("cost", round(u_price * 0.28, 1))
        category = info["category"]
        
        item_total_price = u_price * qty
        item_total_cost = u_cost * qty
        total_amount += item_total_price
        total_cogs += item_total_cost

        # 寫入 order_items
        cursor.execute("""
            INSERT INTO order_items (order_number, item_name, category, quantity, unit_price, unit_cost, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (order_no, item_name, category, qty, u_price, u_cost, now_str))

        # 扣減庫存
        cursor.execute("SELECT current_stock, safety_stock FROM inventory WHERE name LIKE ?", (f"%{item_name[:3]}%",))
        inv_row = cursor.fetchone()
        if inv_row:
            curr_stock, s_stock = inv_row
            new_stock = max(0.0, curr_stock - (0.15 * qty))
            cursor.execute("UPDATE inventory SET current_stock = ?, updated_at = ? WHERE name LIKE ?", (new_stock, now_str, f"%{item_name[:3]}%"))
            deducted_summary.append(f"• 自動扣庫存：{item_name} 出單 {qty} 份 (剩餘庫存: {new_stock:.1f})")
            if new_stock <= s_stock:
                low_stock_alerts.append(f"⚠️ {item_name} 原物料庫存已低於安全線！")
        else:
            deducted_summary.append(f"• 銷售登記：{item_name} x {qty} (實收 NT$ {item_total_price:,.0f})")

    cursor.execute("""
        INSERT INTO orders (order_number, customer_name, table_number, total_amount, total_cost, payment_method, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_no, customer_name, table_name, total_amount, total_cogs, payment_method, "COMPLETED", now_str))

    conn.commit()
    conn.close()

    return order_no, total_amount, deducted_summary, low_stock_alerts


# ==========================================
# 現場 POS 主畫面
# ==========================================
def render_orders_page():
    menu_dict = load_official_menu()

    st.markdown("## 🍸 憩Bay 官方真實菜單 POS 點餐台")
    st.caption("內建【45+ 款官方精緻調酒、精釀啤酒、精選套餐、秘製滷味、主食與炸物】，支援現場點餐結帳與即時菜單調價！")

    # 頂部：快速手動修改菜單與售價工具
    with st.expander("✍️ 快速手動更新菜單與品項價格 (即時修改售價 / 成本 / 新增餐點)", expanded=False):
        tab_edit_price, tab_add_item, tab_del_item = st.tabs(["✏️ 修改品項售價與名稱", "➕ 新增全新調酒/料理", "🗑️ 下架品項"])

        with tab_edit_price:
            m_col1, m_col2 = st.columns([1.5, 2.5])
            with m_col1:
                sel_item = st.selectbox("選擇要修改的菜單品項：", list(menu_dict.keys()), key="pos_sel_edit_item")
            
            cur_info = menu_dict[sel_item]
            with m_col2:
                with st.form("edit_official_item_form", clear_on_submit=False):
                    f1, f2 = st.columns(2)
                    with f1:
                        new_name = st.text_input("品項名稱", value=sel_item)
                        cats = ["特色調酒茶酒", "生啤與經典調飲", "敲敲瓶裝精釀", "精選特惠套餐", "經典秘製滷味", "主食與烤物料理", "微醺下酒炸物", "無酒精茶飲"]
                        cat_idx = cats.index(cur_info["category"]) if cur_info["category"] in cats else 0
                        new_cat = st.selectbox("所屬分類", cats, index=cat_idx)
                    with f2:
                        new_price = st.number_input("現場單價 (NT$) *", min_value=1.0, value=float(cur_info["price"]), step=10.0)
                        new_cost = st.number_input("原物料成本 (NT$) *", min_value=1.0, value=float(cur_info["cost"]), step=5.0)

                    margin = ((new_price - new_cost) / new_price * 100) if new_price > 0 else 0
                    st.caption(f"💡 修改後單杯獲利：**NT$ {new_price - new_cost:,.0f}**（毛利率：**{margin:.1f}%**）")

                    if st.form_submit_button("💾 儲存並即時更新吧檯菜單", use_container_width=True):
                        update_official_menu_item(sel_item, new_name.strip(), new_cat, new_price, new_cost)
                        st.success(f"🎉 品項【{new_name}】售價已更新為 NT$ {new_price:,.0f}！左側點餐卡片已即時生效！")
                        st.rerun()

        with tab_add_item:
            with st.form("add_official_item_form", clear_on_submit=True):
                a1, a2 = st.columns(2)
                with a1:
                    add_name = st.text_input("全新調酒/料理名稱 *", placeholder="例：夏日限定蜜桃特調")
                    add_cat = st.selectbox("分類 *", ["特色調酒茶酒", "生啤與經典調飲", "敲敲瓶裝精釀", "精選特惠套餐", "經典秘製滷味", "主食與烤物料理", "微醺下酒炸物", "無酒精茶飲"])
                with a2:
                    add_price = st.number_input("設定售價 (NT$) *", min_value=10.0, value=250.0, step=10.0)
                    add_cost = st.number_input("預估成本 (NT$) *", min_value=1.0, value=65.0, step=5.0)

                if st.form_submit_button("➕ 建立新品項並加入點餐台", use_container_width=True):
                    if add_name.strip():
                        add_official_menu_item(add_name.strip(), add_cat, add_price, add_cost)
                        st.success(f"🎉 成功新增【{add_name}】！已加入點餐酒單！")
                        st.rerun()

        with tab_del_item:
            del_target = st.selectbox("選擇要下架的品項：", list(menu_dict.keys()), key="del_official_item")
            if st.button(f"確認下架【{del_target}】"):
                delete_official_menu_item(del_target)
                st.warning(f"已下架【{del_target}】！")
                st.rerun()

    st.markdown("---")

    # 初始化購物車
    if "pos_cart" not in st.session_state:
        st.session_state.pos_cart = {name: 0 for name in menu_dict.keys()}
    else:
        for k in menu_dict.keys():
            if k not in st.session_state.pos_cart:
                st.session_state.pos_cart[k] = 0

    pos_c1, pos_c2 = st.columns([1.6, 1.4])

    # ==========================================
    # 左側：視覺化酒單分類篩選與點餐卡片
    # ==========================================
    with pos_c1:
        st.markdown("### 📋 憩Bay 官方吧檯酒水與餐點選單")
        
        cat_filters = ["全部品項", "特色調酒茶酒", "生啤與經典調飲", "敲敲瓶裝精釀", "精選特惠套餐", "經典秘製滷味", "主食與烤物料理", "微醺下酒炸物", "無酒精茶飲"]
        sel_cat = st.selectbox("🎯 依官方菜單類別篩選：", cat_filters)

        col_grid1, col_grid2 = st.columns(2)

        idx = 0
        for name, data in menu_dict.items():
            if sel_cat != "全部品項" and data["category"] != sel_cat:
                continue

            target_col = col_grid1 if idx % 2 == 0 else col_grid2
            idx += 1

            with target_col:
                with st.container():
                    st.markdown(f"""
                        <div style="background:#FFFFFF; border:1.5px solid #F1E5D8; border-radius:16px; padding:14px; margin-bottom:10px; box-shadow:0 4px 14px rgba(180, 130, 110, 0.08);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h4 style="margin:0; font-size:14px; font-weight:800; color:#0F172A;">{name}</h4>
                                <span style="font-size:15px; font-weight:900; color:#FF4B72;">NT$ {data['price']:,.0f}</span>
                            </div>
                            <p style="margin:4px 0 8px 0; font-size:11px; color:#64748B;">類別：{data['category']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns([1.2, 1])
                    with btn_c1:
                        if st.button(f"➕ 點 1 份", key=f"btn_add_{name}", use_container_width=True):
                            st.session_state.pos_cart[name] = st.session_state.pos_cart.get(name, 0) + 1
                            st.rerun()
                    with btn_c2:
                        qty = st.session_state.pos_cart.get(name, 0)
                        if qty > 0:
                            if st.button(f"➖ 減 1 ({qty})", key=f"btn_sub_{name}", use_container_width=True):
                                st.session_state.pos_cart[name] = max(0, qty - 1)
                                st.rerun()
                        else:
                            st.caption("未點")

    # ==========================================
    # 右側：即時點單結帳台
    # ==========================================
    with pos_c2:
        st.markdown("### 🧾 即時點單結帳台 (Active Cart)")
        
        info_c1, info_c2 = st.columns(2)
        with info_c1:
            table_no = st.selectbox("席位桌號 *", ["吧檯席 01", "吧檯席 02", "高腳桌 A", "高腳桌 B", "沙發 VIP 包廂", "戶外露天席"])
        with info_c2:
            guest_name = st.text_input("貴賓稱呼", value="現場貴賓")

        pay_method = st.selectbox("支付管道 *", ["LINE Pay (掃碼)", "信用卡 / Apple Pay", "現金支付 (Cash)", "VIP 儲值扣款"])

        st.markdown("---")

        active_items = {k: v for k, v in st.session_state.pos_cart.items() if v > 0}

        if active_items:
            cart_rows = []
            cart_subtotal = 0.0

            for k, qty in active_items.items():
                price = menu_dict.get(k, {}).get("price", 250.0)
                subtot = price * qty
                cart_subtotal += subtot
                cart_rows.append({"品項": k, "單價": f"NT$ {price:,.0f}", "數量": f"{qty} 份", "小計": f"NT$ {subtot:,.0f}"})

            st.dataframe(pd.DataFrame(cart_rows), use_container_width=True, hide_index=True)

            service_charge = round(cart_subtotal * 0.1, 0)
            final_total = cart_subtotal + service_charge

            st.markdown(f"""
                <div style="background:#FFF0F3; border:2px solid #FFCCD5; border-radius:18px; padding:18px; margin:16px 0; text-align:right;">
                    <p style="margin:0; font-size:12px; color:#64748B;">商品小計：NT$ {cart_subtotal:,.0f} ｜ 服務費 (10%)：NT$ {service_charge:,.0f}</p>
                    <h3 style="margin:6px 0 0 0; font-size:26px; font-weight:900; color:#E11D48;">應收總計：NT$ {final_total:,.0f}</h3>
                </div>
            """, unsafe_allow_html=True)

            action_c1, action_c2 = st.columns(2)
            with action_c1:
                if st.button("🗑️ 清空點單台", use_container_width=True):
                    st.session_state.pos_cart = {name: 0 for name in menu_dict.keys()}
                    st.rerun()
            with action_c2:
                if st.button("🚀 立即出單並自動扣庫存", type="primary", use_container_width=True):
                    order_no, charged, deduct_logs, alerts = process_pos_checkout(active_items, table_no, guest_name, pay_method, menu_dict)
                    st.balloons()
                    st.success(f"🎉 結帳成功！單號【{order_no}】，實收 NT$ {final_total:,.0f}")
                    
                    st.markdown("#### 📦 配方庫存自動扣減結果：")
                    for d_log in deduct_logs:
                        st.markdown(d_log)

                    if alerts:
                        for alt in alerts:
                            st.warning(alt)

                    st.session_state.pos_cart = {name: 0 for name in menu_dict.keys()}
        else:
            st.info("🛒 點單清單為空，請點選左側酒水品項加入購物車。")
            st.caption("💡 點餐出單後，系統將自動扣減原物料並同步累計當日營業額！")
