from PyQt5.QtGui import QPalette, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication

class ThemeManager:
    """Manages application themes including light and dark modes"""
    
   
    LIGHT_THEME = "light"
    DARK_THEME = "dark"
    
   
    THEMES = {
        LIGHT_THEME: {
           
            "window": QColor(240, 240, 240),
            "window_text": QColor(0, 0, 0),
            "base": QColor(255, 255, 255),
            "alternate_base": QColor(233, 233, 233),
            "text": QColor(0, 0, 0),
            "button": QColor(240, 240, 240),
            "button_text": QColor(0, 0, 0),
            "bright_text": QColor(255, 0, 0),
            "highlight": QColor(42, 130, 218),
            "highlight_text": QColor(255, 255, 255),
            "link": QColor(0, 0, 255),
            "link_visited": QColor(128, 0, 128),
            
            
            "grid_line": QColor(200, 200, 200, 100),
            "grid_bg": QColor(255, 255, 255),
            "node_bg": QColor(240, 240, 240),
            "node_border": QColor(0, 0, 0),
            "node_title_bg": QColor(230, 230, 230),
            "node_title_text": QColor(0, 0, 0),
            "socket_border": QColor(0, 0, 0),
            "socket_bg": QColor(200, 200, 200),
            "socket_highlight": QColor(42, 130, 218),
            "connection_line": QColor(100, 100, 100),
            "selection_box": QColor(42, 130, 218, 100),
            "selection_border": QColor(42, 130, 218),
            
            
            "socket_input_color": QColor(255, 100, 100),
            "socket_output_color": QColor(100, 255, 100),
            
        
            "connection_valid": QColor(100, 255, 100),
            "connection_invalid": QColor(255, 100, 100),
            "connection_default": QColor(200, 200, 200),
        },
        
        DARK_THEME: {
           
            "window": QColor(45, 45, 45),
            "window_text": QColor(212, 212, 212),
            "base": QColor(30, 30, 30),
            "alternate_base": QColor(45, 45, 45),
            "text": QColor(212, 212, 212),
            "button": QColor(53, 53, 53),
            "button_text": QColor(212, 212, 212),
            "bright_text": QColor(255, 0, 0),
            "highlight": QColor(42, 130, 218),
            "highlight_text": QColor(255, 255, 255),
            "link": QColor(100, 160, 255),
            "link_visited": QColor(180, 120, 220),
            
           
            "grid_line": QColor(60, 60, 60, 100),
            "grid_bg": QColor(30, 30, 30),
            "node_bg": QColor(53, 53, 53),
            "node_border": QColor(90, 90, 90),
            "node_title_bg": QColor(45, 45, 45),
            "node_title_text": QColor(212, 212, 212),
            "socket_border": QColor(90, 90, 90),
            "socket_bg": QColor(70, 70, 70),
            "socket_highlight": QColor(42, 130, 218),
            "connection_line": QColor(180, 180, 180),
            "selection_box": QColor(42, 130, 218, 80),
            "selection_border": QColor(42, 130, 218),
       
            "socket_input_color": QColor(255, 100, 100),
            "socket_output_color": QColor(100, 255, 100),
            
       
            "connection_valid": QColor(100, 255, 100),
            "connection_invalid": QColor(255, 100, 100),
            "connection_default": QColor(180, 180, 180),
        }
    }
    
    @classmethod
    def get_theme_color(cls, theme_name, color_key):
        """Get a specific color from the theme"""
        if theme_name in cls.THEMES and color_key in cls.THEMES[theme_name]:
            return cls.THEMES[theme_name][color_key]
        return QColor(0, 0, 0)  
    
    @classmethod
    def apply_theme(cls, app, theme_name):
        """Apply the selected theme to the application"""
        if theme_name not in cls.THEMES:
            theme_name = cls.DARK_THEME  
        
        theme = cls.THEMES[theme_name]
        
   
        palette = QPalette()
        

        palette.setColor(QPalette.Window, theme["window"])
        palette.setColor(QPalette.WindowText, theme["window_text"])
        palette.setColor(QPalette.Base, theme["base"])
        palette.setColor(QPalette.AlternateBase, theme["alternate_base"])
        palette.setColor(QPalette.Text, theme["text"])
        palette.setColor(QPalette.Button, theme["button"])
        palette.setColor(QPalette.ButtonText, theme["button_text"])
        palette.setColor(QPalette.BrightText, theme["bright_text"])
        palette.setColor(QPalette.Highlight, theme["highlight"])
        palette.setColor(QPalette.HighlightedText, theme["highlight_text"])
        palette.setColor(QPalette.Link, theme["link"])
        palette.setColor(QPalette.LinkVisited, theme["link_visited"])
        

        app.setPalette(palette)
        

        settings = QSettings("LogicGateSimulator", "preferences")
        settings.setValue("theme", theme_name)
        settings.sync()
        

        return theme_name
    
    @classmethod
    def get_current_theme(cls):
        """Get the currently applied theme name from settings"""
        settings = QSettings("LogicGateSimulator", "preferences")
        return settings.value("theme", cls.LIGHT_THEME)
    
    @classmethod
    def toggle_theme(cls, app):
        """Toggle between light and dark themes"""
        current_theme = cls.get_current_theme()
        new_theme = cls.DARK_THEME if current_theme == cls.LIGHT_THEME else cls.LIGHT_THEME
        return cls.apply_theme(app, new_theme)
    
    @classmethod
    def get_grid_pen(cls, theme_name=None):
        """Get pen for drawing the grid"""
        if theme_name is None:
            theme_name = cls.get_current_theme()
        
        grid_pen = QPen(cls.get_theme_color(theme_name, "grid_line"))
        grid_pen.setWidth(1)
        return grid_pen
    
    @classmethod
    def get_node_colors(cls, theme_name=None):
        """Get colors for drawing nodes"""
        if theme_name is None:
            theme_name = cls.get_current_theme()
        
        return {
            "bg": cls.get_theme_color(theme_name, "node_bg"),
            "border": cls.get_theme_color(theme_name, "node_border"),
            "title_bg": cls.get_theme_color(theme_name, "node_title_bg"),
            "title_text": cls.get_theme_color(theme_name, "node_title_text"),
        }
    
    @classmethod
    def get_socket_colors(cls, socket_type, theme_name=None):
        """Get colors for drawing sockets based on their type"""
        if theme_name is None:
            theme_name = cls.get_current_theme()
     
        from src.nodes.base_nodes import Socket
        if socket_type == Socket.TYPE_INPUT:
            socket_color = cls.get_theme_color(theme_name, "socket_input_color")
        else: 
            socket_color = cls.get_theme_color(theme_name, "socket_output_color")
        
        return {
            "bg": socket_color,
            "border": cls.get_theme_color(theme_name, "socket_border"),
            "highlight": cls.get_theme_color(theme_name, "socket_highlight"),
        }
    
    @classmethod
    def get_connection_pen(cls, state="default", theme_name=None):
        """Get pen for drawing connections"""
        if theme_name is None:
            theme_name = cls.get_current_theme()
        
 
        if state == "valid":
            color = cls.get_theme_color(theme_name, "connection_valid")
        elif state == "invalid":
            color = cls.get_theme_color(theme_name, "connection_invalid")
        else: 
            color = cls.get_theme_color(theme_name, "connection_default")
        
        pen = QPen(color)
        pen.setWidth(2)
        return pen
    
    @classmethod
    def get_selection_brush(cls, theme_name=None):
        """Get brush for selection box"""
        if theme_name is None:
            theme_name = cls.get_current_theme()
        
        return QBrush(cls.get_theme_color(theme_name, "selection_box"))
    
    @classmethod
    def get_selection_pen(cls, theme_name=None):
        """Get pen for selection box border"""
        if theme_name is None:
            theme_name = cls.get_current_theme()
        
        pen = QPen(cls.get_theme_color(theme_name, "selection_border"))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        return pen