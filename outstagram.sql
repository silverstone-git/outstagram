-- Create the user table
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    fullname VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    bio TEXT,
    date_of_birth DATE
);

-- Create the media_url table
CREATE TABLE mediaurl (
    post_id VARCHAR(255),
    url VARCHAR(255) NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post(post_id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, url)
);

-- Create the post table
CREATE TABLE post (
    post_id VARCHAR(255) PRIMARY KEY AUTO_INCREMENT,
    media_url_id INT,
    caption TEXT,
    post_category ENUM('tech', 'entertainment', 'business', 'vlog', 'lifestyle') NOT NULL,
    datetime_posted DATETIME DEFAULT CURRENT_TIMESTAMP,
    author_user_id INT,
    highlighted_by_author BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (author_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Create the post_comment table
CREATE TABLE postcomment (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    post_id VARCHAR(255),
    content TEXT NOT NULL,
    author_user_id INT,
    datetime_commented DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES post(post_id) ON DELETE CASCADE,
    FOREIGN KEY (author_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Create the post_like table
CREATE TABLE postlike (
    post_id VARCHAR(255),
    liker_user_id INT,
    datetime_liked DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, liker_user_id),
    FOREIGN KEY (post_id) REFERENCES post(post_id) ON DELETE CASCADE,
    FOREIGN KEY (liker_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Create the post_comment_like table
CREATE TABLE postcommentlike (
    comment_id INT,
    liker_user_id INT,
    datetime_liked DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (comment_id, liker_user_id),
    FOREIGN KEY (comment_id) REFERENCES postcomment(comment_id) ON DELETE CASCADE,
    FOREIGN KEY (liker_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);


CREATE TABLE followrequest (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    requester_user_id INT,
    requested_user_id INT,
    datetime_requested DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (requester_user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (requested_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE friendship (
    friendship_id INT PRIMARY KEY AUTO_INCREMENT,
    user1_id INT,
    user2_id INT,
    datetime_friended DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES user(user_id) ON DELETE CASCADE,
    UNIQUE (user1_id, user2_id)  -- Ensure that each friendship is unique
);

