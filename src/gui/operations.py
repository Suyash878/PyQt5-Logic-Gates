from PyQt5.QtWidgets import QUndoStack, QUndoCommand, QApplication
from PyQt5.QtCore import QPointF, QByteArray, QDataStream, QIODevice, QMimeData
from PyQt5.QtGui import QClipboard
from src.nodes.base_nodes import Node, Connection, Socket
from src.nodes.node_factory import NodeFactory
from PyQt5.QtGui import QCursor

class NodeEditorCommand(QUndoCommand):
    """Base class for all node editor commands"""
    def __init__(self, editor_view, description=""):
        super().__init__(description)
        self.editor_view = editor_view
        self.scene = editor_view.scene

class AddNodeCommand(NodeEditorCommand):
    """Command to add a node"""
    def __init__(self, editor_view, node_type, position):
        super().__init__(editor_view, f"Add {node_type}")
        self.node_type = node_type
        self.position = position
        self.node_id = None
        
    def redo(self):
       
        node = NodeFactory.create_node(self.scene, self.node_type)
        node.setPos(self.position)
        self.node_id = id(node)
        
    def undo(self):
        
        for item in self.scene.items():
            if isinstance(item, Node) and id(item) == self.node_id:
                self.scene.removeItem(item)
                break

class RemoveNodeCommand(NodeEditorCommand):
    """Command to remove a node"""
    def __init__(self, editor_view, node):
        super().__init__(editor_view, f"Remove {node.title}")
        self.node = node
        self.node_data = self._serialize_node(node)
        self.connections_data = []
        
        
        for item in self.scene.items():
            if isinstance(item, Connection):
                if item.start_socket and item.start_socket.node == node:
                    self.connections_data.append(self._serialize_connection(item))
                elif item.end_socket and item.end_socket.node == node:
                    self.connections_data.append(self._serialize_connection(item))
    
    def _serialize_node(self, node):
        """Convert node to serializable data"""
        return {
            'type': node.__class__.__name__,
            'pos_x': node.pos().x(),
            'pos_y': node.pos().y(),
            'title': node.title,
            'socket_values': {
                'inputs': [socket.value for socket in node.input_sockets],
                'outputs': [socket.value for socket in node.output_sockets]
            }
        }
    
    def _serialize_connection(self, connection):
        """Convert connection to serializable data"""
        if not connection.start_socket or not connection.end_socket:
            return None
            
        return {
            'start_node_type': connection.start_socket.node.__class__.__name__,
            'start_socket_index': connection.start_socket.index,
            'start_socket_type': connection.start_socket.socket_type,
            'end_node_type': connection.end_socket.node.__class__.__name__,
            'end_socket_index': connection.end_socket.index,
            'end_socket_type': connection.end_socket.socket_type,
            'start_node_pos': (connection.start_socket.node.pos().x(), connection.start_socket.node.pos().y()),
            'end_node_pos': (connection.end_socket.node.pos().x(), connection.end_socket.node.pos().y())
        }
        
    def redo(self):
  
        for item in list(self.scene.items()):
            if isinstance(item, Connection):
                if (item.start_socket and item.start_socket.node == self.node) or \
                   (item.end_socket and item.end_socket.node == self.node):
                    self.scene.removeItem(item)
                    
      
        self.scene.removeItem(self.node)
    
    def undo(self):
      
        node = NodeFactory.create_node(self.scene, self.node_data['type'])
        node.setPos(self.node_data['pos_x'], self.node_data['pos_y'])
        node.title = self.node_data['title']
        
        
        for i, value in enumerate(self.node_data['socket_values']['inputs']):
            if i < len(node.input_sockets):
                node.input_sockets[i].value = value
                
        for i, value in enumerate(self.node_data['socket_values']['outputs']):
            if i < len(node.output_sockets):
                node.output_sockets[i].value = value
        
     
        self.node = node 

class AddConnectionCommand(NodeEditorCommand):
    """Command to add a connection between nodes"""
    def __init__(self, editor_view, output_socket, input_socket):
        super().__init__(editor_view, "Add Connection")
        self.output_socket = output_socket
        self.input_socket = input_socket
        self.connection = None
        
    def redo(self):
       
        self.connection = Connection(self.scene, self.output_socket, self.input_socket)
        
       
        self.input_socket.value = self.output_socket.value
        self.input_socket.node.calculate_output()
        
    def undo(self):
        if self.connection in self.scene.items():
            self.scene.removeItem(self.connection)

class RemoveConnectionCommand(NodeEditorCommand):
    """Command to remove a connection"""
    def __init__(self, editor_view, connection):
        super().__init__(editor_view, "Remove Connection")
        self.connection = connection
        self.output_socket = connection.start_socket
        self.input_socket = connection.end_socket
        
    def redo(self):
        self.scene.removeItem(self.connection)
        
    def undo(self):
        
        self.connection = Connection(self.scene, self.output_socket, self.input_socket)
        
     
        self.input_socket.value = self.output_socket.value
        self.input_socket.node.calculate_output()

class MoveNodeCommand(NodeEditorCommand):
    """Command to move a node"""
    def __init__(self, editor_view, node, old_pos, new_pos):
        super().__init__(editor_view, "Move Node")
        self.node = node
        self.old_pos = old_pos
        self.new_pos = new_pos
        
    def redo(self):
        self.node.setPos(self.new_pos)
        
    def undo(self):
        self.node.setPos(self.old_pos)

