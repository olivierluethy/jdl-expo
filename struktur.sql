-- Struktur für Tabelle `artists`
CREATE TABLE `artists` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `name_norm` varchar(255) NOT NULL,
  `image_url` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `channel_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `channel_id` (`channel_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `badges`
CREATE TABLE `badges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key_name` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` varchar(255) NOT NULL,
  `category` enum('progression','listener','host','social','engagement','special') NOT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `rarity` enum('common','uncommon','rare','epic','legendary') DEFAULT 'common',
  `is_hidden` tinyint(1) DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `available_from` datetime DEFAULT NULL,
  `available_until` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_name` (`key_name`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `guest_users`
CREATE TABLE `guest_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_token` char(36) NOT NULL,
  `nickname` varchar(50) DEFAULT 'Gast',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guest_token` (`guest_token`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `knex_migrations`
CREATE TABLE `knex_migrations` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `batch` int DEFAULT NULL,
  `migration_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `knex_migrations_lock`
CREATE TABLE `knex_migrations_lock` (
  `index` int unsigned NOT NULL AUTO_INCREMENT,
  `is_locked` int DEFAULT NULL,
  PRIMARY KEY (`index`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `playback_history`
CREATE TABLE `playback_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `youtube_id` varchar(11) DEFAULT NULL,
  `session_id` int DEFAULT NULL,
  `played_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `session_id` (`session_id`),
  KEY `youtube_id` (`youtube_id`),
  CONSTRAINT `playback_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `playback_history_ibfk_2` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE SET NULL,
  CONSTRAINT `playback_history_ibfk_3` FOREIGN KEY (`youtube_id`) REFERENCES `youtube_video_cache` (`youtube_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13045 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `playback_sync`
CREATE TABLE `playback_sync` (
  `session_id` int NOT NULL,
  `current_video_id` varchar(11) DEFAULT NULL,
  `progress_seconds` float DEFAULT '0',
  `is_playing` tinyint(1) DEFAULT '0',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `video_start_time` bigint DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `playback_sync_ibfk_2` (`current_video_id`),
  CONSTRAINT `playback_sync_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `playback_sync_ibfk_2` FOREIGN KEY (`current_video_id`) REFERENCES `youtube_video_cache` (`youtube_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `queue_items`
CREATE TABLE `queue_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `video_id` varchar(11) DEFAULT NULL,
  `added_by` int DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `status` enum('queued','playing','played','skipped','archived','suggested') DEFAULT 'queued',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `playedAt` datetime DEFAULT NULL,
  `startedAt` datetime DEFAULT NULL,
  `pause_duration_seconds` int DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `item_type` enum('music','pause') NOT NULL DEFAULT 'music',
  `item_source` enum('user','guest','ai') DEFAULT 'user',
  `voting_round_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `session_video` (`session_id`,`video_id`),
  KEY `added_by` (`added_by`),
  KEY `guest_id` (`guest_id`),
  KEY `queue_items_ibfk_4` (`video_id`),
  KEY `idx_session_status` (`session_id`,`status`),
  KEY `idx_round_status` (`voting_round_id`,`status`),
  KEY `idx_status` (`status`),
  CONSTRAINT `queue_items_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `queue_items_ibfk_2` FOREIGN KEY (`added_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `queue_items_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `guest_users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `queue_items_ibfk_4` FOREIGN KEY (`video_id`) REFERENCES `youtube_video_cache` (`youtube_id`) ON DELETE RESTRICT,
  CONSTRAINT `ck_queue_items_kind` CHECK ((((`item_type` = _utf8mb4'music') and (`video_id` is not null) and (`pause_duration_seconds` is null)) or ((`item_type` = _utf8mb4'pause') and (`video_id` is null) and (`pause_duration_seconds` is not null))))
) ENGINE=InnoDB AUTO_INCREMENT=13593 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `session_invites`
CREATE TABLE `session_invites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `invited_by_user_id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `invited_user_id` int DEFAULT NULL,
  `status` enum('pending','accepted','rejected','revoked') NOT NULL DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  `accepted_at` timestamp NULL DEFAULT NULL,
  `rejected_at` timestamp NULL DEFAULT NULL,
  `revoked_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_invite` (`session_id`,`email`),
  KEY `idx_invited_user` (`invited_user_id`),
  KEY `idx_invited_by` (`invited_by_user_id`),
  KEY `idx_session` (`session_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `session_invites_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_invites_ibfk_2` FOREIGN KEY (`invited_by_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_invites_ibfk_3` FOREIGN KEY (`invited_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `session_participants`
CREATE TABLE `session_participants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `role` enum('host','user','guest') NOT NULL,
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `left_at` timestamp NULL DEFAULT NULL,
  `is_live` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_participant` (`session_id`,`user_id`),
  UNIQUE KEY `unique_guest` (`session_id`,`guest_id`),
  KEY `user_id` (`user_id`),
  KEY `guest_id` (`guest_id`),
  CONSTRAINT `session_participants_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_participants_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `guest_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `session_song_listens`
CREATE TABLE `session_song_listens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `queue_item_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `listened_from` datetime NOT NULL,
  `listened_to` datetime NOT NULL,
  `listen_seconds` int NOT NULL,
  `completed` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_song` (`session_id`,`queue_item_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_guest` (`guest_id`),
  KEY `queue_item_id` (`queue_item_id`),
  CONSTRAINT `session_song_listens_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_song_listens_ibfk_2` FOREIGN KEY (`queue_item_id`) REFERENCES `queue_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_song_listens_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_song_listens_ibfk_4` FOREIGN KEY (`guest_id`) REFERENCES `guest_users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_song_listens_chk_1` CHECK ((((`user_id` is not null) and (`guest_id` is null)) or ((`user_id` is null) and (`guest_id` is not null))))
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `sessions`
CREATE TABLE `sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(100) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ended_at` timestamp NULL DEFAULT NULL,
  `is_live` tinyint(1) DEFAULT '0',
  `is_private` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `shout_likes`
CREATE TABLE `shout_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `shout_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_like` (`shout_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `shout_likes_ibfk_1` FOREIGN KEY (`shout_id`) REFERENCES `shouts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `shout_likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Struktur für Tabelle `shouts`
CREATE TABLE `shouts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `artist_id` int NOT NULL,
  `user_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) DEFAULT '0',
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_artist` (`artist_id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_user` (`user_id`),
  CONSTRAINT `shouts_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`) ON DELETE CASCADE,
  CONSTRAINT `shouts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `shouts_ibfk_3` FOREIGN KEY (`parent_id`) REFERENCES `shouts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Struktur für Tabelle `user_badge_progress`
CREATE TABLE `user_badge_progress` (
  `user_id` int NOT NULL,
  `badge_id` int NOT NULL,
  `current_value` int NOT NULL,
  `target_value` int NOT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`badge_id`),
  KEY `badge_id` (`badge_id`),
  CONSTRAINT `user_badge_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_badge_progress_ibfk_2` FOREIGN KEY (`badge_id`) REFERENCES `badges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `user_badges`
CREATE TABLE `user_badges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `badge_id` int NOT NULL,
  `awarded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_badge` (`user_id`,`badge_id`),
  KEY `badge_id` (`badge_id`),
  CONSTRAINT `user_badges_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_badges_ibfk_2` FOREIGN KEY (`badge_id`) REFERENCES `badges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `users`
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `google_id` varchar(255) DEFAULT NULL,
  `facebook_id` varchar(255) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `imageUrl` varchar(255) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reset_token` varchar(64) DEFAULT NULL,
  `reset_token_expiry` datetime DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `imageType` varchar(255) DEFAULT NULL,
  `imageData` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `google_id` (`google_id`),
  UNIQUE KEY `facebook_id` (`facebook_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `votes`
CREATE TABLE `votes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `queue_item_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `guest_id` int DEFAULT NULL,
  `vote` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_vote_user` (`queue_item_id`,`user_id`),
  UNIQUE KEY `unique_vote_guest` (`queue_item_id`,`guest_id`),
  KEY `user_id` (`user_id`),
  KEY `guest_id` (`guest_id`),
  CONSTRAINT `votes_ibfk_1` FOREIGN KEY (`queue_item_id`) REFERENCES `queue_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `votes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `votes_ibfk_3` FOREIGN KEY (`guest_id`) REFERENCES `guest_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13087 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `voting_rounds`
CREATE TABLE `voting_rounds` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `started_by_user_id` int DEFAULT NULL,
  `started_by_guest_id` int DEFAULT NULL,
  `started_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ends_at` timestamp NULL DEFAULT NULL,
  `phase` enum('suggestion','voting','closed') NOT NULL DEFAULT 'suggestion',
  `phase_ends_at` datetime DEFAULT NULL,
  `suggestion_duration` int DEFAULT '90',
  `voting_duration` int DEFAULT '60',
  `max_suggestions` int DEFAULT '10',
  `status` enum('open','closed','computed') DEFAULT 'open',
  `winner_queue_item_id` int DEFAULT NULL,
  `quorum_percent` float DEFAULT '0.66',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `voting_rounds_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20640 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Struktur für Tabelle `youtube_video_cache`
CREATE TABLE `youtube_video_cache` (
  `id` int NOT NULL AUTO_INCREMENT,
  `youtube_id` varchar(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `title_norm` varchar(255) NOT NULL,
  `artist_id` int DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `thumbnail` text,
  `cached_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `youtube_id` (`youtube_id`),
  KEY `artist_id` (`artist_id`),
  CONSTRAINT `youtube_video_cache_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=132576 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

