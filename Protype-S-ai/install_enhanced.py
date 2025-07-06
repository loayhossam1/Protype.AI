#!/usr/bin/env python3
"""
Enhanced Installation Script for Protype.AI
Developed by Islam Ibrahim (Enhanced by AI Assistant)
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path

# Installation configuration
PYTHON_VERSION_MIN = (3, 8)
ENHANCED_REQUIREMENTS = [
    "flask==2.3.3",
    "flask-cors==4.0.0", 
    "requests==2.31.0",
    "beautifulsoup4==4.12.2",
    "google-generativeai==0.3.1",
    "networkx==3.2.1",
    "redis==5.0.1",
    "psycopg2-binary==2.9.9",
    "transformers>=4.35.0",
    "torch>=2.0.1",
    "sentence-transformers>=2.2.2",
    "faiss-cpu>=1.7.4",
    "scikit-learn>=1.3.0",
    "numpy>=1.24.0",
    "pillow>=10.0.0",
    "python-dateutil>=2.8.2",
    "celery>=5.3.0"
]

OPTIONAL_REQUIREMENTS = [
    "spacy>=3.7.0",
    "matplotlib>=3.7.0",
    "plotly>=5.18.0",
    "pandas>=2.1.0",
    "jupyter>=1.0.0"
]

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(message, color=Colors.OKBLUE):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    """Print header message"""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f" {message}", Colors.HEADER + Colors.BOLD)
    print_colored(f"{'='*60}", Colors.HEADER)

def print_success(message):
    """Print success message"""
    print_colored(f"✅ {message}", Colors.OKGREEN)

def print_warning(message):
    """Print warning message"""
    print_colored(f"⚠️  {message}", Colors.WARNING)

def print_error(message):
    """Print error message"""
    print_colored(f"❌ {message}", Colors.FAIL)

def run_command(command, capture_output=True, check=True):
    """Run shell command safely"""
    try:
        if isinstance(command, str):
            command = command.split()
        
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command)}")
        print_error(f"Error: {e}")
        return None
    except FileNotFoundError:
        print_error(f"Command not found: {command[0]}")
        return None

def check_python_version():
    """Check if Python version meets requirements"""
    print_header("Checking Python Version")
    
    current_version = sys.version_info[:2]
    print_colored(f"Current Python version: {sys.version}")
    
    if current_version >= PYTHON_VERSION_MIN:
        print_success(f"Python version {current_version} meets requirements (>= {PYTHON_VERSION_MIN})")
        return True
    else:
        print_error(f"Python version {current_version} is too old. Minimum required: {PYTHON_VERSION_MIN}")
        return False

def check_system_requirements():
    """Check system requirements and available tools"""
    print_header("Checking System Requirements")
    
    system_info = {
        'os': platform.system(),
        'architecture': platform.machine(),
        'platform': platform.platform(),
        'python_version': platform.python_version()
    }
    
    print_colored(f"Operating System: {system_info['os']}")
    print_colored(f"Architecture: {system_info['architecture']}")
    print_colored(f"Platform: {system_info['platform']}")
    
    # Check for essential system tools
    tools_to_check = ['git', 'curl', 'wget']
    available_tools = {}
    
    for tool in tools_to_check:
        result = run_command(['which', tool], capture_output=True, check=False)
        if result and result.returncode == 0:
            available_tools[tool] = True
            print_success(f"{tool} is available")
        else:
            available_tools[tool] = False
            print_warning(f"{tool} is not available")
    
    return system_info, available_tools

def setup_virtual_environment():
    """Set up Python virtual environment"""
    print_header("Setting Up Virtual Environment")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_warning("Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").lower().strip()
        if response == 'y':
            print_colored("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            print_colored("Using existing virtual environment")
            return True
    
    print_colored("Creating virtual environment...")
    result = run_command([sys.executable, '-m', 'venv', 'venv'])
    
    if result:
        print_success("Virtual environment created successfully")
        return True
    else:
        print_error("Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the correct pip command for the virtual environment"""
    if platform.system() == "Windows":
        return str(Path("venv") / "Scripts" / "pip")
    else:
        return str(Path("venv") / "bin" / "pip")

