"""
契約容量最佳化計算工具
✨ 使用 st.form 優化,避免不必要的重新渲染
"""
import json
import streamlit as st
from utils.sheet_tracker import log_visit, get_stats
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import warnings
from dotenv import load_dotenv

load_dotenv()

# 匯入自定義模組
from utils.calculator import (
    calculate_annual_fee,
    calculate_waste_and_penalty,
    find_optimal_capacity,
    get_fee_distribution
)

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
    .block-container {
        max-width: 1200px;   /* increase this to whatever you like */
        padding-left: 2rem;
        padding-right: 2rem;
    }
    [data-testid="stSidebar"] {
        min-width: 400px;
        max-width: 1000px;
        width: 1000px;
    }

    @media (max-width: 786px) {
        [data-testid="stSidebar"] {
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            width: min(90vw, 360px);
            max-width: min(90vw, 360px);
            min-width: 0;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
            z-index: 100;
        }

        [data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0);
        }

        [data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-105%);
        }

        [data-testid="collapsedControl"] {
            position: fixed;
            left: 1rem;
            top: 1rem;
            z-index: 300;
            pointer-events: auto;
        }

        [data-testid="collapsedControl"] button {
            pointer-events: auto;
        }

        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
    }

     /* ✨ 新增:隱藏 form 的邊框 */
    [data-testid="stForm"] {
        border: 0px;
        padding: 0px;
    }
    </style>
       
   
    """,
    unsafe_allow_html=True
)

# ✨ 在行動裝置寬度下，自動收合側欄，避免初次載入時遮擋主內容。
#   做法：透過前端腳本等待 Streamlit 側欄節點與收合按鈕生成，
#   若畫面寬度 <= 786px 且側欄仍展開，就自動觸發一次收合。
#   另監聽視窗尺寸變化，在桌面寬度時重置狀態，保留桌機使用者習慣。
st.markdown(
    """
    <script>
    (function() {
        const threshold = 786;
        const parentDocument = window.parent?.document || document;

        const collapseIfNeeded = () => {
            const sidebar = parentDocument.querySelector('[data-testid="stSidebar"]');
            const toggleButton = parentDocument.querySelector('[data-testid="collapsedControl"] button');
            if (!sidebar || !toggleButton) {
                return false;
            }

            const isMobile = window.innerWidth <= threshold;
            const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';

            if (isMobile && isExpanded && !window.__sidebarAutoCollapsed) {
                toggleButton.click();
                window.__sidebarAutoCollapsed = true;
            } else if (!isMobile) {
                window.__sidebarAutoCollapsed = false;
            }
            return true;
        };

        const initializeWatcher = () => {
            if (!collapseIfNeeded()) {
                const observer = new MutationObserver(() => {
                    if (collapseIfNeeded()) {
                        observer.disconnect();
                        window.addEventListener('resize', collapseIfNeeded, { passive: true });
                    }
                });

                observer.observe(parentDocument.body, { childList: true, subtree: true });
            } else {
                window.addEventListener('resize', collapseIfNeeded, { passive: true });
            }
        };

        if (document.readyState === 'complete') {
            initializeWatcher();
        } else {
            window.addEventListener('load', initializeWatcher, { once: true });
        }
    })();
    </script>
    """,
    unsafe_allow_html=True
)

def inject_seo_metadata():
    """將 SEO 相關的 meta、Open Graph 與結構化資料注入頁面"""
    canonical_url = "https://optipower.streamlit.app/"
    description = (
        "OptiPower 契約容量最佳化計算工具，專為台灣低壓電力用戶打造，"
        "只要輸入 12 個月最高需量即可評估最佳契約容量，降低浪費與罰款電費。"
    )
    keywords = (
        "契約容量, 電費試算, 台電, 最高需量, 社區電費, 低壓電力, 電費最佳化, "
        "電費節省, optipower"
    )
    seo_markup = f"""
    <link rel="canonical" href="{canonical_url}">
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta property="og:title" content="OptiPower 契約容量最佳化計算工具">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:image" content="{canonical_url}static/optipower-og.png">
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="OptiPower 契約容量最佳化計算工具">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="{canonical_url}static/optipower-og.png">
    """

    schema_data = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "OptiPower 契約容量最佳化計算工具",
        "url": canonical_url,
        "description": description,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "inLanguage": "zh-Hant",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "TWD"
        },
        "publisher": {
            "@type": "Person",
            "name": "Chris Du"
        },
        "potentialAction": {
            "@type": "Action",
            "name": "計算最佳契約容量",
            "target": canonical_url
        }
    }

    st.markdown(seo_markup, unsafe_allow_html=True)
    st.markdown(
        f'<script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False)}</script>',
        unsafe_allow_html=True
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
    """
    渲染輸入區塊
    ✨ 使用 st.form 包裝,只有提交時才重新渲染
    """
    # ✨ 使用 form 包裝所有輸入元件
    with st.form("calculation_form"):
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
        months_per_row = 4
        rows = (12 + months_per_row - 1) // months_per_row

        for row in range(rows):
            cols = st.columns(months_per_row)
            for col_idx in range(months_per_row):
                month_index = row * months_per_row + col_idx
                if month_index >= 12:
                    break
                with cols[col_idx]:
                    default_value = max(1, int(current_capacity * 0.8))
                    demand = st.number_input(
                        f"{month_index + 1}月",
                        min_value=1,
                        value=default_value,
                        key=f"month_{month_index}",
                        help=f"{month_index + 1}月的最高需量"
                    )
                    monthly_demands.append(demand)

        # ✨ 提交按鈕必須在 form 內部
        st.write("---")
        submitted = st.form_submit_button(
            "🔍 開始計算最佳容量",
            type="primary",
            use_container_width=True
        )

    # ✨ 表單提交後才進行驗證 (在 form 外部)
    if submitted:
        # 驗證契約容量
        is_valid_capacity, error_msg = validate_capacity(current_capacity)
        if not is_valid_capacity:
            st.error(f"❌ {error_msg}")
            return None, None, False

        # 驗證需量資料
        is_valid_demands, error_msg = validate_monthly_demands(monthly_demands)
        if not is_valid_demands:
            st.error(f"❌ {error_msg}")
            return None, None, False

        # 驗證需量與契約容量的合理性
        is_valid, error_msg, warnings_list = validate_demand_vs_capacity(
            monthly_demands, current_capacity
        )

        if warnings_list:
            warning_text = format_validation_messages(warnings_list)
            st.warning(warning_text)

        # 返回資料和提交狀態
        return current_capacity, monthly_demands, True

    # 未提交時返回 None
    return None, None, False


def render_intro_section():
    """顯示頁面主標題與重要使用說明"""
    st.title("契約容量最佳化計算工具｜OptiPower")
    st.subheader("專為台灣低壓電力用戶打造的免費電費最佳化試算")

    st.markdown(
        """
        只要輸入近 12 個月的最高需量，OptiPower 就能即時計算出最省錢的契約容量，
        並估算每年可節省的基本電費與潛在罰款。適合社區大樓管理委員會，
        以及所有想降低固定用電成本的用戶。
        """
    )

    st.markdown("## 為什麼需要重新檢視契約容量？")
    st.markdown(
        """
        - 契約容量設定過高，等同每月多繳固定電費。
        - 夏月與非夏月用電差異大，容易在淡季造成資源浪費。
        - 未預估到尖峰用電時的罰款，導致被動支出增加。
        - 台電申請流程繁雜，缺乏透明的計算依據。
        """
    )

    st.markdown("## OptiPower 能帶來的價值")
    st.markdown(
        """
        - 即時呈現不同契約容量下的年費用比較。
        - 自動比對浪費與罰款，快速找到最佳平衡點。
        - 清楚的圖表與報表，協助向住戶或主管說明決策依據。
        - 全中文介面，符合台灣電價制與低壓電力規範。
        """
    )

    st.markdown("## 使用步驟")
    st.markdown(
        """
        1. 準備電費帳單上過去 12 個月的最高需量（經常／尖峰）。
        2. 在下方表單輸入目前契約容量與逐月需量。
        3. 送出後，即可看到最佳方案、節省金額與視覺化圖表。
        4. 評估後即可向台電提出調整申請，減少固定電費支出。
        """
    )


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
            <h2 style='color: #000;
                       font-weight: 700;
                       text-align: center;
                       padding: 12px 0;'>
                🔥 最佳契約容量建議：
                <span style='font-size: 1.3em; font-weight: 700; color: #D00000;
                             text-decoration: underline;
                             text-decoration-color: #000;
                             text-decoration-thickness: 3px;
                             text-decoration-skip-ink: none;'>
                    {optimal_capacity} 千瓦
                </span>
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
        saved_percentage = (saved_fee / current_fee * 100) if current_fee else 0

        st.markdown(
            f"### 💰 優化後一年可節省金額："
            f"<span style='font-weight: 700; color: #D00000;"
            f"text-decoration: underline;"
            f"text-decoration-color: #000;"
            f"text-decoration-thickness: 3px;"
            f"text-decoration-skip-ink: none;'>"
            f"{saved_fee:.2f} 元</span>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"### 📆 平均每個月可節省金額："
            f"<span style='font-weight: 700; color: #D00000;"
            f"text-decoration: underline;"
            f"text-decoration-color: #000;"
            f"text-decoration-thickness: 3px;"
            f"text-decoration-skip-ink: none;'>"
            f"{monthly_saved_fee:.2f} 元</span>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"### 📉 優化後可節省"
            f"<span style='font-weight: 700; color: #D00000;"
            f"text-decoration: underline;"
            f"text-decoration-color: #000;"
            f"text-decoration-thickness: 3px;"
            f"text-decoration-skip-ink: none;'>"
            f"{saved_percentage:.1f}%</span>"
            f" 的基本電費",
            unsafe_allow_html=True
        )

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

def render_faq_section():
    """呈現常見問題與補充說明"""
    st.markdown("## 常見問題（FAQ）")

    with st.expander("Q1. OptiPower 支援哪些電價方案？"):
        st.write(
            "目前工具聚焦於台電的「低壓電力」、「非時間電價」且採用「非營業用」的方案。"
            "這類用戶通常包含中小型社區大樓、小型社區。"
            "若您使用的是高壓或時間電價方案，建議改用台電官方工具或諮詢能源顧問。"
        )

    with st.expander("Q2. 契約容量調整需要多少時間？"):
        st.write(
            "若由高調降至低，通常申請後一週內台電人員即可到場調整電表；"
            "若未來可能擴增設備，建議保留安全餘裕，以免再度申請提高契約容量時耗費額外時間與手續費。"
        )


    with st.expander("Q3. 試算結果能否下載？"):
        st.markdown(
            "1. 請先將左側說明欄位縮起。  \n"
            "2. 點選右上角 3 個點的選單，點取 Print。  \n"
            "3. 點選列印後，就會跳出存檔畫面。  \n"
            "4. 輸入檔案名稱，按下存檔，就可以下載 PDF 檔了。"
        )


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
    # 設定字體
    setup_matplotlib_font()

    # 注入 SEO 資訊 (需在版面主內容前)
    inject_seo_metadata()

    # 記錄訪客 (可選,如果需要的話)
    if "initialized" not in st.session_state:
        log_visit()
        st.session_state["initialized"] = True

    # 渲染側邊欄
    render_sidebar()

    # 首屏靜態內容
    render_intro_section()

    # ✨ 渲染輸入區塊 (使用 form,會返回提交狀態)
    current_capacity, monthly_demands, submitted = render_input_section()

    # ✨ 只有當表單提交且驗證通過時才計算和顯示結果
    if submitted and current_capacity is not None:
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

    # FAQ 與補充說明
    render_faq_section()

    # 渲染頁尾
    render_footer()


if __name__ == "__main__":
    main()
