import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from datetime import datetime

# === APP SETUP ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("✨ Task Manager ✨")
app.geometry("620x550")
app.resizable(False, False)

# === DATABASE SETUP ===
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date Date,
        completed INTEGER DEFAULT 0
    )
""")
conn.commit()

# === FUNCTIONS ===
def refresh_tasks():
    task_display.configure(state="normal")
    task_display.delete("1.0", ctk.END)
    cursor.execute("SELECT id, title, due_date, completed FROM tasks")
    rows = cursor.fetchall()

    if not rows:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        conn.commit()

    header = f"{'ID':<5}{'Task':<30}{'Due Date':<15}{'Status':<10}\n"
    separator = f"{'-'*60}\n"
    task_display.insert(ctk.END, header)
    task_display.insert(ctk.END, separator)
    for row in rows:
        status = "✔️ Done" if row[3] else "❌ Pending"
        task_display.insert(ctk.END, f"{row[0]:<5}{row[1]:<30}{row[2]:<15}{status:<10}\n")
    task_display.configure(state="disabled")

def validate_date(date_str):
    try:
        # Convert from DD/MM/YYYY to datetime object
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def add_task():
    title = task_entry.get()
    due_date = date_entry.get()

    if title.strip() == "" or due_date.strip() == "":
        messagebox.showwarning("Missing Info", "Please enter both title and due date.")
        return

    if not validate_date(due_date):
        messagebox.showerror("Invalid Date", "Please enter a valid date in DD/MM/YYYY format.")
        return

    cursor.execute("INSERT INTO tasks (title, due_date) VALUES (?, ?)", (title, due_date))
    conn.commit()
    task_entry.delete(0, ctk.END)
    date_entry.delete(0, ctk.END)
    refresh_tasks()

def delete_task():
    selected = get_selected_task_id()
    if selected:
        cursor.execute("DELETE FROM tasks WHERE id=?", (selected,))
        conn.commit()
        refresh_tasks()

def mark_done():
    selected = get_selected_task_id()
    if selected:
        cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (selected,))
        conn.commit()
        refresh_tasks()

selected_task_id = None

def on_task_click(event):
    global selected_task_id
    index = task_display.index(f"@{event.x},{event.y}")
    line = index.split(".")[0]
    content = task_display.get(f"{line}.0", f"{line}.end")
    if line == "1" or "--" in content:
        return
    if content:
        task_display.tag_remove("highlight", "1.0", ctk.END)
        task_display.tag_add("highlight", f"{line}.0", f"{line}.end")
        task_display.tag_config("highlight", background="#7D5AFC")
        try:
            selected_task_id = int(content.split()[0])
        except ValueError:
            selected_task_id = None

def get_selected_task_id():
    return selected_task_id

def format_date(event):
    content = date_entry.get().replace("/", "")
    if not content.isdigit():
        return
    if len(content) > 8:
        content = content[:8]
    result = ""
    for i, c in enumerate(content):
        result += c
        if i == 1 or i == 3:
            result += "/"
    date_entry.delete(0, ctk.END)
    date_entry.insert(0, result)

# === UI ===
header = ctk.CTkLabel(app, text="Task Manager", font=("Segoe UI", 24, "bold"), text_color="#FFCF96")
header.pack(pady=10)

frame = ctk.CTkFrame(app)
frame.pack(pady=5)

ctk.CTkLabel(frame, text="Task Title:").grid(row=0, column=0, padx=10, pady=10)
task_entry = ctk.CTkEntry(frame, width=200)
task_entry.grid(row=0, column=1, padx=10, pady=10)

ctk.CTkLabel(frame, text="Due Date (DD/MM/YYYY):").grid(row=1, column=0, padx=10, pady=10)
date_entry = ctk.CTkEntry(frame, width=200)
date_entry.grid(row=1, column=1, padx=10, pady=10)
date_entry.bind("<KeyRelease>", format_date)

add_btn = ctk.CTkButton(app, text="➕ Add Task", command=add_task, fg_color="#94ADD7")
add_btn.pack(pady=10)

task_display = ctk.CTkTextbox(app, width=590, height=230, state="disabled")
task_display.pack(pady=5)
task_display.bind("<Button-1>", on_task_click)

actions = ctk.CTkFrame(app)
actions.pack(pady=5)

delete_btn = ctk.CTkButton(actions, text="🗑️ Delete Task", command=delete_task, fg_color="#FF8080")
delete_btn.grid(row=0, column=0, padx=20, pady=10)

done_btn = ctk.CTkButton(actions, text="✅ Mark Done", command=mark_done, fg_color="#3FA796", text_color="white")
done_btn.grid(row=0, column=1, padx=20, pady=10)

footer = ctk.CTkLabel(app, text="Made with ❤️ by Siddharth | Stay focused ✨", text_color="#C3EDC0", font=("Segoe UI", 12))
footer.pack(pady=10)

refresh_tasks()
app.mainloop()
