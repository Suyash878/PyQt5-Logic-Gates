from PyQt5.QtWidgets import QGraphicsItem, QLineEdit, QPushButton, QGraphicsProxyWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

class Node(QGraphicsItem):
    def __init__(self, scene, title, inputs=0, outputs=0):
        super().__init__()
        self.scene = scene
        self.title = title
        self.width = 150
        self.height = 100
        
        # Enable item flags
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        
        # Set up inputs and outputs
        self.input_sockets = []
        self.output_sockets = []
        
        # Create sockets
        for i in range(inputs):
            socket = Socket(self, i, Socket.INPUT)
            self.input_sockets.append(socket)
            
        for i in range(outputs):
            socket = Socket(self, i, Socket.OUTPUT)
            self.output_sockets.append(socket)
            
        # Make sure this node is drawn above edges but widgets are on top
        self.setZValue(0)
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget=None):
        # Draw node background
        painter.setPen(QPen(QColor("#3f3f3f")))
        painter.setBrush(QBrush(QColor("#2a2a2a")))
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
        
        # Draw title
        painter.setPen(QPen(Qt.white))
        painter.drawText(10, 20, self.title)
    
    def calculate_output(self):
        """Calculate and propagate the output value"""
        for out_socket in self.output_sockets:
            if out_socket.edges:
                for edge in out_socket.edges:
                    edge.propagate_value()


class Socket:
    INPUT = 1
    OUTPUT = 2
    
    def __init__(self, node, index, socket_type):
        self.node = node
        self.index = index
        self.socket_type = socket_type
        self.value = False
        self.edges = []


class InputNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="Input", inputs=0, outputs=1)
        self.value = False
        
        # Add input field with larger size and better positioning
        self.input_field = QLineEdit()
        self.input_field.setFixedSize(40, 25)  # Make it bigger
        self.input_field.setText("0")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3f3f3f;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        self.input_field.textChanged.connect(self._on_value_changed)
        
        # Add to scene with adjusted position
        proxy = scene.addWidget(self.input_field)
        proxy.setParentItem(self)
        proxy.setPos(20, 30)  # Adjust position to be more visible
        proxy.setZValue(1)    # Ensure it's drawn above the node
        
        # Store the proxy for future reference
        self.input_proxy = proxy
    
    def _on_value_changed(self, text):
        """Handle input value changes"""
        try:
            self.value = bool(int(text))
            self.output_sockets[0].value = self.value
            # Propagate change
            self.calculate_output()
        except ValueError:
            self.input_field.setText("0")
            
    def paint(self, painter, option, widget=None):
        # First call the parent class paint method
        super().paint(painter, option, widget)
        
        # Force update of the widget visibility
        if hasattr(self, 'input_proxy'):
            self.input_proxy.update()


class OutputNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="Output", inputs=1, outputs=0)
        self.value = False
        
        # Add display field
        self.display = QLineEdit()
        self.display.setFixedWidth(30)
        self.display.setReadOnly(True)
        self.display.setText("0")
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3f3f3f;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        
        # Add to scene
        proxy = scene.addWidget(self.display)
        proxy.setParentItem(self)
        proxy.setPos(60, 40)
        proxy.setZValue(1)  # Ensure it's drawn above the node
        
        # Store the proxy for future reference
        self.display_proxy = proxy
    
    def calculate_output(self):
        """Update display value"""
        if self.input_sockets:
            self.value = self.input_sockets[0].value
            self.display.setText("1" if self.value else "0")
            
    def paint(self, painter, option, widget=None):
        # First call the parent class paint method
        super().paint(painter, option, widget)
        
        # Force update of the widget visibility
        if hasattr(self, 'display_proxy'):
            self.display_proxy.update()


class FileOutputNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="File Output", inputs=1, outputs=0)
        self.value = False
        
        # Add save button
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3f3f3f;
                border-radius: 3px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
            QPushButton:pressed {
                background-color: #1b1b1b;
            }
        """)
        self.save_button.clicked.connect(self._save_to_file)
        
        # Add to scene
        proxy = scene.addWidget(self.save_button)
        proxy.setParentItem(self)
        proxy.setPos(40, 40)
        proxy.setZValue(1)  # Ensure it's drawn above the node
        
        # Store the proxy for future reference
        self.button_proxy = proxy
    
    def _save_to_file(self):
        """Save output value to file"""
        if self.input_sockets:
            with open("output.txt", "w") as f:
                f.write(str(int(self.input_sockets[0].value)))
                
    def paint(self, painter, option, widget=None):
        # First call the parent class paint method
        super().paint(painter, option, widget)
        
        # Force update of the widget visibility
        if hasattr(self, 'button_proxy'):
            self.button_proxy.update()