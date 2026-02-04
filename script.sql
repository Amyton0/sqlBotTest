CREATE TABLE videos (
    id TEXT PRIMARY KEY,
    video_created_at DATE,
    views_count INT,
    likes_count INT,
    reports_count INT,
    comments_count INT,
    creator_id TEXT,
    created_at DATE,
    updated_at DATE
);

CREATE TABLE video_snapshots (
    id TEXT PRIMARY KEY,
    video_created_at DATE,
    views_count INT,
    likes_count INT,
    reports_count INT,
    comments_count INT,
    delta_views_count INT,
    delta_likes_count INT,
    delta_reports_count INT,
    delta_comments_count INT,
    created_at DATE,
    updated_at DATE
);
