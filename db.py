"""
qibar_project/db.py
憩Bay餐酒館 (Chill Bar) - 官方真實菜單 (45+ 款調酒、精釀、套餐、滷味、主食與炸物) 資料庫核心
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "qibar.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# 憩Bay 官方真實菜單清冊
OFFICIAL_MENU_ITEMS = [
    # 1. 特色調酒茶酒
    ("泰式奶茶酒8%", "特色調酒茶酒", 85.0, 300.0, 140),
    ("紅心芭樂梅8%", "特色調酒茶酒", 65.0, 250.0, 185),
    ("芭樂梅茶酒8%", "特色調酒茶酒", 65.0, 290.0, 160),
    ("柚香梅沙瓦", "特色調酒茶酒", 65.0, 260.0, 150),
    ("伯爵覆盆子8%", "特色調酒茶酒", 70.0, 290.0, 135),
    ("梅啤氣", "特色調酒茶酒", 65.0, 260.0, 140),
    ("野莓洛神4%", "特色調酒茶酒", 55.0, 220.0, 110),
    ("Mojito冰茶4%", "特色調酒茶酒", 55.0, 220.0, 145),
    ("雷檸紫蘇3.5%", "特色調酒茶酒", 60.0, 250.0, 95),
    ("荔枝茶酒8%", "特色調酒茶酒", 65.0, 250.0, 120),
    ("次波草莓Cider8%", "特色調酒茶酒", 65.0, 250.0, 115),
    
    # 2. 生啤酒與經典調飲
    ("Whisky Coke (威士忌可樂)", "生啤與經典調飲", 50.0, 200.0, 90),
    ("威士忌 蘇打 (Highball)", "生啤與經典調飲", 50.0, 200.0, 160),
    ("Vodka Lime (伏特加萊姆)", "生啤與經典調飲", 45.0, 200.0, 130),
    ("台啤18天生啤酒(中)", "生啤與經典調飲", 70.0, 250.0, 190),
    ("台啤18天生啤酒(大杯)", "生啤與經典調飲", 90.0, 320.0, 220),
    ("朝日Asahi生啤(中)", "生啤與經典調飲", 75.0, 250.0, 180),
    ("朝日Asahi生啤(大杯)", "生啤與經典調飲", 95.0, 320.0, 210),

    # 3. 敲敲瓶裝精釀
    ("朝日Asahi瓶裝啤酒", "敲敲瓶裝精釀", 55.0, 160.0, 80),
    ("Busch Beer (布希啤酒)", "敲敲瓶裝精釀", 70.0, 210.0, 75),
    ("歸剛ㄟ | 零糖啤酒", "敲敲瓶裝精釀", 75.0, 220.0, 105),
    ("小滿 | 冬瓜茶啤酒", "敲敲瓶裝精釀", 75.0, 220.0, 115),
    ("立秋 | 東方美人茶啤酒", "敲敲瓶裝精釀", 75.0, 220.0, 125),
    ("貓頭鷹蘋果氣泡酒", "敲敲瓶裝精釀", 80.0, 220.0, 95),
    ("貓頭鷹粉紅蘋果氣泡酒", "敲敲瓶裝精釀", 80.0, 220.0, 110),
    ("燒酒Somaek (燒啤)", "敲敲瓶裝精釀", 75.0, 220.0, 135),
    ("美韓轟炸機組合", "敲敲瓶裝精釀", 120.0, 390.0, 85),

    # 4. 精選套餐
    ("義大利麵+無酒精飲品大杯套餐", "精選特惠套餐", 65.0, 200.0, 110),
    ("義大利麵+微醺調酒($250)套餐", "精選特惠套餐", 115.0, 410.0, 140),
    ("一夜干+炸物雙拼+18天生啤大*2 豪飲組", "精選特惠套餐", 320.0, 980.0, 75),

    # 5. 經典秘製滷下酒菜
    ("秘製滷花生", "經典秘製滷味", 25.0, 90.0, 150),
    ("秘製滷毛豆", "經典秘製滷味", 20.0, 80.0, 190),
    ("秘製滷花生+毛豆雙拼", "經典秘製滷味", 40.0, 150.0, 130),
    ("滷甜不辣 (台式風味)", "經典秘製滷味", 22.0, 75.0, 160),

    # 6. 主食與烤物分享料理
    ("肉醬義大利麵", "主食與烤物料理", 60.0, 200.0, 120),
    ("青醬義大利麵 (平打麵)", "主食與烤物料理", 60.0, 200.0, 115),
    ("紐澳良烤雞翅 (四隻)", "主食與烤物料理", 75.0, 230.0, 135),
    ("烤一夜干 (午仔魚)", "主食與烤物料理", 110.0, 300.0, 95),

    # 7. 微醺下酒炸物
    ("脆薯 (附沾醬)", "微醺下酒炸物", 28.0, 100.0, 180),
    ("雞塊 (香酥雞塊)", "微醺下酒炸物", 35.0, 120.0, 160),

    # 8. 無酒精飲品
    ("有機野莓洛神檸檬冰茶", "無酒精茶飲", 35.0, 130.0, 85),
    ("有機爽身檸檬冰茶", "無酒精茶飲", 35.0, 120.0, 90),
    ("椰子氣泡水", "無酒精茶飲", 38.0, 120.0, 70),
    ("可樂 / 雪碧", "無酒精茶飲", 20.0, 80.0, 110),
    ("蘇打水", "無酒精茶飲", 20.0, 80.0, 60),
]

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 建立 menu_items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            monthly_sales INTEGER NOT NULL DEFAULT 100,
            updated_at TEXT NOT NULL
        )
    """)

    # 2. 建立 orders & order_items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL UNIQUE,
            customer_name TEXT DEFAULT '現場散客',
            table_number TEXT DEFAULT '吧檯席',
            total_amount REAL NOT NULL,
            total_cost REAL NOT NULL DEFAULT 0,
            payment_method TEXT DEFAULT '現金/LINE Pay',
            status TEXT NOT NULL DEFAULT 'COMPLETED',
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            unit_cost REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 3. 建立 expenses 費用表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            expense_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 4. 建立 inventory 原物料庫存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            current_stock REAL NOT NULL,
            unit TEXT NOT NULL,
            safety_stock REAL NOT NULL,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 清除舊有停售品項
    obsolete_items = ["白桃茉莉茶酒8%", "薄荷蜂蜜柚子8%", "檸檬紫蘇3.5%"]
    cursor.executemany("DELETE FROM menu_items WHERE name = ?", [(item,) for item in obsolete_items])

    # 匯入真實菜單
    for name, cat, cost, price, sales in OFFICIAL_MENU_ITEMS:
        cursor.execute("""
            INSERT OR REPLACE INTO menu_items (name, category, cost_price, selling_price, monthly_sales, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, cat, cost, price, sales, now_str))

    # 匯入初始原物料庫存
    raw_ingredients = [
        ("泰奶特調基酒", "利口酒", 12.5, "瓶 (700ml)", 4.0, 450.0, 0.0),
        ("紅心芭樂梅調和酒", "風味酒", 14.0, "瓶 (700ml)", 5.0, 380.0, 0.0),
        ("白桃茉莉茶酒", "茶酒", 16.0, "瓶 (700ml)", 4.0, 420.0, 0.0),
        ("台啤18天生啤酒桶 (20L)", "桶裝啤酒", 3.0, "桶 (20L)", 1.0, 2400.0, 0.0),
        ("朝日Asahi生啤酒桶 (19L)", "桶裝啤酒", 4.0, "桶 (19L)", 1.0, 2600.0, 0.0),
        ("野火雞101波本威士忌", "威士忌", 8.0, "瓶 (1000ml)", 2.0, 850.0, 0.0),
        ("龐貝藍鑽琴酒", "琴酒", 6.5, "瓶 (750ml)", 2.0, 520.0, 0.0),
        ("午仔魚一夜干 (特選真空包)", "生鮮海鮮", 25.0, "尾", 8.0, 110.0, 0.0),
        ("特級熟成義大利肉醬", "義麵食材", 18.0, "份 (200g)", 5.0, 45.0, 0.0),
        ("紐澳良醃漬烤雞翅", "肉品食材", 30.0, "份 (4隻)", 10.0, 65.0, 0.0),
        ("秘製滷毛豆/花生 (熟成滷包)", "自製滷味", 40.0, "份", 12.0, 20.0, 0.0),
        ("進口香脆細薯條 (大包裝)", "炸物食材", 15.0, "包 (2kg)", 4.0, 180.0, 0.0),
    ]
    for r_name, r_cat, r_stock, r_unit, r_safety, r_cost, r_price in raw_ingredients:
        cursor.execute("""
            INSERT OR REPLACE INTO inventory (name, category, current_stock, unit, safety_stock, cost_price, selling_price, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (r_name, r_cat, r_stock, r_unit, r_safety, r_cost, r_price, now_str))

    # 初始化歷史營收與訂單範例
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        base_date = datetime.today() - timedelta(days=14)
        for d in range(15):
            cur_d = (base_date + timedelta(days=d)).strftime("%Y-%m-%d")
            # 每日 10~22 筆訂單
            orders_in_day = 12 + (d % 8) * 2
            daily_rev = 24000 + (d % 7) * 4500 + (orders_in_day * 400)
            daily_cogs = daily_rev * 0.28
            
            for i in range(1, orders_in_day + 1):
                ord_no = f"ORD-{cur_d.replace('-','')}-{i:03d}"
                avg_t = daily_rev / orders_in_day
                avg_c = daily_cogs / orders_in_day
                cursor.execute("""
                    INSERT INTO orders (order_number, customer_name, table_number, total_amount, total_cost, payment_method, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ord_no, f"貴賓 #{i}", f"吧檯席 {i%6 + 1:02d}", avg_t, avg_c, "LINE Pay / 信用卡", "COMPLETED", f"{cur_d} 21:{i*2 % 60:02d}:00"))
                
                # 插入 order_items
                item_choice = OFFICIAL_MENU_ITEMS[i % len(OFFICIAL_MENU_ITEMS)]
                cursor.execute("""
                    INSERT INTO order_items (order_number, item_name, category, quantity, unit_price, unit_cost, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ord_no, item_choice[0], item_choice[1], 2, item_choice[3], item_choice[2], f"{cur_d} 21:{i*2 % 60:02d}:00"))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database and official QiBar menu initialized successfully.")
