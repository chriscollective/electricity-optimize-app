"""
側邊欄 UI 元件模組
"""
import streamlit as st
from utils.sheet_tracker import get_stats

def render_sidebar():
    """
    渲染側邊欄內容


    """
    st.sidebar.header("🔖 網站說明")

    # 契約容量說明
    st.sidebar.markdown("### 什麼是契約容量？")
    st.sidebar.write(
        "契約容量是指台電與用戶之間約定的最高用電需求量(平均15分鐘內)，以千瓦(kW)為單位，超過會加倍收取費用。"
    )
    st.sidebar.write(
        "你可以想像契約容量像是手機的月租費，不管用電量多或少，都是固定的支出費用。"
        "另一種比喻是契約容量就像水管的粗細大小，如果你同時間需要的水量(電量)越大，"
        "那你的水管直徑大小(契約容量)也要越大，這個與你的總用水量(總用電量)沒關係，而是與你的瞬間需求量有關。"
    )
    st.sidebar.write(
        "舉例來說，同一時間公設區域用的電量越多(照明、冷氣、電梯、抽水馬達等等)，那你也需要更高的契約容量。"
    )
    st.sidebar.markdown("---")

    # 適用對象
    st.sidebar.markdown("### 👤 誰適合使用本網站？")
    st.sidebar.write("這個網站適用於使用「低壓電力」、「非時間電價」方案，契約容量小於100WK(千瓦)的用戶，特別適合台灣中小型社區。")
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

    # 電費計算方式
    st.sidebar.markdown("### 電費的計算方式")
    st.sidebar.write(
        "電費 = 契約容量 × 基本電費 + 用電量 × 流動電費，依夏月（6~9月）與非夏月不同計價。"
        "<<此網站只計算基本電費總額>>，因為流動電費與契約容量無關。"
    )
    st.sidebar.write(
        "夏月: 基本電費236.2元/千瓦，流動電費3.44/度\n\n"
        "非夏月:基本電費173.2元/千瓦，流動電費3.26/度"
    )
    st.sidebar.write(
        "超額罰款:超出契約容量10%以內為2倍電價，10%以上為3倍電價。"
    )
    st.sidebar.write(
        "P.S.如果社區每月用電需求量差異很大(夏天與非夏天)，那麼很有可能偶爾被罰錢還會比較便宜。"
        "(因為基本費用省下的金額>罰款的金額)"
    )
    st.sidebar.markdown("---")

    # 注意事項
    st.sidebar.markdown("### ⚠️ 注意事項")
    st.sidebar.write(
        "契約容量由高改成低不用額外的變更費用，但是若為由低改高則需額外的變更費用。"
        "如果確定社區內短期間不會再新增任何的公共設備，那麼由高改低不會有太大的問題。"
        "反之，如果社區未來可能會新增設備，用電量可能會上升，那麼建議是可以預留多一點的空間，"
        "不用一次調得太低。不過站主認為省下來的錢都可以申請好幾次了"
        "(依站主自身社區的例子是這樣，但每個社區狀況不一樣，請各主委自行判斷。)"
    )
    st.sidebar.markdown("---")

    # 申請變更方式
    st.sidebar.markdown("### 📝 申請變更方式")
    st.sidebar.write(
        "主委帶著大小章（社區大章、主委個人章）、身分證、區公所公文（申報公文，證明主委身份），"
        "到台電服務處臨櫃申請契約容量變更，直接告訴櫃檯人員說你要改為多少千瓦"
        "(其實你也可以請台電人員幫你計算改為多少最合理，他可以查閱歷年資料來計算，但是你看不到他是怎麼算的)，"
        "通過後大約一周內，會有台電人員到社區內調整電表。"
    )
    st.sidebar.markdown("---")

    # 為什麼要做這個網站
    st.sidebar.markdown("### 為什麼站主要寫這個網站")
    st.sidebar.write(
        "因為站主接任了30年的老社區主委，發現電費頗高，花了很多時間研究，才明白其中原因。"
        "(如果當初社區管理人員早一點調整，30年的時間至少可以省下將近90萬的電費!)"
        "希望藉由這個網站幫助更多人省錢!也練習與AI溝通的能力!"
    )
    st.sidebar.markdown("---")

    # 贊助支持
    st.sidebar.header("🙌 贊助與支持")
    st.sidebar.write(
        "如果你覺得這個網站對你有幫助，歡迎透過以下LINE Pay QR code自由樂捐給站主，感謝你的支持！"
    )
    st.sidebar.image(
        "linepay_qrcode.JPG",
        width=200,
        caption="LINE Pay QR Code－贊助 OptiPower"
    )
    st.sidebar.markdown("---")

    # 聯繫與反饋
    st.sidebar.markdown("### 📬 聯繫與反饋")
    st.sidebar.write("如果有任何網站相關的問題，歡迎寄信到以下信箱聯繫站主：")
    st.sidebar.code("justakiss918@gmail.com")
    st.sidebar.write("網站最新更新日期:2025/10/19")
    st.sidebar.markdown("---")

    # 瀏覽統計
    st.sidebar.markdown("### 📈 瀏覽人數統計")
    try:
        today_count, total_count = get_stats()
        st.sidebar.write(f"🔢 今日瀏覽次數：{today_count}")
        st.sidebar.write(f"📊 總瀏覽次數：{total_count}")
    except Exception as e:
        st.sidebar.write("⚠️ 無法讀取人數統計")
        st.sidebar.code(str(e))
    st.sidebar.markdown("---")
