import os
import subprocess
import sys
import platform

def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error running: {command}")
        sys.exit(1)

def main():
    print("🔧 Creating virtual environment...")
    run_command(f"{sys.executable} -m venv venv")

    if platform.system() == "Windows":
        activate_cmd = r"venv\Scripts\activate"
    else:
        activate_cmd = "source venv/bin/activate"

    print(f"✅ Virtual environment created.")
    print(f"👉 To activate it, run:\n    {activate_cmd}")

    print("📦 Installing dependencies from requirements.txt...")
    pip_path = os.path.join("venv", "Scripts" if platform.system() == "Windows" else "bin", "pip")
    run_command(f"{pip_path} install -r requirements.txt")

    print("✅ Setup complete!")

if __name__ == "__main__":
    main()
