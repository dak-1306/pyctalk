-- Add message status tracking to private_messages table
USE pyctalk;

-- Add columns for message status
ALTER TABLE private_messages 
ADD COLUMN is_read BOOLEAN DEFAULT FALSE,
ADD COLUMN read_at DATETIME NULL;

-- Add index for better performance on unread messages queries
CREATE INDEX idx_receiver_read ON private_messages (receiver_id, is_read);
CREATE INDEX idx_sender_time ON private_messages (sender_id, time_send);
