import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import datetime
import time

# 1. 串接 Google Sheets 認證
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)

# 2. 🚀 終極連線法：直接使用網址 (避開檔名搜尋的錯誤)
# 👇👇👇 請把下面引號裡面的中文，換成你真實的 Google 試算表網址！ 👇👇👇
SHEET_URL = "https://docs.google.com/spreadsheets/d/1e6l3j6LoZ_-C5zDfBAmP454h4dM2DUFfUlq7UHPSD4U/edit?gid=0#gid=0"

try:
    sheet = client.open_by_url(SHEET_URL).worksheet("登載紀錄")
except Exception as e:
    # 這次我把系統真實的錯誤代碼 (e) 顯示出來，如果還失敗，我們就能精準抓漏！
    st.error(f"無法連動！請確認「共用」有設定，且分頁叫「登載紀錄」。\n\n系統除錯代碼: {e}")
    st.stop()

st.set_page_config(page_title="工作室統計系統", layout="centered")
st.title("📊 工作室管理系統 (雲端同步版)")

# 讀取目前所有的簽到紀錄
records = sheet.get_all_records()
df = pd.DataFrame(records)

# 預設學員名單
DEFAULT_STUDENTS = ["Eric", "Marurice", "李知庭", "林劭貞", "黃允麗", "吳若瑀", "李雨蕎", "豬豬", "楊秉睿", "林伯駿", "Kevin"]

# 計算每位學員的總堂數
student_counts = {}
for name in DEFAULT_STUDENTS:
    if not df.empty and "姓名" in df.columns:
        count = len(df[df["姓名"] == name])
    else:
        count = 0
    student_counts[name] = count

# 建立功能頁籤
tab1, tab2 = st.tabs(["📋 總覽", "✅ 快速簽到"])

# ---------- 第一頁：總覽 ----------
with tab1:
    st.subheader("學員列表")
    for name, count in student_counts.items():
        st.write(f"**{name}**: 已上 {count} 堂")

# ---------- 第二頁：快速簽到 ----------
with tab2:
    st.subheader("今日簽到")
    
    student_name = st.selectbox("請選擇學員", DEFAULT_STUDENTS)
    
    if st.button("確認簽到"):
        today = datetime.date.today().strftime("%Y-%m-%d")
        sheet.append_row([today, student_name])
        
        st.success(f"✅ 已成功記錄 {student_name} 的簽到！已同步至 Google 雲端。")
        st.info("網頁將在 2 秒後自動重新整理...")
        
        time.sleep(2)
        st.rerun()
