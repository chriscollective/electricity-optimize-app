"""
契約容量最佳化計算工具
"""
import streamlit as st
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import warnings
from dotenv import load_dotenv

import streamlit.components.v1 as components

load_dotenv()
from utils.ga_mp import send_page_view
# 匯入自定義模組
from utils.calculator import (
    calculate_annual_fee,
    calculate_waste_and_penalty,
    find_optimal_capacity,
    get_fee_distribution
)
from utils.ga_integration import (inject_google_analytics)  # inject_ga
from utils.validators import (
    validate_capacity,
    validate_monthly_demands,
    validate_demand_vs_capacity,
    format_validation_messages
)
from components.sidebar import render_sidebar




# 頁面設定
st.set_page_config(
    page_title="契約容量最佳化計算工具",
    page_icon="⚡",
    initial_sidebar_state='expanded'
)



# 關閉多餘警告
warnings.filterwarnings("ignore")

# 自訂側邊欄寬度
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

def get_ga_id() -> str | None:
    # 讀取優先序：Secrets > 環境變數 > None
    return (
        st.secrets.get("GA_MEASUREMENT_ID")
        or os.getenv("GA_MEASUREMENT_ID")
    )


def setup_matplotlib_font():
    """設定 Matplotlib 中文字體"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, 'fonts', 'NotoSansTC-Regular.ttf')

    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False
    else:
        st.warning("⚠️ 找不到中文字體檔案，圖表可能無法正確顯示中文")




def render_input_section():
    """渲染輸入區塊"""
    st.title("契約容量最佳化計算工具｜快速找出最省電費方案")
    st.subheader("(非時間電價｜低壓電力)")

    # 契約容量輸入
    current_capacity = st.number_input(
        "目前契約容量（千瓦）(經常(尖峰)契約)",
        min_value=1,
        value=25,
        help="請輸入電費帳單上的契約容量"
    )

    # 12 個月需量輸入
    st.subheader("輸入1~12月的最高需量（千瓦）")
    st.caption("通常在電費帳單➞最高需量(千瓦)➞經常(尖峰)需量")

    monthly_demands = []
    cols = st.columns(4)

    for i in range(12):
        with cols[i % 4]:
            default_value = max(1, int(current_capacity * 0.8))
            demand = st.number_input(
                f"{i+1}月",
                min_value=1,
                value=default_value,
                key=f"month_{i}",
                help=f"{i+1}月的最高需量"
            )
            monthly_demands.append(demand)

    # 驗證契約容量
    is_valid_capacity, error_msg = validate_capacity(current_capacity)
    if not is_valid_capacity:
        st.error(f"❌ {error_msg}")
        return None, None

    # 驗證需量資料
    is_valid_demands, error_msg = validate_monthly_demands(monthly_demands)
    if not is_valid_demands:
        st.error(f"❌ {error_msg}")
        return None, None

    # 驗證需量與契約容量的合理性
    is_valid, error_msg, warnings_list = validate_demand_vs_capacity(
        monthly_demands, current_capacity
    )

    if warnings_list:
        warning_text = format_validation_messages(warnings_list)
        st.warning(warning_text)

    return current_capacity, monthly_demands


def render_current_status(current_capacity, monthly_demands):
    """渲染目前狀態區塊"""
    try:
        # 計算目前的年基本電費
        current_fee = calculate_annual_fee(current_capacity, monthly_demands)

        st.write(f"## 目前契約容量 {current_capacity} 千瓦，一年基本電費總額為：{current_fee:.2f} 元")

        # 計算浪費與罰款
        waste_total, penalty_total = calculate_waste_and_penalty(current_capacity, monthly_demands)

        st.write(f"### 🧊 尚未用滿契約容量的浪費金額（年）：{waste_total:.2f} 元")
        st.write(f"### 🔥 超過契約容量的罰款金額（年）：{penalty_total:.2f} 元")
        st.write("---")

        return current_fee, waste_total, penalty_total

    except Exception as e:
        st.error(f"❌ 計算錯誤: {e}")
        return None, None, None


def render_optimization_results(monthly_demands, current_fee):
    """渲染最佳化結果區塊"""
    try:
        # 尋找最佳容量
        optimal_capacity, optimal_fee, details = find_optimal_capacity(monthly_demands)

        # 使用 HTML 和 CSS 為最佳容量加上鮮明背景色
        st.markdown(
            f"""
            <h2 style='background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
                       color: white;
                       padding: 20px;
                       border-radius: 10px;
                       text-align: center;
                       box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                🔥 最佳契約容量建議：<span style='font-size: 1.3em; font-weight: bold;'>{optimal_capacity} 千瓦</span>
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.write(f"### 🌟 最低一年基本電費總額：{optimal_fee:.2f} 元")

        st.write(f"### 🧊 優化後契約容量({optimal_capacity}kW)下的浪費金額（年）：{details['waste']:.2f} 元")
        st.write(f"### 🔥 優化後契約容量({optimal_capacity}kW)下的罰款金額（年）：{details['penalty']:.2f} 元")

        # 計算節省金額
        saved_fee = current_fee - optimal_fee
        monthly_saved_fee = saved_fee / 12

        st.write(f"### 💰 優化後一年可節省金額：{saved_fee:.2f} 元")
        st.write(f"### 📆 平均每個月可節省金額：{monthly_saved_fee:.2f} 元")

        return optimal_capacity, optimal_fee

    except Exception as e:
        st.error(f"❌ 最佳化計算錯誤: {e}")
        return None, None


