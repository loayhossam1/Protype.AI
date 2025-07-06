#!/usr/bin/env python3
"""
Enhanced Protype.AI Startup Script
Developed by Islam Ibrahim, Director of Carrot Studio

This script provides an easy way to start the enhanced Protype.AI system
with automatic dependency checking, database initialization, and 
comprehensive startup diagnostics.
"""

import os
import sys
import subprocess
import importlib
import time
from pathlib import Path

def print_banner():
    """Print enhanced startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     🚀 Enhanced Protype.AI - Advanced AI Platform 🚀          ║
    ║                                                               ║
    ║              Developed by Islam Ibrahim                       ║
    ║                   Carrot Studio                               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    🔧 Starting enhanced system initialization...
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_required_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking required dependencies...")
    
    required_packages = [
        'flask',
        'google.generativeai',
        'sqlite3',
        'requests',
        'threading',
        'json',
        'logging',
        'datetime',
        'uuid',
        'hashlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'google.generativeai':
                import google.generativeai as genai
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing dependencies: {', '.join(missing_packages)}")
        print("   Run: pip install -r enhanced_requirements.txt")
        return False
    
    print("✅ All required dependencies are available")
    return True

def check_environment_variables():
    """Check for required environment variables"""
    print("\n🔑 Checking environment variables...")
    
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_key:
        print("⚠️  GEMINI_API_KEY not found in environment")
        print("   The system will use the default key, but you should set your own")
        print("   Add to your environment: export GEMINI_API_KEY=your_api_key")
    else:
        print("✅ GEMINI_API_KEY configured")
    
    # Check optional keys
    optional_keys = ['SERPAPI_KEY', 'ELEVENLABS_API_KEY', 'SECRET_KEY']
    for key in optional_keys:
        if os.environ.get(key):
            print(f"✅ {key} configured")
        else:
            print(f"⚠️  {key} not configured (optional)")
    
    return True

def initialize_database():
    """Initialize the enhanced database"""
    print("\n💾 Initializing enhanced database...")
    
    try:
        # Import the enhanced web app to trigger database initialization
        from enhanced_web_app import db
        print("✅ Enhanced database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def check_port_availability():
    """Check if the default port is available"""
    print("\n🌐 Checking port availability...")
    
    import socket
    port = 8080
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
        print(f"✅ Port {port} is available")
        return True
    except OSError:
        print(f"⚠️  Port {port} is already in use")
        print("   The system will try to find an alternative port")
        return True  # Not critical, Flask can handle this

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = ['templates', 'static', 'static/js', 'static/css']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}")
    
    return True

def run_system_diagnostics():
    """Run comprehensive system diagnostics"""
    print("\n🔍 Running system diagnostics...")
    
    diagnostics = [
        ("Python Version", check_python_version),
        ("Dependencies", check_required_dependencies),
        ("Environment", check_environment_variables),
        ("Database", initialize_database),
        ("Network", check_port_availability),
        ("Directories", create_directories)
    ]
    
    all_passed = True
    
    for name, check_func in diagnostics:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            all_passed = False
    
    return all_passed

def start_enhanced_application():
    """Start the enhanced Protype.AI application"""
    print("\n🚀 Starting Enhanced Protype.AI...")
    
    try:
        # Import and run the enhanced web application
        from enhanced_web_app import app, logger
        
        print("✅ Enhanced web application loaded successfully")
        print("\n" + "="*60)
        print("🎉 ENHANCED PROTYPE.AI IS READY!")
        print("="*60)
        print(f"🌐 Web Interface: http://localhost:8080")
        print(f"📊 Dashboard: http://localhost:8080/dashboard")
        print(f"🔧 Admin: Check the console for system logs")
        print("="*60)
        print("\n🎯 Features Available:")
        print("  • Modern Material Design Interface")
        print("  • Dark/Light Theme Support")
        print("  • Achievement Tracking System")
        print("  • Enhanced AI Learning")
        print("  • Real-time Analytics")
        print("  • Professional Chat Experience")
        print("  • Autonomous Learning Sessions")
        print("\n💡 Tips:")
        print("  • Try asking questions to see the enhanced responses")
        print("  • Teach the AI new information to earn achievements")
        print("  • Check the dashboard for analytics and progress")
        print("  • Toggle between dark and light themes")
        print("\n⚡ Press Ctrl+C to stop the server")
        print("-"*60)
        
        # Start the Flask application
        app.run(host='0.0.0.0', port=8080, debug=False)
        
    except ImportError as e:
        print(f"❌ Failed to import enhanced application: {e}")
        print("   Make sure enhanced_web_app.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main startup function"""
    print_banner()
    
    # Run system diagnostics
    if not run_system_diagnostics():
        print("\n❌ System diagnostics failed!")
        print("   Please fix the issues above before starting the application")
        return 1
    
    print("\n✅ All system checks passed!")
    time.sleep(2)  # Brief pause before starting
    
    # Start the enhanced application
    try:
        start_enhanced_application()
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 Enhanced Protype.AI stopped by user")
        print("   Thank you for using Enhanced Protype.AI!")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)