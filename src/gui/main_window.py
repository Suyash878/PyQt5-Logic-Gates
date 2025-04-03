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
        
        
        self._setup_ui()
        self._setup_actions()
        self._setup_menus()
        
       
        self.operations = NodeOperations(self)
        
        
        self._apply_current_theme()
        
    def _setup_ui(self):
        """Set up the user interface"""
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        
        self._create_new_tab()
        
        
        self._setup_side_panel()
        
    def _setup_side_panel(self):
        """Set up the side panel with nodes"""
        
        self.side_panel_dock = QDockWidget("Nodes", self)
        self.side_panel_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        
        self.side_panel = SidePanel()
        self.side_panel_dock.setWidget(self.side_panel)
        
       
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_panel_dock)
        
    def _setup_actions(self):
        """Set up actions for menus"""
        
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
        
        
        self.action_toggle_theme = QAction("Toggle Light/Dark Mode", self)
        self.action_toggle_theme.setShortcut("Ctrl+T")
        
        
        self.action_new.triggered.connect(self._create_new_tab)
        self.action_save.triggered.connect(self._save_current_tab)
        self.action_save_as.triggered.connect(self._save_as_current_tab)
        self.action_open.triggered.connect(self._open_file)
        self.action_exit.triggered.connect(self.close)
        self.action_toggle_theme.triggered.connect(self._toggle_theme)
        
        
        self.action_undo.triggered.connect(self._undo)
        self.action_redo.triggered.connect(self._redo)
        self.action_cut.triggered.connect(self._cut)
        self.action_copy.triggered.connect(self._copy)
        self.action_paste.triggered.connect(self._paste)
        self.action_delete.triggered.connect(self._delete)
        
    def _setup_menus(self):
        """Set up the menu bars"""
        
        self.menu_bar = self.menuBar()
        
        
        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)
        
        
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addAction(self.action_delete)
        
        
        self.view_menu = self.menu_bar.addMenu("View")
        self.view_menu.addAction(self.action_toggle_theme)
        
    def _apply_current_theme(self):
        """Apply the current theme saved in settings"""
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        theme = ThemeManager.get_current_theme()
        ThemeManager.apply_theme(app, theme)
        
        
        theme_text = "Light Mode" if theme == ThemeManager.LIGHT_THEME else "Dark Mode"
        self.action_toggle_theme.setText(f"Toggle Theme (Current: {theme_text})")
        
        
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if hasattr(editor, 'update_theme'):
                editor.update_theme()
    
    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        new_theme = ThemeManager.toggle_theme(app)
        
       
        theme_text = "Light Mode" if new_theme == ThemeManager.LIGHT_THEME else "Dark Mode"
        self.action_toggle_theme.setText(f"Toggle Theme (Current: {theme_text})")
        
        
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if hasattr(editor, 'update_theme'):
                editor.update_theme()
        
        
        self.statusBar().showMessage(f"Theme changed to {theme_text}", 3000)
        
    def _create_new_tab(self):
        """Create a new tab with node editor"""
        editor = NodeEditorView()
        
        
        editor.setAcceptDrops(True)
        
        
        tab_index = self.tab_widget.addTab(editor, f"Untitled {self.tab_widget.count() + 1}")
        
       
        self.tab_widget.setCurrentIndex(tab_index)
        
        
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
            return 
            
        
        file_path = self.tab_file_paths.get(current_tab)
        if file_path:
            self._save_to_file(file_path)
        else:
            self._save_as_current_tab()
    
    def _save_as_current_tab(self):
        """Save the current tab with a new file name"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == -1:
            return  
            
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Circuit", 
            "", 
            "Logic Gate Simulator Files (*.lgs);;All Files (*)"
        )
        
        if file_path:
           
            if not file_path.endswith('.lgs'):
                file_path += '.lgs'
                
            
            if self._save_to_file(file_path):
                
                file_name = os.path.basename(file_path)
                self.tab_widget.setTabText(current_tab, file_name)
                
               
                self.tab_file_paths[current_tab] = file_path
    
    def _save_to_file(self, file_path):
        """Save editor content to file"""
        editor = self._get_current_editor()
        if not editor:
            return False
            
        try:
         
            scene_data = self._serialize_scene(editor.scene)
            
           
            with open(file_path, 'w') as file:
                json.dump(scene_data, file, indent=4)
                
           
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
            
            self._create_new_tab()
            current_tab = self.tab_widget.currentIndex()
            
           
            self._load_from_file(file_path)
            
            
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
                
               
                for socket in item.input_sockets:
                    socket_data = {
                        'id': id(socket),
                        'index': socket.index,
                        'value': socket.value
                    }
                    node_data['inputs'].append(socket_data)
                
               
                for socket in item.output_sockets:
                    socket_data = {
                        'id': id(socket),
                        'index': socket.index,
                        'value': socket.value
                    }
                    node_data['outputs'].append(socket_data)
                
                data['nodes'].append(node_data)
        
      
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
       
        scene.clear()
        
    
        nodes = {}
        node_sockets = {}
        
     
        for node_data in data['nodes']:
            node_type = node_data['type']
            
            
            node = NodeFactory.create_node(scene, node_type)
            node.setPos(node_data['pos_x'], node_data['pos_y'])
            
         
            if 'properties' in node_data and hasattr(node, 'set_properties'):
                node.set_properties(node_data['properties'])
            
           
            nodes[node_data['id']] = node
            
            
            for i, socket_data in enumerate(node_data['inputs']):
                if i < len(node.input_sockets):
                    node_sockets[socket_data['id']] = node.input_sockets[i]
                    node.input_sockets[i].value = socket_data['value']
            
            for i, socket_data in enumerate(node_data['outputs']):
                if i < len(node.output_sockets):
                    node_sockets[socket_data['id']] = node.output_sockets[i]
                    node.output_sockets[i].value = socket_data['value']
        
       
        for conn_data in data['connections']:
            if (conn_data['start_node'] in nodes and conn_data['end_node'] in nodes):
                start_node = nodes[conn_data['start_node']]
                end_node = nodes[conn_data['end_node']]
                
                if (conn_data['start_socket'] < len(start_node.output_sockets) and 
                    conn_data['end_socket'] < len(end_node.input_sockets)):
                    
                    start_socket = start_node.output_sockets[conn_data['start_socket']]
                    end_socket = end_node.input_sockets[conn_data['end_socket']]
                    
                   
                    conn = Connection(scene, start_socket=start_socket, end_socket=end_socket)
        
        
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
        
        for tab_index in range(self.tab_widget.count()):
            if self.tab_file_paths.get(tab_index) is None:
                return True
        return False
    
    def tabCloseRequested(self, index):
        """Handle tab close request"""
        
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
        
        self.tab_widget.removeTab(index)
        
        if index in self.tab_file_paths:
            del self.tab_file_paths[index]
            
        updated_paths = {}
        for old_index, path in self.tab_file_paths.items():
            new_index = old_index if old_index < index else old_index - 1
            updated_paths[new_index] = path
        self.tab_file_paths = updated_paths