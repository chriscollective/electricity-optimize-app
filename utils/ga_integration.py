# utils/analytics.py
import os
import streamlit as st

# 本機讀 .env（雲端沒有也不報錯）
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_ga_id() -> str | None:
    """
    優先讀取 Streamlit Secrets，其次讀取環境變數/本機 .env
    """
    try:
        # 嘗試從 Streamlit secrets 讀取
        ga_id = st.secrets.get("GA_MEASUREMENT_ID")
        if ga_id:
            return ga_id
    except (KeyError, AttributeError):
        pass

    # 從環境變數讀取
    return os.getenv("GA_MEASUREMENT_ID")


def inject_google_analytics(ga_id: str | None = None, *, show_debug: bool = False) -> None:
    """
    注入 GA4（不顯示同意彈窗）
    - 避免 parent 跨域：以 document.referrer / window.location 取得 URL
    - 加上匿名化 IP
    - 先 'config' 再顯式送一筆 'page_view'
    - 使用 session_state 避免重複注入
    - show_debug=True 時會使用 Streamlit 原生元件顯示訊息
    """
    # 使用 session_state 避免重複注入
    if "ga_injected" in st.session_state and st.session_state.ga_injected:
        return

    ga_id = ga_id or get_ga_id()
    if not ga_id:
        # 未設定 ID 則略過
        if show_debug:
            st.warning("⚠️ Google Analytics ID 未設定")
        return

    # 使用 Streamlit 原生元件顯示 debug 訊息
    if show_debug:
        st.info(f"✅ Google Analytics 已啟用：{ga_id}")

    # 純 JavaScript 注入，不包含 HTML 元素
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      (function() {{
        if (window.__gaInjected) return;   // 前端旗標，避免重複
        window.__gaInjected = true;

        // 在 iframe 內：referrer 通常就是父頁 URL；否則退回當前頁
        var page_location = (document.referrer && document.referrer !== "")
                            ? document.referrer
                            : window.location.href;

        var page_path;
        try {{
          var u = new URL(page_location);
          page_path = u.pathname + u.search + u.hash;
        }} catch (e) {{
          page_path = window.location.pathname + window.location.search + window.location.hash;
        }}

        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}

        gtag('js', new Date());

        // 初始化：不使用 debug_mode（避免被 Developer traffic 過濾）
        gtag('config', '{ga_id}', {{
          anonymize_ip: true,
          page_location: page_location,
          page_path: page_path
        }});

        // 顯式送出一筆 page_view（有些情境不會自動觸發）
        gtag('event', 'page_view', {{
          page_location: page_location,
          page_path: page_path
        }});

        {"console.log('[GA4 injected]', '" + ga_id + "', page_location);" if show_debug else ""}
      }})();
    </script>
    """

    # 高度設為 0，不佔用頁面空間
    st.components.v1.html(ga_code, height=0)

    # 標記已注入
    st.session_state.ga_injected = True
