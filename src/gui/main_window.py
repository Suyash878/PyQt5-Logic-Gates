from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QDockWidget, 
                            QVBoxLayout, QWidget, QMessageBox, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QByteArray, QDataStream, QIODevice
from src.gui.node_editor import NodeEditorView
from src.gui.side_panel import SidePanel
from src.nodes.node_factory import NodeFactory
from src.nodes.base_nodes import Connection, Node, Socket
from src.gui.operations import NodeOperations
from src.gui.theme_manager import ThemeManager
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
        
        # Initialize operations
        self.operations = NodeOperations(self)
        
        # Apply saved theme or default
        self._apply_current_theme()
        
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
        self.action_undo.setShortcut("Ctrl+Z")
        
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut("Ctrl+Shift+Z")
        
        self.action_cut = QAction("Cut", self)
        self.action_cut.setShortcut("Ctrl+X")
        
        self.action_copy = QAction("Copy", self)
        self.action_copy.setShortcut("Ctrl+C")
        
        self.action_paste = QAction("Paste", self)
        self.action_paste.setShortcut("Ctrl+V")
        
        self.action_delete = QAction("Delete", self)
        self.action_delete.setShortcut("Delete")
        
        # Theme actions
        self.action_toggle_theme = QAction("Toggle Light/Dark Mode", self)
        self.action_toggle_theme.setShortcut("Ctrl+T")
        
        # Connect actions
        self.action_new.triggered.connect(self._create_new_tab)
        self.action_save.triggered.connect(self._save_current_tab)
        self.action_save_as.triggered.connect(self._save_as_current_tab)
        self.action_open.triggered.connect(self._open_file)
        self.action_exit.triggered.connect(self.close)
        self.action_toggle_theme.triggered.connect(self._toggle_theme)
        
        # Connect edit actions
        self.action_undo.triggered.connect(self._undo)
        self.action_redo.triggered.connect(self._redo)
        self.action_cut.triggered.connect(self._cut)
        self.action_copy.triggered.connect(self._copy)
        self.action_paste.triggered.connect(self._paste)
        self.action_delete.triggered.connect(self._delete)
        
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
        
        # View menu
        self.view_menu = self.menu_bar.addMenu("View")
        self.view_menu.addAction(self.action_toggle_theme)
        
    def _apply_current_theme(self):
        """Apply the current theme saved in settings"""
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        theme = ThemeManager.get_current_theme()
        ThemeManager.apply_theme(app, theme)
        
        # Update theme-specific status in the menu
        theme_text = "Light Mode" if theme == ThemeManager.LIGHT_THEME else "Dark Mode"
        self.action_toggle_theme.setText(f"Toggle Theme (Current: {theme_text})")
        
        # Update all open node editors
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if hasattr(editor, 'update_theme'):
                editor.update_theme()
    
    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        new_theme = ThemeManager.toggle_theme(app)
        
        # Update action text
        theme_text = "Light Mode" if new_theme == ThemeManager.LIGHT_THEME else "Dark Mode"
        self.action_toggle_theme.setText(f"Toggle Theme (Current: {theme_text})")
        
        # Update all open node editors
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if hasattr(editor, 'update_theme'):
                editor.update_theme()
        
        # Show status message
        self.statusBar().showMessage(f"Theme changed to {theme_text}", 3000)
        
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
                
            # Show success message
            self.statusBar().showMessage(f"File saved to {file_path}", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving file: {str(e)}")
            return False
    
    def _open_file(self):
        """Open a circuit file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Circuit",
            "",
            "Logic Gate Simulator Files (*.lgs);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Create a new tab
            self._create_new_tab()
            current_tab = self.tab_widget.currentIndex()
            
            # Load the file into the current tab
            self._load_from_file(file_path)
            
            # Update tab name and path
            file_name = os.path.basename(file_path)
            self.tab_widget.setTabText(current_tab, file_name)
            self.tab_file_paths[current_tab] = file_path
            
            self.statusBar().showMessage(f"File opened: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Open Error", f"Error opening file: {str(e)}")
    
    def _load_from_file(self, file_path):
        """Load circuit from file into current editor"""
        editor = self._get_current_editor()
        if not editor:
            return
            
        try:
            with open(file_path, 'r') as file:
                scene_data = json.load(file)
                
            # Deserialize scene data
            self._deserialize_scene(editor.scene, scene_data)
            
            return True
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def _serialize_scene(self, scene):
        """Serialize scene data to JSON-compatible format"""
        data = {
            'nodes': [],
            'connections': []
        }
        
        # Serialize nodes
        for item in scene.items():
            if isinstance(item, Node):
                node_data = {
                    'id': id(item),
                    'type': item.__class__.__name__,
                    'pos_x': item.pos().x(),
                    'pos_y': item.pos().y(),
                    'inputs': [],
                    'outputs': [],
                    'properties': item.get_properties() if hasattr(item, 'get_properties') else {}
                }
                
                # Serialize input sockets
                for socket in item.input_sockets:
                    socket_data = {
                        'id': id(socket),
                        'index': socket.index,
                        'value': socket.value
                    }
                    node_data['inputs'].append(socket_data)
                
                # Serialize output sockets
                for socket in item.output_sockets:
                    socket_data = {
                        'id': id(socket),
                        'index': socket.index,
                        'value': socket.value
                    }
                    node_data['outputs'].append(socket_data)
                
                data['nodes'].append(node_data)
        
        # Serialize connections
        for item in scene.items():
            if isinstance(item, Connection):
                if item.start_socket and item.end_socket:
                    connection_data = {
                        'id': id(item),
                        'start_node': id(item.start_socket.node),
                        'start_socket': item.start_socket.index,
                        'end_node': id(item.end_socket.node),
                        'end_socket': item.end_socket.index
                    }
                    data['connections'].append(connection_data)
        
        return data
    
    def _deserialize_scene(self, scene, data):
        """Deserialize scene data from JSON"""
        # Clear current scene
        scene.clear()
        
        # Dictionary to store nodes by their id for connection reconstruction
        nodes = {}
        node_sockets = {}
        
        # Create nodes
        for node_data in data['nodes']:
            node_type = node_data['type']
            
            # Create node
            node = NodeFactory.create_node(scene, node_type)
            node.setPos(node_data['pos_x'], node_data['pos_y'])
            
            # Restore properties if available
            if 'properties' in node_data and hasattr(node, 'set_properties'):
                node.set_properties(node_data['properties'])
            
            # Store node and socket references
            nodes[node_data['id']] = node
            
            # Store socket references
            for i, socket_data in enumerate(node_data['inputs']):
                if i < len(node.input_sockets):
                    node_sockets[socket_data['id']] = node.input_sockets[i]
                    node.input_sockets[i].value = socket_data['value']
            
            for i, socket_data in enumerate(node_data['outputs']):
                if i < len(node.output_sockets):
                    node_sockets[socket_data['id']] = node.output_sockets[i]
                    node.output_sockets[i].value = socket_data['value']
        
        # Create connections
        for conn_data in data['connections']:
            if (conn_data['start_node'] in nodes and conn_data['end_node'] in nodes):
                start_node = nodes[conn_data['start_node']]
                end_node = nodes[conn_data['end_node']]
                
                if (conn_data['start_socket'] < len(start_node.output_sockets) and 
                    conn_data['end_socket'] < len(end_node.input_sockets)):
                    
                    start_socket = start_node.output_sockets[conn_data['start_socket']]
                    end_socket = end_node.input_sockets[conn_data['end_socket']]
                    
                    # Create connection
                    conn = Connection(scene, start_socket=start_socket, end_socket=end_socket)
        
        # Update all nodes (propagate values)
        for node in nodes.values():
            if hasattr(node, 'calculate_output'):
                node.calculate_output()
    
    def _undo(self):
        """Undo the last operation"""
        editor = self._get_current_editor()
        if editor and hasattr(self.operations, 'undo'):
            self.operations.undo()
    
    def _redo(self):
        """Redo the last undone operation"""
        editor = self._get_current_editor()
        if editor and hasattr(self.operations, 'redo'):
            self.operations.redo()
    
    def _cut(self):
        """Cut selected nodes"""
        editor = self._get_current_editor()
        if editor and hasattr(self.operations, 'cut'):
            self.operations.cut()
    
    def _copy(self):
        """Copy selected nodes"""
        editor = self._get_current_editor()
        if editor and hasattr(self.operations, 'copy'):
            self.operations.copy()
    
    def _paste(self):
        """Paste copied nodes"""
        editor = self._get_current_editor()
        if editor and hasattr(self.operations, 'paste'):
            self.operations.paste()
    
    def _delete(self):
        """Delete selected nodes"""
        editor = self._get_current_editor()
        if editor and hasattr(self.operations, 'delete'):
            self.operations.delete()
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Check for unsaved changes
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self._save_current_tab()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        event.accept()
    
    def _has_unsaved_changes(self):
        """Check if there are any unsaved changes"""
        # In a real implementation, this would check for actual changes
        # For now, we'll assume tabs without saved paths have unsaved changes
        for tab_index in range(self.tab_widget.count()):
            if self.tab_file_paths.get(tab_index) is None:
                return True
        return False
    
    def tabCloseRequested(self, index):
        """Handle tab close request"""
        # Check for unsaved changes
        if self.tab_file_paths.get(index) is None:
            reply = QMessageBox.question(
                self,
                "Unsaved Tab",
                f"Tab '{self.tab_widget.tabText(index)}' has unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.tab_widget.setCurrentIndex(index)
                self._save_current_tab()
            elif reply == QMessageBox.Cancel:
                return
        
        # Close the tab
        self.tab_widget.removeTab(index)
        
        # Clean up file path reference
        if index in self.tab_file_paths:
            del self.tab_file_paths[index]
            
        # Update remaining tab indices in the file paths dictionary
        updated_paths = {}
        for old_index, path in self.tab_file_paths.items():
            new_index = old_index if old_index < index else old_index - 1
            updated_paths[new_index] = path
        self.tab_file_paths = updated_paths