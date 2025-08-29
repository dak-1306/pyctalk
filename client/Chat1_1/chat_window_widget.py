from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication
import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from UI.messenger_ui.message_bubble_widget import MessageBubble
from UI.messenger_ui.time_formatter import TimeFormatter

class ChatWindow(QtWidgets.QWidget):
    def showEvent(self, event):
        """Reload lịch sử chat khi widget được hiển thị lại (quay lại bạn bè)"""
        super().showEvent(event)
        try:
            if getattr(self.logic, "current_friend_id", None):
                import asyncio
                asyncio.create_task(self.logic.get_chat_history(self.logic.user_id, self.logic.current_friend_id))
        except Exception as e:
            import logging
            logging.exception("Failed to reload chat history on showEvent: %s", e)
    """Individual chat window UI only"""
    back_clicked = pyqtSignal()
    message_send_requested = pyqtSignal(str)   # UI phát tín hiệu khi muốn gửi tin nhắn

    def __init__(self, chat_data=None, parent=None, **kwargs):
        super().__init__(parent)
        self.chat_data = chat_data or {
            'friend_name': kwargs.get('friend_username', 'Friend'),
            'friend_id': kwargs.get('friend_id', 1),
            'current_username': kwargs.get('current_username', 'You'),
            'friend_avatar': kwargs.get('friend_avatar', ''),
            'last_message': kwargs.get('last_message', ''),
            'unread_count': kwargs.get('unread_count', 0)
        }
        
        # Store current user ID for message comparison
        self.current_user_id = kwargs.get('current_user_id', 0)
        if chat_data and 'current_user_id' in chat_data:
            self.current_user_id = chat_data['current_user_id']
        
        # Track previous message for timestamp logic
        self.last_message_time = None
        self.last_message_sender = None
        self.message_count = 0
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self._create_header(layout)
        self._create_chat_area(layout)
        self._create_input_area(layout)

    # ===== UI components =====
    def _create_header(self, main_layout):
        header = QtWidgets.QWidget()
        header.setFixedHeight(75)
        header.setStyleSheet("background-color: #667eea; border-bottom: 1px solid #e1e5e9;")
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20,0,20,0)
        layout.setSpacing(15)

        self.btn_back = QtWidgets.QPushButton("←")
        self.btn_back.clicked.connect(self.back_clicked.emit)

        friend_avatar = QtWidgets.QLabel(self.chat_data['friend_name'][0].upper())
        friend_avatar.setFixedSize(50,50)
        friend_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        friend_name = QtWidgets.QLabel(self.chat_data['friend_name'])
        friend_name.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

        layout.addWidget(self.btn_back)
        layout.addWidget(friend_avatar)
        layout.addWidget(friend_name)
        layout.addStretch()
        main_layout.addWidget(header)

    def _create_chat_area(self, main_layout):
        # Create container for loading spinner and messages
        chat_container = QtWidgets.QWidget()
        chat_layout = QtWidgets.QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # Loading spinner
        self.loading_spinner = QtWidgets.QLabel()
        self.loading_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_spinner.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border-radius: 20px;
                font-size: 14px;
                color: #666;
                padding: 20px;
                margin: 20px;
            }
        """)
        self.loading_spinner.setText("⏳ Đang tải tin nhắn...")
        self.loading_spinner.hide()
        chat_layout.addWidget(self.loading_spinner)
        
        # Loading bar for lazy loading
        self.loading_bar = QtWidgets.QProgressBar()
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
                text-align: center;
                height: 3px;
                border-radius: 1px;
                margin: 0px;
            }
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 1px;
            }
        """)
        self.loading_bar.setRange(0, 0)  # Indeterminate progress
        self.loading_bar.hide()
        chat_layout.addWidget(self.loading_bar)
        
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.messages_widget = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(8)
        
        # Không thêm stretch ở đây vì nó có thể gây vấn đề visibility
        # self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_widget)
        chat_layout.addWidget(self.scroll_area)
        
        main_layout.addWidget(chat_container)

    def _create_input_area(self, main_layout):
        input_area = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(input_area)

        self.txt_message = QtWidgets.QLineEdit()
        self.txt_message.setPlaceholderText("Type a message...")

        self.btn_send = QtWidgets.QPushButton("➤")
        self.btn_send.clicked.connect(self._on_send_clicked)

        layout.addWidget(self.txt_message)
        layout.addWidget(self.btn_send)
        main_layout.addWidget(input_area)

    # ===== UI actions =====
    def _on_send_clicked(self):
        text = self.txt_message.text().strip()
        print(f"[DEBUG][ChatWindow] _on_send_clicked: text='{text}'")
        if text:
            print(f"[DEBUG][ChatWindow] Emitting message_send_requested signal")
            self.message_send_requested.emit(text)
            self.txt_message.clear()
        else:
            print(f"[DEBUG][ChatWindow] Empty text, not sending")

    def add_message(self, message, is_sent, timestamp=None, sender_name=None, is_read=None):
        print(f"[DEBUG][ChatWindow] add_message: message={message}, is_sent={is_sent}, timestamp={timestamp}, is_read={is_read}")
        try:
            # Hide status on all previous sent messages if adding a new sent message
            if is_sent:
                self._hide_previous_message_status()
            
            # Determine current sender
            current_sender = self.chat_data.get('current_username', 'You') if is_sent else self.chat_data.get('friend_name', 'Friend')
            if sender_name:
                current_sender = sender_name
            
            # Determine if timestamp should be shown based on Messenger logic
            is_first_message = self.message_count == 0
            show_timestamp = TimeFormatter.should_show_timestamp(
                timestamp, 
                self.last_message_time, 
                current_sender, 
                self.last_message_sender,
                is_first_message
            )
            
            print(f"[DEBUG][ChatWindow] Timestamp logic: show_timestamp={show_timestamp}, is_first={is_first_message}, current_sender={current_sender}, prev_sender={self.last_message_sender}")
            
            # Create message bubble with timestamp logic and read status
            # Only show status for sent messages and only for the latest one
            show_status = is_sent  # Show status for all sent messages initially, will hide older ones
            bubble = MessageBubble(
                message=message, 
                is_sent=is_sent, 
                timestamp=timestamp,
                sender_name=current_sender,
                show_sender_name=False,  # For 1-1 chat, don't show sender name
                show_timestamp=show_timestamp,
                is_read=is_read if show_status else None  # Pass read status only if showing status
            )
            print(f"[DEBUG][ChatWindow] Created MessageBubble: {bubble}")
            
            # Update tracking variables
            self.last_message_time = timestamp
            self.last_message_sender = current_sender
            self.message_count += 1
            
            # Kiểm tra layout count trước khi insert
            count_before = self.messages_layout.count()
            print(f"[DEBUG][ChatWindow] Layout count before insert: {count_before}")
            
            # Loại bỏ stretch item cuối cùng nếu có
            if count_before > 0:
                last_item = self.messages_layout.itemAt(count_before - 1)
                if last_item and last_item.spacerItem():
                    self.messages_layout.removeItem(last_item)
                    print(f"[DEBUG][ChatWindow] Removed stretch item")
            
            # Thêm message bubble vào layout
            self.messages_layout.addWidget(bubble)
            
            # Thêm stretch ở cuối để đẩy messages lên trên
            self.messages_layout.addStretch()
            
            # Kiểm tra layout count sau khi insert
            count_after = self.messages_layout.count()
            print(f"[DEBUG][ChatWindow] Layout count after insert: {count_after}")
            
            # Force widget updates và visibility
            bubble.setVisible(True)
            bubble.show()
            
            # Force layout updates
            self.messages_layout.update()
            self.messages_widget.updateGeometry()
            self.scroll_area.updateGeometry()
            
            # Force repaint
            bubble.repaint()
            self.messages_widget.repaint()
            
            # Debug widget properties
            print(f"[DEBUG][ChatWindow] Bubble visible: {bubble.isVisible()}")
            print(f"[DEBUG][ChatWindow] Bubble size: {bubble.size()}")
            print(f"[DEBUG][ChatWindow] Messages widget visible: {self.messages_widget.isVisible()}")
            print(f"[DEBUG][ChatWindow] Scroll area visible: {self.scroll_area.isVisible()}")
            
            # Debug parent chain
            print(f"[DEBUG][ChatWindow] Bubble parent: {bubble.parent()}")
            print(f"[DEBUG][ChatWindow] Messages widget parent: {self.messages_widget.parent()}")
            print(f"[DEBUG][ChatWindow] Self visible: {self.isVisible()}")
            
            # Debug widget geometry
            print(f"[DEBUG][ChatWindow] Bubble geometry: {bubble.geometry()}")
            print(f"[DEBUG][ChatWindow] Messages widget geometry: {self.messages_widget.geometry()}")
            print(f"[DEBUG][ChatWindow] Scroll area geometry: {self.scroll_area.geometry()}")
            self.messages_widget.setVisible(True) 
            self.messages_widget.show()
            self.scroll_area.setVisible(True)
            self.scroll_area.show()
            self.setVisible(True)
            self.show()
            
            # Force updates và repaints
            bubble.repaint()
            self.messages_widget.update()
            self.messages_widget.repaint()
            self.scroll_area.update()
            self.scroll_area.repaint()
            self.update()
            self.repaint()
            
            QTimer.singleShot(50, self._scroll_to_bottom)
            print(f"[DEBUG][ChatWindow] Message bubble added successfully with forced updates")
        except Exception as e:
            print(f"[ERROR][ChatWindow] Error adding message: {e}")
            import traceback
            traceback.print_exc()

    def add_system_message(self, message):
        """Add a system message (like friendship notification)"""
        try:
            system_label = QtWidgets.QLabel(message)
            system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            system_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    color: #1976d2;
                    padding: 10px;
                    border-radius: 15px;
                    border: 1px solid #bbdefb;
                    font-style: italic;
                    margin: 10px 20px;
                }
            """)
            system_label.setWordWrap(True)
            
            # Add to layout
            self.messages_layout.addWidget(system_label)
            
            # Force visibility
            system_label.setVisible(True)
            system_label.show()
            
            QTimer.singleShot(50, self._scroll_to_bottom)
            print(f"[DEBUG][ChatWindow] System message added: {message}")
            
        except Exception as e:
            print(f"[ERROR][ChatWindow] Error adding system message: {e}")

    def clear_messages(self):
        """Clear all messages from chat window"""
        try:
            while self.messages_layout.count() > 0:
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            print(f"[DEBUG][ChatWindow] All messages cleared")
        except Exception as e:
            print(f"[ERROR][ChatWindow] Error clearing messages: {e}")

    def show_loading_spinner(self, text="Đang tải..."):
        """Show loading spinner with custom text"""
        if hasattr(self, 'loading_spinner'):
            self.loading_spinner.setText(f"⏳ {text}")
            self.loading_spinner.show()
            print(f"[DEBUG][ChatWindow] Loading spinner shown: {text}")

    def hide_loading_spinner(self):
        """Hide loading spinner"""
        if hasattr(self, 'loading_spinner'):
            self.loading_spinner.hide()
            print(f"[DEBUG][ChatWindow] Loading spinner hidden")

    def show_loading_bar(self):
        """Show loading bar for lazy loading"""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.show()

    def hide_loading_bar(self):
        """Hide loading bar"""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.hide()

    def setup_scroll_loading(self, load_more_callback):
        """Setup scroll detection for lazy loading"""
        self.load_more_callback = load_more_callback
        self.scroll_debounce_timer = QTimer()
        self.scroll_debounce_timer.setSingleShot(True)
        self.scroll_debounce_timer.timeout.connect(self._execute_load_more)
        
        if hasattr(self, 'scroll_area'):
            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.valueChanged.connect(self._on_scroll_changed)
            print(f"[DEBUG][ChatWindow] Scroll loading setup completed")

    def _on_scroll_changed(self, value):
        """Detect scroll to top for loading more messages"""
        scrollbar = self.scroll_area.verticalScrollBar()
        
        # If scrolled near top (within 50 pixels), debounce and load more
        if value <= 50:
            print(f"[DEBUG][ChatWindow] Near top of scroll, scheduling load more...")
            # Stop any existing timer and start a new one (debounce)
            self.scroll_debounce_timer.stop()
            self.scroll_debounce_timer.start(300)  # 300ms debounce
    
    def _execute_load_more(self):
        """Execute the load more callback after debounce"""
        if hasattr(self, 'load_more_callback'):
            print(f"[DEBUG][ChatWindow] Executing load more after debounce")
            asyncio.create_task(self.load_more_callback())

    def prepend_messages(self, messages):
        """Prepend older messages to the beginning of chat"""
        print(f"[DEBUG][ChatWindow] Prepending {len(messages)} older messages")
        
        # Remember current scroll position
        scroll_bar = self.scroll_area.verticalScrollBar()
        old_scroll_value = scroll_bar.value()
        old_max_value = scroll_bar.maximum()
        
        # Reverse messages since they come newest first from server
        # We want to add them in chronological order at the top
        reversed_messages = list(reversed(messages))
        
        # Add messages at the beginning
        for i, message in enumerate(reversed_messages):
            sender_id = int(message.get("from") or message.get("user_id", 0))
            content = message.get("message", "")
            timestamp = message.get("timestamp")
            is_read = message.get("is_read", None)
            
            # Determine if this is from current user
            is_current_user = (sender_id == getattr(self, 'current_user_id', 0))
            
            # For sent messages, pass read status; for received messages, don't show status
            message_is_read = is_read if is_current_user else None
            
            # Create message bubble
            bubble = MessageBubble(content, is_current_user, timestamp, message_is_read)
            bubble.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            
            # Insert at the top (after any existing messages)
            self.messages_layout.insertWidget(i, bubble)
        
        # Adjust scroll position to maintain user's view
        # Calculate new position to keep same relative position
        QApplication.processEvents()  # Process layout changes
        new_max_value = scroll_bar.maximum()
        
        if old_max_value > 0:
            # Calculate the content that was added
            added_content_height = new_max_value - old_max_value
            new_scroll_value = old_scroll_value + added_content_height
        else:
            new_scroll_value = old_scroll_value
            
        scroll_bar.setValue(new_scroll_value)
        print(f"[DEBUG][ChatWindow] Adjusted scroll from {old_scroll_value} to {new_scroll_value}")

    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def showEvent(self, event):
        """Override showEvent to ensure all message bubbles are visible"""
        super().showEvent(event)
        print(f"[DEBUG][ChatWindow] showEvent triggered")
        self._force_show_all_messages()
    
    def _force_show_all_messages(self):
        """Force show all message bubbles in the layout"""
        print(f"[DEBUG][ChatWindow] Forcing show all message bubbles")
        for i in range(self.messages_layout.count()):
            item = self.messages_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'message'):  # Check if it's a MessageBubble
                    print(f"[DEBUG][ChatWindow] Force showing bubble: {widget.message}")
                    widget.setVisible(True)
                    widget.show()
    
    def clear_messages(self):
        """Clear all messages and reset tracking variables"""
        print(f"[DEBUG][ChatWindow] Clearing all messages")
        
        # Remove all widgets from layout
        while self.messages_layout.count():
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Reset tracking variables
        self.last_message_time = None
        self.last_message_sender = None
        self.message_count = 0
        
        print(f"[DEBUG][ChatWindow] Messages cleared, tracking reset")
        
        # Force updates of parent widgets too
        self.messages_widget.show()
        self.scroll_area.show()
        self.update()
        self.repaint()

    def clear_messages(self):
        while self.messages_layout.count() > 1:
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_messages_read_status(self):
        """Update all sent messages to show as read"""
        try:
            # Only update the last sent message to show as read
            last_sent_bubble = None
            for i in range(self.messages_layout.count() - 1, -1, -1):
                item = self.messages_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, MessageBubble) and widget.is_sent:
                        last_sent_bubble = widget
                        break
            
            if last_sent_bubble:
                last_sent_bubble.update_read_status(True)
                print(f"[DEBUG][ChatWindow] Updated last sent message to read status")
        except Exception as e:
            print(f"[ERROR][ChatWindow] Error updating read status: {e}")

    def _hide_previous_message_status(self):
        """Hide status indicators on all previous sent messages"""
        try:
            for i in range(self.messages_layout.count()):
                item = self.messages_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, MessageBubble) and widget.is_sent:
                        # Hide status on previous sent messages
                        widget.hide_status_indicator()
        except Exception as e:
            print(f"[ERROR][ChatWindow] Error hiding previous status: {e}")
