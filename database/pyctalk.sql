-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 29, 2025 at 04:14 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pyctalk`
--

-- --------------------------------------------------------

--
-- Table structure for table `friends`
--

CREATE TABLE `friends` (
  `id` int(11) NOT NULL,
  `user1_id` int(11) NOT NULL,
  `user2_id` int(11) NOT NULL,
  `status` enum('accepted') NOT NULL DEFAULT 'accepted',
  `created_at` datetime DEFAULT current_timestamp()
) ;

--
-- Dumping data for table `friends`
--

INSERT INTO `friends` (`id`, `user1_id`, `user2_id`, `status`, `created_at`) VALUES
(1, 1, 3, 'accepted', '2025-08-27 22:06:37'),
(2, 2, 4, 'accepted', '2025-08-27 22:06:37'),
(3, 1, 5, 'accepted', '2025-08-27 22:06:37'),
(4, 3, 5, 'accepted', '2025-08-27 22:09:30'),
(5, 3, 4, 'accepted', '2025-08-27 22:10:48'),
(6, 8, 10, 'accepted', '2025-08-29 21:11:16');

-- --------------------------------------------------------

--
-- Table structure for table `friend_requests`
--

CREATE TABLE `friend_requests` (
  `id` int(11) NOT NULL,
  `from_user_id` int(11) NOT NULL,
  `to_user_id` int(11) NOT NULL,
  `status` enum('pending','accepted','rejected') NOT NULL DEFAULT 'pending',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `friend_requests`
--

INSERT INTO `friend_requests` (`id`, `from_user_id`, `to_user_id`, `status`, `created_at`) VALUES
(1, 1, 2, 'pending', '2025-08-27 22:06:37'),
(2, 3, 4, 'accepted', '2025-08-27 22:06:37'),
(3, 1, 5, 'accepted', '2025-08-27 22:06:37'),
(4, 3, 5, 'accepted', '2025-08-27 22:09:17'),
(5, 3, 7, 'pending', '2025-08-28 16:19:25'),
(6, 10, 8, 'accepted', '2025-08-29 21:10:45');

-- --------------------------------------------------------

--
-- Table structure for table `group_chat`
--

CREATE TABLE `group_chat` (
  `group_id` int(11) NOT NULL,
  `group_name` text NOT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `group_chat`
--

INSERT INTO `group_chat` (`group_id`, `group_name`, `created_by`, `created_at`) VALUES
(1, 'tạo thử', 3, '2025-08-27 22:21:44'),
(2, 'khó', 3, '2025-08-29 10:34:05'),
(3, 'test', 3, '2025-08-29 16:00:31');

-- --------------------------------------------------------

--
-- Table structure for table `group_members`
--

CREATE TABLE `group_members` (
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `joined_at` datetime DEFAULT current_timestamp(),
  `role` enum('admin','member') DEFAULT 'member'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `group_members`
--

INSERT INTO `group_members` (`group_id`, `user_id`, `joined_at`, `role`) VALUES
(1, 4, '2025-08-27 22:21:44', 'admin'),
(2, 1, '2025-08-29 10:34:05', 'member'),
(2, 4, '2025-08-29 10:34:05', 'member'),
(3, 1, '2025-08-29 16:00:31', 'member'),
(3, 2, '2025-08-29 16:24:41', 'member'),
(3, 3, '2025-08-29 16:22:18', 'member'),
(3, 4, '2025-08-29 16:00:31', 'admin'),
(3, 5, '2025-08-29 16:00:31', 'member');

-- --------------------------------------------------------

--
-- Table structure for table `group_messages`
--

CREATE TABLE `group_messages` (
  `message_group_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `time_send` datetime DEFAULT current_timestamp(),
  `message_type` enum('text','image','file','audio','video') DEFAULT 'text',
  `file_path` varchar(500) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` bigint(20) DEFAULT NULL,
  `mime_type` varchar(100) DEFAULT NULL,
  `thumbnail_path` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `group_messages`
--

INSERT INTO `group_messages` (`message_group_id`, `sender_id`, `group_id`, `content`, `time_send`, `message_type`, `file_path`, `file_name`, `file_size`, `mime_type`, `thumbnail_path`) VALUES
(1, 3, 1, 'hi mấy em', '2025-08-27 22:29:16', 'text', NULL, NULL, NULL, NULL, NULL),
(2, 1, 1, 'gì cha', '2025-08-27 22:29:44', 'text', NULL, NULL, NULL, NULL, NULL),
(3, 3, 1, 'đâu gì đâu', '2025-08-28 21:35:31', 'text', NULL, NULL, NULL, NULL, NULL),
(4, 3, 1, 'tạo để test thử thôi à', '2025-08-28 21:35:39', 'text', NULL, NULL, NULL, NULL, NULL),
(5, 1, 1, 'ê m biết vụ gì chưa', '2025-08-28 22:30:15', 'text', NULL, NULL, NULL, NULL, NULL),
(6, 3, 1, 'gì cha', '2025-08-28 22:30:22', 'text', NULL, NULL, NULL, NULL, NULL),
(7, 1, 1, 'không j m', '2025-08-28 22:37:35', 'text', NULL, NULL, NULL, NULL, NULL),
(8, 1, 1, 'tại t kiếm chuyện z thôi à', '2025-08-28 22:37:54', 'text', NULL, NULL, NULL, NULL, NULL),
(9, 3, 1, 'rảnh ha m', '2025-08-28 22:38:01', 'text', NULL, NULL, NULL, NULL, NULL),
(10, 3, 1, 'helo mn', '2025-08-29 10:12:45', 'text', NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `private_messages`
--

CREATE TABLE `private_messages` (
  `message_private_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `time_send` datetime DEFAULT current_timestamp(),
  `is_read` tinyint(1) DEFAULT 0,
  `read_at` datetime DEFAULT NULL,
  `message_type` enum('text','image','file','audio','video') DEFAULT 'text',
  `file_path` varchar(500) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` bigint(20) DEFAULT NULL,
  `mime_type` varchar(100) DEFAULT NULL,
  `thumbnail_path` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `private_messages`
--

INSERT INTO `private_messages` (`message_private_id`, `sender_id`, `receiver_id`, `content`, `time_send`, `is_read`, `read_at`, `message_type`, `file_path`, `file_name`, `file_size`, `mime_type`, `thumbnail_path`) VALUES
(1, 5, 3, 'alo', '2025-08-27 22:09:35', 1, '2025-08-29 16:33:19', 'text', NULL, NULL, NULL, NULL, NULL),
(2, 3, 1, 'hi d7', '2025-08-27 22:22:51', 1, '2025-08-29 00:07:35', 'text', NULL, NULL, NULL, NULL, NULL),
(3, 3, 5, 'gì á', '2025-08-27 22:23:02', 0, NULL, 'text', NULL, NULL, NULL, NULL, NULL),
(4, 3, 1, 'hi', '2025-08-28 16:19:07', 1, '2025-08-29 00:07:35', 'text', NULL, NULL, NULL, NULL, NULL),
(5, 3, 1, 'hi', '2025-08-28 21:35:23', 1, '2025-08-29 00:07:35', 'text', NULL, NULL, NULL, NULL, NULL),
(6, 3, 1, 'hello  danny', '2025-08-28 21:55:18', 1, '2025-08-29 00:07:35', 'text', NULL, NULL, NULL, NULL, NULL),
(7, 3, 4, 'hi test2', '2025-08-28 22:03:10', 1, '2025-08-29 00:07:07', 'text', NULL, NULL, NULL, NULL, NULL),
(8, 4, 3, 'hi nha', '2025-08-28 22:04:06', 1, '2025-08-28 23:52:20', 'text', NULL, NULL, NULL, NULL, NULL),
(9, 3, 4, 'ừa', '2025-08-28 22:05:22', 1, '2025-08-29 00:07:07', 'text', NULL, NULL, NULL, NULL, NULL),
(10, 4, 3, 'ông tên gì', '2025-08-28 22:14:41', 1, '2025-08-28 23:52:20', 'text', NULL, NULL, NULL, NULL, NULL),
(11, 3, 4, 'tui tên Nam', '2025-08-28 22:20:27', 1, '2025-08-29 00:07:07', 'text', NULL, NULL, NULL, NULL, NULL),
(12, 3, 4, 'còn ông tên gì', '2025-08-28 22:20:34', 1, '2025-08-29 00:07:07', 'text', NULL, NULL, NULL, NULL, NULL),
(13, 4, 3, 'tui tên Vy', '2025-08-28 22:20:47', 1, '2025-08-28 23:52:20', 'text', NULL, NULL, NULL, NULL, NULL),
(14, 3, 4, 'ủa con gái hả', '2025-08-28 22:24:26', 1, '2025-08-29 00:07:07', 'text', NULL, NULL, NULL, NULL, NULL),
(15, 4, 3, 'đr ông', '2025-08-28 22:24:32', 1, '2025-08-28 23:52:20', 'text', NULL, NULL, NULL, NULL, NULL),
(16, 3, 4, 'oke', '2025-08-28 22:24:42', 1, '2025-08-29 00:07:07', 'text', NULL, NULL, NULL, NULL, NULL),
(17, 4, 3, 'uk', '2025-08-28 23:16:14', 1, '2025-08-28 23:52:20', 'text', NULL, NULL, NULL, NULL, NULL),
(18, 3, 1, 'xem ko rep m', '2025-08-29 10:13:06', 0, NULL, 'text', NULL, NULL, NULL, NULL, NULL),
(19, 3, 4, 'hi bà', '2025-08-29 16:49:29', 1, '2025-08-29 16:49:29', 'text', NULL, NULL, NULL, NULL, NULL),
(20, 4, 3, 'gì ông', '2025-08-29 16:49:49', 1, '2025-08-29 16:50:49', 'text', NULL, NULL, NULL, NULL, NULL),
(21, 3, 4, 'bà có ngiu chưa', '2025-08-29 16:51:08', 1, '2025-08-29 16:51:08', 'text', NULL, NULL, NULL, NULL, NULL),
(22, 4, 3, 'chi z', '2025-08-29 16:51:13', 1, '2025-08-29 16:51:13', 'text', NULL, NULL, NULL, NULL, NULL),
(23, 3, 4, 'tại tui hỏi cho bít thoi', '2025-08-29 16:51:27', 1, '2025-08-29 16:51:27', 'text', NULL, NULL, NULL, NULL, NULL),
(24, 4, 3, 'ừa', '2025-08-29 16:56:29', 1, '2025-08-29 16:56:29', 'text', NULL, NULL, NULL, NULL, NULL),
(25, 3, 4, 'lạnh lùng thế', '2025-08-29 16:56:37', 1, '2025-08-29 16:56:37', 'text', NULL, NULL, NULL, NULL, NULL),
(26, 3, 4, 'hình như bà học chung trường với tui mà ha', '2025-08-29 16:57:11', 1, '2025-08-29 16:57:11', 'text', NULL, NULL, NULL, NULL, NULL),
(27, 4, 3, 'đr', '2025-08-29 17:02:30', 1, '2025-08-29 17:02:30', 'text', NULL, NULL, NULL, NULL, NULL),
(28, 3, 4, 'oh', '2025-08-29 17:02:38', 1, '2025-08-29 17:02:38', 'text', NULL, NULL, NULL, NULL, NULL),
(29, 3, 4, 'bà nghỉ hè chưa', '2025-08-29 17:02:50', 1, '2025-08-29 17:02:50', 'text', NULL, NULL, NULL, NULL, NULL),
(30, 4, 3, 'nghỉ r', '2025-08-29 17:02:58', 1, '2025-08-29 17:02:58', 'text', NULL, NULL, NULL, NULL, NULL),
(31, 4, 3, 'ông nghỉ chưa', '2025-08-29 17:03:06', 1, '2025-08-29 17:03:06', 'text', NULL, NULL, NULL, NULL, NULL),
(32, 3, 4, 'tui chưa á', '2025-08-29 17:03:12', 1, '2025-08-29 17:03:12', 'text', NULL, NULL, NULL, NULL, NULL),
(33, 3, 4, 'tui học hè nè', '2025-08-29 17:03:18', 1, '2025-08-29 17:03:18', 'text', NULL, NULL, NULL, NULL, NULL),
(34, 4, 3, 'uk', '2025-08-29 17:03:21', 1, '2025-08-29 17:03:21', 'text', NULL, NULL, NULL, NULL, NULL),
(35, 3, 4, ':v', '2025-08-29 17:03:27', 1, '2025-08-29 17:03:27', 'text', NULL, NULL, NULL, NULL, NULL),
(36, 3, 5, 'ê', '2025-08-29 17:03:52', 0, NULL, 'text', NULL, NULL, NULL, NULL, NULL),
(37, 3, 4, '', '2025-08-29 20:55:24', 0, NULL, 'image', 'uploads\\images\\20250829_205524_789d0dfa-9f89-43eb-8112-78d439af2dad.png', 'Ảnh chụp màn hình 2025-08-29 110601.png', 60208, 'image/png', 'uploads\\thumbnails\\thumb_20250829_205524_789d0dfa-9f89-43eb-8112-78d439af2dad.jpg'),
(38, 3, 4, 'nè', '2025-08-29 20:55:35', 0, NULL, 'text', NULL, NULL, NULL, NULL, NULL),
(39, 3, 4, '', '2025-08-29 21:02:34', 0, NULL, 'image', 'uploads\\images\\20250829_210234_bdca03d3-855a-4b78-b435-092833ecd69d.png', 'Ảnh chụp màn hình (118).png', 1547249, 'image/png', 'uploads\\thumbnails\\thumb_20250829_210234_bdca03d3-855a-4b78-b435-092833ecd69d.jpg'),
(40, 3, 4, '', '2025-08-29 21:02:51', 0, NULL, 'file', 'uploads\\files\\20250829_210251_c1e95155-b65d-46cd-9c7c-b0dc7d2be211.docx', 'Chương 9 Quản lý bộ nhớ 9.1_9.2.docx', 222172, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', NULL),
(41, 8, 10, 'chào', '2025-08-29 21:11:25', 1, '2025-08-29 21:11:48', 'text', NULL, NULL, NULL, NULL, NULL),
(42, 10, 8, 'lô', '2025-08-29 21:11:52', 0, NULL, 'text', NULL, NULL, NULL, NULL, NULL),
(43, 10, 8, '', '2025-08-29 21:12:05', 0, NULL, 'image', 'uploads\\images\\20250829_211204_39726c78-e8e1-4d7e-90c3-e86902c1b74e.png', 'Ảnh chụp màn hình 2025-08-24 162859.png', 156723, 'image/png', 'uploads\\thumbnails\\thumb_20250829_211204_39726c78-e8e1-4d7e-90c3-e86902c1b74e.jpg'),
(44, 10, 8, '', '2025-08-29 21:12:19', 0, NULL, 'file', 'uploads\\files\\20250829_211219_d6ac5b2a-c585-4395-9ead-64a771a6ecb2.docx', 'BÀI TẬP LAB 2.docx', 24404, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', NULL),
(45, 10, 8, '', '2025-08-29 21:12:50', 0, NULL, 'video', 'uploads\\files\\20250829_211250_c8612122-b24f-45c6-b79b-9abe1f77197e.mp4', 'Recording 2024-01-20 211332.mp4 - Google Drive - Google Chrome 2024-01-20 21-59-07.mp4', 9113503, 'video/mp4', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `email`, `created_at`) VALUES
(1, 'danny07', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'danny@gmail.com', '2025-08-01 16:09:30'),
(2, 'danny04', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'danny04@gmail.com', '2025-08-02 23:25:05'),
(3, 'test', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test@gmail.com', '2025-08-02 23:31:57'),
(4, 'test2', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test2@gmail.com', '2025-08-02 23:36:03'),
(5, 'test3', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test3@gmail.com', '2025-08-02 23:37:29'),
(6, 'test4', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test4@gmail.com', '2025-08-02 23:37:55'),
(7, 'test6', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'test6@gmail.com', '2025-08-02 23:40:26'),
(8, 'phuong', 'b093c3890ce8360a4e447e2f4ed16587c06d6f6b59109e5be907ec98f5f97a4f', 'phuong@gmail.com', '2025-08-28 21:42:46'),
(10, 'tuananh', 'db36ec7774a41dca97b8fd4eb5999484cf2c7fd843a1c51fce45d02ecd6a82fb', 'anh@gmail.com', '2025-08-29 21:10:11');

-- --------------------------------------------------------

--
-- Table structure for table `user_profiles`
--

CREATE TABLE `user_profiles` (
  `user_id` int(11) NOT NULL,
  `display_name` varchar(100) DEFAULT '',
  `bio` text DEFAULT '',
  `gender` enum('male','female','other','not_specified') DEFAULT 'not_specified',
  `birth_date` date DEFAULT NULL,
  `phone` varchar(20) DEFAULT '',
  `location` varchar(100) DEFAULT '',
  `avatar_url` varchar(255) DEFAULT '',
  `privacy_settings` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`privacy_settings`)),
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_profiles`
--

