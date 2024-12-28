## Entity Sets
- user
- post
- post_comment
- media_url

## Tables
- user -> user_id, fullname, username, bio, date_of_birth
- post -> post_id, media_url_id, caption, post_category (tech/entertainment/business/vlog/lifestyle), datetime_posted, author_user_id, highlighted_by_author (boolean)
- media_url -> media_url_id, post_id, url
- post_comment -> comment_id, post_id, content, author_user_id, datetime_commented
- post_like -> post_id, liker_user_id, datetime_liked
- post_comment_like -> comment_id, liker_user_id, datetime_liked
- friendship (
    friendship_id INT PRIMARY KEY AUTO_INCREMENT,
    user1_id INT,
    user2_id INT,
    datetime_friended DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES user(user_id) ON DELETE CASCADE,
    UNIQUE (user1_id, user2_id)  -- Ensure that each friendship is unique
);

- follow_request (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    requester_user_id INT,
    requested_user_id INT,
    datetime_requested DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (requester_user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (requested_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);
