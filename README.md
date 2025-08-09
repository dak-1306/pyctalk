## pyctalk - Cấu trúc dự án

```
pyctalk/
│
├── client/
│   ├── main.py              # Điểm bắt đầu của client
│   ├── ui.py                # Giao diện người dùng (CLI hoặc GUI)
│   ├── client_tcp.py        # Giao tiếp TCP với server
│   ├── client_p2p.py        # Kết nối P2P (UDP)
│   ├── friend.py            # Xử lý kết bạn
│   ├── group.py             # Xử lý tạo nhóm, gửi nhóm
│   └── utils.py             # Hàm phụ trợ: mã hóa, kiểm tra, log...
│
├── server/
│   ├── main.py              # Điểm bắt đầu của server
│   ├── connection_handler.py# Lắng nghe kết nối TCP từ client
│   ├── client_session.py    # Quản lý từng phiên client (dạng thread)
│   ├── user_handler.py      # Xử lý đăng ký, đăng nhập
│   ├── friend_handler.py    # Xử lý kết bạn
│   ├── group_handler.py     # Xử lý tạo nhóm, gửi tin nhóm
│   ├── relay.py             # Relay tin nhắn nếu P2P không thành công
│   └── p2p_coordinator.py   # Trung gian thiết lập P2P (NAT traversal/hole punching)
│
├── database/
│   ├── db.py                # Kết nối và truy vấn DB (SQLite hoặc PostgreSQL)
│   └── schema.sql           # Câu lệnh SQL tạo bảng ban đầu
│
├── docs/
│   └── design_doc.md        # Tài liệu thiết kế, sơ đồ luồng, ý tưởng
│
└── README.md                # Hướng dẫn chạy ứng dụng
```

### Mô tả các thư mục chính

- **client/**: Mã nguồn phía client, bao gồm giao diện, xử lý kết nối, bạn bè, nhóm...
- **server/**: Mã nguồn phía server, quản lý kết nối, người dùng, nhóm, relay tin nhắn...
- **database/**: Kết nối, truy vấn và cấu trúc cơ sở dữ liệu.
- **docs/**: Tài liệu thiết kế, sơ đồ, ý tưởng phát triển.
- **README.md**: Hướng dẫn tổng quan dự án.
