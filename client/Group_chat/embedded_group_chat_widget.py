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
        from client.UI.messenger_ui.message_bubble_widget import MessageBubble
        bubble = MessageBubble(message, is_sent, timestamp)
        self.messages_layout.insertWidget(self.messages_layout.count()-1, bubble)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    def clear_messages(self):
        """Xóa toàn bộ message bubbles khỏi UI (cho logic gọi)"""
        self._clear_message_bubbles()
    message_send_requested = QtCore.pyqtSignal(str)
    group_selected = QtCore.pyqtSignal(dict)
    """
    Phiên bản embedded giữ NGUYÊN logic cũ:
    - Tự tạo GroupAPIClient, GroupChatLogic
    - Set logic.current_group = group_data và load_group_messages() ngay khi init
    - Hàm display_messages/update_group_info/send_message giữ nguyên tên/ý nghĩa
    Chỉ thay UI hiển thị tin bằng MessageBubble + ScrollArea (thay vì QTextEdit.append).
    """

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

    def _setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Thông tin nhóm
        self.group_info_label = QtWidgets.QLabel(
            f"Nhóm: {self.group_data['group_name']} (ID: {self.group_data['group_id']})"
        )
        self.group_info_label.setStyleSheet("font-size: 15px; font-weight: 600;")
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
        self.message_input.returnPressed.connect(lambda: asyncio.create_task(self.send_message()))
        input_layout.addWidget(self.message_input)

        self.send_btn = QtWidgets.QPushButton("Gửi")
        self.send_btn.clicked.connect(lambda: asyncio.create_task(self.send_message()))
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

    # ---------------------------
    # Các hàm UI để LOGIC gọi (giữ tên/signature cũ)
    # ---------------------------
    def display_messages(self, messages, offset, username):
        print(f"[UI] Displaying {len(messages)} messages, username={username}")
        for msg in messages:
            print(f"[UI] Message: sender={msg.get('sender_name')}, content={msg.get('content')}, time={msg.get('time_send')}")
        if offset == 0:
            self._clear_message_bubbles()
        for msg in messages:
            sender = msg.get('sender_name', 'Unknown')
            time_str = msg.get("time_send", None)
            content = msg.get('content', '')
            is_sent = (sender == username)
            self._add_message_bubble(content, is_sent, time_str)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def update_group_info(self, group_data):
        """LOGIC gọi: cập nhật nhãn thông tin nhóm (giữ nguyên tên hàm)."""
        self.group_info_label.setText(
            f"Nhóm: {group_data['group_name']} (ID: {group_data['group_id']})"
        )

    async def send_message(self):
        """
        UI gọi trực tiếp (giữ nguyên flow cũ):
        - Lấy content từ input
        - Gọi api_client.send_group_message(...)
        - Clear input, reload messages
        """
        if not self.logic.current_group:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhóm trước")
            return

        content = self.message_input.text().strip()
        if not content:
            return

        # Giữ nguyên việc dùng self.group_data["group_id"] như bản cũ
        response = await self.api_client.send_group_message(
            self.user_id, self.group_data["group_id"], content
        )

        if response and response.get("success"):
            self.message_input.clear()
            await self.logic.load_group_messages(offset=0)
        else:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể gửi tin nhắn")

    # ---------------------------
    # Helper UI nội bộ
    # ---------------------------    def _add_message_bubble(self, message, is_sent, timestamp=None):
        bubble = MessageBubble(message, is_sent=is_sent, timestamp=timestamp)
        # Chèn trước stretch ở cuối
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

    def _clear_message_bubbles(self):
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
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())
