import streamlit as st
import json
import os

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
    student_name = st.text_input("輸入學員姓名")
    if st.button("確認簽到"):
        if student_name in students:
            students[student_name]["history"].append("2026-06-20")
            save_data(students)
            st.success(f"已成功記錄 {student_name} 的簽到！")
        else:
            st.error("找不到該學員")