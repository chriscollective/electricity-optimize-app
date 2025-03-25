import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 解決中文亂碼
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 費率設定
BASIC_FEE_NON_SUMMER = 173.2
BASIC_FEE_SUMMER = 236.2

# 計算年基本電費函數
def calculate_annual_fee(capacity, monthly_demands):
    total_fee = 0
    for i, demand in enumerate(monthly_demands):
        # 夏月定義：6,7,8,9月使用夏月電費
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

#計算範圍
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
st.write(f"### 💰 優化後可節省金額：{saved_fee:.2f} 元")

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
