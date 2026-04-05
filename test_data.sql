USE `todo_list`;

-- ======================
-- Users (password: 123123)
-- ======================
INSERT INTO `users` (`username`, `first_name`, `last_name`, `email`, `birthdate`, `contact_number`, `hashed_password`, `is_verified`) VALUES
('johndoe',   'John',  'Doe',     'john@example.com',  '1995-03-12', '0901234567', '$2b$12$cpVR1BgwLZBEa4INltQgW.v1I08q3Ma3t0G0lvscxF02tvegTJRvC', TRUE),
('janedoe',   'Jane',  'Doe',     'jane@example.com',  '1998-07-24', '0912345678', '$2b$12$cpVR1BgwLZBEa4INltQgW.v1I08q3Ma3t0G0lvscxF02tvegTJRvC', TRUE),
('minhtu',    'Minh',  'Tu',      'minh@example.com',  '2000-01-15', '0923456789', '$2b$12$cpVR1BgwLZBEa4INltQgW.v1I08q3Ma3t0G0lvscxF02tvegTJRvC', TRUE),
('unverified','Test',  'Unverified','unverified@example.com', NULL, NULL,          '$2b$12$cpVR1BgwLZBEa4INltQgW.v1I08q3Ma3t0G0lvscxF02tvegTJRvC', FALSE);

-- ======================
-- Projects
-- ======================
INSERT INTO `projects` (`user_id`, `title`, `description`, `created_at`, `updated_at`) VALUES
(1, 'Personal Website', 'Build a portfolio website from scratch', '2024-01-10 08:00:00', '2024-01-10 08:00:00'),
(1, 'Fitness Tracker', 'Track daily workouts and calories', '2024-02-05 09:30:00', '2024-02-05 09:30:00'),
(2, 'Recipe Blog', 'A blog for sharing cooking recipes', '2024-03-01 10:00:00', '2024-03-01 10:00:00'),
(3, 'Study Planner', 'Plan and track study sessions', '2024-03-15 11:00:00', '2024-03-15 11:00:00');

-- ======================
-- Tasks
-- ======================
INSERT INTO `tasks` (`project_id`, `task_index`, `title`, `description`, `due_date`, `status`, `created_at`, `updated_at`) VALUES
-- Project 1: Personal Website
(1, 1, 'Design wireframes',     'Sketch layout for homepage and about page',  '2024-01-15 23:59:59', 1, '2024-01-10 08:00:00', '2024-01-15 20:00:00'),
(1, 2, 'Setup hosting',         'Configure VPS and domain',                   '2024-01-20 23:59:59', 1, '2024-01-10 08:00:00', '2024-01-20 18:00:00'),
(1, 3, 'Build homepage',        'Implement HTML/CSS for homepage',             '2024-02-01 23:59:59', 0, '2024-01-10 08:00:00', '2024-01-10 08:00:00'),
(1, 4, 'Add contact form',      'Implement contact form with email sending',   '2024-02-10 23:59:59', 0, '2024-01-10 08:00:00', '2024-01-10 08:00:00'),

-- Project 2: Fitness Tracker
(2, 1, 'Define data model',     'Design schema for workouts and calories',     '2024-02-10 23:59:59', 1, '2024-02-05 09:30:00', '2024-02-10 15:00:00'),
(2, 2, 'Build input form',      'Create form for logging daily workouts',      '2024-02-20 23:59:59', 0, '2024-02-05 09:30:00', '2024-02-05 09:30:00'),
(2, 3, 'Add progress chart',    'Visualize weekly progress with charts',       '2024-03-01 23:59:59',-1, '2024-02-05 09:30:00', '2024-02-05 09:30:00'),

-- Project 3: Recipe Blog
(3, 1, 'Setup WordPress',       'Install and configure WordPress',             '2024-03-10 23:59:59', 1, '2024-03-01 10:00:00', '2024-03-10 12:00:00'),
(3, 2, 'Write first post',      'Publish first recipe article',                '2024-03-20 23:59:59', 0, '2024-03-01 10:00:00', '2024-03-01 10:00:00'),
(3, 3, 'Design theme',          'Customize blog theme and colors',             '2024-04-01 23:59:59', 0, '2024-03-01 10:00:00', '2024-03-01 10:00:00'),

-- Project 4: Study Planner
(4, 1, 'List study subjects',   'List all subjects and topics to cover',       '2024-03-20 23:59:59', 1, '2024-03-15 11:00:00', '2024-03-20 09:00:00'),
(4, 2, 'Create weekly schedule','Plan study sessions for each week',           '2024-03-25 23:59:59', 1, '2024-03-15 11:00:00', '2024-03-25 10:00:00'),
(4, 3, 'Mock exam prep',        'Prepare practice questions for each subject', '2024-04-05 23:59:59', 0, '2024-03-15 11:00:00', '2024-03-15 11:00:00');