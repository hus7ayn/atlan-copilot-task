#!/usr/bin/env python3
"""
Full System Startup Script
Starts both backend and frontend with proper error handling
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class SystemStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting Backend Server...")
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                port = os.getenv("PORT", "8000")
                print(f"✅ Backend server started on http://localhost:{port}")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Backend failed to start: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the React frontend"""
        print("🚀 Starting Frontend Server...")
        try:
            client_dir = Path("client")
            if not client_dir.exists():
                print("❌ Client directory not found")
                return False
            
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=client_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend server started on http://localhost:3000")
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                print(f"❌ Frontend failed to start: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
    
    def check_health(self):
        """Check if both services are running"""
        backend_ok = self.backend_process and self.backend_process.poll() is None
        frontend_ok = self.frontend_process and self.frontend_process.poll() is None
        
        return backend_ok, frontend_ok
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🛑 Shutting down services...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("⚠️ Backend force stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("⚠️ Frontend force stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Main run function"""
        print("🎯 ATLAN CUSTOMER COPILOT - FULL SYSTEM STARTUP")
        print("=" * 60)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check if we're in the right directory
        if not Path("main.py").exists():
            print("❌ main.py not found. Please run from the project root directory.")
            return False
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Exiting.")
            return False
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend. Stopping backend.")
            self.cleanup()
            return False
        
        # Success message
        print("\n" + "=" * 60)
        print("🎉 SYSTEM IS RUNNING!")
        print("=" * 60)
        print("📱 Access the application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n🔧 Features available:")
        print("   • Sentiment Analysis Report")
        print("   • Interactive AI Agent with Tavily Integration")
        print("   • Real-time Documentation Search")
        print("   • Smart Ticket Routing")
        print("\n💡 Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Monitor services
        try:
            while self.running:
                backend_ok, frontend_ok = self.check_health()
                
                if not backend_ok:
                    print("⚠️ Backend service stopped unexpectedly")
                    break
                
                if not frontend_ok:
                    print("⚠️ Frontend service stopped unexpectedly")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

def main():
    """Main function"""
    starter = SystemStarter()
    success = starter.run()
    
    if success:
        print("✅ System shutdown complete")
    else:
        print("❌ System startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
