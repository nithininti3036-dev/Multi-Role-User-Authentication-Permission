-- ====================================================================
-- Initial Seed Data for RBAC System
-- ====================================================================

USE `rbac_db`;

-- --------------------------------------------------------------------
-- 1. Insert Base Permissions
-- --------------------------------------------------------------------
INSERT INTO `permissions` (`id`, `name`, `resource`, `action`, `description`) VALUES
(1, '*:*', 'all', 'all', 'Full wildcard access to every resource'),
(2, 'user:create', 'user', 'create', 'Create new users'),
(3, 'user:read', 'user', 'read', 'View user profiles and list'),
(4, 'user:update', 'user', 'update', 'Modify user information'),
(5, 'user:delete', 'user', 'delete', 'Delete or deactivate users'),
(6, 'user:manage', 'user', 'manage', 'Full management of users'),
(7, 'role:create', 'role', 'create', 'Create custom roles'),
(8, 'role:read', 'role', 'read', 'View roles and their permissions'),
(9, 'role:update', 'role', 'update', 'Modify role details and assign permissions'),
(10, 'role:delete', 'role', 'delete', 'Delete custom roles'),
(11, 'role:assign', 'role', 'assign', 'Assign or unassign roles to users'),
(12, 'permission:read', 'permission', 'read', 'View available system permissions'),
(13, 'permission:create', 'permission', 'create', 'Create new custom permissions'),
(14, 'content:create', 'content', 'create', 'Create new articles or content'),
(15, 'content:read', 'content', 'read', 'View content items'),
(16, 'content:update', 'content', 'update', 'Edit existing content'),
(17, 'content:delete', 'content', 'delete', 'Remove content items'),
(18, 'report:create', 'report', 'create', 'Generate new analytical reports'),
(19, 'report:read', 'report', 'read', 'Access business reports'),
(20, 'report:export', 'report', 'export', 'Export reports to CSV/PDF'),
(21, 'report:delete', 'report', 'delete', 'Delete reports'),
(22, 'audit:read', 'audit', 'read', 'View system audit security logs'),
(23, 'system:admin', 'system', 'admin', 'Access system maintenance endpoints')
ON DUPLICATE KEY UPDATE `description` = VALUES(`description`);

-- --------------------------------------------------------------------
-- 2. Insert Core Roles
-- --------------------------------------------------------------------
INSERT INTO `roles` (`id`, `name`, `description`, `is_system`) VALUES
(1, 'SuperAdmin', 'Full unrestricted system owner access', TRUE),
(2, 'Admin', 'System administrator with user, role, and resource management rights', TRUE),
(3, 'Manager', 'Department manager with content & reporting permissions', TRUE),
(4, 'User', 'Standard registered member with default read access', TRUE)
ON DUPLICATE KEY UPDATE `description` = VALUES(`description`);

-- --------------------------------------------------------------------
-- 3. Map Roles to Permissions
-- --------------------------------------------------------------------
-- SuperAdmin has wildcard (*:*) and all permissions
INSERT IGNORE INTO `role_permissions` (`role_id`, `permission_id`)
SELECT 1, id FROM `permissions`;

-- Admin has all permissions except wildcard
INSERT IGNORE INTO `role_permissions` (`role_id`, `permission_id`)
SELECT 2, id FROM `permissions` WHERE `name` != '*:*';

-- Manager has user:read, content:*, and report:*
INSERT IGNORE INTO `role_permissions` (`role_id`, `permission_id`)
SELECT 3, id FROM `permissions` WHERE `name` IN (
    'user:read',
    'content:create', 'content:read', 'content:update',
    'report:create', 'report:read', 'report:export'
);

-- User has content:read and report:read
INSERT IGNORE INTO `role_permissions` (`role_id`, `permission_id`)
SELECT 4, id FROM `permissions` WHERE `name` IN (
    'content:read', 'report:read'
);

-- --------------------------------------------------------------------
-- 4. Insert Default Users
-- Default Passwords:
-- admin@example.com / Admin@123456
-- user@example.com  / User@123456
-- manager@example.com / Manager@123456
-- --------------------------------------------------------------------
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `full_name`, `is_active`, `is_verified`) VALUES
(1, 'superadmin', 'admin@example.com', '$2b$12$K17/g35c91uKmsiV96W0v.FfOq/O.24/P.Y16y0oF.6xN.YfX.9wW', 'Master Administrator', TRUE, TRUE),
(2, 'sarah_manager', 'manager@example.com', '$2b$12$K17/g35c91uKmsiV96W0v.FfOq/O.24/P.Y16y0oF.6xN.YfX.9wW', 'Sarah Jenkins', TRUE, TRUE),
(3, 'johndoe', 'user@example.com', '$2b$12$K17/g35c91uKmsiV96W0v.FfOq/O.24/P.Y16y0oF.6xN.YfX.9wW', 'John Doe', TRUE, TRUE)
ON DUPLICATE KEY UPDATE `full_name` = VALUES(`full_name`);

-- --------------------------------------------------------------------
-- 5. Map Users to Roles
-- --------------------------------------------------------------------
INSERT IGNORE INTO `user_roles` (`user_id`, `role_id`) VALUES
(1, 1), -- superadmin -> SuperAdmin
(1, 2), -- superadmin -> Admin
(2, 3), -- sarah_manager -> Manager
(3, 4); -- johndoe -> User