class NodeClipboard:
    """Class to handle clipboard operations for nodes"""
    @staticmethod
    def serialize_nodes(nodes):
        """Convert nodes to serializable data for clipboard"""
        data = {
            'nodes': [],
            'connections': []
        }
        
        
        node_mapping = {}
        
       
        for i, node in enumerate(nodes):
            node_data = {
                'type': node.__class__.__name__,
                'pos_x': node.pos().x(),
                'pos_y': node.pos().y(),
                'title': node.title,
                'socket_values': {
                    'inputs': [socket.value for socket in node.input_sockets],
                    'outputs': [socket.value for socket in node.output_sockets]
                }
            }
            data['nodes'].append(node_data)
            node_mapping[id(node)] = i
        
  
        for node in nodes:
            for socket in node.output_sockets:
                for conn in socket.connections:
                    if conn.end_socket and conn.end_socket.node in nodes:
                       
                        conn_data = {
                            'start_node_index': node_mapping[id(socket.node)],
                            'start_socket_index': socket.index,
                            'end_node_index': node_mapping[id(conn.end_socket.node)],
                            'end_socket_index': conn.end_socket.index
                        }
                        data['connections'].append(conn_data)
                        
        return data
    
    @staticmethod
    def deserialize_nodes(scene, data, position_offset=QPointF(20, 20)):
        """Recreate nodes from serialized data"""
   
        created_nodes = []
        
     
        for node_data in data['nodes']:
            node = NodeFactory.create_node(scene, node_data['type'])
            
         
            node.setPos(node_data['pos_x'] + position_offset.x(), 
                       node_data['pos_y'] + position_offset.y())
            
            node.title = node_data['title']
            

            for i, value in enumerate(node_data['socket_values']['inputs']):
                if i < len(node.input_sockets):
                    node.input_sockets[i].value = value
                    
            for i, value in enumerate(node_data['socket_values']['outputs']):
                if i < len(node.output_sockets):
                    node.output_sockets[i].value = value
                    
            created_nodes.append(node)
        
      
        for conn_data in data['connections']:
            if (0 <= conn_data['start_node_index'] < len(created_nodes) and
                0 <= conn_data['end_node_index'] < len(created_nodes)):
                
                start_node = created_nodes[conn_data['start_node_index']]
                end_node = created_nodes[conn_data['end_node_index']]
                
                if (conn_data['start_socket_index'] < len(start_node.output_sockets) and
                    conn_data['end_socket_index'] < len(end_node.input_sockets)):
                    
                    output_socket = start_node.output_sockets[conn_data['start_socket_index']]
                    input_socket = end_node.input_sockets[conn_data['end_socket_index']]
                    
                  
                    Connection(scene, output_socket, input_socket)
                    
                
                    input_socket.value = output_socket.value
                    input_socket.node.calculate_output()
        
        return created_nodes

class NodeOperations:
    """Class to handle operations for node editor"""
    def __init__(self, main_window):
        self.main_window = main_window
        self.undo_stack = QUndoStack(main_window)
        
   
        self.main_window.action_undo.triggered.connect(self.undo_stack.undo)
        self.main_window.action_redo.triggered.connect(self.undo_stack.redo)
        
   
        self.main_window.action_cut.triggered.connect(self.cut)
        self.main_window.action_copy.triggered.connect(self.copy)
        self.main_window.action_paste.triggered.connect(self.paste)
        self.main_window.action_delete.triggered.connect(self.delete)
        
    def get_current_editor(self):
        """Get the current node editor view"""
        return self.main_window._get_current_editor()
    
    def get_selected_nodes(self):
        """Get all selected nodes in the current editor"""
        editor = self.get_current_editor()
        if not editor:
            return []
            
        return [item for item in editor.scene.selectedItems() if isinstance(item, Node)]
    
    def get_selected_connections(self):
        """Get all selected connections in the current editor"""
        editor = self.get_current_editor()
        if not editor:
            return []
            
        return [item for item in editor.scene.selectedItems() if isinstance(item, Connection)]
    
    def cut(self):
        """Cut selected nodes to clipboard"""
        if self.copy():
            self.delete()
    
    def copy(self):
        """Copy selected nodes to clipboard"""
        editor = self.get_current_editor()
        if not editor:
            return False
            
        selected_nodes = self.get_selected_nodes()
        if not selected_nodes:
            return False
            
      
        data = NodeClipboard.serialize_nodes(selected_nodes)
        
        
        mime_data = QMimeData()
        
        
        import json
        json_data = json.dumps(data)
        
  
        mime_data.setText(json_data)
        

        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setMimeData(mime_data)
        
        return True
    
    def paste(self):
        """Paste nodes from clipboard"""
        editor = self.get_current_editor()
        if not editor:
            return False
            

        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if not mime_data.hasText():
            return False
            
        try:
          
            import json
            data = json.loads(mime_data.text())
            
           
            cursor_pos = editor.mapToScene(editor.mapFromGlobal(QCursor().pos()))
            
            
            created_nodes = NodeClipboard.deserialize_nodes(
                editor.scene, 
                data, 
                QPointF(cursor_pos.x(), cursor_pos.y())
            )
            
          
            editor.scene.clearSelection()
            for node in created_nodes:
                node.setSelected(True)
                
            return True
            
        except Exception as e:
            print(f"Error pasting nodes: {str(e)}")
            return False
    
    def delete(self):
        """Delete selected items"""
        editor = self.get_current_editor()
        if not editor:
            return

        selected_connections = self.get_selected_connections()
        selected_nodes = self.get_selected_nodes()
      
        for connection in selected_connections:
            self.undo_stack.push(RemoveConnectionCommand(editor, connection))
            

        for node in selected_nodes:
            self.undo_stack.push(RemoveNodeCommand(editor, node))

