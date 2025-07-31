create database pyctalk;
use pyctalk;

create table users (
    User_id int not null primary key AUTO_INCREMENT ,
    Username char(30) unique not null,
    Password_hash char(255),
    Email char(30) unique not null,
    Created_at datetime default current_timestamp
);

create table friends (
    user1_id int not null,
    user2_id int not null,
    requester_id int not null, -- người gửi lời mời
    status enum('pending', 'accepted', 'rejected') not null default 'pending',
    created_at datetime default current_timestamp,
    primary key (user1_id, user2_id),
    foreign key (user1_id) references users(user_id) on delete cascade,
    foreign key (user2_id) references users(user_id) on delete cascade,
    foreign key (requester_id) references users(user_id) on delete cascade
);
-- khi INSERT, bạn phải sắp user1_id < user2_id để đảm bảo tính duy nhất của quan hệ.
-- A (ID=3) gửi lời mời kết bạn B (ID=5):
-- vì 3 < 5 nên user1_id = 3, user2_id = 5
-- INSERT INTO friends (user1_id, user2_id, requester_id, status)
-- VALUES (3, 5, 3, 'pending');
-- B chấp nhận:
-- UPDATE friends
-- SET status = 'accepted'
-- WHERE user1_id = 3 AND user2_id = 5;
-- B từ chối:
-- UPDATE friends
-- SET status = 'rejected'
-- WHERE user1_id = 3 AND user2_id = 5;
-- Truy vấn bạn bè:
-- Lấy danh sách bạn bè của user_id = 3
-- SELECT u.*
-- FROM friends f
-- JOIN users u ON (u.user_id = IF(f.user1_id = 3, f.user2_id, f.user1_id))
-- WHERE (f.user1_id = 3 OR f.user2_id = 3) AND f.status = 'accepted';

-- Bảng nhóm chat
create table group_chat (
    group_id int not null primary key auto_increment,
    group_name text not null,
    created_by int not null,
    foreign key (created_by) references users(user_id) on delete cascade
);

-- Bảng tin nhắn 1-1
create table private_messages (
    message_private_id int not null primary key auto_increment,
    sender_id int not null,
    receiver_id int not null,  -- Có thể là user_id hoặc group_id tùy thuộc type
    content text not null,
    time_send datetime default current_timestamp,
    foreign key (sender_id) references users(user_id) on delete cascade,
    foreign key (receiver_id) references users(user_id) on delete cascade
);

-- Bảng tin nhắn nhóm
create table group_messages (
    message_group_id int not null primary key auto_increment,
    sender_id int not null,
    group_id int not null,  -- Có thể là user_id hoặc group_id tùy thuộc type
    content text not null,
    time_send datetime default current_timestamp,
    foreign key (sender_id) references users(user_id) on delete cascade,
    foreign key (group_id) references group_chat(group_id) on delete cascade
);

-- Bảng thành viên nhóm
create table group_members (
    group_id int not null,
    user_id int not null,
    primary key (group_id, user_id),
    foreign key (group_id) references group_chat(group_id) on delete cascade,
    foreign key (user_id) references users(user_id) on delete cascade
);

