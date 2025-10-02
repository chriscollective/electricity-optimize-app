"""
Google Analytics 整合模組
用於 Streamlit 應用的 GA 追蹤和 Cookie 同意橫幅
"""
import streamlit.components.v1 as components


def inject_google_analytics(ga_id: str = "G-MFRF3RTP11"):
    """
    直接啟用 GA4（不彈同意），避開跨網域存取 parent 的問題。
    - page_location 優先用 document.referrer（在 iframe 內會是父頁網址）
    - 保留 anonymize_ip，避免隱私告警
    - 不使用 debug_mode，避免被 Developer traffic 過濾
    """
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      (function() {{
        // 安全取得實際頁面位置（不觸碰 window.parent）
        var page_location = document.referrer && document.referrer !== "" 
                            ? document.referrer 
                            : window.location.href;

        var page_path;
        try {{
          // 從 referrer 拆出 path（若 referrer 不可解析就退回當前頁）
          var url = new URL(page_location);
          page_path = url.pathname + url.search + url.hash;
        }} catch (e) {{
          page_path = window.location.pathname + window.location.search + window.location.hash;
        }}

        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}

        gtag('js', new Date());

        // 初始化你的 GA
        gtag('config', '{ga_id}', {{
          anonymize_ip: true,
          page_location: page_location,
          page_path: page_path
        }});

        // 顯式送出一筆 page_view
        gtag('event', 'page_view', {{
          page_location: page_location,
          page_path: page_path
        }});
      }})();
    </script>
    """
    # 注入到頁面 (高度設為 0,不佔空間)
    components.html(ga_code, height=0)
    
    



    """
    簡化版 Google Analytics (不含 Cookie 橫幅)
    適合不需要符合 GDPR 或用戶主要在非歐盟地區的情況
    
    使用方式:
        用此函數取代 inject_google_analytics() + inject_cookie_banner()
    """
    GA_ID = "G-XXXXXXXXXX"  # ⚠️ 請替換成你的真實 Google Analytics ID
    
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    """
    
    components.html(ga_code, height=0)