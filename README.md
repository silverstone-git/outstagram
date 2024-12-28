# Outstagram

A fastapi server for social media frontends to connect to


## Installation and running

Pip Packages needed
- fastapi[all]
- passlib
- python-jose
- argon2-cffi


## Running

Development server ->

```bash

fastapi dev main.py

```


## Entity Sets
- user
- post
- post_comment
- media_url

## Tables
- user -> user_id, fullname, username, email, password, bio, date_of_birth
- post -> post_id, media_url_id, caption, post_category (tech/entertainment/business/vlog/lifestyle), datetime_posted, author_user_id, highlighted_by_author (boolean)
- mediaurl -> post_id, url -> both primary key
- postcomment -> comment_id, post_id, content, author_user_id, datetime_commented
- postlike -> post_id, liker_user_id, datetime_liked -> first two primary key
- postcomment_like -> comment_id, liker_user_id, datetime_liked
- friendship (
    friendship_id INT PRIMARY KEY AUTO_INCREMENT,
    user1_id INT,
    user2_id INT,
    datetime_friended DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES user(user_id) ON DELETE CASCADE,
    UNIQUE (user1_id, user2_id)  -- Ensure that each friendship is unique
);

- followrequest (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    requester_user_id INT,
    requested_user_id INT,
    datetime_requested DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (requester_user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (requested_user_id) REFERENCES user(user_id) ON DELETE CASCADE
);


## Test Queries

- for account creation

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "yourfullname",
    "username": "yourusername",
    "bio": "yourbio",
    "email": "youremail@example.com",
    "password": "very complicated password",
    "date_of_birth": "1970-01-01"
  }' \
  http://127.0.0.1:8000/register

```

- for access token

```bash

curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=yourusername&password=yourpassword"
```


- for posting

```bash
curl -X POST "http://localhost:8000/posts" \
-H "Authorization: Bearer YOUR_BEARER_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "post_id": "dummy field",
    "author": "dummy field",
    "media_urls": ["YOUR_MEDIA_URL1", "YOU_MEDIA_URL2"],
    "highlighted_by_author": YOUR_HIGHLIGHTED_SELECTION,
    "caption": "YOUR_CAPTION",
    "post_category": "YOUR_POST_CATEGORY",
    "datetime_posted": "1970-01-01",
}'

```
