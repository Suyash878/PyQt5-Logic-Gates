from PyQt5.QtWidgets import QGraphicsItem, QLineEdit
from .base_nodes import Node

class AndNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="AND", inputs=2, outputs=1)
    
    def _calculate(self):
        """Perform AND operation"""
        return all(socket.value for socket in self.input_sockets)

class OrNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="OR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Perform OR operation"""
        return any(socket.value for socket in self.input_sockets)

class NotNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="NOT", inputs=1, outputs=1)
    
    def _calculate(self):
        """Perform NOT operation"""
        if self.input_sockets:
            return not self.input_sockets[0].value
        return False

class NandNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="NAND", inputs=2, outputs=1)
    
    def _calculate(self):
        """Perform NAND operation"""
        return not all(socket.value for socket in self.input_sockets)

class NorNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="NOR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Perform NOR operation"""
        return not any(socket.value for socket in self.input_sockets)

class XorNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="XOR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Perform XOR operation"""
        return sum(socket.value for socket in self.input_sockets) == 1

class XnorNode(Node):
    def __init__(self, scene):
        super().__init__(scene, title="XNOR", inputs=2, outputs=1)
    
    def _calculate(self):
        """Perform XNOR operation"""
        return sum(socket.value for socket in self.input_sockets) != 1