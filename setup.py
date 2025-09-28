#!/usr/bin/env python3
"""
Setup script for Student Dropout Prevention Portal
This script helps users set up the application quickly
"""

import os
import shutil
import subprocess
import sys

def print_header():
    print("=" * 60)
    print("🎓 Student Dropout Prevention Portal - Setup")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    if os.path.exists('venv'):
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing dependencies...")
        if os.name == 'nt':  # Windows
            pip_path = os.path.join('venv', 'Scripts', 'pip')
        else:  # Unix/Linux/macOS
            pip_path = os.path.join('venv', 'bin', 'pip')
        
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_config_files():
    """Set up configuration files"""
    print("⚙️ Setting up configuration files...")
    
    # Email config
    if not os.path.exists('email_config.py'):
        if os.path.exists('email_config.py.example'):
            shutil.copy('email_config.py.example', 'email_config.py')
            print("✅ Created email_config.py from template")
        else:
            print("⚠️ email_config.py.example not found")
    else:
        print("✅ email_config.py already exists")
    
    # Service account key
    if not os.path.exists('service-account-key.json'):
        if os.path.exists('service-account-key.json.example'):
            shutil.copy('service-account-key.json.example', 'service-account-key.json')
            print("✅ Created service-account-key.json from template")
        else:
            print("⚠️ service-account-key.json.example not found")
    else:
        print("✅ service-account-key.json already exists")
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Edit email_config.py with your Gmail credentials")
    print("2. Get service-account-key.json from your team lead")
    print("3. Run the application:")
    print("   - Windows: venv\\Scripts\\activate && python app.py")
    print("   - macOS/Linux: source venv/bin/activate && python app.py")
    print("4. Open http://localhost:5000 in your browser")
    print("\n📖 For detailed instructions, see README.md")

def main():
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup config files
    setup_config_files()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
