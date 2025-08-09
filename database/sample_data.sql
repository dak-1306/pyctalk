-- Insert dữ liệu mẫu cho PycTalk
USE pyctalk;

-- Insert users mẫu (password hash là của "1")
INSERT INTO users (id, username, password_hash, email, created_at) VALUES 
(1, 'danny07', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'danny@gmail.com', '2025-08-01 16:09:30'),
(2, 'danny04', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'danny04@gmail.com', '2025-08-02 23:25:05'),
(3, 'test', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test@gmail.com', '2025-08-02 23:31:57'),
(4, 'test2', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test2@gmail.com', '2025-08-02 23:36:03'),
(5, 'test3', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test3@gmail.com', '2025-08-02 23:37:29'),
(6, 'test4', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test4@gmail.com', '2025-08-02 23:37:55'),
(7, 'test6', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test6@gmail.com', '2025-08-02 23:40:26');

-- Insert một số lời mời kết bạn mẫu
INSERT INTO friend_requests (from_user_id, to_user_id, status) VALUES
(1, 2, 'pending'),
(3, 4, 'pending'),
(1, 5, 'accepted');

-- Insert một số quan hệ bạn bè mẫu (user1_id < user2_id)
INSERT INTO friends (user1_id, user2_id) VALUES
(1, 3),
(2, 4),
(1, 5);

-- Thông báo hoàn thành
SELECT 'Sample data inserted successfully!' as status;
