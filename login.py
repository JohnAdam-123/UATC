import os
import tkinter as tk
import sqlite3
from tkinter import messagebox
from db_utils import *
import admin_gui, student_gui
from security_utils import verify_hash
from config import ICON_LOGO
from PIL import Image, ImageTk


initialize_db()

img_path = os.path.join(os.path.dirname(__file__), "assets", "uatc_.png")
img = Image.open(img_path)

def login_window():
    def login():
        username = entry_username.get()
        password = entry_password.get()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash, salt, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            user_id, pw_hash, salt, role = result
            if verify_password(pw_hash, salt, password):
                save_session(user_id, username, role)
                root.destroy()
                if role == "admin":
                    admin_gui.open_admin_dashboard()
                else:
                    student_gui.open_student_dashboard(user_id)
            else:
                messagebox.showerror("Login Failed", "Incorrect password")
        else:
            messagebox.showerror("Login Failed", "User not found")

    def register(): 
        def do_register():
            username = reg_user.get()
            password = reg_pass.get()
            security_word = reg_sec_word.get()
            role = var_role.get()

            if not security_word:
                messagebox.showerror("Error", "Security word is required")
                return

            pw_hash, salt = hash_password(password)
            sec_word_hash, _ = hash_password(security_word)  # You can reuse hash_password function for security word

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""INSERT INTO users (username, password_hash, salt, role, security_word_hash)
                              VALUES (?, ?, ?, ?, ?)""",
                           (username, pw_hash, salt, role, sec_word_hash))
                conn.commit()
                messagebox.showinfo("Success", "User registered successfully")
                reg_win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")
            finally:
                conn.close()

        reg_win = tk.Toplevel(root)
        reg_win.title("Register")
        reg_win.iconbitmap(ICON_LOGO)
        reg_win.geometry("300x300")  # Slightly taller to fit new field

        tk.Label(reg_win, text="Username").pack()
        reg_user = tk.Entry(reg_win)
        reg_user.pack()

        tk.Label(reg_win, text="Password").pack()
        reg_pass = tk.Entry(reg_win, show="*")
        reg_pass.pack()

        tk.Label(reg_win, text="Security Word (for password reset)").pack()
        reg_sec_word = tk.Entry(reg_win, show="*")  # You can omit show="*" if you want it visible
        reg_sec_word.pack()

        tk.Label(reg_win, text="Role").pack()
        var_role = tk.StringVar(value="student")
        tk.OptionMenu(reg_win, var_role, "student", "admin").pack()

        tk.Button(reg_win, text="Register", bg="green", command=do_register).pack(pady=5)
        
        # 👇 Enable login on Enter key
        root.bind('<Return>', lambda event: do_register())  

    def forgot_password():
        def reset():
            username = fp_user.get().strip()
            security_word = fp_sec_word.get().strip()
            new_pw = fp_new.get()

            if not username or not security_word or not new_pw:
                messagebox.showerror("Error", "All fields are required")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            # Fetch stored security_word_hash for the user
            cursor.execute("SELECT security_word_hash, salt FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row is None:
                messagebox.showerror("Error", "Username not found")
                conn.close()
                return

            stored_sec_word_hash, stored_salt = row

            # Verify security word hash matches stored hash
            if not verify_hash(security_word, stored_sec_word_hash, stored_salt):
                messagebox.showerror("Error", "Security word does not match")
                conn.close()
                return

            # Security word verified, hash new password and update
            pw_hash, salt = hash_password(new_pw)
            cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", (pw_hash, salt, username))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Password reset successfully")
            fp_win.destroy()

        fp_win = tk.Toplevel(root)
        fp_win.title("Reset Password")
        fp_win.geometry("300x300")
        fp_win.iconbitmap(ICON_LOGO)

        tk.Label(fp_win, text="Username").pack()
        fp_user = tk.Entry(fp_win)
        fp_user.pack()

        tk.Label(fp_win, text="Security Word").pack()
        fp_sec_word = tk.Entry(fp_win, show="*")
        fp_sec_word.pack()

        tk.Label(fp_win, text="New Password").pack()
        fp_new = tk.Entry(fp_win, show="*")
        fp_new.pack()

        tk.Button(fp_win, text="Reset Password", bg="yellow", fg="red", command=reset).pack(pady=5)

        # 👇 Enable login on Enter key
        root.bind('<Return>', lambda event: reset())


    #Main Window
    root = tk.Tk()
    root.title("UATC - Student Management System")
    root.geometry("600x450")
    root.iconbitmap(ICON_LOGO)

    # Load university logo
    img = Image.open(img_path)
    img = img.resize((250, 250))
    photo = ImageTk.PhotoImage(img)
    label_logo = tk.Label(root, image=photo)
    label_logo.pack()

    tk.Label(root, text="Username").pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    tk.Label(root, text="Password").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    tk.Button(root, text="Login", bg="orange", command=login).pack(pady=5)
    tk.Button(root, text="Register", bg="green", command=register).pack()
    tk.Button(root, text="Forgot Password", bg="blue", fg="white", command=forgot_password).pack()
    
    # 👇 Enable login on Enter key
    root.bind('<Return>', lambda event: login())

    root.mainloop()


if __name__ == '__main__':
    login_window()
