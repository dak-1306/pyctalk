-- Update schema to support media messages (images, files)

USE pyctalk;

-- Add columns to private_messages table for media support
ALTER TABLE private_messages 
ADD COLUMN message_type ENUM('text', 'image', 'file', 'audio', 'video') DEFAULT 'text',
ADD COLUMN file_path VARCHAR(500) NULL,
ADD COLUMN file_name VARCHAR(255) NULL,
ADD COLUMN file_size BIGINT NULL,
ADD COLUMN mime_type VARCHAR(100) NULL,
ADD COLUMN thumbnail_path VARCHAR(500) NULL;

-- Add columns to group_messages table for media support  
ALTER TABLE group_messages
ADD COLUMN message_type ENUM('text', 'image', 'file', 'audio', 'video') DEFAULT 'text',
ADD COLUMN file_path VARCHAR(500) NULL,
ADD COLUMN file_name VARCHAR(255) NULL,
ADD COLUMN file_size BIGINT NULL,
ADD COLUMN mime_type VARCHAR(100) NULL,
ADD COLUMN thumbnail_path VARCHAR(500) NULL;

-- Create uploads directory structure
-- Note: This will be handled by Python code to create actual directories
