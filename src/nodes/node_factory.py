from src.nodes.base_nodes import Node
from PyQt5.QtWidgets import QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class NodeFactory:
    """Factory for creating different node types"""
    
    @staticmethod
    def create_node(scene, node_type):
        """Create a node based on type"""
        if node_type == "input":
            return InputNode(scene)
        elif node_type == "output":
            return OutputNode(scene)
        elif node_type == "and":
            return AndNode(scene)
        elif node_type == "or":
            return OrNode(scene)
        elif node_type == "not":
            return NotNode(scene)
        elif node_type == "nand":
            return NandNode(scene)
        elif node_type == "nor":
            return NorNode(scene)
        elif node_type == "xor":
            return XorNode(scene)
        elif node_type == "xnor":
            return XnorNode(scene)
        elif node_type == "file_output":
            return FileOutputNode(scene)
        else:
            return Node(scene, title="Default Node")

# Node placeholder classes
class InputNode(Node):
    """Input node with editable value"""
    def __init__(self, scene):
        super().__init__(scene, title="Input", inputs=0, outputs=1)
        # Initialize value attribute
        self.value = False
        
        # Add input field
        self.input_field = QLineEdit()
        self.input_field.setFixedSize(40, 25)
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
        
        # Add to scene
        proxy = scene.addWidget(self.input_field)
        proxy.setParentItem(self)
        proxy.setPos(20, 30)

    def _on_value_changed(self, text):
        """Handle input value changes"""
        try:
            # Convert input text to boolean
            self.value = bool(int(text))
            
            # Update output socket value
            if self.output_sockets:
                self.output_sockets[0].value = self.value
                
                # Propagate changes through connected nodes
                for connection in self.output_sockets[0].connections:
                    if connection.end_socket:
                        connection.end_socket.value = self.value
                        connection.end_socket.node.calculate_output()
                        
        except ValueError:
            self.input_field.setText("0")

    def calculate_output(self):
        """Calculate and propagate the output value"""
        if self.output_sockets:
            self.output_sockets[0].value = self.value
            
            # Propagate to all connected nodes
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = self.value
                    connection.end_socket.node.calculate_output()

class OutputNode(Node):
    """Output node that displays result"""
    def __init__(self, scene):
        super().__init__(scene, title="Output", inputs=1, outputs=0)
        
        # Add display field
        self.display = QLineEdit()
        self.display.setFixedSize(40, 25)
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
        proxy.setPos(20, 30)

    def calculate_output(self):
        """Update display value"""
        if self.input_sockets:
            value = self.input_sockets[0].value
            self.display.setText("1" if value else "0")

class FileOutputNode(Node):
    """Output node that writes result to file"""
    def __init__(self, scene):
        super().__init__(scene, title="Write Output", inputs=1, outputs=0)
        
        # Add save button
        self.save_button = QPushButton("Save to File")
        self.save_button.setFixedSize(80, 25)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3f3f3f;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
            QPushButton:pressed {
                background-color: #1b1b1b;
            }
        """)
        self.save_button.clicked.connect(self._save_to_file)
        
        # Add button to scene
        proxy = scene.addWidget(self.save_button)
        proxy.setParentItem(self)
        proxy.setPos(35, 40)  # Center the button in node
        
    def _save_to_file(self):
        """Save output value to file"""
        if self.input_sockets:
            try:
                with open("output.txt", "w") as f:
                    value = "1" if self.input_sockets[0].value else "0"
                    f.write(value)
                print(f"Output saved to output.txt: {value}")
            except Exception as e:
                print(f"Error writing to file: {str(e)}")

    def calculate_output(self):
        """Handle input value changes"""
        # Optional: Auto-save on input change
        if self.input_sockets:
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b;
                    color: white;
                    border: 1px solid #3f3f3f;
                    border-radius: 3px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #3b3b3b;
                }
            """)

# Logic gate nodes
class AndNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="AND", inputs=2, outputs=1)
    
    def _calculate(self):
        """Calculate AND result"""
        return all(socket.value for socket in self.input_sockets)
    
    def calculate_output(self):
        """Perform AND operation and propagate"""
        # Calculate result
        result = self._calculate()
        
        # Update output and propagate
        if self.output_sockets:
            self.output_sockets[0].value = result
            # Propagate to connected nodes
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()

class OrNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="OR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Calculate OR result"""
        return any(socket.value for socket in self.input_sockets)
    
    def calculate_output(self):
        result = self._calculate()
        if self.output_sockets:
            self.output_sockets[0].value = result
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()

class NotNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="NOT", inputs=1, outputs=1)
    
    def _calculate(self):
        """Calculate NOT result"""
        if self.input_sockets:
            return not self.input_sockets[0].value
        return False
    
    def calculate_output(self):
        result = self._calculate()
        if self.output_sockets:
            self.output_sockets[0].value = result
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()

class NandNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="NAND", inputs=2, outputs=1)
    
    def _calculate(self):
        """Calculate NAND result"""
        return not all(socket.value for socket in self.input_sockets)
    
    def calculate_output(self):
        result = self._calculate()
        if self.output_sockets:
            self.output_sockets[0].value = result
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()

class NorNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="NOR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Calculate NOR result"""
        return not any(socket.value for socket in self.input_sockets)
    
    def calculate_output(self):
        result = self._calculate()
        if self.output_sockets:
            self.output_sockets[0].value = result
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()

class XorNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="XOR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Calculate XOR result"""
        if len(self.input_sockets) >= 2:
            return self.input_sockets[0].value != self.input_sockets[1].value
        return False
    
    def calculate_output(self):
        result = self._calculate()
        if self.output_sockets:
            self.output_sockets[0].value = result
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()

class XnorNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="XNOR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Calculate XNOR result"""
        if len(self.input_sockets) >= 2:
            return self.input_sockets[0].value == self.input_sockets[1].value
        return True
    
    def calculate_output(self):
        result = self._calculate()
        if self.output_sockets:
            self.output_sockets[0].value = result
            for connection in self.output_sockets[0].connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    connection.end_socket.node.calculate_output()