# mainClient_integrated.py
# Tích hợp chat_list_main + messenger_main vào mainClient (navbar + body mặc định)
# Ghi chú: file này dùng các class đã có trong project:
#   - UI.Main client: Ui_MainWindow (từ mainClient.py)
#   - Chat list: ChatListWindow (từ chat_list_main.py)
#   - Messenger: MessengerChatList (từ messenger_main.py)
#
# Cách chạy: python mainClient_integrated.py

import sys
import types
from PyQt6 import QtWidgets, QtCore

# IMPORT các module từ project (giữ nguyên đường import hiện tại)
# Lưu ý: đường dẫn module tương đối có thể khác trong project của bạn,
# nếu module không tìm thấy, chạy file này từ thư mục gốc project.
try:
    from UI.mainClient import Ui_MainWindow
except Exception:
    # nếu UI/mainClient.py khác vị trí, thử import trực tiếp
    try:
        from mainClient import Ui_MainWindow
    except Exception as e:
        raise

try:
    from UI.chat_list_main import ChatListWindow
except Exception:
    try:
        from chat_list_main import ChatListWindow
    except Exception:
        raise

try:
    from UI.messenger_main import MessengerChatList
except Exception:
    try:
        from messenger_main import MessengerChatList
    except Exception:
        raise


