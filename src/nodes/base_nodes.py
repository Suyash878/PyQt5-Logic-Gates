from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath

class Socket:
    """Socket class for node connections"""
    
    TYPE_INPUT = 1
    TYPE_OUTPUT = 2
    
    def __init__(self, node, socket_type, index=0):
        self.node = node
        self.socket_type = socket_type
        self.index = index
        self.position = QPointF(0, 0)
        self.connections = []
        self.value = False
        self.radius = 6
        self.hit_radius = 20  # Increased from 12 to 20 for easier connections
        self.hover_state = False  # Track if socket is being hovered
        
        # Calculate position
        self.calculate_socket_position()
        
    def get_position(self):
        """Calculate global position of the socket"""
        return self.node.pos() + self.position
    
    def calculate_socket_position(self):
        """Calculate position in local node coordinates"""
        if self.socket_type == self.TYPE_INPUT:
            # Position inputs on the left side
            self.position = QPointF(0, self.node.title_height + 20 + self.index * 20)
        else:
            # Position outputs on the right side
            self.position = QPointF(self.node.width, self.node.title_height + 20 + self.index * 20)

    def hitTest(self, pos):
        """Test if position hits this socket with improved detection logic"""
        socket_pos = self.get_position()
        # Use Euclidean distance for more natural feel
        dx = pos.x() - socket_pos.x()
        dy = pos.y() - socket_pos.y()
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Update hover state for visual feedback
        old_hover_state = self.hover_state
        self.hover_state = distance < self.hit_radius
        
        # If hover state changed, repaint the node
        if old_hover_state != self.hover_state:
            self.node.update()
            
        return self.hover_state

