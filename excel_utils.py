import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db_utils import *
from db_utils import get_db_connection
import pandas as pd
import sqlite3

def import_excel_to_db(file_path):
    try:
        df = pd.read_excel(file_path)

        required = {"name", "course", "ca", "se", "level", "year", "semester"}
        if not required.issubset(df.columns):
            return False, "Missing required columns"

        conn = get_db_connection()
        cur = conn.cursor()

        for _, row in df.iterrows():
            ca = float(row["ca"])
            se = float(row["se"])
            total = ca + se
            grade, status = calculate_grade_and_status(total)

            cur.execute("SELECT id FROM levels WHERE name=?", (row["level"],))
            level_id = cur.fetchone()
            cur.execute("SELECT id FROM academic_years WHERE year=?", (row["year"],))
            year_id = cur.fetchone()
            cur.execute("SELECT id FROM semesters WHERE name=?", (row["semester"],))
            semester_id = cur.fetchone()

            if not all([level_id, year_id, semester_id]):
                continue

            cur.execute("""
                INSERT INTO students (name, course, ca, se, total, grade, status, level_id, year_id, semester_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["name"], row["course"], ca, se, total, grade, status,
                level_id[0], year_id[0], semester_id[0]
            ))

        conn.commit()
        conn.close()
        return True, "Data imported successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


STUDENTS_PER_PAGE = 10

def calculate_grade_and_status(total):
    if total >= 80:
        grade = "A"
    elif total >= 65:
        grade = "B"
    elif total >= 55:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"
    status = "Pass" if total >= 50 else "SUPPLEMENTARY"
    return grade, status


def open_admin_dashboard():
    root = tk.Tk()
    root.mainloop()
