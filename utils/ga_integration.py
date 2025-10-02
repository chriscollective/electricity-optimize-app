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


def inject_google_analytics(ga_id: str | None = None, *, show_debug: bool = True) -> None:
    if "ga_injected" in st.session_state and st.session_state.ga_injected:
        return

    ga_id = ga_id or get_ga_id()
    if not ga_id:
        if show_debug:
            st.warning("⚠️ Google Analytics ID 未設定")
        return

    # 顯示一條可見的 debug 橫幅，確保 component 有渲染
    if show_debug:
        st.markdown(
            f"""<div style="font:12px/1.4 system-ui; background:#ffe08a; color:#222;
                 padding:6px 10px; border:1px solid #d4b556; border-radius:6px; width:fit-content; margin-bottom:6px;">
                 GA4 tag injected → <b>{ga_id}</b></div>""",
            unsafe_allow_html=True
        )

    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      (function() {{
        if (window.__gaInjected) return;
        window.__gaInjected = true;

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

        // 初始化 + 明確送出 page_view
        gtag('config', '{ga_id}', {{
          anonymize_ip: true,
          page_location: page_location,
          page_path: page_path
        }});
        gtag('event', 'page_view', {{
          page_location: page_location,
          page_path: page_path
        }});

        // 再送一筆測試事件，方便在 Network/DebugView 抓到
        gtag('event', 'test_ping', {{ ping: '1' }});

        console.log('[GA4 injected]', '{ga_id}', page_location);
      }})();
    </script>
    """
    st.components.v1.html(ga_code, height=60)  # 先給高度，驗證用
    st.session_state.ga_injected = True
