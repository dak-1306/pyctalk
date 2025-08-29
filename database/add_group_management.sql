-- Add group management features
USE pyctalk;

-- Add role column to group_members table to distinguish admin/member
ALTER TABLE group_members 
ADD COLUMN role ENUM('admin', 'member') DEFAULT 'member';

-- Add created_at column to track when members joined
ALTER TABLE group_members 
ADD COLUMN joined_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Set existing group creators as admin
UPDATE group_members gm
INNER JOIN group_chat gc ON gm.group_id = gc.group_id
SET gm.role = 'admin'
WHERE gm.user_id = gc.created_by;

-- Add indexes for better performance
CREATE INDEX idx_group_role ON group_members (group_id, role);
CREATE INDEX idx_group_joined ON group_members (group_id, joined_at);

-- Add constraint to ensure at least one admin per group
-- (This will be enforced by application logic)
