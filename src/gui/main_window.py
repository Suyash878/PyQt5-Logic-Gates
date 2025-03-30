from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QDockWidget, 
                            QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import Qt
from src.gui.node_editor import NodeEditorView
from src.gui.side_panel import SidePanel
from src.nodes.node_factory import NodeFactory

class MainWindow(QMainWindow):
    """Main window for the logic gate simulator"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Logic Gate Simulator")
        self.resize(1200, 800)
        
        # Initialize UI
        self._setup_ui()
        self._setup_actions()
        self._setup_menus()
        
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
        self.action_open = QAction("Open", self)
        self.action_save = QAction("Save", self)
        self.action_exit = QAction("Exit", self)
        
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