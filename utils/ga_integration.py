"""
Google Analytics 整合模組
用於 Streamlit 應用的 GA 追蹤和 Cookie 同意橫幅
"""
import streamlit.components.v1 as components


def inject_google_analytics():
    """
    注入 Google Analytics 追蹤碼
    
    使用方式:
        在 main() 函數開頭呼叫此函數
    """
    GA_ID = "G-MFRF3RTP11"  # ⚠️ 請替換成你的真實 Google Analytics ID
    
    ga_code = f"""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        
        // 預設不啟用追蹤,等待用戶同意
        gtag('consent', 'default', {{
            'analytics_storage': 'denied'
        }});
        
        gtag('config', '{GA_ID}');
    </script>
    """
    
    # 注入到頁面 (高度設為 0,不佔空間)
    components.html(ga_code, height=0)


def inject_cookie_banner():
    """
    注入 Cookie 同意橫幅
    符合 GDPR 規範,用戶同意後才啟用 Google Analytics
    
    使用方式:
        在 main() 函數中,inject_google_analytics() 之後呼叫
    """
    cookie_banner_html = """
    <style>
        /* Cookie 橫幅容器 */
        #cookieBanner {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
            display: none;
            z-index: 9999;
            animation: slideUp 0.4s ease-out;
        }
        
        /* 滑入動畫 */
        @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
        }
        
        /* 顯示橫幅 */
        #cookieBanner.show {
            display: block;
        }
        
        /* 內容容器 */
        .cookie-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        /* 文字區域 */
        .cookie-text {
            flex: 1;
            min-width: 250px;
        }
        
        .cookie-text h3 {
            font-size: 18px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .cookie-text p {
            font-size: 14px;
            opacity: 0.95;
            line-height: 1.5;
        }
        
        /* 按鈕容器 */
        .cookie-buttons {
            display: flex;
            gap: 12px;
        }
        
        /* 按鈕基本樣式 */
        .cookie-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        /* 接受按鈕 */
        .accept-btn {
            background: white;
            color: #667eea;
        }
        
        .accept-btn:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        /* 拒絕按鈕 */
        .reject-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
        }
        
        .reject-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* 手機版響應式 */
        @media (max-width: 768px) {
            .cookie-content {
                flex-direction: column;
                text-align: center;
            }
            
            .cookie-buttons {
                width: 100%;
                justify-content: center;
            }
            
            .cookie-btn {
                flex: 1;
                min-width: 120px;
            }
        }
    </style>
    
    <!-- Cookie 橫幅 HTML -->
    <div id="cookieBanner">
        <div class="cookie-content">
            <div class="cookie-text">
                <h3>🍪 Cookie 使用聲明</h3>
                <p>本網站使用 Google Analytics 來分析訪客流量,以改善使用體驗。我們不會收集個人身份資訊。</p>
            </div>
            <div class="cookie-buttons">
                <button class="cookie-btn accept-btn" onclick="acceptCookies()">接受</button>
                <button class="cookie-btn reject-btn" onclick="rejectCookies()">拒絕</button>
            </div>
        </div>
    </div>
    
    <script>
        /**
         * 檢查用戶之前的 Cookie 同意狀態
         */
        function checkCookieConsent() {
            const consent = localStorage.getItem('cookieConsent');
            
            if (consent === null) {
                // 尚未選擇,顯示橫幅
                document.getElementById('cookieBanner').classList.add('show');
            } else if (consent === 'accepted') {
                // 已接受,啟用 Analytics
                enableAnalytics();
            }
            // 如果是 'rejected',什麼都不做
        }
        
        /**
         * 用戶點擊「接受」按鈕
         */
        function acceptCookies() {
            // 儲存選擇
            localStorage.setItem('cookieConsent', 'accepted');
            
            // 隱藏橫幅
            document.getElementById('cookieBanner').classList.remove('show');
            
            // 啟用 Google Analytics
            enableAnalytics();
        }
        
        /**
         * 用戶點擊「拒絕」按鈕
         */
        function rejectCookies() {
            // 儲存選擇
            localStorage.setItem('cookieConsent', 'rejected');
            
            // 隱藏橫幅
            document.getElementById('cookieBanner').classList.remove('show');
        }
        
        /**
         * 啟用 Google Analytics 追蹤
         */
        function enableAnalytics() {
            // 確保 gtag 函數存在
            if (typeof gtag !== 'undefined') {
                gtag('consent', 'update', {
                    'analytics_storage': 'granted'
                });
            }
        }
        
        // 頁面載入時檢查
        window.addEventListener('load', checkCookieConsent);
    </script>
    """
    
    # 注入 Cookie 橫幅 (高度 120 以確保完整顯示)
    components.html(cookie_banner_html, height=120, scrolling=False)


# ==================== 可選:簡化版本 ====================

def inject_ga_simple():
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