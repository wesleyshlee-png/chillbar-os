"""
qibar_project/app.py
憩Bay餐酒館 (QiBar / Chill Bar) - 全方位智慧餐飲營運大腦主進入點
"""

import streamlit as st
import os
import base64
from styles import apply_custom_styles
from db import init_db
from financials import render_financials_page
from inventory import render_inventory_page
from orders import render_orders_page
from menu_viewer import render_menu_viewer_page
from crm import render_crm_page
from attendance import render_attendance_page
from reservations import render_reservations_page

# 1. 設置頁面基礎設定
st.set_page_config(
    page_title="憩Bay 餐酒館 (Chill Bar) - 智慧營運系統",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 注入法式馬卡龍風格 CSS
apply_custom_styles()

# 3. 初始化資料庫
init_db()

def get_logo_html():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.jpg")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        return f"""
        <div style="text-align:center; margin-bottom:18px;">
            <img src="data:image/jpeg;base64,{b64_data}" style="width:100%; max-width:240px; border-radius:18px; border:2px solid #F1E5D8; box-shadow:0 8px 24px rgba(255,107,139,0.25); margin:0 auto; display:block;" alt="憩Bay Chill Bar Logo">
            <h1 style="font-size:20px; font-weight:900; margin-top:12px; color:#0F172A; letter-spacing:0.02em;">憩Bay <span style="color:#FF4B72;">Chill Bar</span></h1>
            <p style="font-size:10px; font-weight:800; color:#F59E0B; margin:0; letter-spacing:0.12em; text-transform:uppercase;">SMART BISTRO & LOUNGE</p>
        </div>
        """
    else:
        return """
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
            <div style="width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg, #FF6B8B 0%, #FF8E53 100%); display:flex; align-items:center; justify-content:center; font-size:28px;">
                🍸
            </div>
            <div>
                <h2 style="font-size:22px; font-weight:900; margin:0; color:#0F172A;">憩Bay<span style="color:#FF4B72;">.Pro</span></h2>
                <p style="font-size:10px; font-weight:800; color:#F59E0B; margin:0; letter-spacing:0.1em; text-transform:uppercase;">CHILL BAR & BISTRO</p>
            </div>
        </div>
        """


def main():
    # 側邊欄品牌與導覽
    with st.sidebar:
        st.markdown(get_logo_html(), unsafe_allow_html=True)

        st.markdown("#### 📂 系統核心管理看板")
        module_choice = st.radio(
            "選擇要開啟的管理模組：",
            [
                "🍸 吧檯點餐 POS (配方扣庫存)",
                "📖 官方實體菜單相冊 (MENU 6頁全收錄)",
                "👥 VIP 常客偏好與寄酒 CRM (Taste Radar)",
                "⏰ 調酒師排班與夜場打卡 (Staff Payroll)",
                "🪑 席位預約與包廂低消 (Reservations)",
                "📊 財務損益 P&L (黃金指標大腦)",
                "🍾 庫存水位與自動警戒"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.divider()
        st.markdown("""
        <div style="background:#FFFFFF; border:1.5px solid #F1E5D8; border-radius:14px; padding:12px; box-shadow:0 4px 12px rgba(180,130,110,0.06);">
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:800; color:#047857;">
                <span style="width:8px; height:8px; border-radius:50%; background:#10B981; display:inline-block;"></span>
                <span>憩Bay 智慧大腦 • 運作中</span>
            </div>
            <p style="font-size:11px; color:#64748B; margin:4px 0 0 0;">全功能旗艦版 v9.0</p>
        </div>
        """, unsafe_allow_html=True)

    # 主畫面路由
    if module_choice == "🍸 吧檯點餐 POS (配方扣庫存)":
        render_orders_page()
    elif module_choice == "📖 官方實體菜單相冊 (MENU 6頁全收錄)":
        render_menu_viewer_page()
    elif module_choice == "👥 VIP 常客偏好與寄酒 CRM (Taste Radar)":
        render_crm_page()
    elif module_choice == "⏰ 調酒師排班與夜場打卡 (Staff Payroll)":
        render_attendance_page()
    elif module_choice == "🪑 席位預約與包廂低消 (Reservations)":
        render_reservations_page()
    elif module_choice == "📊 財務損益 P&L (黃金指標大腦)":
        render_financials_page()
    elif module_choice == "🍾 庫存水位與自動警戒":
        render_inventory_page()


if __name__ == "__main__":
    main()
