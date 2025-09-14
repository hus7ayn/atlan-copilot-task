#!/usr/bin/env python3
"""
System Diagnostic and Startup Script
Comprehensive check of frontend and backend readiness
"""

import os
import sys
import subprocess
import asyncio
import json
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_environment():
    """Check Python environment and dependencies"""
    print("🐍 Checking Python Environment")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+)")
        return False
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
    else:
        print("⚠️ No virtual environment detected")
    
    return True

def check_backend_dependencies():
    """Check backend dependencies"""
    print("\n🔧 Checking Backend Dependencies")
    print("-" * 40)
    
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('anthropic', 'anthropic'),
        ('chromadb', 'chromadb'),
        ('tavily-python', 'tavily'),
        ('aiohttp', 'aiohttp'),
        ('beautifulsoup4', 'bs4'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        return False
    
    return True

def check_environment_variables():
    """Check environment variables"""
    print("\n🔐 Checking Environment Variables")
    print("-" * 40)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['CLAUDE_API_KEY', 'TAVILY_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✅ {var}")
        else:
            print(f"❌ {var}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def check_backend_imports():
    """Check backend imports"""
    print("\n📦 Checking Backend Imports")
    print("-" * 40)
    
    try:
        # Add ai_pipeline to path
        sys.path.append('ai_pipeline')
        
        from hybrid_rag_system import HybridRAGSystem
        print("✅ HybridRAGSystem")
        
        from tavily_rag_integration import TavilyRAGIntegration
        print("✅ TavilyRAGIntegration")
        
        from enhanced_rag_system import EnhancedRAGSystem
        print("✅ EnhancedRAGSystem")
        
        from sentiment_agent import SentimentAgent
        print("✅ SentimentAgent")
        
        import main
        print("✅ Main application")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_backend_functionality():
    """Test backend functionality"""
    print("\n🧪 Testing Backend Functionality")
    print("-" * 40)
    
    try:
        from hybrid_rag_system import HybridRAGSystem
        
        # Initialize system
        rag = HybridRAGSystem()
        print("✅ Hybrid RAG System initialized")
        
        # Test Tavily topic
        result1 = await rag.process_ticket_hybrid(
            "How do I connect to Snowflake?",
            ["How-to"],
            "neutral",
            "medium"
        )
        print(f"✅ Tavily topic test: {result1.search_type}")
        
        # Test routed topic
        result2 = await rag.process_ticket_hybrid(
            "I need help with data governance",
            ["Glossary"],
            "confused",
            "medium"
        )
        print(f"✅ Routed topic test: {result2.search_type}")
        
        return True
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def check_frontend_dependencies():
    """Check frontend dependencies"""
    print("\n⚛️ Checking Frontend Dependencies")
    print("-" * 40)
    
    client_dir = Path("client")
    if not client_dir.exists():
        print("❌ Client directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = client_dir / "node_modules"
    if not node_modules.exists():
        print("❌ node_modules not found")
        return False
    
    print("✅ node_modules found")
    
    # Check package.json
    package_json = client_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found")
        return False
    
    print("✅ package.json found")
    
    return True

def test_frontend_build():
    """Test frontend build"""
    print("\n🏗️ Testing Frontend Build")
    print("-" * 40)
    
    client_dir = Path("client")
    if not client_dir.exists():
        print("❌ Client directory not found")
        return False
    
    # Try to build
    success = run_command("npm run build", "Frontend build", cwd=client_dir)
    
    if success:
        # Check if build directory exists
        build_dir = client_dir / "build"
        if build_dir.exists():
            print("✅ Build directory created")
            return True
        else:
            print("❌ Build directory not created")
            return False
    
    return False

def check_file_structure():
    """Check file structure"""
    print("\n📁 Checking File Structure")
    print("-" * 40)
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env",
        "client/package.json",
        "client/src/App.tsx",
        "ai_pipeline/hybrid_rag_system.py",
        "ai_pipeline/tavily_rag_integration.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

async def main():
    """Main diagnostic function"""
    print("🔍 ATLAN CUSTOMER COPILOT - SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    checks = [
        ("Python Environment", check_python_environment),
        ("Backend Dependencies", check_backend_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Backend Imports", check_backend_imports),
        ("Backend Functionality", test_backend_functionality),
        ("Frontend Dependencies", check_frontend_dependencies),
        ("Frontend Build", test_frontend_build),
        ("File Structure", check_file_structure)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 SYSTEM IS READY!")
        print("\nTo start the system:")
        print("1. Backend: python3 main.py")
        print("2. Frontend: cd client && npm start")
        print("\nOr use: python3 start_system.py")
    else:
        print(f"\n⚠️ {total - passed} issues need to be fixed before starting")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
