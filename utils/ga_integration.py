# utils/analytics.py (檔名隨意)
import streamlit as st

def inject_google_analytics(ga_id: str = "G-MFRF3RTP11"):
    """
    直接啟用 GA4（不彈同意）。避免觸碰 window.parent，避免 debug_mode 被過濾。
    只注入「一份」gtag（很重要！）
    """
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      (function() {{
        // 在 iframe 環境下，referrer 多半是父頁 URL；否則退回當前頁
        var page_location = document.referrer && document.referrer !== "" 
                            ? document.referrer 
                            : window.location.href;

        var page_path;
        try {{
          var url = new URL(page_location);
          page_path = url.pathname + url.search + url.hash;
        }} catch (e) {{
          page_path = window.location.pathname + window.location.search + window.location.hash;
        }}

        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}

        gtag('js', new Date());

        // 初始化你的 GA（不要 debug_mode，避免 Developer traffic 過濾）
        gtag('config', '{ga_id}', {{
          anonymize_ip: true,
          page_location: page_location,
          page_path: page_path
        }});

        // 顯式送出一筆 page_view（某些情境不會自動觸發）
        gtag('event', 'page_view', {{
          page_location: page_location,
          page_path: page_path
        }});
      }})();
    </script>
    """
    st.components.v1.html(ga_code, height=0)
