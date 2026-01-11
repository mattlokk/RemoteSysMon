"""
Settings Dialog for RemoteSysMon
"""

from typing import Any, Dict, Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton, 
                             QSpinBox, QCheckBox, QColorDialog, QGroupBox,
                             QGridLayout)
from PyQt6.QtGui import QColor

from core.config import Config


class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    def __init__(self, config: Config, parent: Optional[QWidget] = None):
        """
        Initialize settings dialog
        
        Args:
            config: Config instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config: Config = config
        self.bg_color_btn: QPushButton
        self.text_color_btn: QPushButton
        self.tile_background_btn: QPushButton
        self.tile_text_color_btn: QPushButton
        self.font_size_spin: QSpinBox
        self.refresh_rate_spin: QSpinBox
        self.show_graphs_check: QCheckBox
        self.auto_start_check: QCheckBox
        self.minimize_to_tray_check: QCheckBox
        self.start_minimized_check: QCheckBox
        self.target_path_input: QLineEdit
        self.auto_connect_check: QCheckBox
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        
        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        tabs.addTab(appearance_tab, "Appearance")
        
        # Monitoring tab
        monitoring_tab = self._create_monitoring_tab()
        tabs.addTab(monitoring_tab, "Monitoring")
        
        # ADB tab
        adb_tab = self._create_adb_tab()
        tabs.addTab(adb_tab, "ADB")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Colors group
        colors_group = QGroupBox("Colors")
        colors_layout = QGridLayout()
        
        # Background color
        colors_layout.addWidget(QLabel("Background:"), 0, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.clicked.connect(lambda: self._pick_color('bg'))
        colors_layout.addWidget(self.bg_color_btn, 0, 1)
        
        # Text color
        colors_layout.addWidget(QLabel("Text:"), 1, 0)
        self.text_color_btn = QPushButton()
        self.text_color_btn.clicked.connect(lambda: self._pick_color('text'))
        colors_layout.addWidget(self.text_color_btn, 1, 1)
        
        # Tile background color
        colors_layout.addWidget(QLabel("Tile Background:"), 2, 0)
        self.tile_background_btn = QPushButton()
        self.tile_background_btn.clicked.connect(lambda: self._pick_color('tile_background'))
        colors_layout.addWidget(self.tile_background_btn, 2, 1)

        colors_layout.addWidget(QLabel("Tile Text:"), 3, 0)
        self.tile_text_color_btn = QPushButton()
        self.tile_text_color_btn.clicked.connect(lambda: self._pick_color('tile_text'))
        colors_layout.addWidget(self.tile_text_color_btn, 3, 1)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        # Display group
        display_group = QGroupBox("Display")
        display_layout = QGridLayout()
        
        # Font size
        display_layout.addWidget(QLabel("Font Size:"), 0, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSuffix(" pt")
        display_layout.addWidget(self.font_size_spin, 0, 1)

        # Refresh rate
        display_layout.addWidget(QLabel("Refresh Rate:"), 1, 0)
        self.refresh_rate_spin = QSpinBox()
        self.refresh_rate_spin.setRange(100, 10000)
        self.refresh_rate_spin.setSingleStep(100)
        self.refresh_rate_spin.setSuffix(" ms")
        display_layout.addWidget(self.refresh_rate_spin, 1, 1)

        # Show graphs
        self.show_graphs_check = QCheckBox("Show Graphs")
        display_layout.addWidget(self.show_graphs_check, 2, 0, 1, 2)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_monitoring_tab(self) -> QWidget:
        """Create monitoring settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Monitoring Options")
        group_layout = QVBoxLayout()
        
        self.auto_start_check = QCheckBox("Auto-start monitoring on launch")
        group_layout.addWidget(self.auto_start_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimize to system tray on close")
        group_layout.addWidget(self.minimize_to_tray_check)
        
        self.start_minimized_check = QCheckBox("Start minimized")
        group_layout.addWidget(self.start_minimized_check)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_adb_tab(self) -> QWidget:
        """Create ADB settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("ADB Options")
        group_layout = QGridLayout()
        
        # Target path
        group_layout.addWidget(QLabel("Target Path:"), 0, 0)
        self.target_path_input = QLineEdit()
        self.target_path_input.setPlaceholderText("/data/local/tmp/system_stats.json")
        group_layout.addWidget(self.target_path_input, 0, 1)
        
        # Auto-connect
        self.auto_connect_check = QCheckBox("Auto-connect to first device")
        group_layout.addWidget(self.auto_connect_check, 1, 0, 1, 2)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _pick_color(self, color_type: str) -> None:
        """
        Open color picker dialog
        
        Args:
            color_type: Type of color ('bg', 'text', 'tile_background')
        """
        button_map: Dict[str, QPushButton] = {
            'bg': self.bg_color_btn,
            'text': self.text_color_btn,
            'tile_background': self.tile_background_btn,
            'tile_text': self.tile_text_color_btn
        }
        
        button = button_map.get(color_type)
        if not button:
            return
        
        # Get current color
        current_color = button.property('color')
        if current_color:
            initial_color = QColor(current_color)
        else:
            initial_color = QColor('#ffffff')
        
        # Show color picker
        display_name = color_type.replace('_', ' ').title()
        color = QColorDialog.getColor(initial_color, self, f"Choose {display_name} Color")
        
        if color.isValid():
            self._set_button_color(button, color.name())
    
    def _set_button_color(self, button: QPushButton, color: str) -> None:
        """
        Set button color preview
        
        Args:
            button: Button to update
            color: Color hex string
        """
        button.setProperty('color', color)
        button.setStyleSheet(f"background-color: {color}; min-height: 30px;")
        button.setText(color)
    
    def load_settings(self) -> None:
        """Load current settings into UI"""
        # Appearance
        appearance: Dict[str, Any] = self.config.get_appearance()
        self._set_button_color(self.bg_color_btn, appearance.get('background_color', '#1e1e1e'))
        self._set_button_color(self.text_color_btn, appearance.get('text_color', '#ffffff'))
        self._set_button_color(
            self.tile_background_btn,
            appearance.get('tile_background_color', appearance.get('accent_color', '#0078d4'))
        )
        self._set_button_color(
            self.tile_text_color_btn,
            appearance.get('tile_text_color', appearance.get('text_color', '#ffffff'))
        )
        
        self.font_size_spin.setValue(appearance.get('font_size', 14))
        self.refresh_rate_spin.setValue(appearance.get('refresh_rate_ms', 1000))
        self.show_graphs_check.setChecked(appearance.get('show_graphs', True))
        
        # Monitoring
        monitoring: Dict[str, Any] = self.config.get_monitoring_settings()
        self.auto_start_check.setChecked(monitoring.get('auto_start', True))
        self.minimize_to_tray_check.setChecked(monitoring.get('minimize_to_tray', True))
        self.start_minimized_check.setChecked(monitoring.get('start_minimized', False))
        
        # ADB
        adb: Dict[str, Any] = self.config.get_adb_settings()
        self.target_path_input.setText(adb.get('target_path', '/data/local/tmp/system_stats.json'))
        self.auto_connect_check.setChecked(adb.get('auto_connect', True))
    
    def save_settings(self) -> None:
        """Save settings from UI"""
        # Appearance
        self.config.set('appearance', 'background_color', self.bg_color_btn.property('color'))
        self.config.set('appearance', 'text_color', self.text_color_btn.property('color'))
        self.config.set('appearance', 'tile_background_color', self.tile_background_btn.property('color'))
        self.config.set('appearance', 'tile_text_color', self.tile_text_color_btn.property('color'))
        self.config.set('appearance', 'font_size', self.font_size_spin.value())
        self.config.set('appearance', 'refresh_rate_ms', self.refresh_rate_spin.value())
        self.config.set('appearance', 'show_graphs', self.show_graphs_check.isChecked())
        
        # Monitoring
        self.config.set('monitoring', 'auto_start', self.auto_start_check.isChecked())
        self.config.set('monitoring', 'minimize_to_tray', self.minimize_to_tray_check.isChecked())
        self.config.set('monitoring', 'start_minimized', self.start_minimized_check.isChecked())
        
        # ADB
        self.config.set('adb', 'target_path', self.target_path_input.text())
        self.config.set('adb', 'auto_connect', self.auto_connect_check.isChecked())
        
        self.accept()
    
    def reset_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.config.reset_to_defaults()
        self.load_settings()