def install_requirements():
    """Install Python requirements"""
    print_header("Installing Python Requirements")
    
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    print_colored("Upgrading pip...")
    result = run_command([pip_cmd, 'install', '--upgrade', 'pip'])
    if not result:
        print_error("Failed to upgrade pip")
        return False
    
    # Install core requirements
    print_colored("Installing core requirements...")
    
    failed_packages = []
    successful_packages = []
    
    for package in ENHANCED_REQUIREMENTS:
        print_colored(f"Installing {package}...")
        result = run_command([pip_cmd, 'install', package], capture_output=True, check=False)
        
        if result and result.returncode == 0:
            successful_packages.append(package)
            print_success(f"✓ {package}")
        else:
            failed_packages.append(package)
            print_error(f"✗ {package}")
            if result and result.stderr:
                print_colored(f"  Error: {result.stderr[:200]}...", Colors.WARNING)
    
    # Install optional requirements
    print_colored("\nInstalling optional requirements...")
    for package in OPTIONAL_REQUIREMENTS:
        print_colored(f"Installing {package} (optional)...")
        result = run_command([pip_cmd, 'install', package], capture_output=True, check=False)
        
        if result and result.returncode == 0:
            successful_packages.append(package)
            print_success(f"✓ {package}")
        else:
            print_warning(f"⚠ {package} (optional - skipped)")
    
    print_colored(f"\nInstallation Summary:")
    print_success(f"Successfully installed: {len(successful_packages)} packages")
    
    if failed_packages:
        print_warning(f"Failed to install: {len(failed_packages)} packages")
        print_colored("Failed packages:", Colors.WARNING)
        for pkg in failed_packages:
            print_colored(f"  - {pkg}", Colors.WARNING)
    
    return len(failed_packages) == 0

def install_spacy_model():
    """Install spaCy English model"""
    print_header("Installing spaCy English Model")
    
    pip_cmd = get_pip_command()
    
    print_colored("Installing spaCy English model...")
    result = run_command([pip_cmd, 'install', 'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl'], 
                        capture_output=True, check=False)
    
    if result and result.returncode == 0:
        print_success("spaCy English model installed successfully")
        return True
    else:
        print_warning("Failed to install spaCy model - will be downloaded on first use")
        return False

def setup_environment_file():
    """Set up environment variables file"""
    print_header("Setting Up Environment Configuration")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print_warning(".env file already exists")
        response = input("Do you want to update it? (y/N): ").lower().strip()
        if response != 'y':
            return True
    
    print_colored("Creating environment configuration...")
    
    # Get API keys from user
    gemini_api_key = input("Enter your Google Gemini API key (optional): ").strip()
    openai_api_key = input("Enter your OpenAI API key (optional): ").strip()
    redis_url = input("Enter Redis URL (optional, default: redis://localhost:6379): ").strip()
    
    if not redis_url:
        redis_url = "redis://localhost:6379"
    
    env_content = f"""# Protype.AI Environment Configuration
# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}

# AI API Keys
GEMINI_API_KEY={gemini_api_key}
OPENAI_API_KEY={openai_api_key}

# Database Configuration
DATABASE_URL=sqlite:///protype_e0.db
REDIS_URL={redis_url}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# Application Configuration
PROTYPE_VERSION=2.0.0
LOG_LEVEL=INFO
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print_success("Environment file created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create environment file: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    try:
        # Import and initialize the enhanced database
        sys.path.insert(0, '.')
        from database_enhanced import init_db
        
        print_colored("Initializing database schema...")
        success = init_db()
        
        if success:
            print_success("Database initialized successfully")
            return True
        else:
            print_error("Database initialization failed")
            return False
            
    except Exception as e:
        print_error(f"Error initializing database: {e}")
        return False

def create_startup_scripts():
    """Create startup scripts for different operating systems"""
    print_header("Creating Startup Scripts")
    
    # Create Unix/Linux startup script
    unix_script = """#!/bin/bash
# Protype.AI Startup Script

echo "Starting Protype.AI Enhanced..."

# Activate virtual environment
source venv/bin/activate

# Check if required environment variables are set
if [ -z "$GEMINI_API_KEY" ] && [ ! -f .env ]; then
    echo "Warning: GEMINI_API_KEY not set and no .env file found"
fi

# Start the application
python web_app_enhanced.py

echo "Protype.AI has stopped."
"""
    
    # Create Windows startup script
    windows_script = """@echo off
REM Protype.AI Startup Script

echo Starting Protype.AI Enhanced...

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found
)

REM Start the application
python web_app_enhanced.py

