import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
import json
import os

# === matplotlib 圖表相關模組 ===
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# === 新增：Pillow 影像處理模組 ===
from PIL import Image, ImageTk

# 設定存檔檔案的路徑
DATA_FILE = os.path.expanduser("~/Desktop/studio_data.json")

# 設定 Matplotlib 支援中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Taipei Sans TC Beta', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class StudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DrumUp工作室")
        self.root.geometry("950x820") 
        
        # 讀取存檔
        self.students = self.load_data()

        font_label = ("Arial", 14)
        font_entry = ("Arial", 14)
        font_button = ("Arial", 14, "bold")
        
        # === 這裡已經幫你把表格字體加大到 14，行高加大到 40 ===
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        style.configure("Treeview", font=("Arial", 14), rowheight=40)

        # === 頂部標題與 Logo 區塊 ===
        header_frame = tk.Frame(root)
        header_frame.pack(pady=10)

        # 嘗試在桌面尋找 Logo 圖片 (支援 png 或 jpg)
        logo_path_png = os.path.expanduser("~/Desktop/logo.png")
        logo_path_jpg = os.path.expanduser("~/Desktop/logo.jpg")
        
        valid_logo_path = None
        if os.path.exists(logo_path_png):
            valid_logo_path = logo_path_png
        elif os.path.exists(logo_path_jpg):
            valid_logo_path = logo_path_jpg

        if valid_logo_path:
            try:
                # 開啟圖片並縮小至 60x60 像素
                img = Image.open(valid_logo_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img) 
                lbl_logo = tk.Label(header_frame, image=self.logo_img)
                lbl_logo.pack(side="left", padx=10)
            except Exception as e:
                print(f"無法載入 Logo: {e}")

        # 大標題文字
        tk.Label(
            header_frame, 
            text="教學工作室管理系統", 
            font=("Arial", 22, "bold"), 
            fg="#333333"
        ).pack(side="left")

        # === 上方輸入區塊 ===
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, fill="x", padx=20)

        # 1. 上課日期
        tk.Label(input_frame, text="日期:", font=font_label).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.entry_date = tk.Entry(input_frame, font=font_entry, width=12)
        self.entry_date.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        self.entry_date.insert(0, date.today().strftime("%Y-%m-%d"))

        # 2. 學生姓名
        tk.Label(input_frame, text="姓名:", font=font_label).grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.entry_name = ttk.Combobox(input_frame, font=font_entry, width=11)
        self.entry_name.grid(row=0, column=3, padx=5, pady=8, sticky="w")

        # 3. 新增堂數
        tk.Label(input_frame, text="上課堂數:", font=font_label).grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.entry_classes = tk.Entry(input_frame, font=font_entry, width=12)
        self.entry_classes.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        self.entry_classes.insert(0, "0") 

        # 4. 鐘點費
        tk.Label(input_frame, text="鐘點費/堂:", font=font_label).grid(row=1, column=2, padx=5, pady=8, sticky="e")
        self.entry_rate = tk.Entry(input_frame, font=font_entry, width=12)
        self.entry_rate.grid(row=1, column=3, padx=5, pady=8, sticky="w")

        # 5. 繳費金額
        tk.Label(input_frame, text="繳費金額:", font=font_label).grid(row=0, column=4, padx=5, pady=8, sticky="e")
        self.entry_amount = tk.Entry(input_frame, font=font_entry, width=12)
        self.entry_amount.grid(row=0, column=5, padx=5, pady=8, sticky="w")
        self.entry_amount.insert(0, "0") 

        # 6. 繳費日期
        tk.Label(input_frame, text="繳費日期:", font=font_label).grid(row=1, column=4, padx=5, pady=8, sticky="e")
        self.entry_pay_date = tk.Entry(input_frame, font=font_entry, width=12)
        self.entry_pay_date.grid(row=1, column=5, padx=5, pady=8, sticky="w")
        
        tk.Label(input_frame, text="*若有收到學費才需填寫「繳費金額」與「繳費日期」", font=("Arial", 10), fg="gray").grid(row=2, column=0, columnspan=6, sticky="w", padx=10, pady=5)

        # === 中央按鈕 ===
        self.btn_add = tk.Button(root, text="確認提交紀錄", font=font_button, bg="#4CAF50", fg="black", command=self.add_record)
        self.btn_add.pack(pady=5)

        # === 中央結構化表格區塊 ===
        table_frame = tk.Frame(root)
        table_frame.pack(pady=5, fill="both", expand=True, padx=20)

        columns = ("name", "total_classes", "total_cost", "total_paid", "balance", "monthly_subtotal", "last_pay_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("name", text="學生姓名")
        self.tree.heading("total_classes", text="累積上課")
        self.tree.heading("total_cost", text="上課總價值")
        self.tree.heading("total_paid", text="已收學費")
        self.tree.heading("balance", text="帳戶餘額")
        self.tree.heading("monthly_subtotal", text="當月上課")
        self.tree.heading("last_pay_date", text="最新繳費日")

        self.tree.column("name", width=90, anchor="center")
        self.tree.column("total_classes", width=80, anchor="center")
        self.tree.column("total_cost", width=95, anchor="center")
        self.tree.column("total_paid", width=95, anchor="center")
        self.tree.column("balance", width=120, anchor="center")
        self.tree.column("monthly_subtotal", width=120, anchor="center")
        self.tree.column("last_pay_date", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_student_select)

        # 營運統計文字
        self.lbl_grand_total = tk.Label(root, text="💰 總應收累計：0 元  |  實收進帳：0 元", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_grand_total.pack(pady=5)

        # === 管理操作按鈕區 ===
        action_frame = tk.Frame(root)
        action_frame.pack(pady=5)
        
        self.btn_quick_sign = tk.Button(action_frame, text="✅ 今日快速簽到 (+1堂)", font=("Arial", 12, "bold"), bg="#FFC107", fg="black", command=self.quick_sign_in)
        self.btn_quick_sign.pack(side="left", padx=10)

        self.btn_charts = tk.Button(action_frame, text="📊 顯示營運統計圖表", font=("Arial", 12, "bold"), bg="#2196F3", fg="black", command=self.show_statistics_charts)
        self.btn_charts.pack(side="left", padx=10)

        self.btn_delete = tk.Button(action_frame, text="🗑️ 刪除", font=("Arial", 12, "bold"), bg="#FF5722", fg="black", command=self.delete_record)
        self.btn_delete.pack(side="left", padx=10)

        # === 下方詳細歷史紀錄區塊 ===
        tk.Label(root, text="【 點擊上方學員，查看詳細歷史軌跡 】", font=("Arial", 12, "bold"), fg="purple").pack(pady=5)
        self.text_detail = tk.Text(root, height=8, width=105, font=("Courier", 12), bg="#E8E8E8", fg="black")
        self.text_detail.pack(pady=10, padx=20)

        self.update_combobox_values()
        self.update_display()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict): return {}
                    cleaned_data = {}
                    for name, info in data.items():
                        if not isinstance(info, dict): continue
                        cls_val = info.get("classes", info.get("total_classes", 0))
                        rate_val = info.get("rate", 0)
                        old_total = info.get("total", 0)
                        cost_val = info.get("total_cost", old_total if old_total > 0 else (cls_val * rate_val))
                        paid_val = info.get("total_paid", cost_val)
                        cleaned_data[name] = {
                            "classes": int(cls_val), "rate": int(rate_val),
                            "total_cost": int(cost_val), "total_paid": int(paid_val),
                            "history": list(info.get("history", [])),
                            "pay_history": list(info.get("pay_history", [])),
                            "last_pay_date": str(info.get("last_pay_date", "未繳費"))
                        }
                    return cleaned_data
            except: return {}
        return {}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.students, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("存檔失敗", f"無法寫入硬碟：{str(e)}")

    def update_combobox_values(self):
        self.entry_name['values'] = sorted(list(self.students.keys()))

    def add_record(self):
        record_date = self.entry_date.get().strip()
        name = self.entry_name.get().strip()
        pay_date = self.entry_pay_date.get().strip()
        
        if not name:
            messagebox.showwarning("輸入錯誤", "請確認填寫「學生姓名」！")
            return
            
        try:
            classes = int(self.entry_classes.get()) if self.entry_classes.get().strip() else 0
            rate = int(self.entry_rate.get()) if self.entry_rate.get().strip() else 0
            pay_amount = int(self.entry_amount.get()) if self.entry_amount.get().strip() else 0
        except ValueError:
            messagebox.showerror("輸入錯誤", "堂數、鐘點費與繳費金額必須是『整數數字』！")
            return

        if name not in self.students:
            if classes > 0 and rate == 0:
                messagebox.showwarning("輸入錯誤", "新學生請輸入鐘點費！")
                return
            self.students[name] = {
                "classes": 0, "rate": rate, "total_cost": 0, "total_paid": 0,
                "history": [], "pay_history": [], "last_pay_date": "未繳費"
            }
        
        if classes > 0:
            if rate > 0: self.students[name]["rate"] = rate
            self.students[name]["classes"] += classes
            self.students[name]["total_cost"] += classes * self.students[name]["rate"]
            self.students[name]["history"].append(f"{record_date}: 上課 +{classes} 堂")

        if pay_amount > 0:
            self.students[name]["total_paid"] += pay_amount
            final_pay_date = pay_date if pay_date else record_date
            self.students[name]["last_pay_date"] = final_pay_date
            self.students[name]["pay_history"].append(f"{final_pay_date}: 繳費 ${pay_amount} 元")

        self.save_data()
        self.update_combobox_values()

        self.entry_name.set("")
        self.entry_classes.delete(0, tk.END)
        self.entry_classes.insert(0, "0")
        self.entry_rate.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, "0")
        self.entry_pay_date.delete(0, tk.END)

        self.update_display()
        messagebox.showinfo("成功", f"✅ 已成功更新 [{name}] 的紀錄！")

    def quick_sign_in(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("操作提示", "請先在上方表格中點選想要簽到的學生！")
            return
            
        student_name = self.tree.item(selected_items[0])["values"][0]
        today_str = date.today().strftime("%Y-%m-%d")
        
        if student_name in self.students:
            self.students[student_name]["classes"] += 1
            current_rate = self.students[student_name].get("rate", 0)
            self.students[student_name]["total_cost"] += current_rate
            
            self.students[student_name]["history"].append(f"{today_str}: 上課 +1 堂")
            
            self.save_data()
            self.update_display()
            self.text_detail.delete("1.0", tk.END) 
            
            messagebox.showinfo("簽到成功", f"✅ 已成功為 [{student_name}] 登記今日 ({today_str}) 上課 1 堂！")

    def delete_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("操作提示", "請先在上方表格中點選想要刪除的學生！")
            return
        student_name = self.tree.item(selected_items[0])["values"][0]
        if messagebox.askyesno("確認刪除", f"⚠️ 確定要完全刪除學員 [{student_name}] 的所有紀錄嗎？"):
            if student_name in self.students:
                del self.students[student_name]
                self.save_data()
                self.update_combobox_values()
                self.update_display()
                self.text_detail.delete("1.0", tk.END)
                messagebox.showinfo("成功", f"❌ 已完全刪除學員 [{student_name}] 的所有資料。")

    def update_display(self):
        for row in self.tree.get_children(): 
            self.tree.delete(row)
            
        if not self.students: 
            return

        grand_total_cost = 0
        grand_total_paid = 0
        
        current_month = date.today().strftime("%Y-%m")

        sorted_students = sorted(
            self.students.items(), 
            key=lambda x: x[1].get("history", [""])[-1] if x[1].get("history") else ""
        )

        for name, data in sorted_students:
            data["history"].sort()
            data["pay_history"].sort()

            monthly_totals = {}
            for entry in data["history"]:
                if "上課 +" in entry:
                    d_str, c_str = entry.split(": 上課 +", 1)
                elif ": +" in entry:
                    d_str, c_str = entry.split(": +", 1)
                else:
                    continue
                
                m_key = d_str[:7]
                try:
                    num = int(c_str.replace(" 堂", "").strip())
                    monthly_totals[m_key] = monthly_totals.get(m_key, 0) + num
                except ValueError:
                    pass
            
            this_month_classes = monthly_totals.get(current_month, 0)
            monthly_display = f"{current_month} ({this_month_classes}堂)"

            balance_val = data.get("total_cost", 0) - data.get("total_paid", 0)
            if balance_val > 0: 
                balance_display = f"🔴 欠繳 {balance_val} 元"
            elif balance_val < 0: 
                balance_display = f"🟢 預收 {abs(balance_val)} 元"
            else: 
                balance_display = "🟢 已結清"

            self.tree.insert("", "end", values=(
                name, 
                f"{data['classes']} 堂", 
                f"{data.get('total_cost', 0)} 元",
                f"{data.get('total_paid', 0)} 元", 
                balance_display, 
                monthly_display,
                data.get("last_pay_date", "未繳費")
            ))
            
            grand_total_cost += data.get('total_cost', 0)
            grand_total_paid += data.get('total_paid', 0)
            
        self.lbl_grand_total.config(
            text=f"💰 總應收累計：{grand_total_cost} 元  |  實收進帳：{grand_total_paid} 元"
        )

    def on_student_select(self, event):
        self.text_detail.delete("1.0", tk.END)
        selected_items = self.tree.selection()
        if not selected_items: return
        student_name = self.tree.item(selected_items[0])["values"][0]
        
        if student_name in self.students:
            data = self.students[student_name]
            self.text_detail.insert(tk.END, f"【學員詳細帳務與上課歷程】 姓名：{student_name}\n")
            self.text_detail.insert(tk.END, "-" * 95 + "\n")
            self.text_detail.insert(tk.END, f" 🗓️ 歷史上課軌跡：{'、'.join(data['history']) if data['history'] else '暫無歷史上課紀錄'}\n\n")
            self.text_detail.insert(tk.END, f" 💳 歷史繳費明細：{'、'.join(data.get('pay_history', [])) if data.get('pay_history') else '尚未有繳費登記'}\n")
            self.text_detail.insert(tk.END, "-" * 95 + "\n")

    def show_statistics_charts(self):
        monthly_revenue = {}
        monthly_classes = {}

        for name, data in self.students.items():
            for entry in data.get("pay_history", []):
                try:
                    date_str, amount_str = entry.split(": 繳費 $")
                    month = date_str[:7] 
                    amount = int(amount_str.replace(" 元", "").strip())
                    monthly_revenue[month] = monthly_revenue.get(month, 0) + amount
                except: pass

            for entry in data.get("history", []):
                if "上課 +" in entry:
                    try:
                        date_str, classes_str = entry.split(": 上課 +")
                        month = date_str[:7]
                        classes = int(classes_str.replace(" 堂", "").strip())
                        monthly_classes[month] = monthly_classes.get(month, 0) + classes
                    except: pass

        all_months = sorted(list(set(list(monthly_revenue.keys()) + list(monthly_classes.keys()))))
        if not all_months:
            messagebox.showinfo("圖表提示", "目前沒有足夠的歷史資料可以產生圖表！")
            return

        revenue_values = [monthly_revenue.get(m, 0) for m in all_months]
        classes_values = [monthly_classes.get(m, 0) for m in all_months]

        chart_window = tk.Toplevel(self.root)
        chart_window.title("工作室營運統計圖表")
        chart_window.geometry("800x600")

        fig = Figure(figsize=(8, 6), dpi=100)
        
        ax1 = fig.add_subplot(211)
        ax1.bar(all_months, revenue_values, color='#4CAF50', width=0.5)
        ax1.set_title("各月份實收進帳總額 (元)", fontsize=14)
        ax1.set_ylabel("金額 (元)")
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        for i, v in enumerate(revenue_values):
            ax1.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

        ax2 = fig.add_subplot(212)
        ax2.plot(all_months, classes_values, marker='o', color='#2196F3', linewidth=2, markersize=8)
        ax2.set_title("各月份上課總堂數", fontsize=14)
        ax2.set_ylabel("堂數")
        ax2.grid(axis='both', linestyle='--', alpha=0.7)
        for i, v in enumerate(classes_values):
            ax2.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudioApp(root)
    root.mainloop()
