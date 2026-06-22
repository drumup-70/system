import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import datetime
import time
import json

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)

# 👇👇👇 請將引號內的文字替換成你真實的 Google 試算表網址 👇👇👇
SHEET_URL = "https://docs.google.com/spreadsheets/d/1e6l3j6LoZ_-C5zDfBAmP454h4dM2DUFfUlq7UHPSD4U/edit?gid=0#gid=0"
WORKSHEET_NAME = "系統資料庫"

try:
    sh = client.open_by_url(SHEET_URL)
    try:
        sheet = sh.worksheet(WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        sheet = sh.add_worksheet(title=WORKSHEET_NAME, rows="100", cols="5")
except Exception as e:
    st.error(f"無法連動！請確認網址與共用設定。\n\n系統除錯代碼: {e}")
    st.stop()

st.set_page_config(page_title="工作室統計系統", layout="centered")
st.title("📊 工作室管理系統 (雙向同步版)")

# 讀取並解析 JSON 資料庫
records = sheet.get_all_values()
students = {}
for row in records:
    if len(row) >= 2:
        try:
            students[row[0]] = json.loads(row[1])
        except:
            pass

DEFAULT_STUDENTS = ["Eric", "Marurice", "李知庭", "林劭貞", "黃允麗", "吳若瑀", "李雨蕎", "豬豬", "楊秉睿", "林伯駿", "Kevin"]

tab1, tab2 = st.tabs(["📋 總覽", "✅ 快速簽到"])

with tab1:
    st.subheader("學員列表")
    if not students:
        st.write("目前雲端尚無資料，請先從電腦版輸入學生資料，或由下方簽到建立新檔。")
    else:
        for name, data in students.items():
            classes = data.get("classes", 0)
            balance = data.get("total_cost", 0) - data.get("total_paid", 0)
            status = f"🔴欠費 {balance}元" if balance > 0 else "🟢結清"
            st.write(f"**{name}**: 已上 {classes} 堂 | {status}")

with tab2:
    st.subheader("今日簽到")
    student_list = list(students.keys()) if students else DEFAULT_STUDENTS
    student_name = st.selectbox("請選擇學員", student_list)
    
    if st.button("確認簽到"):
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        # 若為新紀錄則初始化
        if student_name not in students:
            students[student_name] = {"classes": 0, "rate": 0, "total_cost": 0, "total_paid": 0, "history": [], "pay_history": [], "last_pay_date": "未繳費"}
            
        # 同步更新邏輯
        students[student_name]["classes"] += 1
        students[student_name]["total_cost"] += students[student_name].get("rate", 0)
        students[student_name]["history"].append(f"{today}: 上課 +1 堂")
        
        # 寫回試算表
        cell_values = [[name, json.dumps(info, ensure_ascii=False)] for name, info in students.items()]
        sheet.clear()
        sheet.update(range_name='A1', values=cell_values)
        
        st.success(f"✅ 已成功記錄 {student_name} 的簽到！已與電腦版完美同步。")
        st.info("網頁將在 2 秒後自動重新整理...")
        time.sleep(2)
        st.rerun()
