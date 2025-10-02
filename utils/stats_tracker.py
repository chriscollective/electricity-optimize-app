"""
統計追蹤模組 - 使用本地檔案和 Cookie 機制避免重複計數
"""
import json
import streamlit as st
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 統計檔案路徑
STATS_FILE = Path(__file__).parent.parent / "data" / "stats.json"


def ensure_data_directory():
    """確保資料目錄存在"""
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_stats() -> Dict:
    """
    從本地檔案載入統計資料

    Returns:
        統計資料字典，格式:
        {
            "daily": {"2025-01-01": 10, "2025-01-02": 15, ...},
            "total": 1234
        }
    """
    ensure_data_directory()

    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 驗證資料格式
                if not isinstance(data, dict) or 'daily' not in data or 'total' not in data:
                    logger.warning("統計檔案格式不正確，將重新初始化")
                    return initialize_stats()
                return data
        else:
            return initialize_stats()
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析錯誤: {e}")
        return initialize_stats()
    except Exception as e:
        logger.error(f"載入統計資料時發生錯誤: {e}")
        return initialize_stats()


def initialize_stats() -> Dict:
    """初始化統計資料"""
    return {
        "daily": {},
        "total": 0
    }


def save_stats(stats: Dict) -> bool:
    """
    儲存統計資料到本地檔案

    Args:
        stats: 統計資料字典

    Returns:
        是否儲存成功
    """
    ensure_data_directory()

    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"儲存統計資料時發生錯誤: {e}")
        return False


def get_visitor_id() -> str:
    """
    取得訪客唯一識別碼（使用 session_state）

    Returns:
        訪客識別碼
    """
    # 使用 Streamlit 的 session_state 來追蹤唯一訪客
    if 'visitor_id' not in st.session_state:
        # 使用時間戳記和隨機數建立唯一 ID
        import hashlib
        import time
        import random
        unique_string = f"{time.time()}_{random.random()}"
        st.session_state.visitor_id = hashlib.md5(unique_string.encode()).hexdigest()

    return st.session_state.visitor_id


def has_visited_today() -> bool:
    """
    檢查今天是否已經計數過（使用 Cookie 機制）

    Returns:
        True 表示已計數，False 表示尚未計數
    """
    today_str = date.today().isoformat()
    visitor_id = get_visitor_id()

    # 使用 session_state 記錄已計數的日期
    if 'counted_dates' not in st.session_state:
        st.session_state.counted_dates = {}

    # 檢查這個訪客今天是否已計數
    return st.session_state.counted_dates.get(visitor_id) == today_str


def mark_visited_today():
    """標記今天已計數"""
    today_str = date.today().isoformat()
    visitor_id = get_visitor_id()

    if 'counted_dates' not in st.session_state:
        st.session_state.counted_dates = {}

    st.session_state.counted_dates[visitor_id] = today_str


def increment_stats() -> Tuple[Dict, bool]:
    """
    增加統計計數（避免重複計數）

    Returns:
        (更新後的統計資料, 是否成功增加計數)
    """
    # 檢查是否已計數
    if has_visited_today():
        logger.info("今日已計數，跳過")
        return load_stats(), False

    # 載入目前統計
    stats = load_stats()
    today_str = date.today().isoformat()

    # 增加計數
    if today_str not in stats['daily']:
        stats['daily'][today_str] = 0

    stats['daily'][today_str] += 1
    stats['total'] += 1

    # 儲存統計
    success = save_stats(stats)

    if success:
        # 標記今天已計數
        mark_visited_today()
        logger.info(f"統計已更新: 今日 {stats['daily'][today_str]} 次，總計 {stats['total']} 次")

    return stats, success


def get_today_stats() -> Tuple[int, int]:
    """
    取得今日與總計統計數據

    Returns:
        (今日瀏覽次數, 總瀏覽次數)
    """
    stats = load_stats()
    today_str = date.today().isoformat()

    today_count = stats['daily'].get(today_str, 0)
    total_count = stats['total']

    return today_count, total_count


def cleanup_old_stats(days_to_keep: int = 90):
    """
    清理舊的每日統計資料（保留總計）

    Args:
        days_to_keep: 保留最近幾天的資料
    """
    stats = load_stats()
    cutoff_date = (date.today() - timedelta(days=days_to_keep)).isoformat()

    # 移除過舊的每日資料
    old_daily = stats['daily'].copy()
    stats['daily'] = {
        day: count for day, count in old_daily.items()
        if day >= cutoff_date
    }

    # 儲存清理後的資料
    if len(stats['daily']) < len(old_daily):
        save_stats(stats)
        logger.info(f"已清理 {len(old_daily) - len(stats['daily'])} 天的舊資料")
