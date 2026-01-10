"""
Main Window for RemoteSysMon Desktop Application
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QGroupBox, 
                             QTextEdit, QLineEdit, QGridLayout, QSlider)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent

from core import ADBDevice, ADBManager, Config, SystemMonitor


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    close_to_tray = pyqtSignal()
    force_quit = pyqtSignal()
    
    def __init__(self, monitor: SystemMonitor, adb_manager: ADBManager, config: Config) -> None:
        """
        Initialize main window
        
        Args:
            monitor: SystemMonitor instance
            adb_manager: ADBManager instance
            config: Config instance
        """
        super().__init__()
        self.monitor: SystemMonitor = monitor
        self.adb: ADBManager = adb_manager
        self.config: Config = config
        self.monitoring: bool = False
        
        self.init_ui()
        self.setup_timer()
        
        # Auto-start if configured
        if self._get_monitoring_flag('auto_start'):
            self.start_monitoring()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("RemoteSysMon Server")
        self.setGeometry(100, 100, 700, 600)
        
        # Central widget
        central = QWidget()
        main_layout = QVBoxLayout()
        
        # Status section
        status_group = self._create_status_section()
        main_layout.addWidget(status_group)
        
        # ADB section
        adb_group = self._create_adb_section()
        main_layout.addWidget(adb_group)
        
        # Control buttons
        control_layout = self._create_control_buttons()
        main_layout.addLayout(control_layout)
        
        # Stats preview
        preview_group = self._create_preview_section()
        main_layout.addWidget(preview_group)
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)
    
    def _create_status_section(self) -> QGroupBox:
        """Create status section"""
        group = QGroupBox("Status")
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Monitoring: <b style='color: red;'>Stopped</b>")
        layout.addWidget(self.status_label)
        
        # Root privilege warning
        if not self.monitor.is_running_as_root():
            warning = QLabel("⚠️ <b>Not running as root</b> - CPU power monitoring unavailable")
            warning.setStyleSheet("color: orange; padding: 5px;")
            layout.addWidget(warning)
        
        group.setLayout(layout)
        return group
    
    def _create_adb_section(self) -> QGroupBox:
        """Create ADB device section"""
        group = QGroupBox("ADB Device")
        layout = QVBoxLayout()
        
        # Device selector
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        device_layout.addWidget(self.device_combo)
        
        self.refresh_devices_btn = QPushButton("Refresh")
        self.refresh_devices_btn.clicked.connect(self.refresh_devices)
        device_layout.addWidget(self.refresh_devices_btn)
        
        layout.addLayout(device_layout)
        
        # ADB commands grid
        commands_layout = QGridLayout()
        
        # Screen controls
        self.screen_on_btn = QPushButton("Screen ON")
        self.screen_on_btn.clicked.connect(self.adb.screen_on)
        commands_layout.addWidget(self.screen_on_btn, 0, 0)

        self.screen_off_btn = QPushButton("Screen OFF")
        self.screen_off_btn.clicked.connect(self.adb.screen_off)
        commands_layout.addWidget(self.screen_off_btn, 0, 1)
        
        layout.addLayout(commands_layout)
        
        # Brightness control
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 255)
        self.brightness_slider.setValue(128)  # Default to middle
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(64)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        
        self.brightness_value_label = QLabel("128")
        self.brightness_value_label.setMinimumWidth(40)
        brightness_layout.addWidget(self.brightness_value_label)
        
        layout.addLayout(brightness_layout)
        
        # Custom command
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom:"))
        self.custom_cmd_input = QLineEdit()
        self.custom_cmd_input.setPlaceholderText("Enter ADB shell command...")
        custom_layout.addWidget(self.custom_cmd_input)
        
        self.exec_custom_btn = QPushButton("Execute")
        self.exec_custom_btn.clicked.connect(self.execute_custom_command)
        custom_layout.addWidget(self.exec_custom_btn)
        
        layout.addLayout(custom_layout)
        
        group.setLayout(layout)
        
        # Initial device refresh
        self.refresh_devices()
        
        return group
    
    def _create_control_buttons(self) -> QHBoxLayout:
        """Create control buttons"""
        layout = QHBoxLayout()
        
        # Start/Stop monitoring
        self.toggle_btn = QPushButton("Start Monitoring")
        self.toggle_btn.clicked.connect(self.toggle_monitoring)
        self.toggle_btn.setMinimumHeight(40)
        layout.addWidget(self.toggle_btn)
        
        # Settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setMinimumHeight(40)
        layout.addWidget(self.settings_btn)
        
        # Minimize button
        self.minimize_btn = QPushButton("Minimize")
        self.minimize_btn.clicked.connect(self.minimize_to_tray)
        self.minimize_btn.setMinimumHeight(40)
        layout.addWidget(self.minimize_btn)
        
        # Quit button
        self.quit_btn = QPushButton("Quit")
        self.quit_btn.clicked.connect(self.force_quit_application)
        self.quit_btn.setMinimumHeight(40)
        self.quit_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; }")
        layout.addWidget(self.quit_btn)
        
        return layout
    
    def _create_preview_section(self) -> QGroupBox:
        """Create stats preview section"""
        group = QGroupBox("Current Stats")
        layout = QVBoxLayout()
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(200)
        self.stats_display.setPlainText("No data yet - start monitoring to see stats")
        
        layout.addWidget(self.stats_display)
        group.setLayout(layout)
        return group
    
    def setup_timer(self) -> None:
        """Setup update timer"""
        self.timer: QTimer = QTimer()
        self.timer.timeout.connect(self.update_data)
    
    def refresh_devices(self) -> None:
        """Refresh ADB device list"""
        self.device_combo.clear()
        devices: List[ADBDevice] = self.adb.get_devices()

        if not devices:
            self.device_combo.addItem("No devices found")
        else:
            for device in devices:
                label = f"{device.model} ({device.device_id}) - {device.state}"
                self.device_combo.addItem(label, device.device_id)
            
            # Auto-select first device
            if self.device_combo.count() > 0:
                first_device_id = self.device_combo.itemData(0)
                if isinstance(first_device_id, str):
                    self.adb.connect(first_device_id)
                    
                    # Get current brightness
                    self.update_brightness_from_device()
    
    def execute_custom_command(self) -> None:
        """Execute custom ADB command"""
        command = self.custom_cmd_input.text().strip()
        if command:
            result: Optional[str] = self.adb.execute_custom_command(command)
            if result:
                print(f"Command output: {result}")
                self.custom_cmd_input.clear()
    
    def on_brightness_changed(self, value: int) -> None:
        """Handle brightness slider change"""
        if self.adb.device_id:
            success: bool = self.adb.set_brightness(value)
            if success:
                self.brightness_value_label.setText(str(value))
            else:
                print(f"Failed to set brightness to {value}")
    
    def update_brightness_from_device(self) -> None:
        """Update brightness slider from current device brightness"""
        if self.adb.device_id:
            current_brightness = self.adb.get_brightness()
            if current_brightness is not None:
                self.brightness_slider.blockSignals(True)
                self.brightness_slider.setValue(current_brightness)
                self.brightness_value_label.setText(str(current_brightness))
                self.brightness_slider.blockSignals(False)
    
    def toggle_monitoring(self) -> None:
        """Toggle monitoring on/off"""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start system monitoring"""
        # Update selected device
        current_index = self.device_combo.currentIndex()
        if current_index >= 0:
            device_id = self.device_combo.itemData(current_index)
            if isinstance(device_id, str):
                self.adb.connect(device_id)
        self.monitoring = True
        refresh_rate = self._get_refresh_rate()
        self.timer.start(refresh_rate)
        self.status_label.setText("Monitoring: <b style='color: green;'>Active</b>")
        self.toggle_btn.setText("Stop Monitoring")
        self.toggle_btn.setStyleSheet("background-color: #d32f2f; color: white;")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        self.timer.stop()
        self.status_label.setText("Monitoring: <b style='color: red;'>Stopped</b>")
        self.toggle_btn.setText("Start Monitoring")
        self.toggle_btn.setStyleSheet("")
    
    def update_data(self) -> None:
        """Update and send monitoring data"""
        try:
            # Get system stats
            stats: Dict[str, Dict[str, float]] = self.monitor.get_all_stats(interval=0.1)
            
            # Get appearance settings
            appearance: Dict[str, Any] = self.config.get_appearance()
            
            warning_message: Optional[str] = None
            if not self.monitor.is_running_as_root():
                warning_message = "CPU power unavailable - run with sudo"

            # Build complete data packet
            data: Dict[str, Any] = {
                "stats": stats,
                "appearance": appearance,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0.0",
                    "warning": warning_message,
                }
            }

            # Send to device
            success: bool = self.adb.push_data(data)

            # Update preview
            self._update_preview(data, success)
            
        except Exception as e:
            print(f"Error updating data: {e}")
    
    def _update_preview(self, data: Dict[str, Any], success: bool) -> None:
        """Update stats preview display"""
        stats: Dict[str, Any] = data.get('stats', {})
        cpu: Dict[str, float] = stats.get('cpu', {})
        mem: Dict[str, float] = stats.get('memory', {})
        gpu: Dict[str, float] = stats.get('gpu', {})
        
        preview = f"""CPU: {cpu.get('cpu_percent', 0):.1f}% | Temp: {cpu.get('cpu_temp_celsius', 0):.1f}°C"""
        if 'cpu_power_watts' in cpu:
            preview += f" | Power: {cpu['cpu_power_watts']:.1f}W"
        
        preview += f"\nMemory: {mem.get('percent', 0):.1f}% ({mem.get('used_gb', 0):.1f}/{mem.get('total_gb', 0):.1f} GB)"
        
        preview += f"\nGPU: {gpu.get('gpu_usage_percent', 0)}% | Temp: {gpu.get('gpu_temp_celsius', 0):.1f}°C"
        if 'gpu_power_watts' in gpu:
            preview += f" | Power: {gpu['gpu_power_watts']:.1f}W"
        
        preview += f"\n\nADB Push: {'✓ Success' if success else '✗ Failed'}"
        preview += f"\nLast Update: {datetime.now().strftime('%H:%M:%S')}"
        
        self.stats_display.setPlainText(preview)

    def _get_monitoring_flag(self, key: str) -> bool:
        value = self.config.get('monitoring', key)
        return isinstance(value, bool) and value

    def _get_refresh_rate(self) -> int:
        refresh_rate = self.config.get('appearance', 'refresh_rate_ms')
        if isinstance(refresh_rate, int) and refresh_rate > 0:
            return refresh_rate

        default_refresh = Config.DEFAULT_CONFIG['appearance']['refresh_rate_ms']
        if isinstance(default_refresh, int):
            return default_refresh

        return 1000
    
    def open_settings(self) -> None:
        """Open settings dialog"""
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Settings were saved, update refresh rate if monitoring
            if self.monitoring:
                refresh_rate = self._get_refresh_rate()
                self.timer.setInterval(refresh_rate)
    
    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:
        """Handle window close event"""
        if a0 is None:
            return
        event: QCloseEvent = a0
        if self._get_monitoring_flag('minimize_to_tray'):
            event.ignore()
            self.hide()
            self.close_to_tray.emit()
        else:
            event.accept()
    
    def minimize_to_tray(self) -> None:
        """Minimize window to system tray"""
        self.hide()
        self.close_to_tray.emit()
    
    def force_quit_application(self) -> None:
        """Force quit the application completely"""
        print("DEBUG: force_quit_application called")
        # Stop monitoring if active
        if self.monitoring:
            self.stop_monitoring()
        
        # Emit signal to force quit the application
        print("DEBUG: emitting force_quit signal")
        self.force_quit.emit()
