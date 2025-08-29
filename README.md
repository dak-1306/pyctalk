# PycTalk - Ứng dụng Chat Messenger

Ứng dụng chat real-time được phát triển bằng Python với PyQt6, hỗ trợ chat 1-1, chat nhóm, gửi file/media.

## 🚀 Tính năng chính

- **💬 Chat 1-1**: Tin nhắn trực tiếp giữa hai người dùng
- **👥 Chat nhóm**: Tạo và quản lý nhóm chat
- **📸 Media messaging**: Gửi ảnh, file và các loại media khác
- **🔔 Real-time messaging**: Tin nhắn thời gian thực
- **👤 Quản lý bạn bè**: Thêm, xóa bạn bè và quản lý danh sách
- **🔐 Xác thực**: Đăng ký, đăng nhập bảo mật
- **📱 Giao diện hiện đại**: UI/UX tương tự Messenger/Zalo

## 📁 Cấu trúc dự án

```
pyctalk/
│
├── client/                      # Mã nguồn phía client
│   ├── main.py                  # Điểm bắt đầu của client
│   ├── UI/                      # Giao diện người dùng (PyQt6)
│   │   ├── loginUI_large.py
│   │   ├── signinUI_large.py
│   │   ├── messenger_ui/        # UI components
│   │   │   ├── file_upload_widget.py
│   │   │   ├── media_message_bubble.py
│   │   │   ├── message_bubble_widget.py
│   │   │   ├── friend_list_window.py
│   │   │   ├── group_management_dialog.py
│   │   │   ├── create_group_window.py
│   │   │   └── time_formatter.py
│   │   └── ui_main/             # Main window components
│   │       ├── ui_main_window.py
│   │       ├── sidebar_widget.py
│   │       └── topbar_widget.py
│   ├── Add_friend/              # Quản lý bạn bè
│   │   ├── friend.py
│   │   └── friend_list_logic.py
│   ├── Group_chat/              # Chat nhóm
│   │   ├── embedded_group_chat_widget.py
│   │   ├── group_api_client.py
│   │   ├── group_chat_logic.py
│   │   └── group_chat_window.py
│   ├── Chat1_1/                 # Chat 1-1
│   │   ├── chat_window_widget.py
│   │   ├── chat1v1_api_client.py
│   │   ├── chat1v1_client.py
│   │   └── chat1v1_logic.py
│   ├── Request/                 # Xử lý request
│   │   └── handle_request_client.py
│   └── Login/                   # Đăng nhập/đăng xuất
│       ├── login_signIn.py
│       └── logout.py
│
├── server/                      # Mã nguồn phía server
│   ├── main_server.py           # Điểm bắt đầu của server
│   ├── connection_handler.py    # Lắng nghe kết nối TCP từ client
│   ├── client_session.py        # Quản lý từng phiên client
│   ├── media_handler.py         # Xử lý file/media
│   ├── Handle_AddFriend/        # Xử lý bạn bè
│   │   └── friend_handle.py
│   ├── HandleChat1_1/           # Xử lý chat 1-1
│   │   └── chat_handler.py
│   ├── HandleGroupChat/         # Xử lý chat nhóm
│   │   └── group_handler.py
│   ├── HandleUserProfile/       # Xử lý profile người dùng
│   │   └── user_profile_handler.py
│   └── Login_server/            # Xử lý đăng nhập
│       ├── LoginHandle.py
│       └── RegisterHandle.py
│
├── database/                    # Cơ sở dữ liệu
│   ├── db.py                    # Kết nối database
│   └── pyctalk.sql              # Schema và dữ liệu mẫu
│
└── media/                       # Lưu trữ file
    ├── chat_files/              # File từ chat 1-1
    └── group_files/             # File từ chat nhóm
```

## 🛠️ Công nghệ sử dụng

- **Frontend**: PyQt6 (Python GUI framework)
- **Backend**: Python asyncio TCP server
- **Database**: MySQL/MariaDB
- **Real-time**: TCP socket connection
- **File handling**: Base64 encoding/decoding

## 📋 Yêu cầu hệ thống

- Python 3.8+
- PyQt6
- MySQL/MariaDB
- aiomysql
- qasync

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install PyQt6 aiomysql qasync
```

### 2. Cài đặt database
```bash
# Import database schema
mysql -u username -p < database/pyctalk.sql
```

### 3. Cấu hình database
Cập nhật thông tin kết nối database trong `database/db.py`

### 4. Chạy server
```bash
python server/main_server.py
```

### 5. Chạy client
```bash
python client/main.py
```

## 📱 Hướng dẫn sử dụng

1. **Đăng ký/Đăng nhập**: Tạo tài khoản mới hoặc đăng nhập với tài khoản có sẵn
2. **Thêm bạn bè**: Tìm kiếm và gửi lời mời kết bạn
3. **Chat 1-1**: Click vào bạn bè để bắt đầu chat
4. **Tạo nhóm**: Tạo nhóm chat và mời bạn bè tham gia
5. **Gửi file**: Sử dụng nút 📎 để gửi ảnh, file

## 🎯 Tính năng nổi bật

### Media Messaging
- Hỗ trợ gửi ảnh (JPG, PNG, GIF)
- Gửi file (PDF, DOC, TXT, v.v.)
- Preview ảnh trực tiếp trong chat
- Download file đã gửi

### Group Chat
- Tạo nhóm với nhiều thành viên
- Quản lý thành viên (thêm/xóa)
- Chuyển quyền admin
- Real-time messaging trong nhóm

### Modern UI/UX
- Giao diện giống Messenger/Zalo
- Dark/Light theme
- Responsive design
- Smooth animations

## 👥 Đóng góp

Dự án được phát triển cho mục đích học tập. Mọi đóng góp đều được chào đón!

## 📄 License

[MIT License](LICENSE)
