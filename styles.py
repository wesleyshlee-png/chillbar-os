import streamlit as st

def apply_custom_styles():
    macaron_css = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
    
    <style>
        /* 🍰 全站馬卡龍奶油杏仁底色 */
        .stApp {
            background-color: #FAF6F0 !important;
            color: #1E293B !important;
            font-family: "Outfit", "Noto Sans TC", sans-serif !important;
        }

        /* 標題優雅法式字體與微字距 */
        h1, h2, h3, h4, h5, h6 {
            font-family: "Outfit", "Noto Sans TC", sans-serif !important;
            font-weight: 800 !important;
            color: #0F172A !important;
            letter-spacing: -0.01em !important;
        }

        /* 🎀 馬卡龍浮雕立體純白卡片 */
        div[data-testid="stMetric"], .macaron-card {
            background: #FFFFFF !important;
            border: 1.5px solid #F1E5D8 !important;
            border-radius: 20px !important;
            padding: 1.2rem 1.4rem !important;
            box-shadow: 0 8px 24px rgba(180, 130, 110, 0.07), 0 2px 6px rgba(0,0,0,0.02) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stMetric"]:hover, .macaron-card:hover {
            border-color: #FFB5C5 !important;
            box-shadow: 0 14px 32px rgba(255, 75, 114, 0.12) !important;
            transform: translateY(-3px) !important;
        }

        /* 指標數字色彩 */
        div[data-testid="stMetricValue"] {
            font-size: 2.1rem !important;
            font-weight: 900 !important;
            color: #0F172A !important;
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 700 !important;
            font-size: 0.85rem !important;
            color: #64748B !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        /* 🍓 草莓馬卡龍高飽和珊瑚粉主按鈕 */
        .stButton>button {
            background: linear-gradient(135deg, #FF6B8B 0%, #FF8E53 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 0.65rem 1.4rem !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 6px 18px rgba(255, 107, 139, 0.35) !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            box-shadow: 0 10px 26px rgba(255, 107, 139, 0.55) !important;
            transform: translateY(-2px) !important;
            color: #FFFFFF !important;
        }

        /* 🍰 側邊欄：法式優雅奶油白 */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1.5px solid #F1E5D8 !important;
            box-shadow: 4px 0 20px rgba(180, 130, 110, 0.04) !important;
        }

        /* 📊 高飽和度、高對比度清晰表格 */
        div[data-testid="stDataFrame"] {
            border: 1.5px solid #E2E8F0 !important;
            border-radius: 16px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
            background: #FFFFFF !important;
        }

        /* 分頁標籤 (Tabs) 美化 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px !important;
            background-color: #F3ECE2 !important;
            padding: 6px 8px !important;
            border-radius: 16px !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px !important;
            color: #64748B !important;
            font-weight: 800 !important;
            padding: 8px 18px !important;
            border: none !important;
            background-color: transparent !important;
            transition: all 0.2s ease !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #FF4B72 !important;
            box-shadow: 0 4px 14px rgba(255, 75, 114, 0.2) !important;
        }

        /* 輸入框與下拉選單 */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            border: 1.5px solid #E2E8F0 !important;
            border-radius: 12px !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #FF6B8B !important;
            box-shadow: 0 0 0 3px rgba(255, 107, 139, 0.15) !important;
        }

        /* 隱藏預設頁首空白 */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
    </style>
    """
    st.markdown(macaron_css, unsafe_allow_html=True)