INSERT INTO `user_profiles` (`user_id`, `display_name`, `bio`, `gender`, `birth_date`, `phone`, `location`, `avatar_url`, `privacy_settings`, `created_at`, `updated_at`) VALUES
(1, 'Danny Nguyễn', 'Yêu thích công nghệ, thích lập trình.', 'male', '2000-01-01', '0901234567', 'Hà Nội', '', NULL, '2025-08-27 22:07:46', '2025-08-27 22:07:46'),
(2, 'Phương Trần', 'Thích du lịch, thích đọc sách.', 'female', '2001-05-12', '0912345678', 'TP.HCM', '', NULL, '2025-08-27 22:07:46', '2025-08-27 22:07:46'),
(3, 'Test User', 'Tôi là người dùng thử nghiệm.', 'male', NULL, '', 'Đà Nẵng', '', NULL, '2025-08-27 22:07:46', '2025-08-28 21:35:57'),
(4, 'Nguyễn Văn A', 'Chào mọi người!', 'male', '1999-12-31', '', 'Hải Phòng', '', NULL, '2025-08-27 22:07:46', '2025-08-27 22:07:46'),
(5, 'Trần Thị B', 'Sống và làm việc tại Sài Gòn.', 'female', '2002-07-15', '0987654321', 'TP.HCM', '', NULL, '2025-08-27 22:07:46', '2025-08-27 22:07:46');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `friends`
--
ALTER TABLE `friends`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_friendship` (`user1_id`,`user2_id`),
  ADD KEY `user2_id` (`user2_id`);

--
-- Indexes for table `friend_requests`
--
ALTER TABLE `friend_requests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_request` (`from_user_id`,`to_user_id`),
  ADD KEY `to_user_id` (`to_user_id`);

--
-- Indexes for table `group_chat`
--
ALTER TABLE `group_chat`
  ADD PRIMARY KEY (`group_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `group_members`
