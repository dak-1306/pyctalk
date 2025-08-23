## pyctalk - Cấu trúc dự án

```
pyctalk/
│
├── client/
│   ├── main.py                  # Điểm bắt đầu của client
│   ├── main_client_terminal.py  # Chạy client qua terminal
│   ├── messenger_demo.py        # Demo messenger
│   ├── UI/                     # Giao diện người dùng (PyQt6)
│   │   ├── main.py
│   │   ├── messenger.py
│   │   ├── mainClient.py
│   │   ├── mainClient_integrated.py
│   │   ├── loginUI.py
│   │   ├── loginUI_large.py
│   │   ├── signinUI.py
│   │   ├── signinUI_large.py
│   │   ├── signinUI_modern.py
│   │   ├── messenger_ui/
│   │   │   ├── friend_list_window.py
│   │   │   ├── chat_list_item_widget.py
│   │   │   └── ...
│   │   ├── ui_main/
│   │   │   ├── sidebar_widget.py
│   │   │   └── ...
│   ├── Add_friend/
│   │   ├── friend.py
│   ├── Group_chat/
│   │   ├── group_api_client.py
│   │   ├── group_chat_logic.py
│   │   ├── group_chat_window.py
│   │   ├── group_threads.py
│   ├── Chat1_1/
│   │   ├── chat1v1_client.py
│   ├── Request/
│   │   ├── handle_request_client.py
│   ├── Login/
│   │   ├── login_signIn.py
│   │   ├── logout.py
│   └── __pycache__/
│
├── server/
│   ├── main_server.py            # Điểm bắt đầu của server
│   ├── connection_handler.py     # Lắng nghe kết nối TCP từ client
│   ├── client_session.py         # Quản lý từng phiên client
│   ├── Handle_AddFriend/
│   │   ├── friend_handle.py
│   ├── HandleChat1_1/
│   │   ├── chat_handler.py
│   ├── HandleGroupChat/
│   │   ├── group_handler.py
│   ├── Login_server/
│   │   ├── LoginHandle.py
│   │   ├── RegisterHandle.py
│   └── __pycache__/
│
├── database/
│   ├── db.py
│   ├── messenger_db.py
│   ├── create_schema.sql
│   ├── sample_data.sql
│   ├── schema.sql
│   └── __pycache__/
│
├── docs/
│   └── design_doc.md
│
└── README.md
```

### Mô tả các thư mục chính

- **client/**: Mã nguồn phía client, bao gồm giao diện, xử lý kết nối, bạn bè, nhóm...
- **server/**: Mã nguồn phía server, quản lý kết nối, người dùng, nhóm, relay tin nhắn...
- **database/**: Kết nối, truy vấn và cấu trúc cơ sở dữ liệu.
- **docs/**: Tài liệu thiết kế, sơ đồ, ý tưởng phát triển.
- **README.md**: Hướng dẫn tổng quan dự án.
