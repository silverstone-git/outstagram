# Outstagram

A fastapi server for social media frontends to connect to


## Installation

Make a virtual environment with

```bash

python -m venv your_venv_name
source ./your_venv_name/bin/activate

```

Pip Packages needed (Install using `pip install`)
- fastapi[all]
- passlib
- python-jose
- argon2-cffi


## Running

Development server ->

```bash

fastapi dev main.py

```

## Environment Variables

### for the mysql database
- OUTSTAGRAM_USERNAME
- OUTSTAGRAM_PASSWORD
- OUTSTAGRAM_DBNAME

### JWT Secret key
- OUTSTAGRAM_SECRET_KEY


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
    user1_id INT PRIMARY KEY,
    user2_id INT PRIMARY KEY,
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
    "fullname": "YOUR_FULL_NAME",
    "username": "YOUR_USERNAME",
    "bio": "YOUR_BIO",
    "email": "YOUR_EMAIL",
    "password": "YOUR_PASSWORD",
    "date_of_birth": "1970-01-01"
  }' \
  http://localhost:8000/register

```

- for access token

```bash

curl -X POST \
http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_USERNAME&password=YOUR_PASSWORD"
```


- for posting

```bash
curl -X POST \
http://localhost:8000/posts \
-H "Authorization: Bearer YOUR_BEARER_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "media_urls": ["YOUR_MEDIA_URL1", "YOU_MEDIA_URL2"],
    "highlighted_by_author": YOUR_HIGHLIGHTED_SELECTION,
    "caption": "YOUR_CAPTION",
    "post_category": "YOUR_POST_CATEGORY",
}'

```

- for liking
```bash

curl -X POST \
    http://localhost:8000/posts/{YOUR_POST_ID}/like \
     -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
     -H "Content-Type: application/json"
```

- for commenting

```bash

curl -X POST \
  http://localhost:8000/posts/{YOUR_POST_ID}/comment \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "YOUR_COMMENT"
  }'
```

- for getting the likes on a Post

```bash

curl http://localhost:8000/posts/{YOUR_POST_ID}/likes/{PAGE_NUMBER} \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json"

```

- for getting the comments on a post

```bash

curl http://localhost:8000/posts/{YOUR_POST_ID}/comments/{PAGE_NUMBER} \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json"

```

- for getting a post

```bash

curl http://localhost:8000/posts/{YOUR_POST_ID} \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json"

```

- for getting the user dashboard information: user information and, 'posts' field

```bash 

curl http://localhost:8000/dashboard/{PAGE_NUMBER} \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json"

```

- for sending a follow request to a user

```bash 
curl -X POST \
  http://localhost:8000/users/{USERNAME_TO_FOLLOW}/follow \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json" \

```


- for getting all the follow requests along with request_id for the logged in user

```bash 

curl http://localhost:8000/follow-requests \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json" \

```


- for approving request given the request_id

```bash 

curl -X POST \
  http://localhost:8000/request-approve/{REQUEST_ID_TO_APPROVE} \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json" \

```

- for getting all the posts of a given username

```bash 

curl http://localhost:8000/users/{USERNAME}/posts/{PAGE_NUMBER} \
 -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
 -H "Content-Type: application/json"

```

- for getting the user profile (posts count, followers/following count, they follow you or not or vice versa)

```bash 

curl http://localhost:8000/users/{USERNAME} \
 -H "Authorization: Bearer {YOUR_BEARER_TOKEN}" \
 -H "Content-Type: application/json"

```

