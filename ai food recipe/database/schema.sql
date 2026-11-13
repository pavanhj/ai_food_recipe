-- ========================================================
-- AI Food Recipe Preparation & Recommendation System
-- Database Schema (MySQL Compatible)
-- ========================================================

CREATE DATABASE IF NOT EXISTS `recipe_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `recipe_db`;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Recipes Table
CREATE TABLE IF NOT EXISTS `recipes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `category` VARCHAR(50) NOT NULL DEFAULT 'Main Course',
    `diet_type` VARCHAR(20) NOT NULL DEFAULT 'Veg', -- 'Veg', 'Non-Veg', 'Vegan'
    `prep_time` INT NOT NULL DEFAULT 15,            -- in minutes
    `cook_time` INT NOT NULL DEFAULT 20,            -- in minutes
    `total_time` INT NOT NULL DEFAULT 35,           -- in minutes
    `servings` INT NOT NULL DEFAULT 4,
    `difficulty` VARCHAR(20) NOT NULL DEFAULT 'Medium', -- 'Easy', 'Medium', 'Hard'
    `ingredients` LONGTEXT NOT NULL,                -- JSON array string or newline list
    `instructions` LONGTEXT NOT NULL,               -- JSON array string or numbered steps
    `nutrition` LONGTEXT,                           -- JSON object: calories, protein, carbs, fats
    `image_url` VARCHAR(500) DEFAULT NULL,
    `chef_tips` TEXT,
    `source` VARCHAR(50) DEFAULT 'gemini_ai',       -- 'gemini_ai', 'system', 'manual'
    `views` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_category` (`category`),
    INDEX `idx_diet_type` (`diet_type`),
    INDEX `idx_title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Favourites Table
CREATE TABLE IF NOT EXISTS `favourites` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `recipe_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `unique_user_recipe` (`user_id`, `recipe_id`),
    CONSTRAINT `fk_favourites_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_favourites_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Search History Table
CREATE TABLE IF NOT EXISTS `search_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT DEFAULT NULL,
    `query` VARCHAR(255) NOT NULL,
    `category_filter` VARCHAR(50) DEFAULT NULL,
    `diet_filter` VARCHAR(20) DEFAULT NULL,
    `time_filter` VARCHAR(20) DEFAULT NULL,
    `searched_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_search_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
