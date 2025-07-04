# Re-run due to environment reset: Create the requirements.txt file again

requirements_content = """\
# Python version requirement
python_version >= "3.10"

# Required packages for UATC_SMS Student Management System
bcrypt==4.3.0
openpyxl==3.1.5
pillow==10.4.0
"""

# Save the requirements.txt to the current directory
requirements_path = "/mnt/data/requirements.txt"
with open(requirements_path, "w") as f:
    f.write(requirements_content)

requirements_path
