#!/usr/bin/env python3
"""
Environment Setup Script
Automatically sets up the Python virtual environment and installs all dependencies
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def main():
    print("=" * 80)
    print("SCPI Instrument Toolkit - Environment Setup")
    print("=" * 80)

    # Get the project directory
    project_dir = Path(__file__).parent
    venv_dir = project_dir / ".venv"

    print(f"\nProject directory: {project_dir}")
    print(f"Virtual environment: {venv_dir}")

    # Check if virtual environment exists
    if venv_dir.exists():
        print(f"\n✓ Virtual environment already exists at {venv_dir}")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == "y":
            print("Removing existing virtual environment...")
            import shutil

            shutil.rmtree(venv_dir)
        else:
            print("Using existing virtual environment")

    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        if not run_command(
            [sys.executable, "-m", "venv", str(venv_dir)],
            "Creating virtual environment",
        ):
            print("\n❌ Failed to create virtual environment")
            return 1
        print("\n✓ Virtual environment created successfully")

    # Determine the pip executable path based on OS
    if sys.platform == "win32":
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"
        python_exe = venv_dir / "bin" / "python"

    # Upgrade pip
    if not run_command(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip"
    ):
        print("\n⚠ Warning: Failed to upgrade pip (continuing anyway)")

    # Install requirements
    requirements_file = project_dir / "requirements.txt"
    if requirements_file.exists():
        if not run_command(
            [str(pip_exe), "install", "-r", str(requirements_file)],
            "Installing dependencies from requirements.txt",
        ):
            print("\n❌ Failed to install dependencies")
            return 1
        print("\n✓ All dependencies installed successfully")
    else:
        print(f"\n⚠ Warning: requirements.txt not found at {requirements_file}")
        print("Installing basic packages...")
        packages = [
            "pyserial",
            "pandas",
            "pyfunctional",
            "numpy",
            "scipy",
            "matplotlib",
            "requests",
            "pyserial-asyncio",
            "openpyxl",
        ]
        if not run_command(
            [str(pip_exe), "install"] + packages, "Installing basic packages"
        ):
            print("\n❌ Failed to install packages")
            return 1

    # Print success message
    print("\n" + "=" * 80)
    print("✓ Environment setup complete!")
    print("=" * 80)
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  PowerShell: {venv_dir}\\Scripts\\Activate.ps1")
        print(f"  CMD:        {venv_dir}\\Scripts\\activate.bat")
    else:
        print(f"  source {venv_dir}/bin/activate")

    print(f"\nTo launch the interactive REPL:")
    print(f"  {python_exe} repl.py")

    print("\nInstalled packages:")
    run_command([str(pip_exe), "list"], "Package list")

    return 0


if __name__ == "__main__":
    sys.exit(main())
