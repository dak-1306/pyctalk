# 📎 Media Messaging Feature Documentation

## 🎯 Tổng quan
Tính năng gửi media (ảnh, file, audio, video) đã được tích hợp vào ứng dụng chat PyCtalk với giao diện hiện đại tương tự Zalo/Messenger.

## ✨ Tính năng mới

### 📸 Hỗ trợ nhiều loại file
- **Ảnh**: .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg
- **Video**: .mp4, .avi, .mov, .wmv, .flv, .webm, .mkv
- **Audio**: .mp3, .wav, .ogg, .aac, .flac, .m4a
- **Documents**: .pdf, .doc, .docx, .txt, .xls, .xlsx, .ppt, .pptx
- **Bất kỳ file nào**: Kích thước tối đa 50MB

### 🎨 Giao diện người dùng
1. **Nút chọn file**: 📎 với dropdown menu phân loại
2. **Nút ảnh nhanh**: 🖼️ để chọn ảnh trực tiếp
3. **Preview file**: Hiển thị file đã chọn trước khi gửi
4. **Message bubbles**: Hiển thị ảnh, file với thumbnail và thông tin

### 💾 Lưu trữ và xử lý
- **Upload directory**: `uploads/` với các thư mục con
  - `uploads/images/` - Ảnh
  - `uploads/files/` - File documents
  - `uploads/thumbnails/` - Thumbnail cho ảnh
- **Database**: Các cột mới trong `private_messages` và `group_messages`
  - `message_type`: loại tin nhắn (text/image/file/audio/video)
  - `file_path`: đường dẫn file
  - `file_name`: tên file gốc
  - `file_size`: kích thước file
  - `mime_type`: loại MIME
  - `thumbnail_path`: đường dẫn thumbnail

## 🚀 Cách sử dụng

### Cho người dùng:
1. **Gửi ảnh**: 
   - Click nút 🖼️ hoặc 📎 → Images
   - Chọn ảnh từ máy tính
   - Thêm caption nếu muốn
   - Click Send ➤

2. **Gửi file**:
   - Click nút 📎 → chọn loại file
   - Browse và chọn file
   - Thêm mô tả nếu cần
   - Click Send ➤

3. **Xem file**:
   - Click vào ảnh để xem full size
   - Click vào file để mở/download

### Cho developers:

#### 1. Cấu trúc API mới:
```python
# Gửi file message
await api_client.send_file_message(user_id, friend_id, file_metadata, caption)

# File metadata structure:
{
    'message_type': 'image|file|audio|video',
    'file_path': '/path/to/file',
    'file_name': 'original_name.ext',
    'file_size': 1024,
    'mime_type': 'image/jpeg',
    'thumbnail_path': '/path/to/thumb.jpg'  # optional
}
```

#### 2. UI Components mới:
- `MediaMessageBubble`: Hiển thị tin nhắn media
- `FileUploadWidget`: Widget chọn file
- `FilePreviewWidget`: Preview file trước khi gửi

#### 3. Server Handler:
- `handle_send_file_message()`: Xử lý gửi file
- Database schema đã cập nhật để lưu metadata

## 🛠️ Cài đặt và Setup

### 1. Dependencies:
```bash
pip install Pillow  # Để xử lý ảnh
```

### 2. Database Update:
```bash
python scripts/update_database_media.py
```

### 3. Test:
```bash
python scripts/test_media_features.py
```

## 📝 Technical Details

### File Upload Flow:
1. User chọn file từ UI
2. `FileUploadWidget` validate file (size, type)
3. `FilePreviewWidget` hiển thị preview
4. User click Send → `send_file_message()`
5. `MediaHandler` copy file vào `uploads/` và tạo thumbnail
6. API gửi metadata đến server
7. Server lưu metadata vào database
8. Server push tin nhắn đến recipient
9. UI hiển thị `MediaMessageBubble`

### Security Features:
- Kiểm tra kích thước file (max 50MB)
- Validate file extension
- Tạo tên file unique để tránh conflict
- Thumbnail tự động cho ảnh

### Performance:
- Lazy loading cho chat history
- Thumbnail cho ảnh lớn
- Batch animation khi load messages
- Background file processing

## 🐛 Troubleshooting

### Lỗi thường gặp:
1. **Import Error**: Đảm bảo đã cài PyQt6 và Pillow
2. **Database Error**: Chạy update schema script
3. **File not found**: Kiểm tra đường dẫn uploads/
4. **Permission Error**: Đảm bảo app có quyền ghi file

### Debug:
- Kiểm tra console logs với prefix `[DEBUG][MediaHandler]`
- Verify database columns: `DESCRIBE private_messages;`
- Test upload directories: `ls -la uploads/`

## 🎉 Kết quả

### Trước:
- Chỉ gửi được text
- UI đơn giản
- Thiếu tính năng hiện đại

### Sau:
✅ Gửi được ảnh, file, audio, video  
✅ UI hiện đại với preview và thumbnail  
✅ Upload và lưu trữ tự động  
✅ Database schema hoàn chỉnh  
✅ Tương thích với lazy loading  
✅ Performance tối ưu  

## 🚀 Tính năng tương lai
- [ ] Drag & drop file
- [ ] Copy/paste ảnh từ clipboard
- [ ] File sharing links
- [ ] Cloud storage integration
- [ ] Audio/video recording
- [ ] Message reactions
- [ ] File search trong conversation
