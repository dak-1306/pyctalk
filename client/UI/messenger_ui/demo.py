#!/usr/bin/env python3
"""
PycTalk Messenger UI Demo
Demonstrates the modular messenger components and integration options
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.messenger_ui import MessengerMainWindow, FriendListWindow, ChatWindow, MessageBubble
from UI.messenger_ui.integration_helper import MessengerIntegration


class MessengerDemo(QMainWindow):
    """Demo application showing all messenger components"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup demo UI"""
        self.setWindowTitle("🚀 PycTalk Messenger UI Demo - Modular Components")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🚀 PycTalk Messenger UI - Modular Architecture Demo")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Demo buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Standalone messenger button
        btn_standalone = QPushButton("💬 Standalone Messenger Window")
        btn_standalone.setMinimumHeight(50)
        btn_standalone.setStyleSheet(self._get_button_style("#3498db"))
        btn_standalone.clicked.connect(self.show_standalone_messenger)
        buttons_layout.addWidget(btn_standalone)
        
        # Friend list only button
        btn_friends = QPushButton("👥 Friend List Component")
        btn_friends.setMinimumHeight(50)
        btn_friends.setStyleSheet(self._get_button_style("#2ecc71"))
        btn_friends.clicked.connect(self.show_friend_list)
        buttons_layout.addWidget(btn_friends)
        
        # Chat window only button
        btn_chat = QPushButton("💭 Chat Window Component")
        btn_chat.setMinimumHeight(50)
        btn_chat.setStyleSheet(self._get_button_style("#e74c3c"))
        btn_chat.clicked.connect(self.show_chat_window)
        buttons_layout.addWidget(btn_chat)
        
        # Integration demo button
        btn_integration = QPushButton("🔧 Integration Demo")
        btn_integration.setMinimumHeight(50)
        btn_integration.setStyleSheet(self._get_button_style("#9b59b6"))
        btn_integration.clicked.connect(self.show_integration_demo)
        buttons_layout.addWidget(btn_integration)
        
        layout.addLayout(buttons_layout)
        
        # Features description
        self._create_features_section(layout)
        
        # Architecture description
        self._create_architecture_section(layout)
        
        # Apply main styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
    
    def _get_button_style(self, color):
        """Get button style with specified color"""
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 20px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color)};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color, 0.8)};
                transform: translateY(0px);
            }}
        """
    
    def _darken_color(self, color, factor=0.9):
        """Darken color for hover effects"""
        # Simple darkening - in real app you'd use proper color manipulation
        color_map = {
            "#3498db": "#2980b9",
            "#2ecc71": "#27ae60", 
            "#e74c3c": "#c0392b",
            "#9b59b6": "#8e44ad"
        }
        return color_map.get(color, color)
    
    def _create_features_section(self, layout):
        """Create features description section"""
        features_widget = QWidget()
        features_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                border: 1px solid #dee2e6;
            }
        """)
        
        features_layout = QVBoxLayout(features_widget)
        
        features_title = QLabel("✨ Modular Features")
        features_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        features_layout.addWidget(features_title)
        
        features_text = QLabel("""
🏗️ <b>Modular Architecture</b> - Separate components for easy integration
💬 <b>MessageBubble Widget</b> - Reusable message bubble component
👥 <b>FriendListWindow</b> - Standalone friend list with search functionality  
🗨️ <b>ChatWindow Widget</b> - Complete chat interface with header and input
🚀 <b>MessengerMainWindow</b> - Full messenger application
🔧 <b>Integration Helper</b> - Easy integration with existing UI
📱 <b>Responsive Design</b> - Modern, mobile-inspired interface
💾 <b>Database Ready</b> - Built-in database integration support
🎨 <b>Beautiful Styling</b> - Facebook Messenger-inspired design
⚡ <b>Real-time Ready</b> - Signal-slot architecture for live updates
        """)
        features_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                line-height: 1.8;
                color: #495057;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }
        """)
        features_layout.addWidget(features_text)
        
        layout.addWidget(features_widget)
    
    def _create_architecture_section(self, layout):
        """Create architecture description section"""
        arch_widget = QWidget()
        arch_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                border: 1px solid #dee2e6;
            }
        """)
        
        arch_layout = QVBoxLayout(arch_widget)
        
        arch_title = QLabel("🏗️ Modular Architecture")
        arch_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        arch_layout.addWidget(arch_title)
        
        arch_text = QLabel("""
<b>UI/messenger_ui/</b> - Modular messenger components
├── <b>__init__.py</b> - Package initialization and exports
├── <b>message_bubble_widget.py</b> - MessageBubble component
├── <b>chat_list_item_widget.py</b> - ChatListItem component  
├── <b>friend_list_window.py</b> - FriendListWindow component
├── <b>chat_window_widget.py</b> - ChatWindow component
├── <b>messenger_main_window.py</b> - MessengerMainWindow main app
└── <b>integration_helper.py</b> - Integration utilities

<b>Integration Options:</b>
• <b>Sidebar Integration</b> - Add messenger tab to existing sidebar
• <b>Main Content Replacement</b> - Replace main content with chat  
• <b>Standalone Window</b> - Open messenger in separate window
• <b>Embedded Widget</b> - Embed components in existing layouts
        """)
        arch_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                line-height: 1.6;
                color: #495057;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2ecc71;
                font-family: 'Courier New', monospace;
            }
        """)
        arch_layout.addWidget(arch_text)
        
        layout.addWidget(arch_widget)
        
        # Footer
        footer = QLabel("🎯 PycTalk Modular Messenger v2.0 - Ready for Integration!")
        footer.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                text-align: center;
                margin-top: 20px;
                padding: 10px;
            }
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
    
    def show_standalone_messenger(self):
        """Show standalone messenger window"""
        self.messenger = MessengerMainWindow("Demo User")
        self.messenger.show()
        self.messenger.raise_()
        self.messenger.activateWindow()
        print("✅ Opened standalone messenger window")
    
    def show_friend_list(self):
        """Show friend list component"""
        self.friend_list = FriendListWindow("Demo User")
        self.friend_list.resize(400, 600)
        self.friend_list.show()
        self.friend_list.raise_()
        self.friend_list.activateWindow()
        print("✅ Opened friend list component")
    
    def show_chat_window(self):
        """Show chat window component"""
        sample_chat_data = {
            'friend_id': 2,
            'friend_name': 'Demo Friend',
            'current_user_id': 1,
            'current_username': 'Demo User'
        }
        
        self.chat_window = ChatWindow(sample_chat_data)
        self.chat_window.resize(500, 700)
        self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()
        print("✅ Opened chat window component")
    
    def show_integration_demo(self):
        """Show integration demo"""
        from PyQt6.QtWidgets import QDialog, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔧 Integration Code Examples")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        code_examples = QTextEdit()
        code_examples.setPlainText("""
