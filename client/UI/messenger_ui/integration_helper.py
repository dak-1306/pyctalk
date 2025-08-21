"""
Integration guide for PycTalk Messenger UI components
This file shows how to integrate messenger components with the existing UI architecture
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from UI.messenger_ui import MessengerMainWindow, FriendListWindow, ChatWindow


class MessengerIntegration:
    """Helper class to integrate messenger components into existing UI"""
    
    @staticmethod
    def integrate_messenger_into_sidebar(sidebar_widget, client=None, user_id=None, username=None):
        """
        Integrate friend list into existing sidebar
        
        Args:
            sidebar_widget: Existing SidebarWidget instance
            client: Client connection object
            user_id: Current user ID
            username: Current username
        """
        # Create messenger tab
        messenger_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(messenger_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create friend list widget
        friend_list = FriendListWindow(username or "Guest")
        
        # Remove the header since sidebar already has one
        friend_list_content = friend_list.findChild(QtWidgets.QScrollArea)
        if friend_list_content:
            tab_layout.addWidget(friend_list_content)
        else:
            tab_layout.addWidget(friend_list)
        
        # Add to sidebar tabs
        if hasattr(sidebar_widget, 'tabWidget'):
            sidebar_widget.tabWidget.addTab(messenger_tab, "💬 Tin nhắn")
        
        return friend_list
    
    @staticmethod
    def create_embedded_messenger_widget(parent, client=None, user_id=None, username=None):
        """
        Create embedded messenger widget for main content area
        
        Args:
            parent: Parent widget
            client: Client connection object
            user_id: Current user ID
            username: Current username
        
        Returns:
            MessengerMainWindow: Configured messenger widget
        """
        messenger = MessengerMainWindow(username or "Guest", parent)
        
        # Configure for embedding
        messenger.setWindowFlags(QtCore.Qt.WindowType.Widget)
        
        return messenger
    
    @staticmethod
    def replace_main_content_with_chat(main_layout, chat_data, client=None, user_id=None, username=None):
        """
        Replace main content area with chat window
        
        Args:
            main_layout: Main layout to replace content in
            chat_data: Chat data dictionary
            client: Client connection object
            user_id: Current user ID
            username: Current username
        
        Returns:
            ChatWindow: Created chat window
        """
        # Clear existing content (keep topbar)
        widgets_to_remove = []
        for i in range(main_layout.count()):
            widget = main_layout.itemAt(i).widget()
            if widget and getattr(widget, 'objectName', lambda: None)() != "topbar":
                widgets_to_remove.append(widget)
        
        for widget in widgets_to_remove:
            main_layout.removeWidget(widget)
            widget.hide()
            widget.deleteLater()
        
        # Add chat window
        chat_data['current_user_id'] = user_id
        chat_data['current_username'] = username
        
        chat_window = ChatWindow(chat_data)
        main_layout.addWidget(chat_window, 1)
        
        return chat_window


# Example integration with existing UI structure
class IntegratedMessengerUI:
    """Example of integrated messenger UI with existing components"""
    
    def __init__(self, main_window, client=None, user_id=None, username=None):
        self.main_window = main_window
        self.client = client
        self.user_id = user_id
        self.username = username
        self.current_chat_window = None
        
    def setup_messenger_integration(self, ui_main_window):
        """
        Setup messenger integration with existing Ui_MainWindow
        
        Args:
            ui_main_window: Instance of Ui_MainWindow
        """
        # Method 1: Add messenger tab to existing sidebar
        if hasattr(ui_main_window, 'sidebar'):
            friend_list = MessengerIntegration.integrate_messenger_into_sidebar(
                ui_main_window.sidebar,
                self.client,
                self.user_id,
                self.username
            )
            
            # Connect friend selection to main content replacement
            friend_list.friend_selected.connect(self._on_friend_selected_for_main_content)
        
        # Method 2: Add messenger button to existing sidebar actions
        if hasattr(ui_main_window, 'sidebar') and hasattr(ui_main_window.sidebar, 'btnGroupChat'):
            # Create messenger button
            btn_messenger = QtWidgets.QPushButton("💬 Messenger")
            btn_messenger.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn_messenger.clicked.connect(self._open_standalone_messenger)
            
            # Add to sidebar actions (find the actions layout)
            actions_layout = self._find_actions_layout(ui_main_window.sidebar)
            if actions_layout:
                actions_layout.insertWidget(-1, btn_messenger)  # Insert before settings
    
    def _on_friend_selected_for_main_content(self, chat_data):
        """Handle friend selection to replace main content with chat"""
        if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'main_layout'):
            self.current_chat_window = MessengerIntegration.replace_main_content_with_chat(
                self.main_window.ui.main_layout,
                chat_data,
                self.client,
                self.user_id,
                self.username
            )
            
            # Connect back button to restore main content
            self.current_chat_window.back_clicked.connect(self._restore_main_content)
    
    def _restore_main_content(self):
        """Restore original main content"""
        if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, '_setup_main_card'):
            # Remove chat window
            if self.current_chat_window:
                self.main_window.ui.main_layout.removeWidget(self.current_chat_window)
                self.current_chat_window.deleteLater()
                self.current_chat_window = None
            
            # Restore main card
            self.main_window.ui._setup_main_card()
    
    def _open_standalone_messenger(self):
        """Open messenger in standalone window"""
        self.messenger_window = MessengerMainWindow(self.username)
        self.messenger_window.show()
        self.messenger_window.raise_()
        self.messenger_window.activateWindow()
    
    def _find_actions_layout(self, sidebar_widget):
        """Find actions layout in sidebar"""
        # This would need to be adapted based on actual sidebar structure
        actions_frame = sidebar_widget.findChild(QtWidgets.QFrame, "actions_frame")
        if actions_frame:
            return actions_frame.layout()
        return None


# Usage example in ui_main_window.py
def integrate_messenger_into_ui_main_window(ui_main_window_instance, client=None, user_id=None, username=None):
    """
    Function to integrate messenger into existing Ui_MainWindow
    Call this after setupUi() is complete
    
    Example usage in main window:
    
    self.ui = Ui_MainWindow(username, client, self)
    self.ui.setupUi(self)
    
    # Integrate messenger
    integrate_messenger_into_ui_main_window(self.ui, client, user_id, username)
    """
    messenger_integration = IntegratedMessengerUI(
        ui_main_window_instance.main_window,
        client,
        user_id,
        username
    )
    
    messenger_integration.setup_messenger_integration(ui_main_window_instance)
    
    return messenger_integration
