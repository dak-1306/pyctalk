-- Sample data for user_profiles table
INSERT INTO user_profiles (user_id, display_name, bio, gender, birth_date, phone, location, avatar_url)
VALUES
  (1, 'Danny Nguyễn', 'Yêu thích công nghệ, thích lập trình.', 'male', '2000-01-01', '0901234567', 'Hà Nội', ''),
  (2, 'Phương Trần', 'Thích du lịch, thích đọc sách.', 'female', '2001-05-12', '0912345678', 'TP.HCM', ''),
  (3, 'Test User', 'Tôi là người dùng thử nghiệm.', 'other', NULL, '', 'Đà Nẵng', ''),
  (4, 'Nguyễn Văn A', 'Chào mọi người!', 'male', '1999-12-31', '', 'Hải Phòng', ''),
  (5, 'Trần Thị B', 'Sống và làm việc tại Sài Gòn.', 'female', '2002-07-15', '0987654321', 'TP.HCM', '');
