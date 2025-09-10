import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ----------------------------
# Global Variables
# ----------------------------
df = None
report = {}

# ----------------------------
# Functions
# ----------------------------
def load_file():
    global df, report
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        df = pd.read_excel(file_path)
        report = {'initial_rows': df.shape[0], 'initial_columns': df.shape[1], 'actions': {}}
        messagebox.showinfo("Loaded", f"File loaded successfully: {file_path}\nRows: {df.shape[0]}, Columns: {df.shape[1]}")
        update_buttons(state="normal")

def update_buttons(state="normal"):
    btn_missing.config(state=state)
    btn_duplicates.config(state=state)
    btn_outliers.config(state=state)
    btn_save.config(state=state)

# ----------------------------
# Preview and Fill Missing Values
# ----------------------------
def preview_missing():
    missing_info = df.isnull().sum()
    missing_cols = missing_info[missing_info > 0].index.tolist()
    if not missing_cols:
        messagebox.showinfo("Missing Values", "No missing values found.")
        return

    preview_window = tk.Toplevel(root)
    preview_window.title("Missing Values Preview")

    tk.Label(preview_window, text="Columns with missing values:").pack()
    tree = ttk.Treeview(preview_window, columns=("MissingCount", "Action"), show="headings")
    tree.heading("MissingCount", text="Missing Count")
    tree.heading("Action", text="Action")
    tree.pack(fill="both", expand=True)

    for col in missing_cols:
        tree.insert("", "end", values=(col, missing_info[col], "Pending"))

    def apply_missing():
        for item in tree.get_children():
            col, count, action = tree.item(item, "values")
            if action.lower() == "fill":
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = df[col].mean()
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    fill_value = df[col].mode()[0] if not df[col].mode().empty else pd.Timestamp.today()
                else:
                    fill_value = "Unknown"
                df[col] = df[col].fillna(fill_value)
                report['actions'][f'missing_filled_{col}'] = count
        preview_window.destroy()
        messagebox.showinfo("Missing Values", "Selected missing values filled successfully.")

    # Add simple instruction for action selection
    tk.Label(preview_window, text="Double-click a row to mark 'Fill' action").pack(pady=5)

    def toggle_action(event):
        selected = tree.selection()[0]
        col, count, action = tree.item(selected, "values")
        new_action = "Fill" if action.lower() == "pending" else "Pending"
        tree.item(selected, values=(col, count, new_action))

    tree.bind("<Double-1>", toggle_action)

    tk.Button(preview_window, text="Apply Selected Actions", command=apply_missing).pack(pady=5)

# ----------------------------
# Preview and Remove Duplicates
# ----------------------------
def preview_duplicates():
    duplicates_count = df.duplicated().sum()
    if duplicates_count == 0:
        messagebox.showinfo("Duplicates", "No duplicate rows found.")
        return
    if messagebox.askyesno("Duplicates", f"{duplicates_count} duplicate rows found.\nDo you want to remove them?"):
        df.drop_duplicates(inplace=True)
        report['actions']['duplicates_removed'] = duplicates_count
        messagebox.showinfo("Duplicates", f"{duplicates_count} duplicate rows removed.")

# ----------------------------
# Preview and Remove Outliers
# ----------------------------
def preview_outliers():
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_rows = pd.DataFrame()
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        col_outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
        if not col_outliers.empty:
            col_outliers["OutlierColumn"] = col
            outlier_rows = pd.concat([outlier_rows, col_outliers])

    if outlier_rows.empty:
        messagebox.showinfo("Outliers", "No outliers detected.")
        return

    preview_window = tk.Toplevel(root)
    preview_window.title("Outliers Preview")

    tk.Label(preview_window, text="Preview of outlier rows:").pack()
    text = tk.Text(preview_window, wrap="none", height=20)
    text.pack(fill="both", expand=True)
    text.insert(tk.END, outlier_rows.head(50).to_string())  # Show first 50 rows

    def apply_outliers():
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            before_rows = df.shape[0]
            df_filtered = df[(df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)]
            removed = before_rows - df_filtered.shape[0]
            df.drop(df.index, inplace=True)
            df_filtered.index = df.index
            df.update(df_filtered)
            if removed > 0:
                report['actions'][f'outliers_removed_{col}'] = removed
        preview_window.destroy()
        messagebox.showinfo("Outliers", "Outliers removed as per IQR method.")

    tk.Button(preview_window, text="Remove Outliers", command=apply_outliers).pack(pady=5)

# ----------------------------
# Save Cleaned Data and Report
# ----------------------------
def save_cleaned():
    cleaned_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx *.xls")])
    if cleaned_file:
        df.to_excel(cleaned_file, index=False)
        report['final_rows'] = df.shape[0]
        report['final_columns'] = df.shape[1]
        report_file = cleaned_file.replace(".xlsx", "_report.xlsx")
        pd.DataFrame.from_dict(report, orient='index').to_excel(report_file)
        messagebox.showinfo("Saved", f"Cleaned data saved to {cleaned_file}\nReport saved to {report_file}")

# ----------------------------
# GUI Setup
# ----------------------------
root = tk.Tk()
root.title("Advanced Excel Data Cleaner")

btn_load = tk.Button(root, text="Load Excel File", command=load_file, width=40)
btn_load.pack(pady=10)

btn_missing = tk.Button(root, text="Preview & Fill Missing Values", command=preview_missing, state="disabled", width=40)
btn_missing.pack(pady=5)

btn_duplicates = tk.Button(root, text="Preview & Remove Duplicates", command=preview_duplicates, state="disabled", width=40)
btn_duplicates.pack(pady=5)

btn_outliers = tk.Button(root, text="Preview & Remove Outliers", command=preview_outliers, state="disabled", width=40)
btn_outliers.pack(pady=5)

btn_save = tk.Button(root, text="Save Cleaned Data & Report", command=save_cleaned, state="disabled", width=40)
btn_save.pack(pady=10)

root.mainloop()