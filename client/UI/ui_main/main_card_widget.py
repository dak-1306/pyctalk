from PyQt6 import QtCore, QtGui, QtWidgets

class MainCardWidget(QtWidgets.QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(700)
        self.setObjectName("main_card")
        self.username = username
        self._setup_ui(username)

    def _setup_ui(self, username):
        # Card shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QtGui.QColor(99, 102, 241, 80))
        self.setGraphicsEffect(shadow)

        # Main card styling
        self.setStyleSheet("""
            QWidget#main_card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f8fafc);
                border-radius: 24px;
                border: 1px solid rgba(99, 102, 241, 0.1);
            }
        """)

        card_layout = QtWidgets.QVBoxLayout(self)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(32)

        # Header section with logo and title
        self._setup_header_section(card_layout)

        # Welcome section
        self._setup_welcome_section(card_layout)

        # Stats section
        self._setup_stats_section(card_layout)

        # Quick actions
        self._setup_quick_actions_section(card_layout)

    def _setup_header_section(self, layout):
        """Setup header with logo and app name"""
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(16)

        # App logo/icon
        logo_label = QtWidgets.QLabel("💬")
        logo_label.setFont(QtGui.QFont("Segoe UI", 48))
        logo_label.setStyleSheet("""
            QLabel {
                color: #6366f1;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(99, 102, 241, 0.1),
                    stop:1 rgba(99, 102, 241, 0.05));
                border-radius: 16px;
                padding: 12px;
                min-width: 72px;
                min-height: 72px;
            }
        """)
        header_layout.addWidget(logo_label)

        # App title and tagline
        title_layout = QtWidgets.QVBoxLayout()
        title_layout.setSpacing(4)

        app_title = QtWidgets.QLabel("PycTalk")
        app_title.setFont(QtGui.QFont("Segoe UI", 36, QtGui.QFont.Weight.Bold))
        app_title.setStyleSheet("color: #1f2937; margin: 0px;")
        title_layout.addWidget(app_title)

        tagline = QtWidgets.QLabel("Ứng dụng nhắn tin hiện đại")
        tagline.setFont(QtGui.QFont("Segoe UI", 14))
        tagline.setStyleSheet("color: #6b7280; margin: 0px;")
        title_layout.addWidget(tagline)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

    def _setup_welcome_section(self, layout):
        """Setup personalized welcome section"""
        welcome_layout = QtWidgets.QVBoxLayout()
        welcome_layout.setSpacing(8)

        # Welcome message
        welcome_msg = QtWidgets.QLabel(f"Chào mừng, {self.username or 'bạn'}! 👋")
        welcome_msg.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Medium))
        welcome_msg.setStyleSheet("color: #374151; margin: 0px;")
        welcome_msg.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_msg)

        # Status message with emoji
        status_msg = QtWidgets.QLabel("🌟 Sẵn sàng kết nối và trò chuyện!")
        status_msg.setFont(QtGui.QFont("Segoe UI", 14))
        status_msg.setStyleSheet("color: #6b7280; margin: 0px;")
        status_msg.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(status_msg)

        layout.addLayout(welcome_layout)

    def _setup_stats_section(self, layout):
        """Setup statistics section"""
        stats_layout = QtWidgets.QHBoxLayout()
        stats_layout.setSpacing(24)

        # Online friends stat
        online_stat = self._create_stat_item("🟢", "Bạn bè online", "12")
        stats_layout.addWidget(online_stat)

        # Messages stat
        messages_stat = self._create_stat_item("💬", "Tin nhắn hôm nay", "47")
        stats_layout.addWidget(messages_stat)

        # Groups stat
        groups_stat = self._create_stat_item("👥", "Nhóm tham gia", "3")
        stats_layout.addWidget(groups_stat)

        layout.addLayout(stats_layout)

    def _create_stat_item(self, icon, label, value):
        """Create a statistics item"""
        stat_widget = QtWidgets.QWidget()
        stat_layout = QtWidgets.QVBoxLayout(stat_widget)
        stat_layout.setContentsMargins(16, 12, 16, 12)
        stat_layout.setSpacing(4)

        # Icon
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setFont(QtGui.QFont("Segoe UI", 24))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stat_layout.addWidget(icon_label)

        # Value
        value_label = QtWidgets.QLabel(value)
        value_label.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        value_label.setStyleSheet("color: #6366f1;")
        value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stat_layout.addWidget(value_label)

        # Label
        text_label = QtWidgets.QLabel(label)
        text_label.setFont(QtGui.QFont("Segoe UI", 10))
        text_label.setStyleSheet("color: #6b7280;")
        text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stat_layout.addWidget(text_label)

        # Styling
        stat_widget.setStyleSheet("""
            QWidget {
                background: rgba(99, 102, 241, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(99, 102, 241, 0.1);
            }
        """)

        return stat_widget

    def _setup_quick_actions_section(self, layout):
        """Setup quick action buttons"""
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(20)

        # Quick chat button
        quick_chat_btn = self._create_action_button(
            "💬 Chat nhanh",
            "Bắt đầu cuộc trò chuyện mới",
            "#10b981"
        )
        actions_layout.addWidget(quick_chat_btn)

        # Find friends button
        find_friends_btn = self._create_action_button(
            "👥 Tìm bạn bè",
            "Kết nối với người mới",
            "#f59e0b"
        )
        actions_layout.addWidget(find_friends_btn)

        # Create group button
        create_group_btn = self._create_action_button(
            "➕ Tạo nhóm",
            "Tạo nhóm trò chuyện",
            "#8b5cf6"
        )
        actions_layout.addWidget(create_group_btn)

        layout.addLayout(actions_layout)

    def _create_action_button(self, text, tooltip, accent_color):
        """Create a styled action button"""
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(50)
        btn.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Medium))
        btn.setToolTip(tooltip)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent_color},
                    stop:1 {self._darken_color(accent_color, 0.8)});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._lighten_color(accent_color, 0.2)},
                    stop:1 {self._darken_color(accent_color, 0.6)});
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._darken_color(accent_color, 0.9)},
                    stop:1 {self._darken_color(accent_color, 1.0)});
                transform: translateY(0px);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)

        return btn

    def _lighten_color(self, color_hex, factor):
        """Lighten a hex color"""
        color = QtGui.QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = min(255, int(v * (1 + factor)))
        color.setHsv(h, s, v, a)
        return color.name()

    def _darken_color(self, color_hex, factor):
        """Darken a hex color"""
        color = QtGui.QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = max(0, int(v * factor))
        color.setHsv(h, s, v, a)
        return color.name()

    # Keep original properties for compatibility
    @property
    def title(self):
        return self.findChild(QtWidgets.QLabel, "app_title")

    @property
    def subtitle(self):
        return self.findChild(QtWidgets.QLabel, "welcome_msg")

    @property
    def status_message(self):
        return self.findChild(QtWidgets.QLabel, "status_msg")
