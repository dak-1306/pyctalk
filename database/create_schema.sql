-- PycTalk Database Schema
-- Tạo database và sử dụng nó
CREATE DATABASE IF NOT EXISTS pyctalk;
USE pyctalk;

-- Xóa bảng nếu đã tồn tại (để có thể chạy lại script)
DROP TABLE IF EXISTS group_members;
DROP TABLE IF EXISTS group_messages;
DROP TABLE IF EXISTS private_messages;
DROP TABLE IF EXISTS group_chat;
DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS friend_requests;
DROP TABLE IF EXISTS users;

-- Bảng users
CREATE TABLE users (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(30) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lời mời kết bạn
CREATE TABLE friend_requests (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    from_user_id INT NOT NULL,
    to_user_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_request (from_user_id, to_user_id)
);

-- Bảng quan hệ bạn bè (chỉ chứa những quan hệ đã được chấp nhận)
CREATE TABLE friends (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user1_id INT NOT NULL,
    user2_id INT NOT NULL,
    status ENUM('accepted') NOT NULL DEFAULT 'accepted',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_friendship (user1_id, user2_id),
    CHECK (user1_id < user2_id)
);

-- Bảng nhóm chat
CREATE TABLE group_chat (
    group_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    group_name TEXT NOT NULL,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Bảng tin nhắn 1-1
CREATE TABLE private_messages (
    message_private_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    time_send DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Bảng tin nhắn nhóm
CREATE TABLE group_messages (
    message_group_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    group_id INT NOT NULL,
    content TEXT NOT NULL,
    time_send DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES group_chat(group_id) ON DELETE CASCADE
);

-- Bảng thành viên nhóm
CREATE TABLE group_members (
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES group_chat(group_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Thông báo hoàn thành
SELECT 'Database schema created successfully!' as status;
