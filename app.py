import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import datetime
import time

# 1. 串接 Google Sheets 認證
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)

# 2. 開啟指定試算表 (請確保名稱與你的 Google 試算表完全一致)
SPREADSHEET_NAME = "工作室管理系統"
try:
    sheet = client.open(SPREADSHEET_NAME).worksheet("登載紀錄")
except Exception as e:
    st.error(f"無法連動試算表，請確認試算表名稱是否為 '{SPREADSHEET_NAME}'，且已共用權限給服務帳戶。")
    st.stop()

st.set_page_config(page_title="工作室統計系統", layout="centered")
st.title("📊 工作室管理系統 (雲端同步版)")

# 讀取目前所有的簽到紀錄
records = sheet.get_all_records()
df = pd.DataFrame(records)

# 你的專屬學員名單
DEFAULT_STUDENTS = ["Eric", "Marurice", "李知庭", "林劭貞", "黃允麗", "吳若瑀", "李雨蕎", "豬豬", "楊秉睿", "林伯駿", "Kevin"]

# 計算每位學員的總堂數
student_counts = {}
for name in DEFAULT_STUDENTS:
    if not df.empty and "姓名" in df.columns:
        # 計算該姓名在試算表中出現的次數
        count = len(df[df["姓名"] == name])
    else:
        count = 0
    student_counts[name] = count

# 建立功能頁籤，手機操作更直覺
tab1, tab2 = st.tabs(["📋 總覽", "✅ 快速簽到"])

# ---------- 第一頁：總覽 ----------
with tab1:
    st.subheader("學員列表")
    for name, count in student_counts.items():
        st.write(f"**{name}**: 已上 {count} 堂")

# ---------- 第二頁：快速簽到 ----------
with tab2:
    st.subheader("今日簽到")
    
    # 下拉式選單選擇學員
    student_name = st.selectbox("請選擇學員", DEFAULT_STUDENTS)
    
    if st.button("確認簽到"):
        # 取得今天日期
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        # 將新紀錄直接附加寫入到 Google 試算表的最後一行
        sheet.append_row([today, student_name])
        
        st.success(f"✅ 已成功記錄 {student_name} 的簽到！系統已同步寫入雲端試算表。")
        st.info("網頁將在 2 秒後自動重新整理...")
        
        # 延遲後重整頁面以更新堂數
        time.sleep(2)
        st.rerun()