echo Protype.AI has stopped.
pause
"""
    
    try:
        # Write Unix script
        with open("start_protype.sh", "w") as f:
            f.write(unix_script)
        os.chmod("start_protype.sh", 0o755)
        
        # Write Windows script
        with open("start_protype.bat", "w") as f:
            f.write(windows_script)
        
        print_success("Startup scripts created successfully")
        return True
        
    except Exception as e:
        print_error(f"Failed to create startup scripts: {e}")
        return False

def create_project_info():
    """Create project information file"""
    print_header("Creating Project Documentation")
    
    info = {
        "name": "Protype.AI Enhanced",
        "version": "2.0.0",
        "description": "Advanced Conversational AI Platform with Self-Reflection and Learning",
        "developer": "Islam Ibrahim, Director of Carrot Studio",
        "enhanced_by": "AI Assistant",
        "installation_date": time.strftime('%Y-%m-%d %H:%M:%S'),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "features": [
            "Self-Reflection with Chain of Thought reasoning",
            "Advanced Memory using FAISS and RAG",
            "Multimodal Intelligence (text, images, audio)",
            "Autonomous Agent for self-directed learning",
            "Knowledge Graph with Graph Neural Networks",
            "Professional web interface with dark/light themes",
            "Enhanced database with caching and optimization",
            "Real-time analytics and monitoring"
        ],
        "startup_commands": {
            "linux_mac": "./start_protype.sh",
            "windows": "start_protype.bat",
            "manual": "source venv/bin/activate && python web_app_enhanced.py"
        },
        "urls": {
            "main_interface": "http://localhost:8080",
            "dashboard": "http://localhost:8080/dashboard",
            "api_health": "http://localhost:8080/health"
        }
    }
    
    try:
        with open("INSTALLATION_INFO.json", "w") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print_success("Project information file created")
        return True
        
    except Exception as e:
        print_error(f"Failed to create project info: {e}")
        return False

def run_system_test():
    """Run basic system test"""
    print_header("Running System Test")
    
    try:
        # Test database connection
        print_colored("Testing database connection...")
        sys.path.insert(0, '.')
        from database_enhanced import get_statistics
        
        stats = get_statistics()
        if stats:
            print_success("Database connection successful")
        else:
            print_warning("Database test returned empty results")
        
        # Test AI components
        print_colored("Testing AI components...")
        try:
            import google.generativeai as genai
            print_success("Google Generative AI module loaded")
        except Exception as e:
            print_warning(f"Google Generative AI test failed: {e}")
        
        # Test web framework
        print_colored("Testing web framework...")
        try:
            from flask import Flask
            print_success("Flask web framework loaded")
        except Exception as e:
            print_error(f"Flask test failed: {e}")
            return False
        
        print_success("System test completed successfully")
        return True
        
    except Exception as e:
        print_error(f"System test failed: {e}")
        return False

def main():
    """Main installation function"""
    print_colored("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                      Protype.AI Enhanced                     ║
    ║                   Installation Script v2.0                   ║
    ║                                                              ║
    ║   Developed by: Islam Ibrahim, Director of Carrot Studio     ║
    ║   Enhanced by: AI Assistant                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """, Colors.HEADER + Colors.BOLD)
    
    print_colored("This script will install and configure Protype.AI Enhanced", Colors.OKBLUE)
    print_colored("The installation includes:", Colors.OKBLUE)
    print_colored("  • Advanced AI capabilities with self-reflection", Colors.OKCYAN)
    print_colored("  • Professional web interface", Colors.OKCYAN)
    print_colored("  • Enhanced database with caching", Colors.OKCYAN)
    print_colored("  • Multimodal intelligence features", Colors.OKCYAN)
    print_colored("  • Autonomous learning agent", Colors.OKCYAN)
    
    response = input("\nDo you want to proceed with the installation? (Y/n): ").lower().strip()
    if response == 'n':
        print_colored("Installation cancelled by user.", Colors.WARNING)
        return
    
    installation_steps = [
        ("Check Python Version", check_python_version),
        ("Check System Requirements", lambda: check_system_requirements()[0] is not None),
        ("Setup Virtual Environment", setup_virtual_environment),
        ("Install Requirements", install_requirements),
        ("Install spaCy Model", install_spacy_model),
        ("Setup Environment File", setup_environment_file),
        ("Initialize Database", initialize_database),
        ("Create Startup Scripts", create_startup_scripts),
        ("Create Project Info", create_project_info),
        ("Run System Test", run_system_test)
    ]
    
    failed_steps = []
    
    for step_name, step_function in installation_steps:
        try:
            success = step_function()
            if not success:
                failed_steps.append(step_name)
        except Exception as e:
            print_error(f"Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Final summary
    print_header("Installation Summary")
    
    if failed_steps:
        print_warning(f"Installation completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print_colored(f"  ⚠️  {step}", Colors.WARNING)
        print_colored("\nThe system may still work, but some features might be limited.", Colors.WARNING)
    else:
        print_success("🎉 Installation completed successfully!")
    
    print_colored("\nNext steps:", Colors.OKBLUE)
    print_colored("1. Configure your API keys in the .env file", Colors.OKCYAN)
    print_colored("2. Start the application:", Colors.OKCYAN)
    
    if platform.system() == "Windows":
        print_colored("   start_protype.bat", Colors.OKGREEN)
    else:
        print_colored("   ./start_protype.sh", Colors.OKGREEN)
    
    print_colored("3. Access the web interface at http://localhost:8080", Colors.OKCYAN)
    print_colored("4. Access the dashboard at http://localhost:8080/dashboard", Colors.OKCYAN)
    
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored("Thank you for using Protype.AI Enhanced!", Colors.HEADER + Colors.BOLD)
    print_colored(f"{'='*60}", Colors.HEADER)

if __name__ == "__main__":
    main()