# Example 1: Integrate into existing sidebar
from UI.messenger_ui.integration_helper import MessengerIntegration

def setup_messenger_in_sidebar(sidebar_widget, client, user_id, username):
    friend_list = MessengerIntegration.integrate_messenger_into_sidebar(
        sidebar_widget, client, user_id, username
    )
    friend_list.friend_selected.connect(on_friend_selected)
    return friend_list

# Example 2: Replace main content with chat
def open_chat_in_main_area(main_layout, chat_data, client, user_id, username):
    chat_window = MessengerIntegration.replace_main_content_with_chat(
        main_layout, chat_data, client, user_id, username
    )
    chat_window.back_clicked.connect(restore_main_content)
    return chat_window

# Example 3: Embed messenger widget
def embed_messenger(parent_widget, client, user_id, username):
    messenger = MessengerIntegration.create_embedded_messenger_widget(
        parent_widget, client, user_id, username
    )
    return messenger

# Example 4: Use individual components
from UI.messenger_ui import MessageBubble, ChatListItem, ChatWindow

def create_custom_chat():
    # Create individual components
    message_bubble = MessageBubble("Hello!", is_sent=True)
    chat_item = ChatListItem({'friend_name': 'Alice', 'last_message': 'Hi!'})
    
    # Create chat window
    chat_data = {'friend_id': 1, 'friend_name': 'Alice'}
    chat_window = ChatWindow(chat_data)
    
    return message_bubble, chat_item, chat_window

# Example 5: Integration with existing UI main window
from UI.messenger_ui.integration_helper import integrate_messenger_into_ui_main_window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup existing UI
        self.ui = Ui_MainWindow(username, client, self)
        self.ui.setupUi(self)
        
        # Integrate messenger
        self.messenger_integration = integrate_messenger_into_ui_main_window(
            self.ui, client, user_id, username
        )
""")
        
        code_examples.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #2d3748;
                color: #e2e8f0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout.addWidget(code_examples)
        dialog.exec()
        print("✅ Showed integration code examples")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Create and show demo
    demo = MessengerDemo()
    demo.show()
    
    print("🚀 PycTalk Messenger UI Demo - Modular Architecture")
    print("=" * 60)
    print("✅ Modular components created successfully!")
    print("✅ Integration helpers available")
    print("✅ Demo interface ready")
    print("=" * 60)
    print("Components available:")
    print("  • MessageBubble - Individual message widget")
    print("  • ChatListItem - Friend list item widget") 
    print("  • FriendListWindow - Complete friend list")
    print("  • ChatWindow - Complete chat interface")
    print("  • MessengerMainWindow - Full messenger app")
    print("  • Integration helpers for existing UI")
    print("=" * 60)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
