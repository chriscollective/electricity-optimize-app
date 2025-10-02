"""
Google Analytics 整合模組
用於 Streamlit 應用的 GA 追蹤和 Cookie 同意橫幅
"""
import streamlit.components.v1 as components


def inject_google_analytics(ga_id: str = "G-MFRF3RTP11"):
    """
    直接啟用 GA4（不彈出同意），支援 Streamlit iframe 場景。
    - 避免重複注入：window.__gaInjected 旗標
    - 正確回報網址：優先取父視窗的 URL（Streamlit 會把 component 放在 iframe）
    - 匿名化 IP：anonymize_ip=True
    """
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      if (!window.__gaInjected) {{
        window.__gaInjected = true;

        // 取得實際頁面位置（優先父視窗）
        const loc = (window.parent && window.parent.location) ? window.parent.location : window.location;
        const page_location = loc.href;
        const page_path = loc.pathname + loc.search + loc.hash;

        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}
        gtag('js', new Date());

        // 直接啟用追蹤（不做 consent）
        gtag('config', '{ga_id}', {{
          anonymize_ip: true,
          debug_mode: true,
          page_location: page_location,
          page_path: page_path
        }});
      }}
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