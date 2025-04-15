import streamlit as st
import numpy as np
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import warnings
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 設定 sidebar 初始為展開
st.set_page_config(initial_sidebar_state='expanded')

# 關閉多餘警告
warnings.filterwarnings("ignore")

# ✅ 連線並讀取 Google Sheets 上的統計資料
from datetime import datetime, timedelta

def load_google_sheet_stats():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1iD0iKKg8yDRZ55MjzbTMaZNBbc7EmugEp-4_pCzmeeE").sheet1

        records = sheet.get_all_records()

        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        today_count = 0
        yesterday_total = 0

        for row in records:
            row_date = str(row.get("日期", "")).strip()
            try:
                today_value = int(row.get("今日瀏覽次數", 0))
                total_value = int(row.get("累積瀏覽次數", 0))
            except:
                today_value, total_value = 0, 0

            if row_date == today:
                today_count = today_value
            elif row_date == yesterday:
                yesterday_total = total_value

        total_count = today_count + yesterday_total
        return today, today_count, total_count
    except Exception as e:
        st.warning(f"⚠️ 無法從 Google Sheet 讀取初始值：{e}")
        return date.today().isoformat(), 0, 0

# ✅ 將今日資料寫入 Google Sheets（若有則更新，否則新增）
def record_to_google_sheet(today_str, today_count, total_count):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1iD0iKKg8yDRZ55MjzbTMaZNBbc7EmugEp-4_pCzmeeE").sheet1

        records = sheet.get_all_records()
        st.write("📋 Google Sheet 現有資料：")
        st.write(records)

        updated = False
        for i, row in enumerate(records):
            row_date = str(row.get("日期", "")).strip()
            if row_date == today_str:
                st.success(f"✅ 找到今日資料在第 {i+2} 列，準備更新！")
                sheet.update(f"A{i+2}:C{i+2}", [[today_str, today_count, total_count]])
                updated = True
                break

        if not updated:
            st.warning("⚠️ 沒有找到今天的資料，將新增一列")
            sheet.append_row([today_str, today_count, total_count])
            st.success("✅ 已新增一列今日資料")

    except Exception as e:
        st.error(f"❌ 寫入 Google Sheet 發生錯誤：{e}")


# ✅ 初始化統計資料
today_str, today_count, total_count = load_google_sheet_stats()

# # ✅ 若尚未統計過，則 +1 並更新 Google Sheet
if "counted" not in st.session_state:
    today_count += 1
    total_count += 1
    st.session_state.counted = True
    record_to_google_sheet(today_str, today_count, total_count)

# # 測試模式：每次重新整理都 +1
# today_count += 1
# total_count += 1
# record_to_google_sheet(today_str, today_count, total_count)

# ✅ 統計資料寫入變數供後續介面使用
stats = {
    "daily": {today_str: today_count},
    "total": total_count
}







