-- Create database
CREATE DATABASE IF NOT EXISTS `todo_list`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `todo_list`;

-- ======================
-- Table: user
-- ======================
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL UNIQUE,
    `first_name` VARCHAR(100),
    `last_name` VARCHAR(100),
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `birthdate` DATE,
    `contact_number` VARCHAR(20),
    `hashed_password` VARCHAR(255) NOT NULL,
    `is_verified` BOOLEAN DEFAULT FALSE,
    `verification_code` INT,
	`code_expire_time` DATETIME
) ENGINE=InnoDB;

-- ======================
-- Table: project
-- ======================
CREATE TABLE `projects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT `fk_project_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ======================
-- Table: task
-- ======================
CREATE TABLE `tasks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `project_id` INT NOT NULL,
    `task_index` INT,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `due_date` DATETIME,
    `status` INT DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT `fk_task_project`
        FOREIGN KEY (`project_id`)
        REFERENCES `projects`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;