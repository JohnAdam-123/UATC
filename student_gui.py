import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db_utils import get_db_connection, clear_session, hash_password, verify_password
from config import ICON_LOGO

def open_student_dashboard(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    username = user[0] if user else "Unknown"
    
    cursor.execute("SELECT course, ca, se, total, grade, status FROM students WHERE name = ?", (username,))
    records = cursor.fetchall()
    conn.close()

    root = tk.Tk()
    root.title(f"Student Dashboard - {username}")
    root.iconbitmap(ICON_LOGO)
    root.geometry("1000x450")
    
    welcome_label = tk.Label(root, text=f"Welcome, {username}", font=("Arial", 16, "bold"))
    welcome_label.pack(pady=10)
    
    frame = tk.Frame(root)
    frame.pack(pady=5, fill="both", expand=True)

    columns = ("Course", "CA", "SE", "Total", "Grade", "Status")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=80, anchor="center")
    tree.pack(fill="both", expand=True)

    def load_records():
        for row in tree.get_children():
            tree.delete(row)
        if not records:
            messagebox.showinfo("No Results", "No results found for your courses.")
        else:
            for rec in records:
                tree.insert("", "end", values=rec)
    
    load_records()

    def edit_profile():
        def submit_changes():
            new_username = username_entry.get().strip()
            pwd = password_entry.get()
            pwd_confirm = password_confirm_entry.get()

            if not new_username:
                messagebox.showerror("Error", "Username cannot be empty")
                return
            
            if pwd or pwd_confirm:
                if pwd != pwd_confirm:
                    messagebox.showerror("Error", "Passwords do not match")
                    return
                new_pwd_hash = hash_password(pwd)
            else:
                new_pwd_hash = None
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                # Check if new username taken by other user
                cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username already taken")
                    return
                
                if new_pwd_hash:
                    cursor.execute("UPDATE users SET username = ?, password_hash = ? WHERE id = ?", (new_username, new_pwd_hash, user_id))
                else:
                    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Profile updated successfully")
                edit_win.destroy()
                # Update welcome label
                welcome_label.config(text=f"Welcome, {new_username}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile: {e}")

        edit_win = tk.Toplevel(root)
        edit_win.title("Edit Profile")
        edit_win.iconbitmap(ICON_LOGO)
        edit_win.geometry("300x250")

        tk.Label(edit_win, text="Username:").pack(pady=5)
        username_entry = tk.Entry(edit_win)
        username_entry.pack(pady=5)
        username_entry.insert(0, username)

        tk.Label(edit_win, text="New Password:").pack(pady=5)
        password_entry = tk.Entry(edit_win, show="*")
        password_entry.pack(pady=5)

        tk.Label(edit_win, text="Confirm Password:").pack(pady=5)
        password_confirm_entry = tk.Entry(edit_win, show="*")
        password_confirm_entry.pack(pady=5)

        tk.Button(edit_win, text="Submit", bg="green", command=submit_changes).pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Refresh", bg="orange", command=load_records).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Edit Profile", bg="green", command=edit_profile).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Logout", bg="blue", fg="white",  command=lambda: logout(root)).pack(side=tk.LEFT, padx=10)
    
    root.mainloop()

def logout(win):
    clear_session()
    win.destroy()
    import login
    login.login_window()