def render_chart(monthly_demands, optimal_capacity, optimal_fee):
    """渲染圖表"""
    try:
        st.write("#### 以下圖表顯示在不同契約容量下的基本電費總額變化")

        # 取得費用分布資料
        capacities, fees = get_fee_distribution(monthly_demands)

        # 繪製圖表
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(capacities, fees, color='skyblue', label='基本電費')
        ax.bar(optimal_capacity, optimal_fee, color='orange', label='最佳容量')

        ax.set_xlabel("契約容量(千瓦)")
        ax.set_ylabel("基本電費總額(元)")
        ax.set_title("契約容量 vs 一年基本電費總額")

        # 標註最佳容量
        ax.text(
            optimal_capacity, optimal_fee,
            f'{optimal_fee:.2f} 元',
            ha='center', va='bottom',
            fontsize=10, color='black'
        )

        # 加入網格
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.legend()

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ 圖表繪製錯誤: {e}")


def render_footer():
    """渲染頁尾"""
    st.markdown(
        "<div style='text-align: center; color: gray; padding: 10px;'>"
        "Copyright ©2025 Chris Du. All rights reserved."
        "</div>",
        unsafe_allow_html=True
    )




def main():
    """主程式"""

    # 注入 GA
    #inject_google_analytics("G-MFRF3RTP11",show_debug=True)
    ok = send_page_view()
    # 設定字體
    setup_matplotlib_font()

    
 


    # 渲染側邊欄
    render_sidebar()

    # 渲染輸入區塊
    result = render_input_section()
    if result[0] is None:
        return

    current_capacity, monthly_demands = result

    # 加入計算按鈕
    st.write("---")
    calculate_button = st.button("🔍 開始計算最佳容量", type="primary", use_container_width=True)

    # 只有按下按鈕才開始計算
    if calculate_button:
        # 渲染目前狀態
        current_result = render_current_status(current_capacity, monthly_demands)
        if current_result[0] is None:
            return

        current_fee, waste_total, penalty_total = current_result

        # 渲染最佳化結果
        optimal_result = render_optimization_results(monthly_demands, current_fee)
        if optimal_result[0] is None:
            return

        optimal_capacity, optimal_fee = optimal_result

        # 渲染圖表
        render_chart(monthly_demands, optimal_capacity, optimal_fee)

    # 渲染頁尾
    render_footer()


if __name__ == "__main__":
    main()
