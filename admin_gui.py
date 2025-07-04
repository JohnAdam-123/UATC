import tkinter as tk
import sqlite3
from config import ICON_LOGO
from tkinter import ttk, messagebox, simpledialog, filedialog
from db_utils import *
from excel_utils import *

DB_NAME = "data/students.db"
ROWS_PER_PAGE = 10

class StudentAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")
        self.root.iconbitmap(ICON_LOGO)
        self.root.geometry("1200x500")

        self.page = 0

        # Search field
        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search by Name:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_students).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Show All", command=self.load_students).pack(side=tk.LEFT)


        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Course", "CA", "SE", "Total", "Grade", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        # Set custom headings
        self.configure_treeview_columns()
        self.tree.pack(fill="both", expand=True)

        self.load_students()

        # Entry Form
        form_frame = tk.Frame(root)
        form_frame.pack(pady=9)

        self.name_entry = self._add_labeled_entry(form_frame, "Name")
        self.course_entry = self._add_labeled_entry(form_frame, "Course")
        self.ca_entry = self._add_labeled_entry(form_frame, "CA")
        self.se_entry = self._add_labeled_entry(form_frame, "SE")

        tk.Button(form_frame, text="Add Student", bg="green", command=self.add_student).grid(row=0, column=6, padx=5)
        tk.Button(form_frame, text="Delete Selected", bg="red", command=self.delete_selected).grid(row=1, column=6, padx=5)
        tk.Button(form_frame, text="Import Excel", bg="green", command=self.import_excel).grid(row=2, column=6, padx=5)
        tk.Button(form_frame, text="Update Student", bg="green", command=self.update_selected).grid(row=3, column=6, padx=5)
        tk.Button(form_frame, text="Logout", bg="blue", fg="white", command=self.logout).grid(row=4, column=6, padx=5)

    def _add_labeled_entry(self, parent, label):
        row = len(parent.grid_slaves()) // 2
        tk.Label(parent, text=label).grid(row=row, column=0, padx=5)
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1, padx=5)
        return entry
    
    def configure_treeview_columns(self):
        widths = {
            "ID": 50, 
            "Name": 150,
            "Course": 120,
            "CA": 50,
            "SE": 50,
            "Total": 60,
            "Grade": 60,
            "Status": 100
           
        }

        for col in self.tree["columns"]:
            stretch = col not in {"ID", "CA", "SE", "Total"}
            self.tree.column(col, width=widths.get(col, 100), stretch=stretch)

    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            success, msg = import_excel_to_db(file_path)
            if success:
                messagebox.showinfo("Import Success", msg)
                self.load_students()
            else:
                messagebox.showerror("Import Failed", msg)


    def fetch_students(self, name_filter=None):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if name_filter:
            cursor.execute("SELECT id, name, course, ca, se, total, grade, status FROM students WHERE name LIKE ?", ('%' + name_filter + '%',))
        else:
            cursor.execute("SELECT id, name, course, ca, se, total, grade, status FROM students")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, course, ca, se, total, grade, status FROM students")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def search_students(self):
        name = self.search_var.get()
        self.all_rows = self.fetch_students(name_filter=name)
        self.page = 0
        self.show_page()

    def show_page(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        start = self.page * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        for row in self.all_rows[start:end]:
            self.tree.insert("", tk.END, values=row)

    def next_page(self):
        if (self.page + 1) * ROWS_PER_PAGE < len(self.all_rows):
            self.page += 1
            self.show_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.show_page()

    def add_student(self):
        name = self.name_entry.get()
        course = self.course_entry.get()
        try:
            ca = float(self.ca_entry.get())
            se = float(self.se_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "CA and SE must be numeric")
            return

        total = ca + se
        grade, status = calculate_grade_and_status(total)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, course, ca, se, total, grade, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (name, course, ca, se, total, grade, status))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Student Added Successfully")
        self.load_students()

        # Clear the input fields here:
        self.name_entry.delete(0, tk.END)
        self.course_entry.delete(0, tk.END)
        self.ca_entry.delete(0, tk.END)
        self.se_entry.delete(0, tk.END)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a student to delete")
            return

        student_id = self.tree.item(selected[0])["values"][0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        self.load_students()
        messagebox.showinfo("Deleted", "Student record deleted")

    def update_selected(self):
        self.root.iconbitmap(ICON_LOGO)
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a student to update.")
            return

        data = self.tree.item(selected[0])["values"]
        student_id = data[0]

        # Prompt for new values
        new_name = simpledialog.askstring("Update", "New Name:", initialvalue=data[1])
        new_course = simpledialog.askstring("Update", "New Course:", initialvalue=data[2])
        try:
            new_ca = float(simpledialog.askstring("Update", "New CA Marks:", initialvalue=data[3]))
            new_se = float(simpledialog.askstring("Update", "New SE Marks:", initialvalue=data[4]))
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "CA/SE must be numeric.")
            return

        total = new_ca + new_se
        grade, status = calculate_grade_and_status(total)
        status = "Pass" if total >= 50 else "SUPPLEMENTARY"

        # Update in DB
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""UPDATE students 
                          SET name = ?, course = ?, ca = ?, se = ?, total = ?, grade = ?, status = ?
                          WHERE id = ?""",
                       (new_name, new_course, new_ca, new_se, total, grade, status, student_id))
        conn.commit()
        conn.close()

        self.load_students()
        messagebox.showinfo("Updated", f"Student with ID {student_id} updated.")


    def logout(self):
        clear_session()
        self.root.destroy()
        import login
        login.login_window()


def open_admin_dashboard():
    root = tk.Tk()
    root.iconbitmap(ICON_LOGO)
    app = StudentAdminApp(root)
    root.mainloop()
