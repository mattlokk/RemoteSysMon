"""
System Tray Icon for RemoteSysMon
"""

from typing import Optional

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import QObject, pyqtSignal, Qt
import os


class TrayIcon(QObject):
    """System tray icon with menu"""
    
    # Signals
    show_window = pyqtSignal()
    start_monitoring = pyqtSignal()
    stop_monitoring = pyqtSignal()
    quit_app = pyqtSignal()
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize system tray icon
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️  WARNING: System tray is not available on this system!")
            print("   The tray icon will not be shown.")
        
        self.tray_icon = QSystemTrayIcon(parent)
        self.setup_icon()
        self.setup_menu()
        
        # Connect activation signal
        self.tray_icon.activated.connect(self.on_activated)
    
    def setup_icon(self):
        """Setup tray icon"""
        # Try to load custom icon, fallback to generated icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        
        icon = None
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            print(f"Loaded custom icon from {icon_path}")
        
        # Try system theme icon if custom not found
        if not icon or icon.isNull():
            icon = QIcon.fromTheme('utilities-system-monitor')
            if not icon.isNull():
                print("Using system theme icon")
        
        # If still no icon, create a simple colored pixmap
        if icon.isNull():
            print("Creating fallback icon")
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(0, 120, 212))  # Blue color
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPixelSize(48)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "R")
            painter.end()
            
            icon = QIcon(pixmap)
        
        if not icon.isNull():
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip("RemoteSysMon Server")
            print("✅ Tray icon set successfully")
        else:
            print("❌ Failed to create tray icon")
    
    def setup_menu(self):
        """Setup tray menu"""
        menu = QMenu()
        
        # Show/Hide window
        self.show_action = QAction("Show Window", self)
        self.show_action.triggered.connect(self.show_window.emit)
        menu.addAction(self.show_action)
        
        menu.addSeparator()
        
        # Start monitoring
        self.start_action = QAction("Start Monitoring", self)
        self.start_action.triggered.connect(self.start_monitoring.emit)
        menu.addAction(self.start_action)
        
        # Stop monitoring
        self.stop_action = QAction("Stop Monitoring", self)
        self.stop_action.triggered.connect(self.stop_monitoring.emit)
        menu.addAction(self.stop_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def show(self):
        """Show tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            print("✅ System tray icon shown")
        else:
            print("⚠️  Cannot show tray icon - system tray not available")
    
    def hide(self):
        """Hide tray icon"""
        self.tray_icon.hide()
    
    def show_message(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
    ) -> None:
        """
        Show notification message
        
        Args:
            title: Message title
            message: Message content
            icon: Message icon type
        """
        self.tray_icon.showMessage(title, message, icon, 3000)
    
    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Handle tray icon activation
        
        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()
    
    def update_monitoring_state(self, is_monitoring: bool):
        """
        Update menu based on monitoring state
        
        Args:
            is_monitoring: Whether monitoring is active
        """
        self.start_action.setEnabled(not is_monitoring)
        self.stop_action.setEnabled(is_monitoring)
