# utils/sheet_tracker.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import uuid

SHEET_NAME = "OptipowerSheet"  # 你的 Google Sheet 名稱

def get_sheet():
    # 使用 Cloud Secrets 裡的 [GOOGLE_SERVICE_ACCOUNT]
    creds = Credentials.from_service_account_info(
        st.secrets["GOOGLE_SERVICE_ACCOUNT"],  # <-- 注意這裡
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def log_visit():
    """只在使用者 session 第一次訪問時記錄到 Google Sheet"""

    # 已初始化過就不再執行（避免互動 rerun 重複執行）
    if st.session_state.get("initialized", False):
        return False

    sheet = get_sheet()

    # 每個使用者 session 給一個唯一 ID
    if "visitor_id" not in st.session_state:
        st.session_state.visitor_id = str(uuid.uuid4())

    today = date.today().isoformat()
    sheet.append_row([today, st.session_state.visitor_id])

    # 標記已初始化
    st.session_state["initialized"] = True
    return True


def get_stats():
    """回傳今日訪客數 & 總訪客數"""
    sheet = get_sheet()
    data = sheet.get_all_records()

    total = len(data)
    today = date.today().isoformat()
    today_count = sum(1 for row in data if row.get("Date") == today)

    return today_count, total