class IntegratedMain(QtWidgets.QMainWindow):
    """
    Cửa sổ tích hợp:
    - Sử dụng Ui_MainWindow để giữ navbar + cấu trúc body mặc định
    - Thay phần sidebar trong Ui_MainWindow bằng ChatListWindow (UI có sẵn)
    - Khi click 1 người -> khởi MessengerChatList và hiển thị trong main_content
    """

    def __init__(self, username="Guest"):
        super().__init__()

        # 1) Khởi UI chính từ mainClient.Ui_MainWindow
        # Ui_MainWindow.__init__ signature trong project là: (username, client, main_window)
        # Mình truyền client=None, main_window=self để tránh lỗi nếu UI dùng chúng.
        try:
            self.ui = Ui_MainWindow(username, None, self)
        except TypeError:
            # nếu signature khác, thử một số cách fallback
            try:
                # đôi khi signature: (client, main_window)
                self.ui = Ui_MainWindow(None, self)
            except Exception:
                # fallback tạo object rồi gọi setupUi như thường
                self.ui = Ui_MainWindow(username, None, self)

        # Chuẩn bị main window (Ui_MainWindow.setupUi cần QMainWindow)
        # Nếu setupUi tồn tại, gọi nó
        if hasattr(self.ui, "setupUi"):
            self.ui.setupUi(self)

        # Lưu refs
        self.chat_list_win = None
        self.messenger_win = None
        self.current_chat_widget = None

        # 2) Thay thế sidebar bằng ChatListWindow UI
        self._inject_chat_list_into_sidebar()

    def _clear_layout(self, layout: QtWidgets.QLayout):
        """Xóa widget con của layout (không delete object để tránh crash nếu object còn dùng)"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                # detach widget from layout but do not delete (we may reparent)
                w.setParent(None)

    def _inject_chat_list_into_sidebar(self):
        """Tạo ChatListWindow, lấy centralWidget và đưa vào ui.sidebar"""
        # Tạo instance ChatListWindow (không show)
        self.chat_list_win = ChatListWindow()

        # ChatListWindow là QMainWindow: có centralWidget(); lấy widget chính của nó
        try:
            chat_central = self.chat_list_win.centralWidget()
        except Exception:
            # fallback: nếu không có centralWidget, tìm widget con đầu tiên
            children = self.chat_list_win.findChildren(QtWidgets.QWidget)
            chat_central = children[0] if children else None

        # Nếu không tìm được sidebar trong Ui_MainWindow, tạo 1 frame mặc định
        if not hasattr(self.ui, "sidebar") or getattr(self.ui, "sidebar") is None:
            # tạo 1 frame ở left nếu ui không có sidebar (rất hiếm)
            sidebar_frame = QtWidgets.QFrame()
            sidebar_frame.setFixedWidth(260)
            layout = getattr(self.ui, "outer_layout", None)
            if isinstance(layout, QtWidgets.QBoxLayout):
                layout.insertWidget(0, sidebar_frame, 2)
            self.ui.sidebar = sidebar_frame

        # Thêm chat_central vào ui.sidebar (thực hiện reparent)
        sidebar_layout = self.ui.sidebar.layout()
        if sidebar_layout is None:
            sidebar_layout = QtWidgets.QVBoxLayout(self.ui.sidebar)
            sidebar_layout.setContentsMargins(0, 0, 0, 0)
            sidebar_layout.setSpacing(0)

        # Clear existing sidebar layout content and add chat_central
        self._clear_layout(sidebar_layout)
        if chat_central is not None:
            # reparent widget
            chat_central.setParent(self.ui.sidebar)
            sidebar_layout.addWidget(chat_central)
        else:
            # làm fallback: tạo label báo lỗi
            lbl = QtWidgets.QLabel("Không tải được danh sách chat")
            sidebar_layout.addWidget(lbl)

        # Monkeypatch: thay đổi hàm open_chat của chat_list_win để gọi local handler
        # ChatListWindow có method open_chat(self, chat_data) hoặc tương tự.
        if hasattr(self.chat_list_win, "open_chat"):
            # giữ ref hàm cũ (nếu cần)
            self.chat_list_win._open_chat_original = getattr(self.chat_list_win, "open_chat")
            # gán method mới để khi ChatListWindow gọi open_chat(...) -> sẽ gọi self._on_chat_selected(...)
            def _forward_open_chat(chat_data):
                # chat_data có thể là dict hoặc id tuỳ implement
                self._on_chat_selected(chat_data)
            # Bind as method
            try:
                self.chat_list_win.open_chat = types.MethodType(lambda self_, chat_data: _forward_open_chat(chat_data), self.chat_list_win)
            except Exception:
                # fallback khi không thể bind: gán trực tiếp
                self.chat_list_win.open_chat = lambda chat_data: _forward_open_chat(chat_data)
        else:
            # Nếu không có open_chat, cố gắng tìm các ChatListItem clicked signal.
            # Tìm tất cả ChatListItem (custom) trong chat_central và connect clicked
            try:
                items = self.chat_list_win.findChildren(QtCore.QObject)
                for it in items:
                    if hasattr(it, "clicked") and isinstance(getattr(it, "clicked"), QtCore.pyqtSignal.__class__):
                        try:
                            it.clicked.connect(self._on_chat_selected)
                        except Exception:
                            pass
            except Exception:
                pass

    def _on_chat_selected(self, chat_data):
        """
        Được gọi khi người dùng nhấp 1 bạn trong sidebar.
        - Tạo MessengerChatList nếu chưa có
        - Bật messenger UI trong main_content và gọi open_chat_window(chat_data)
        """
        # 1) Khởi messenger window (nếu chưa)
        if self.messenger_win is None:
            try:
                self.messenger_win = MessengerChatList()
            except Exception as e:
                # nếu MessengerChatList cần tham số, thử khởi không tham số
                try:
                    self.messenger_win = MessengerChatList(None)
                except Exception:
                    # fallback: báo lỗi
                    QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không tải được MessengerChatList: {e}")
                    return

        # 2) Lấy central widget của messenger_win và hiển thị trong main_content
        try:
            messenger_central = self.messenger_win.centralWidget()
        except Exception:
            # fallback tìm widget con
            children = self.messenger_win.findChildren(QtWidgets.QWidget)
            messenger_central = children[0] if children else None

        # Ensure ui has main_content area
        if not hasattr(self.ui, "main_content") or getattr(self.ui, "main_content") is None:
            # Nếu không có main_content, thử đặt vào centralwidget
            target_parent = self.centralWidget()
            if target_parent is None:
                target_parent = QtWidgets.QWidget()
                self.setCentralWidget(target_parent)
            main_layout = target_parent.layout() or QtWidgets.QVBoxLayout(target_parent)
        else:
            target_parent = self.ui.main_content
            main_layout = target_parent.layout() or QtWidgets.QVBoxLayout(target_parent)

        # Clear main_content layout (lưu nội dung mặc định nếu cần)
        self._clear_layout(main_layout)

        # reparent messenger_central và add vào main layout
        if messenger_central is not None:
            messenger_central.setParent(target_parent)
            main_layout.addWidget(messenger_central)
            self.current_chat_widget = messenger_central
        else:
            main_layout.addWidget(QtWidgets.QLabel("Không tải được giao diện chat"))

        # 3) Gọi method để mở chat tương ứng nếu messenger_win hỗ trợ
        if hasattr(self.messenger_win, "open_chat_window"):
            try:
                # Tùy implement, chat_data có thể là id hoặc dict
                self.messenger_win.open_chat_window(chat_data)
            except Exception:
                # nếu open_chat_window yêu cầu khác, thử truyền chat_data.get('id') nếu dict
                try:
                    if isinstance(chat_data, dict) and "id" in chat_data:
                        self.messenger_win.open_chat_window(chat_data.get("id"))
                except Exception:
                    pass

        # finally: ensure layout updates
        self.repaint()

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = IntegratedMain(username="TestUser")
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