st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 400px;
        max-width: 1000px;
        width: 1000px;
    }
    </style>
    """,
    unsafe_allow_html=True
)




# 明確取得字體檔案的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, 'fonts', 'NotoSansTC-Regular.ttf')

# 正式將字體加入Matplotlib字體管理器
fm.fontManager.addfont(font_path)

# 取得字體名稱並設定給 Matplotlib 使用
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False




# 費率設定
BASIC_FEE_NON_SUMMER = 173.2
BASIC_FEE_SUMMER = 236.2

# 計算年基本電費函數
def calculate_annual_fee(capacity, monthly_demands):
    total_fee = 0
    for i, demand in enumerate(monthly_demands):
        basic_fee_rate = BASIC_FEE_SUMMER if i+1 in [6, 7, 8, 9] else BASIC_FEE_NON_SUMMER
        excess = demand - capacity
        if excess <= 0:
            fee = capacity * basic_fee_rate
        else:
            allowed_10_percent = capacity * 0.10
            if excess <= allowed_10_percent:
                fee = capacity * basic_fee_rate + excess * basic_fee_rate * 2
            else:
                fee = (capacity * basic_fee_rate +
                    allowed_10_percent * basic_fee_rate * 2 +
                    (excess - allowed_10_percent) * basic_fee_rate * 3)
        total_fee += fee
    return total_fee

# Streamlit界面
st.title("契約容量最佳化計算工具｜快速找出最省電費方案") 
st.subheader("(非時間電價｜低壓電力)")

# 側邊欄的額外說明
st.sidebar.header("🔖 網站說明")
st.sidebar.markdown("### 什麼是契約容量？")
st.sidebar.write("契約容量是指台電與用戶之間約定的最高用電需求量(平均15分鐘內)，以千瓦(kW)為單位，超過會加倍收取費用。")
st.sidebar.write("你可以想像契約容量像是手機的月租費，不管用電量多或少，都是固定的支出費用。另一種比喻是契約容量就像水管的粗細大小，如果你同時間需要的水量(電量)越大，那你的水管直徑大小(契約容量)也要越大，這個與你的總用水量(總用電量)沒關係，而是與你的瞬間需求量有關。")
st.sidebar.write("舉例來說，同一時間公設區域用的電量越多(照明、冷氣、電梯、抽水馬達等等)，那你也需要更高的契約容量。")
st.sidebar.markdown("---")

st.sidebar.markdown("### 👤 誰適合使用本網站？")
st.sidebar.write("這個網站適用於使用「低壓電力」方案的用戶，特別適合台灣中小型社區。")
st.sidebar.write(
    "拿起你收到的電費帳單，看一下用戶資訊：\n\n"
    "- **電價種類**：電力需量非營業用\n"
    "- **時間種類**：非時間電價\n\n"
    "接著看下方資訊是否有：\n\n"
    "- 契約容量\n"
    "- 最高需量\n"
    "- 計費度數\n\n"
    "如果以上條件都符合，那麼你就非常適合使用這個網站！一起省錢吧٩(๑•̀ω•́๑)۶!"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 電費的計算方式")
st.sidebar.write("電費 = 契約容量 × 基本電費 + 用電量 × 流動電費，依夏月（6~9月）與非夏月不同計價。<<此網站只計算基本電費總額>>，因為流動電費與契約容量無關。")
st.sidebar.write("夏月: 基本電費236.2元/千瓦，流動電費3.44/度\n\n"
                 "非夏月:基本電費173.2元/千瓦，流動電費3.26/度"
)
st.sidebar.write("超額罰款:超出契約容量10%以內為2倍電價，10%以上為3倍電價。")
st.sidebar.write("P.S.如果社區每月用電需求量差異很大(夏天與非夏天)，那麼很有可能偶爾被罰錢還會比較便宜。(因為基本費用省下的金額>罰款的金額)")
st.sidebar.markdown("---")

st.sidebar.markdown("### ⚠️ 注意事項")
st.sidebar.write(
    "契約容量由高改成低不用額外的變更費用，但是若為由低改高則需額外的變更費用。"
    "如果確定社區內短期間不會再新增任何的公共設備，那麼由高改低不會有太大的問題。"
    "反之，如果社區未來可能會新增設備，用電量可能會上升，那麼建議是可以預留多一點的空間，"
    "不用一次調得太低。不過站主認為省下來的錢都可以申請好幾次了(依站主自身社區的例子是這樣，但每個社區狀況不一樣，請各主委自行判斷。)"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 申請變更方式")
st.sidebar.write(
    "主委帶著大小章（社區大章、主委個人章）、身分證、區公所公文（申報公文，證明主委身份），"
    "到台電服務處臨櫃申請契約容量變更，直接告訴櫃檯人員說你要改為多少千瓦(其實你也可以請台電人員幫你計算改為多少最合理，他可以查閱歷年資料來計算，但是你看不到他是怎麼算的)，通過後大約一周內，會有台電人員到社區內調整電表。"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 為什麼站主要寫這個網站")
st.sidebar.write("因為站主接任了30年的老社區主委，發現電費頗高，花了很多時間研究，才明白其中原因。(如果當初社區管理人員早一點調整，30年的時間至少可以省下將近90萬的電費!)希望藉由這個網站幫助更多人省錢!也練習與AI溝通的能力!")
st.sidebar.markdown("---")


st.sidebar.header("🙌 贊助與支持")
st.sidebar.write("如果你覺得這個網站對你有幫助，歡迎透過以下LINE Pay QR code自由樂捐給站主，感謝你的支持！")
st.sidebar.image("linepay_qrcode.JPG",width=200)
st.sidebar.markdown("---")

st.sidebar.markdown("### 📬 聯繫與反饋")
st.sidebar.write("如果有任何網站相關的問題，歡迎寄信到以下信箱聯繫站主：")
st.sidebar.code("justakiss918@gmail.com")
st.sidebar.write("網站最新更新日期:2025/03/27")
st.sidebar.markdown("---")

# 顯示瀏覽統計資訊

st.sidebar.markdown("### 📈 瀏覽人數統計")
st.sidebar.write(f"🔢 今日瀏覽次數：{stats['daily'][today_str]}")
st.sidebar.write(f"📊 總瀏覽次數：{stats['total']}")
st.sidebar.markdown("---")


# 使用者輸入
current_capacity = st.number_input("目前契約容量（千瓦）(經常(尖峰)契約)", min_value=1, value=25)
monthly_demands = []
st.subheader("輸入1~12月的最高需量（千瓦）")
st.caption("通常在電費帳單➞最高需量(千瓦)➞經常(尖峰)需量")
cols = st.columns(4)
for i in range(12):
    with cols[i % 4]:
        demand = st.number_input(f"{i+1}月", min_value=0, value=int(current_capacity*0.8), key=f"month_{i}")
        monthly_demands.append(demand)

# 計算目前的年基本電費
current_fee = calculate_annual_fee(current_capacity, monthly_demands)
st.write(f"## 目前契約容量 {current_capacity} 千瓦，一年基本電費總額為：{current_fee:.2f} 元")

# 計算最佳容量
min_demand = max(1, int(min(monthly_demands) * 0.8))
max_demand = int(max(monthly_demands) * 1.5)
capacities = np.arange(min_demand, max_demand + 1)

fees = [calculate_annual_fee(cap, monthly_demands) for cap in capacities]
optimal_idx = np.argmin(fees)
optimal_capacity = capacities[optimal_idx]
optimal_fee = fees[optimal_idx]

# 顯示最佳化結果
st.write(f"## 🔥 最佳契約容量建議：{optimal_capacity} 千瓦")
st.write(f"### 🌟 最低一年基本電費總額：{optimal_fee:.2f} 元")

# 顯示優化後節省的金額
saved_fee = current_fee - optimal_fee
monthly_saved_fee = saved_fee / 12
st.write(f"### 💰 優化後一年可節省金額：{saved_fee:.2f} 元")
st.write(f"### 📆 平均每個月可節省金額：{monthly_saved_fee:.2f} 元")

# 圖表呈現

st.write(f"#### 以下圖表顯示在不同契約容量下的基本電費總額變化")
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(capacities, fees, color='skyblue')
ax.bar(optimal_capacity, optimal_fee, color='orange')
ax.set_xlabel("契約容量(千瓦)")
ax.set_ylabel("基本電費總額(元)")
ax.set_title("契約容量 vs 一年基本電費總額")

# 在最低總和長條圖上方標註總額
ax.text(optimal_capacity, optimal_fee, f'{optimal_fee:.2f} 元', ha='center', va='bottom', fontsize=10, color='black')
# 在圖表中加上網格，增加閱讀性
ax.grid(axis='y', linestyle='--', alpha=0.5)
st.pyplot(fig)


# 加入這段版權聲明
st.markdown(
    "<div style='text-align: center; color: gray; padding: 10px;'>Copyright ©2025 Chris Du. All rights reserved.</div>",
    unsafe_allow_html=True
)