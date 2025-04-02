from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                            QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QSize, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(base_dir, "assets", "images.png")

class NodeListWidget(QListWidget):
    """Widget that displays the list of available nodes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up drag and drop
        self.setDragEnabled(True)
        self.setIconSize(QSize(32, 32))
        
        # Add node types
        self._add_node_items()
        
    def _add_node_items(self):
        """Add items to the list"""
        node_types = [
            {"name": "Input", "type": "input", "icon": os.path.join(base_dir, "assets", "images.png")},
            {"name": "Output", "type": "output"},
            {"name": "AND Gate", "type": "and"},
            {"name": "OR Gate", "type": "or"},
            {"name": "NOT Gate", "type": "not"},
            {"name": "NAND Gate", "type": "nand"},
            {"name": "NOR Gate", "type": "nor"},
            {"name": "XOR Gate", "type": "xor"},
            {"name": "XNOR Gate", "type": "xnor"},
            {"name": "Write Output", "type": "file_output"}  # Added this line
        ]
        
        for node in node_types:
            item = QListWidgetItem(node["name"])
            item.setData(Qt.UserRole, node["type"])
            self.addItem(item)
    
    def startDrag(self, supported_actions):
        """Start drag operation with selected node type"""
        item = self.currentItem()
        if not item:
            return
        
        # Get node type from item data
        node_type = item.data(Qt.UserRole)
        
        # Create mime data
        mime_data = QMimeData()
        mime_data.setText(node_type)
        
        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        # Create pixmap for drag visualization
        pixmap = QPixmap(100, 60)
        pixmap.fill(QColor(240, 240, 240))
        
        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        painter.drawText(10, 20, item.text())
        painter.drawRect(0, 0, 99, 59)
        painter.end()
        
        drag.setPixmap(pixmap)
        
        # Start drag operation
        drag.exec_(supported_actions)

class SidePanel(QWidget):
    """Side panel showing available nodes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add title label
        title_label = QLabel("Available Nodes")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add node list
        self.node_list = NodeListWidget()
        layout.addWidget(self.node_list)