# Complete Messenger UI Demo with Database Integration
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from UI.chatUI_clean import Ui_ChatWindow, MessageBubble
    from Chat1_1.database_chat_window import DatabaseChatWindow
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Import error: {e}")
    DatabaseChatWindow = None
    MessengerDatabase = None

class MessengerDemo(QMainWindow):
    """Complete demo of Messenger-style UI with database"""
    
    def __init__(self):
        super().__init__()
        self.current_user_id = 1
        self.current_username = "Nguyễn Văn A"
        
        # Test database connection
        if MessengerDatabase:
            try:
                self.messenger_db = MessengerDatabase()
                self.db_status = "✅ Database Connected"
            except Exception as e:
                self.messenger_db = None
                self.db_status = f"❌ DB Error: {str(e)}"
        else:
            self.messenger_db = None
            self.db_status = "❌ No Database Module"
        
        self.setup_ui()
        self.load_demo_data()
    
    def setup_ui(self):
        """Setup main demo UI"""
        self.setWindowTitle("🎯 PycTalk Messenger Demo - Facebook Style")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title with gradient background
        title_widget = QWidget()
        title_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        title_layout = QVBoxLayout(title_widget)
        
        main_title = QLabel("🚀 PycTalk Messenger Demo")
        main_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                text-align: center;
            }
        """)
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Facebook Messenger-style UI with Database Integration")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.9);
                font-size: 16px;
                text-align: center;
                margin-top: 5px;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_widget)
        
        # Status info
        status_widget = QWidget()
        status_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        status_layout = QHBoxLayout(status_widget)
        
        user_info = QLabel(f"👤 Current User: {self.current_username} (ID: {self.current_user_id})")
        user_info.setStyleSheet("font-size: 14px; font-weight: 500; color: #495057;")
        
        db_info = QLabel(f"🗄️ {self.db_status}")
        db_info.setStyleSheet("font-size: 14px; font-weight: 500; color: #495057;")
        
        status_layout.addWidget(user_info)
        status_layout.addStretch()
        status_layout.addWidget(db_info)
        
        layout.addWidget(status_widget)
        
        # Demo buttons
        demos_widget = QWidget()
        demos_layout = QVBoxLayout(demos_widget)
        
        demos_title = QLabel("🎮 Choose Demo Mode:")
        demos_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        demos_layout.addWidget(demos_title)
        
        # Buttons grid
        buttons_layout = QHBoxLayout()
        
        # UI Only Demo
        btn_ui_demo = QPushButton("🎨 UI Demo\n(Design Only)")
        btn_ui_demo.setFixedSize(200, 100)
        btn_ui_demo.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
        """)
        btn_ui_demo.clicked.connect(self.open_ui_demo)
        
        # Database Demo
        btn_db_demo = QPushButton("💾 Database Demo\n(Real Chat)")
        btn_db_demo.setFixedSize(200, 100)
        btn_db_demo.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff7eb3, stop:1 #ff758c);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6ba0, stop:1 #ff6579);
            }
        """)
        btn_db_demo.clicked.connect(self.open_db_demo)
        btn_db_demo.setEnabled(self.messenger_db is not None)
        
        # Full Featured Demo
        btn_full_demo = QPushButton("⭐ Full Demo\n(All Features)")
        btn_full_demo.setFixedSize(200, 100)
        btn_full_demo.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffecd2, stop:1 #fcb69f);
                color: #2c3e50;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fde2c7, stop:1 #fbab94);
            }
        """)
        btn_full_demo.clicked.connect(self.open_full_demo)
        
        buttons_layout.addWidget(btn_ui_demo)
        buttons_layout.addWidget(btn_db_demo)
        buttons_layout.addWidget(btn_full_demo)
        
        demos_layout.addLayout(buttons_layout)
        layout.addWidget(demos_widget)
        
        # Features list
        features_widget = QWidget()
        features_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        features_layout = QVBoxLayout(features_widget)
        
        features_title = QLabel("✨ Features Implemented:")
        features_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        features_layout.addWidget(features_title)
        
        features_text = QLabel("""
✅ Facebook Messenger-style gradient header
✅ Avatar with gradient background
✅ Message bubbles with proper styling
✅ Real-time database integration
✅ Auto-scroll and message history
✅ Modern input area with emoji button
✅ Call/Video/Info action buttons
✅ Responsive design and animations
✅ Send button enable/disable logic
✅ Professional UI/UX design
        """)
        features_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                line-height: 1.6;
                color: #495057;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
            }
        """)
        features_layout.addWidget(features_text)
        
        layout.addWidget(features_widget)
        
        # Footer
        footer = QLabel("🎯 PycTalk v2.0 - Made with ❤️ using PyQt6")
        footer.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                text-align: center;
                margin-top: 20px;
            }
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
    
    def load_demo_data(self):
        """Load demo data if database available"""
        if self.messenger_db:
            try:
                # Create sample data for demo
                self.messenger_db.create_sample_data()
                print("✅ Demo data loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load demo data: {e}")
    
    def open_ui_demo(self):
        """Open UI-only demo"""
        print("🎨 Opening UI Demo...")
        try:
            from UI.messenger_test import MessengerTestWindow
            self.ui_demo = MessengerTestWindow()
            self.ui_demo.show()
        except Exception as e:
            print(f"Error opening UI demo: {e}")
    
    def open_db_demo(self):
        """Open database demo"""
        if not self.messenger_db:
            print("❌ Database not available")
            return
        
        print("💾 Opening Database Demo...")
        try:
            if DatabaseChatWindow:
                self.db_demo = DatabaseChatWindow(
                    current_user_id=self.current_user_id,
                    friend_id=2,
                    friend_name="Trần Thị B",
                    current_username=self.current_username
                )
                self.db_demo.show()
            else:
                print("❌ DatabaseChatWindow not available")
        except Exception as e:
            print(f"Error opening database demo: {e}")
    
    def open_full_demo(self):
        """Open full featured demo"""
        print("⭐ Opening Full Demo...")
        try:
            # Open chat launcher with all features
            from Chat1_1.chat_launcher import ChatLauncher
            self.full_demo = ChatLauncher()
            self.full_demo.show()
        except Exception as e:
            print(f"Error opening full demo: {e}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set modern style
    app.setStyle('Fusion')
    
    demo = MessengerDemo()
    demo.show()
    
    print("🎯 PycTalk Messenger Demo Started!")
    print("Choose your demo mode from the window.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
