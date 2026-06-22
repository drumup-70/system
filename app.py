import streamlit as st
import json
import os
import datetime

# 設定資料檔案路徑
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

st.set_page_config(page_title="工作室統計系統", layout="centered")
st.title("📊 工作室管理系統 (手機版)")

students = load_data()

# 頁面選單
menu = st.sidebar.selectbox("功能選單", ["總覽", "快速簽到"])

if menu == "總覽":
    st.subheader("學員列表")
    for name, data in students.items():
        st.write(f"**{name}**: 已上 {len(data.get('history', []))} 堂")

elif menu == "快速簽到":
    st.subheader("今日簽到")
    
    if students:
        # 將手動輸入改為「下拉式選單」
        student_list = list(students.keys())
        student_name = st.selectbox("請選擇學員", student_list)
        
        if st.button("確認簽到"):
            # 防呆機制：確保該學員有 history 欄位可以存紀錄
            if "history" not in students[student_name]:
                students[student_name]["history"] = []
                
            # 自動抓取今天的日期
            today = datetime.date.today().strftime("%Y-%m-%d")
            students[student_name]["history"].append(today)
            
            save_data(students)
            st.success(f"✅ 已成功記錄 {student_name} 的簽到！(目前共 {len(students[student_name]['history'])} 堂)")
    else:
        st.warning("目前系統中沒有學員資料。") 
