import streamlit as st
import numpy as np
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os

# 明確取得字體檔案的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, 'fonts', 'NotoSansTC-Regular.ttf')

# 正式將字體加入Matplotlib字體管理器
fm.fontManager.addfont(font_path)

# 取得字體名稱並設定給 Matplotlib 使用
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# 加入Google Analytics追蹤碼
with open("analytics.html", "r", encoding='utf-8') as f:
    analytics_code = f.read()

st.components.v1.html(analytics_code, height=0, width=0)

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
st.title("契約容量最佳化計算工具")
st.subheader("(非時間電價)")

# 側邊欄的額外說明
st.sidebar.header("🔖 網站說明")
st.sidebar.markdown("### 什麼是契約容量？")
st.sidebar.write("契約容量是指台電與用戶之間約定的最高用電需求量(平均15分鐘內)，以千瓦(kW)為單位，超過會加倍收取費用。")
st.sidebar.write("你可以想像契約容量像是手機的月租費，不管用電量多或少，都是固定的支出費用。另一種比喻是契約容量就像水管的粗細大小，如果你同時間需要的水量(電量)越大，那你的水管直徑大小(契約容量)也要越大，這個與你的總用水量(總用電量)沒關係，而是與你的瞬間需求量有關。")
st.sidebar.write("舉例來說，同一時間公設區域用的電量越多(照明、冷氣、電梯、抽水馬達等等)，那你也需要更高的契約容量。")
st.sidebar.markdown("---")
st.sidebar.markdown("### 電費的計算方式")
st.sidebar.write("電費 = 契約容量 × 基本電費 + 用電量 × 流動電費，依夏月（6~9月）與非夏月不同計價。")
st.sidebar.write("超額罰款:超出契約容量10%以內為2倍電價，10%以上為3倍電價。")
st.sidebar.write("P.S.如果社區每月用電需求量差異很大(夏天與非夏天)，那麼很有可能偶爾被罰錢還會比較便宜。(因為基本費用省下的金額>罰款的金額)")
st.sidebar.markdown("---")

st.sidebar.markdown("### 為什麼我要寫這個網站")
st.sidebar.write("因為版主接任了30年的老社區主委，發現電費高得驚人，花了很久研究才明白其中原因，希望藉由這個網站幫助更多人，也藉此練習程式開發能力。")
st.sidebar.markdown("---")


st.sidebar.header("🙌 贊助與支持")
st.sidebar.write("如果你覺得這個網站對你有幫助，歡迎透過以下LINE Pay QR code自由樂捐給我，感謝你的支持！")
st.sidebar.image("linepay_qrcode.JPG",width=200)

# 使用者輸入
current_capacity = st.number_input("目前契約容量（千瓦）", min_value=1, value=25)
monthly_demands = []
st.subheader("輸入1~12月的最高需量（千瓦）")
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
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(capacities, fees, color='skyblue')
ax.bar(optimal_capacity, optimal_fee, color='orange')
ax.set_xlabel("契約容量(千瓦)")
ax.set_ylabel("基本電費總額(元)")
ax.set_title("契約容量 vs 一年基本電費總額")

# 在最低總和長條圖上方標註總額
ax.text(optimal_capacity, optimal_fee, f'{optimal_fee:.2f} 元', ha='center', va='bottom', fontsize=10, color='black')

st.pyplot(fig)

# 加入這段版權聲明
st.markdown(
    "<div style='text-align: center; color: gray; padding: 10px;'>Copyright ©2025 Chris Du. All rights reserved.</div>",
    unsafe_allow_html=True
)