class Connection(QGraphicsItem):
    """Connection between nodes"""
    
    def __init__(self, scene, start_socket=None, end_socket=None):
        super().__init__()
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.start_pos = QPointF(0, 0)
        self.end_pos = QPointF(0, 0)
        
        # Set up pen for drawing
        self.pen = QPen(Qt.black)
        self.pen.setWidth(2)
        
        # Add to scene
        scene.addItem(self)
        
        # Update connection points and propagate initial value
        self.update_positions()
        
        # Initialize the connection properly
        if start_socket and end_socket:
            # Make sure connections are added to both sockets
            if self not in start_socket.connections:
                start_socket.connections.append(self)
            if self not in end_socket.connections:
                end_socket.connections.append(self)
            
            # Propagate the initial value
            end_socket.value = start_socket.value
            end_socket.node.calculate_output()
        
        # Add highlighting state
        self.hovered = False
        self.setAcceptHoverEvents(True)  # Enable hover events
        
    def update_positions(self):
        """Update the position of the line"""
        if self.start_socket:
            self.start_pos = self.start_socket.get_position()
        if self.end_socket:
            self.end_pos = self.end_socket.get_position()
        self.update()
        
    def boundingRect(self):
        """Define the bounding rectangle for the connection"""
        if not self.start_socket or not self.end_socket:
            return QRectF(
                min(self.start_pos.x(), self.end_pos.x()),
                min(self.start_pos.y(), self.end_pos.y()),
                abs(self.end_pos.x() - self.start_pos.x()) + 1,
                abs(self.end_pos.y() - self.start_pos.y()) + 1
            ).adjusted(-10, -10, 10, 10)
            
        return QRectF(
            min(self.start_pos.x(), self.end_pos.x()),
            min(self.start_pos.y(), self.end_pos.y()),
            abs(self.end_pos.x() - self.start_pos.x()),
            abs(self.end_pos.y() - self.start_pos.y())
        ).adjusted(-10, -10, 10, 10)
    
    def paint(self, painter, option, widget=None):
        """Draw the connection line with improved visibility"""
        if not self.start_socket and not self.end_socket:
            return
            
        # Draw bezier curve
        path = QPainterPath(self.start_pos)
        
        # Control points for bezier curve
        dx = self.end_pos.x() - self.start_pos.x()
        control1 = QPointF(
            self.start_pos.x() + dx * 0.5,
            self.start_pos.y()
        )
        control2 = QPointF(
            self.end_pos.x() - dx * 0.5,
            self.end_pos.y()
        )
        
        path.cubicTo(control1, control2, self.end_pos)
        
        # Draw glow effect when hovered
        if self.hovered:
            glow_pen = QPen(QColor(255, 255, 255, 100), 6)
            painter.setPen(glow_pen)
            painter.drawPath(path)
        
        # Set wire color based on value and state
        if self.start_socket and hasattr(self.start_socket, 'value'):
            if self.start_socket.value:
                color = QColor(0, 255, 0) if not self.hovered else QColor(100, 255, 100)
            else:
                color = QColor(0, 100, 0) if not self.hovered else QColor(0, 150, 0)
        else:
            color = QColor(200, 200, 200) if not self.hovered else QColor(255, 255, 255)
        
        self.pen.setColor(color)
        painter.setPen(self.pen)
        painter.drawPath(path)
        
        # Draw direction indicators
        self._draw_direction_arrow(painter, path)
    
    def _draw_direction_arrow(self, painter, path):
        """Draw small arrow indicating signal flow direction"""
        if not self.start_socket or not self.end_socket:
            return
            
        # Get point at middle of path
        percent = 0.5
        point = path.pointAtPercent(percent)
        angle = path.angleAtPercent(percent)
        
        # Draw arrow
        painter.save()
        painter.translate(point)
        painter.rotate(-angle)
        
        arrow_size = 8
        painter.drawLines([
            QLineF(0, 0, -arrow_size, -arrow_size/2),
            QLineF(0, 0, -arrow_size, arrow_size/2)
        ])
        painter.restore()
    
    def hoverEnterEvent(self, event):
        """Handle hover enter event"""
        self.hovered = True
        self.update()
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave event"""
        self.hovered = False
        self.update()
        
    def find_nearest_socket(self, scene_pos, socket_type):
        """Find the nearest socket within range to snap to
        
        Args:
            scene_pos: Current position in scene coordinates
            socket_type: Type of socket to find (input or output)
            
        Returns:
            Nearest Socket object or None if none found in range
        """
        nearest_socket = None
        min_distance = float('inf')
        snap_radius = 30  # Maximum distance for snapping
        
        # Get all items in the scene
        for item in self.scene.items():
            if isinstance(item, Node):
                # Check appropriate sockets based on type
                sockets_to_check = item.input_sockets if socket_type == Socket.TYPE_INPUT else item.output_sockets
                
                for socket in sockets_to_check:
                    socket_pos = socket.get_position()
                    dx = socket_pos.x() - scene_pos.x()
                    dy = socket_pos.y() - scene_pos.y()
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance < snap_radius and distance < min_distance:
                        min_distance = distance
                        nearest_socket = socket
        
        return nearest_socket

class Node(QGraphicsItem):
    """Base class for all nodes in the logic gate simulator"""
    
    def __init__(self, scene, title="Node", inputs=1, outputs=1):
        super().__init__()
        self.scene = scene
        self.title = title
        self.width = 150
        self.height = 100
        self.title_height = 30
        self.edge_roundness = 10
        self.edge_padding = 10
        
        # Make item movable
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Create sockets
        self.input_sockets = []
        self.output_sockets = []
        self.init_sockets(inputs, outputs)
        
        # Add to scene
        self.scene.addItem(self)
        
    def init_sockets(self, inputs, outputs):
        """Initialize input and output sockets"""
        # Create input sockets
        for i in range(inputs):
            socket = Socket(self, Socket.TYPE_INPUT, i)
            self.input_sockets.append(socket)
            
        # Create output sockets
        for i in range(outputs):
            socket = Socket(self, Socket.TYPE_OUTPUT, i)
            self.output_sockets.append(socket)
            
    def boundingRect(self):
        """Define the bounding rectangle of the node"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget=None):
        """Draw the node"""
        # Node background
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, 
                                 self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, 
                          self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness, 
                          self.edge_roundness, self.edge_roundness)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(80, 80, 80))
        painter.drawPath(path_title)
        
        # Node content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, 
                                   self.height - self.title_height, 
                                   self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, 
                            self.edge_roundness, self.edge_roundness)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(240, 240, 240))
        painter.drawPath(path_content)
        
        # Node outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, 
                                   self.edge_roundness, self.edge_roundness)
        
        # Draw outline based on selection state
        if self.isSelected():
            painter.setPen(QPen(QColor(0, 156, 255), 2))
        else:
            painter.setPen(QPen(Qt.black, 1))
            
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline)
        
        # Draw the title
        painter.setPen(QPen(Qt.white, 1))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(self.edge_padding, self.title_height - self.edge_padding, 
                        self.title)
        
        # Draw sockets
        self._draw_sockets(painter)
    
    def _draw_sockets(self, painter):
        """Draw input and output sockets with hover highlight"""
        # Draw input sockets
        for socket in self.input_sockets:
            x = int(socket.position.x())
            y = int(socket.position.y())
            radius = int(socket.radius)
            
            # Add glow effect for hover
            if socket.hover_state:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
                painter.drawEllipse(x - radius*2, y - radius*2, radius * 4, radius * 4)
            
            painter.setPen(QPen(Qt.black, 1))
            
            # Socket color depending on value
            socket_color = Qt.red if socket.value else Qt.darkRed
            # Brighten if hovered
            if socket.hover_state:
                if socket.value:
                    socket_color = QColor(255, 100, 100)  # Brighter red
                else:
                    socket_color = QColor(180, 60, 60)    # Brighter dark red
                    
            painter.setBrush(QBrush(socket_color))
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
        
        # Draw output sockets
        for socket in self.output_sockets:
            x = int(socket.position.x())
            y = int(socket.position.y())
            radius = int(socket.radius)
            
            # Add glow effect for hover
            if socket.hover_state:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
                painter.drawEllipse(x - radius*2, y - radius*2, radius * 4, radius * 4)
            
            painter.setPen(QPen(Qt.black, 1))
            
            # Socket color depending on value
            socket_color = Qt.green if socket.value else Qt.darkGreen
            # Brighten if hovered
            if socket.hover_state:
                if socket.value:
                    socket_color = QColor(100, 255, 100)  # Brighter green
                else:
                    socket_color = QColor(60, 180, 60)    # Brighter dark green
                    
            painter.setBrush(QBrush(socket_color))
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
    
    def _calculate(self):
        """Virtual method to be implemented by logic gate nodes
        Returns the calculated output value based on inputs"""
        return False
    
    def calculate_output(self):
        """Calculate and propagate the output value"""
        # Calculate output value
        result = self._calculate()
        
        # Update output sockets
        for socket in self.output_sockets:
            socket.value = result
            
            # Propagate to connected nodes
            for connection in socket.connections:
                if connection.end_socket:
                    connection.end_socket.value = result
                    # Trigger recalculation on the destination node
                    connection.end_socket.node.calculate_output()
    
    def itemChange(self, change, value):
        """Handle changes to the node"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update all connections after node position change
            self.update_connections()
            
        return super().itemChange(change, value)
    
    def update_connections(self):
        """Update all connections connected to this node"""
        for socket in self.input_sockets + self.output_sockets:
            for connection in socket.connections:
                connection.update_positions()