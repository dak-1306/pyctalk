import logging
import asyncio
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QTimer

# Giữ nguyên import API + Logic như bản cũ
from client.Group_chat.group_api_client import GroupAPIClient
from client.Group_chat.group_chat_logic import GroupChatLogic

# Import MessageBubble (ưu tiên theo cấu trúc dự án của bạn, fallback nếu chạy độc lập)
from client.UI.messenger_ui.message_bubble_widget import MessageBubble

logger = logging.getLogger(__name__)

class EmbeddedGroupChatWidget(QtWidgets.QWidget):
    # Signals should be declared at class level
    message_send_requested = QtCore.pyqtSignal(str)
    group_selected = QtCore.pyqtSignal(dict)

    def __init__(self, client, user_id, username, group_data):
        super().__init__()
        # --- giữ logic cũ ---
        self.api_client = GroupAPIClient(client)
        self.logic = GroupChatLogic(self, self.api_client, user_id, username)
        self.user_id = user_id
        self.username = username
        self.group_data = group_data

        self._setupUI()

        # Thiết lập nhóm hiện tại và load tin nhắn như bản cũ
        self.logic.current_group = group_data
        asyncio.create_task(self.logic.load_group_messages())

    def showEvent(self, event):
        """Reload tin nhắn khi widget được hiển thị lại (quay lại nhóm)"""
        super().showEvent(event)
        logger.info("[EmbeddedGroupChatWidget] showEvent triggered - reload group messages")
        try:
            if getattr(self.logic, "current_group", None):
                import asyncio
                asyncio.create_task(self.logic.load_group_messages(offset=0))
        except Exception as e:
            logger.error(f"[EmbeddedGroupChatWidget] Lỗi reload tin nhắn: {e}")

    def add_message(self, message, is_sent, timestamp=None):
        """Thêm một message bubble vào UI (cho logic gọi)"""
        bubble = MessageBubble(message, is_sent, timestamp)
        self.messages_layout.insertWidget(self.messages_layout.count()-1, bubble)
        
        # Force visibility after layout insertion to prevent hiding
        QtCore.QTimer.singleShot(0, lambda: bubble.setVisible(True))
        QtCore.QTimer.singleShot(10, lambda: bubble.show())
        QtCore.QTimer.singleShot(50, lambda: bubble.raise_())
        
        self._scroll_to_bottom()

    def clear_messages(self):
        """Xóa toàn bộ message bubbles khỏi UI (cho logic gọi)"""
        self._clear_message_bubbles()

    def _setupUI(self):
        """Tạo UI layout"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Hiển thị tên nhóm
        self.group_info_label = QtWidgets.QLabel()
        self.group_info_label.setStyleSheet("font-weight: bold; padding: 8px;")
        self.update_group_info()
        layout.addWidget(self.group_info_label)

        # Khu vực tin nhắn: ScrollArea + VBox (dùng MessageBubble)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.messages_widget = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(12)
        # Stretch để các bubble dồn lên trên, chừa chỗ cuối
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area, stretch=1)

        # Input gửi tin
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn...")
        self.message_input.returnPressed.connect(self._on_send_message)

        self.send_button = QtWidgets.QPushButton("Gửi")
        self.send_button.clicked.connect(self._on_send_message)

        input_layout.addWidget(self.message_input, stretch=1)
        input_layout.addWidget(self.send_button)
        layout.addWidget(QtWidgets.QWidget())  # spacer
        layout.addLayout(input_layout)

    def update_group_info(self):
        """Cập nhật thông tin nhóm hiển thị"""
        if self.group_data:
            group_name = self.group_data.get("group_name", "Unknown Group")
            group_id = self.group_data.get("group_id", "?")
            self.group_info_label.setText(f"Nhóm: {group_name} (ID: {group_id})")

    def _on_send_message(self):
        """Xử lý gửi tin nhắn"""
        content = self.message_input.text().strip()
        if content:
            asyncio.create_task(self._send_message_async(content))

    async def _send_message_async(self, content):
        """Gửi tin nhắn async (giữ nguyên logic cũ)"""
        # Giữ nguyên việc dùng self.group_data["group_id"] như bản cũ
        response = await self.api_client.send_group_message(
            self.user_id, self.group_data["group_id"], content
        )

        if response and response.get("success"):
            self.message_input.clear()
            await self.logic.load_group_messages(offset=0)
        else:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể gửi tin nhắn")

    def _add_message_bubble(self, message, is_sent, timestamp=None):
        """Helper method for adding message bubbles"""
        bubble = MessageBubble(message, is_sent=is_sent, timestamp=timestamp)
        # Chèn trước stretch ở cuối
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

    def _clear_message_bubbles(self):
        """Clear all message bubbles from layout"""
        try:
            if self.messages_layout and not self.messages_layout.isEmpty():
                while self.messages_layout.count() > 1:
                    item = self.messages_layout.takeAt(0)
                    if item:
                        w = item.widget()
                        if w:
                            w.deleteLater()
        except RuntimeError as e:
            # Layout đã bị delete, ignore error
            pass

    def _scroll_to_bottom(self):
        """Scroll to bottom of message area"""
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())
