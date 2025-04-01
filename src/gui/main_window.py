from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QDockWidget, 
                            QVBoxLayout, QWidget, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QByteArray, QDataStream, QIODevice
from src.gui.node_editor import NodeEditorView
from src.gui.side_panel import SidePanel
from src.nodes.node_factory import NodeFactory
from src.nodes.base_nodes import Connection, Node, Socket
import json
import os

class MainWindow(QMainWindow):
    """Main window for the logic gate simulator"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Logic Gate Simulator")
        self.resize(1200, 800)

        self.tab_file_paths = {}
        
        # Initialize UI
        self._setup_ui()
        self._setup_actions()
        self._setup_menus()
        
        # # Track file paths for each tab
        # self.tab_file_paths = {}
        
    def _setup_ui(self):
        """Set up the user interface"""
        # Create tab widget for multiple node editors
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create first tab with node editor
        self._create_new_tab()
        
        # Create side panel
        self._setup_side_panel()
        
    def _setup_side_panel(self):
        """Set up the side panel with nodes"""
        # Create dock widget
        self.side_panel_dock = QDockWidget("Nodes", self)
        self.side_panel_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create side panel widget
        self.side_panel = SidePanel()
        self.side_panel_dock.setWidget(self.side_panel)
        
        # Add to main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_panel_dock)
        
    def _setup_actions(self):
        """Set up actions for menus"""
        # File actions
        self.action_new = QAction("New", self)
        self.action_new.setShortcut("Ctrl+N")
        
        self.action_open = QAction("Open", self)
        self.action_open.setShortcut("Ctrl+O")
        
        self.action_save = QAction("Save", self)
        self.action_save.setShortcut("Ctrl+S")
        
        self.action_save_as = QAction("Save As...", self)
        self.action_save_as.setShortcut("Ctrl+Shift+S")
        
        self.action_exit = QAction("Exit", self)
        self.action_exit.setShortcut("Alt+F4")
        
        # Edit actions
        self.action_undo = QAction("Undo", self)
        self.action_redo = QAction("Redo", self)
        self.action_cut = QAction("Cut", self)
        self.action_copy = QAction("Copy", self)
        self.action_paste = QAction("Paste", self)
        self.action_delete = QAction("Delete", self)
        
        # Window actions
        self.action_change_theme = QAction("Change Theme", self)
        
        # Connect actions
        self.action_new.triggered.connect(self._create_new_tab)
        self.action_save.triggered.connect(self._save_current_tab)
        self.action_save_as.triggered.connect(self._save_as_current_tab)
        self.action_open.triggered.connect(self._open_file)
        self.action_exit.triggered.connect(self.close)
        
    def _setup_menus(self):
        """Set up the menu bars"""
        # Create menus
        self.menu_bar = self.menuBar()
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)
        
        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addAction(self.action_delete)
        
        # Window menu
        self.window_menu = self.menu_bar.addMenu("Window")
        self.window_menu.addAction(self.action_change_theme)
        
    def _create_new_tab(self):
        """Create a new tab with node editor"""
        editor = NodeEditorView()
        
        # Enable drag and drop for the view
        editor.setAcceptDrops(True)
        
        # Add view to a new tab
        tab_index = self.tab_widget.addTab(editor, f"Untitled {self.tab_widget.count() + 1}")
        
        # Set the new tab as current
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Initialize file path as None for this tab
        self.tab_file_paths[tab_index] = None
        
    def _get_current_editor(self):
        """Get the current active node editor view"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab != -1:
            return self.tab_widget.widget(current_tab)
        return None
    
    def _save_current_tab(self):
        """Save the current tab"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == -1:
            return  # No tabs open
            
        # If file path exists, save directly; otherwise do Save As
        file_path = self.tab_file_paths.get(current_tab)
        if file_path:
            self._save_to_file(file_path)
        else:
            self._save_as_current_tab()
    
    def _save_as_current_tab(self):
        """Save the current tab with a new file name"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == -1:
            return  # No tabs open
            
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Circuit", 
            "", 
            "Logic Gate Simulator Files (*.lgs);;All Files (*)"
        )
        
        if file_path:
            # Add .lgs extension if not present
            if not file_path.endswith('.lgs'):
                file_path += '.lgs'
                
            # Save the file
            if self._save_to_file(file_path):
                # Update tab name to file name
                file_name = os.path.basename(file_path)
                self.tab_widget.setTabText(current_tab, file_name)
                
                # Store file path
                self.tab_file_paths[current_tab] = file_path
    
    def _save_to_file(self, file_path):
        """Save editor content to file"""
        editor = self._get_current_editor()
        if not editor:
            return False
            
        try:
            # Get scene data
            scene_data = self._serialize_scene(editor.scene)
            
            # Save to file
            with open(file_path, 'w') as file:
                json.dump(scene_data, file, indent=4)
                
            self.statusBar().showMessage(f"Saved to {file_path}", 3000)
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving file: {str(e)}")
            return False
    
    def _open_file(self):
        """Open a saved circuit file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Circuit", 
            "", 
            "Logic Gate Simulator Files (*.lgs);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load file data
                with open(file_path, 'r') as file:
                    scene_data = json.load(file)
                
                # Create new tab
                editor = NodeEditorView()
                editor.setAcceptDrops(True)
                
                # Deserialize data into scene
                self._deserialize_scene(editor.scene, scene_data)
                
                # Add to tab widget
                file_name = os.path.basename(file_path)
                tab_index = self.tab_widget.addTab(editor, file_name)
                
                # Set as current and store file path
                self.tab_widget.setCurrentIndex(tab_index)
                self.tab_file_paths[tab_index] = file_path
                
                self.statusBar().showMessage(f"Opened {file_path}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Error opening file: {str(e)}")
    
    def _serialize_scene(self, scene):
        """Convert scene to serializable data structure"""
        data = {
            'nodes': [],
            'connections': []
        }
        
        # Serialize all nodes
        for item in scene.items():
            if isinstance(item, Node):
                node_data = {
                    'id': id(item),  # Use object ID as unique identifier
                    'type': item.__class__.__name__,
                    'pos_x': item.pos().x(),
                    'pos_y': item.pos().y(),
                    'title': item.title,
                    'inputs': len(item.input_sockets),
                    'outputs': len(item.output_sockets),
                    'socket_values': {
                        'inputs': [socket.value for socket in item.input_sockets],
                        'outputs': [socket.value for socket in item.output_sockets]
                    }
                }
                data['nodes'].append(node_data)
        
        # Serialize all connections
        for item in scene.items():
            if isinstance(item, Connection) and item.start_socket and item.end_socket:
                connection_data = {
                    'start_node': id(item.start_socket.node),
                    'start_socket_index': item.start_socket.index,
                    'start_socket_type': item.start_socket.socket_type,
                    'end_node': id(item.end_socket.node),
                    'end_socket_index': item.end_socket.index,
                    'end_socket_type': item.end_socket.socket_type
                }
                data['connections'].append(connection_data)
        
        return data
    
    def _deserialize_scene(self, scene, data):
        """Reconstruct scene from serialized data"""
        # Clear existing scene
        scene.clear()
        
        # Dictionary to map node IDs to actual nodes
        node_map = {}
        
        # Create nodes first
        for node_data in data['nodes']:
            # Create node using factory
            node = NodeFactory.create_node(scene, node_data['type'])
            
            # Set position and properties
            node.setPos(node_data['pos_x'], node_data['pos_y'])
            node.title = node_data['title']
            
            # Store in map for connection creation
            node_map[node_data['id']] = node
            
            # Set socket values if available
            if 'socket_values' in node_data:
                for i, value in enumerate(node_data['socket_values']['inputs']):
                    if i < len(node.input_sockets):
                        node.input_sockets[i].value = value
                
                for i, value in enumerate(node_data['socket_values']['outputs']):
                    if i < len(node.output_sockets):
                        node.output_sockets[i].value = value
        
        # Create connections
        for conn_data in data['connections']:
            if conn_data['start_node'] in node_map and conn_data['end_node'] in node_map:
                start_node = node_map[conn_data['start_node']]
                end_node = node_map[conn_data['end_node']]
                
                # Get sockets
                start_socket = None
                end_socket = None
                
                if conn_data['start_socket_type'] == Socket.TYPE_INPUT:
                    start_socket = start_node.input_sockets[conn_data['start_socket_index']]
                else:
                    start_socket = start_node.output_sockets[conn_data['start_socket_index']]
                    
                if conn_data['end_socket_type'] == Socket.TYPE_INPUT:
                    end_socket = end_node.input_sockets[conn_data['end_socket_index']]
                else:
                    end_socket = end_node.output_sockets[conn_data['end_socket_index']]
                
                # Create connection
                if start_socket and end_socket:
                    # Determine output and input correctly
                    output_socket = start_socket if start_socket.socket_type == Socket.TYPE_OUTPUT else end_socket
                    input_socket = end_socket if end_socket.socket_type == Socket.TYPE_INPUT else start_socket
                    
                    Connection(scene, output_socket, input_socket)
                    
        # Calculate outputs to update the visual state
        for node in node_map.values():
            node.calculate_output()