--
ALTER TABLE `group_members`
  ADD PRIMARY KEY (`group_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `group_messages`
--
ALTER TABLE `group_messages`
  ADD PRIMARY KEY (`message_group_id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `group_id` (`group_id`);

--
-- Indexes for table `private_messages`
--
ALTER TABLE `private_messages`
  ADD PRIMARY KEY (`message_private_id`),
  ADD KEY `idx_receiver_read` (`receiver_id`,`is_read`),
  ADD KEY `idx_sender_time` (`sender_id`,`time_send`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_profiles`
--
ALTER TABLE `user_profiles`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `friends`
--
ALTER TABLE `friends`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `friend_requests`
--
ALTER TABLE `friend_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `group_chat`
--
ALTER TABLE `group_chat`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `group_messages`
--
ALTER TABLE `group_messages`
  MODIFY `message_group_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `private_messages`
--
ALTER TABLE `private_messages`
  MODIFY `message_private_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `friends`
--
ALTER TABLE `friends`
  ADD CONSTRAINT `friends_ibfk_1` FOREIGN KEY (`user1_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `friends_ibfk_2` FOREIGN KEY (`user2_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `friend_requests`
--
ALTER TABLE `friend_requests`
  ADD CONSTRAINT `friend_requests_ibfk_1` FOREIGN KEY (`from_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `friend_requests_ibfk_2` FOREIGN KEY (`to_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `group_chat`
--
ALTER TABLE `group_chat`
  ADD CONSTRAINT `group_chat_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `group_members`
--
ALTER TABLE `group_members`
  ADD CONSTRAINT `group_members_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `group_chat` (`group_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `group_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `group_messages`
--
ALTER TABLE `group_messages`
  ADD CONSTRAINT `group_messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `group_messages_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `group_chat` (`group_id`) ON DELETE CASCADE;

--
-- Constraints for table `private_messages`
--
ALTER TABLE `private_messages`
  ADD CONSTRAINT `private_messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `private_messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_profiles`
--
ALTER TABLE `user_profiles`
  ADD CONSTRAINT `user_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
