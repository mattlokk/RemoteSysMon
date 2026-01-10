#!/usr/bin/env python3
"""
RemoteSysMon Desktop Application
Main entry point for the desktop GUI application
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import SystemMonitor, ADBManager, Config
from gui import MainWindow, TrayIcon


class RemoteSysMonApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        # Enable high DPI scaling BEFORE creating QApplication
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("RemoteSysMon")
        self.app.setOrganizationName("RemoteSysMon")
        
        # Initialize core components
        self.config = Config()
        self.monitor = SystemMonitor()
        self.adb = ADBManager()
        
        # Update ADB target path from config
        self.adb.target_path = self.config.get('adb', 'target_path') or self.adb.target_path
        
        # Create main window
        self.main_window = MainWindow(self.monitor, self.adb, self.config)
        
        # Create system tray
        self.tray = TrayIcon()
        self.setup_tray()
        
        # Show tray icon
        self.tray.show()
        
        # Show main window unless configured to start minimized
        if not self.config.get('monitoring', 'start_minimized'):
            self.main_window.show()
        else:
            self.tray.show_message("RemoteSysMon", "Running in background")
    
    def setup_tray(self):
        """Setup system tray connections"""
        # Connect tray signals to main window
        self.tray.show_window.connect(self.show_main_window)
        self.tray.start_monitoring.connect(self.main_window.start_monitoring)
        self.tray.stop_monitoring.connect(self.main_window.stop_monitoring)
        self.tray.quit_app.connect(self.quit_application)
        
        # Connect main window signals to tray
        self.main_window.close_to_tray.connect(self.on_minimize_to_tray)
        self.main_window.force_quit.connect(self.quit_application)
    
    def show_main_window(self):
        """Show and raise main window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def on_minimize_to_tray(self):
        """Handle minimize to tray"""
        self.tray.show_message("RemoteSysMon", "Running in background")
    
    def quit_application(self):
        """Quit application completely"""
        print("DEBUG: quit_application called")
        # Stop monitoring if active
        if self.main_window.monitoring:
            self.main_window.stop_monitoring()
        
        # Hide tray icon
        self.tray.hide()
        print("DEBUG: tray hidden, calling app.quit()")
        
        # Quit
        self.app.quit()
    
    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    """Main entry point"""
    # Check if running as root and warn user
    if os.geteuid() != 0:
        print("⚠️  WARNING: Not running as root!")
        print("   CPU power monitoring will not be available.")
        print("   Run with: sudo python3 main.py")
        print()
    
    # Check if ADB is available
    try:
        result = subprocess.run(['adb', 'version'], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode != 0:
            print("⚠️  WARNING: ADB not found or not working!")
            print("   Make sure Android Debug Bridge is installed.")
            print()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  WARNING: ADB not found!")
        print("   Install with: sudo apt install adb  (or platform-tools)")
        print()
    
    # Create and run application
    app = RemoteSysMonApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
