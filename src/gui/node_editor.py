from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from src.nodes.base_nodes import Connection, Socket, Node
from src.nodes.node_factory import NodeFactory
from src.gui.theme_manager import ThemeManager

class NodeEditorScene(QGraphicsScene):
    """Scene for the node editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 5000, 5000)
        self.grid_size = 20
        self.grid_squares = 5
        
       
        self.connecting = False
        self.temp_connection = None
        self.start_socket = None
        
       
        theme = ThemeManager.get_current_theme()
        self.setBackgroundBrush(ThemeManager.get_theme_color(theme, "grid_bg"))
    
    def drawBackground(self, painter, rect):
        """Draw grid in the background"""
        super().drawBackground(painter, rect)
        
        
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        
        gridPen = ThemeManager.get_grid_pen()
        painter.setPen(gridPen)
        
        
        for x in range(left, int(rect.right()), self.grid_size):
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
        
        
        for y in range(top, int(rect.bottom()), self.grid_size):
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
    
    def update_theme(self):
        """Update scene appearance when theme changes"""
        theme = ThemeManager.get_current_theme()
        self.setBackgroundBrush(ThemeManager.get_theme_color(theme, "grid_bg"))
        
       
        for item in self.items():
            if hasattr(item, 'update_theme'):
                item.update_theme()
        
        self.update()

class NodeEditorView(QGraphicsView):
    """View for the node editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
     
        self.scene = NodeEditorScene(self)
        self.setScene(self.scene)
        
       
        self.setRenderHints(QPainter.Antialiasing | 
                           QPainter.TextAntialiasing | 
                           QPainter.SmoothPixmapTransform)
        
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        
        self.centerOn(0, 0)
        
        
        self.connecting = False
        self.temp_connection = None
        self.start_socket = None

    def find_socket_at_position(self, pos):
        """Find socket at given position"""
        scene_pos = self.mapToScene(pos)
        
       
        items = self.items(pos)
        
        for item in items:
          
            if isinstance(item, Node):
                for socket in item.input_sockets + item.output_sockets:
                    if socket.hitTest(scene_pos):
                        return socket
        return None

    def wheelEvent(self, event):
        """Handle zooming with mouse wheel"""
       
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        
       
        oldPos = self.mapToScene(event.pos())
        
        
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        
        self.scale(zoomFactor, zoomFactor)
        
       
        newPos = self.mapToScene(event.pos())
        
        
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
        
    def mousePressEvent(self, event):
        """Handle mouse press events for connecting nodes"""
        if event.button() == Qt.LeftButton:
            socket = self.find_socket_at_position(event.pos())
            if socket:
                self.connecting = True
                self.start_socket = socket
                
               
                self.temp_connection = Connection(
                    self.scene,
                    start_socket=socket,
                    end_socket=None
                )
                
                
                if self.temp_connection in socket.connections:
                    socket.connections.remove(self.temp_connection)
                
               
                self.temp_connection.end_pos = self.mapToScene(event.pos())
                return
                
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.connecting and self.temp_connection:
            
            self.temp_connection.end_pos = self.mapToScene(event.pos())
            
            
            hover_socket = self.find_socket_at_position(event.pos())
            if hover_socket and hover_socket != self.start_socket:
                
                valid = ((self.start_socket.socket_type == Socket.TYPE_OUTPUT and 
                         hover_socket.socket_type == Socket.TYPE_INPUT) or
                        (self.start_socket.socket_type == Socket.TYPE_INPUT and 
                         hover_socket.socket_type == Socket.TYPE_OUTPUT))
                
               
                state = "valid" if valid else "invalid"
                self.temp_connection.pen = ThemeManager.get_connection_pen(state)
            else:
                self.temp_connection.pen = ThemeManager.get_connection_pen("default")
                
            self.temp_connection.update()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton and self.connecting:
            end_socket = self.find_socket_at_position(event.pos())
            
            if end_socket and end_socket != self.start_socket:
                
                valid_connection = (
                    (self.start_socket.socket_type == Socket.TYPE_OUTPUT and 
                     end_socket.socket_type == Socket.TYPE_INPUT) or
                    (self.start_socket.socket_type == Socket.TYPE_INPUT and 
                     end_socket.socket_type == Socket.TYPE_OUTPUT)
                )
                
                if valid_connection:
                   
                    output_socket = self.start_socket if self.start_socket.socket_type == Socket.TYPE_OUTPUT else end_socket
                    input_socket = end_socket if end_socket.socket_type == Socket.TYPE_INPUT else self.start_socket
                    
                   
                    if self.temp_connection:
                        self.scene.removeItem(self.temp_connection)
                    
                  
                    connection = Connection(
                        self.scene,
                        start_socket=output_socket,
                        end_socket=input_socket
                    )
                    
                    
                    input_socket.value = output_socket.value
                    input_socket.node.calculate_output()
            else:
                
                if self.temp_connection:
                    self.scene.removeItem(self.temp_connection)
            
            self.temp_connection = None
            self.connecting = False
            self.start_socket = None
            
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Handle drag move events"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop events to create new nodes"""
        if event.mimeData().hasText():
            
            node_type = event.mimeData().text()
            
          
            drop_position = self.mapToScene(event.pos())
            
           
            node = NodeFactory.create_node(self.scene, node_type)
            
           
            node.setPos(drop_position)
            
         
            event.acceptProposedAction()
    
    def update_theme(self):
        """Update the view when theme changes"""
        if self.scene:
            self.scene.update_theme()