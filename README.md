# Outstagram

A fastapi server for social media frontends to connect to. Outstagram helps users maintain a healthy balance of social life and student life by allowing them to submit their exam results, compare with their friends, and grow together as a group.


## Installation

Make a virtual environment with

```bash

python -m venv your_venv_name
source ./your_venv_name/bin/activate

```

### Pip Packages needed

Install using `pip install -r requirements.txt`


## Environment Variables

### Run-time variables, for the postgres database
- OUTSTAGRAM_USERNAME
- OUTSTAGRAM_PASSWORD
- OUTSTAGRAM_DBNAME
- OUTSTAGRAM_DBHOST

### Run-time, variable, JWT Secret key
- OUTSTAGRAM_SECRET_KEY

### Build-time variables, for the docker building / fetching
- DOCKER_USERNAME=cyt0
- LATEST_TAG=latest


## Running

Development server ->

```bash

fastapi dev main.py

```

Production server ->

```bash

fastapi run main.py --port {YOUR_DESIRED_PORT}

```

### Running using Docker

- As an alternative to cloning the repository, you can directly install and run using the [docker image](https://hub.docker.com/r/cyt0/outstagram)

```bash

mkdir outstagram
cd outstagram
curl -L -o ./docker-compose.yaml https://raw.githubusercontent.com/silverstone-git/outstagram/main/docker-compose.yaml
docker-compose pull
docker-compose down
docker-compose up -d

```



## Entity Sets
- user
- post
- post_comment
- media_url
- exam



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
    "media_urls": [{"url": "YOUR_MEDIA_URL1", "media_type": "image"}, {"url": "YOUR_MEDIA_URL2", "media_type": "video"}],
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

- for getting the post feed (reverse chronological order, with category and page optional url params)

```bash 

curl "http://localhost:8000/feed?page={PAGE_NUMBER}&category={YOUR_POST_CATEGORY}" \
 -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
 -H "Content-Type: application/json"

```

- for creating an exam

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d 
  '{
    "exam_title": "YOUR_EXAM_TITLE",
    "exam_json_str": "{\"subject\": \"Maths\", \"marks\": 100}"
  }' \
  http://localhost:8000/pariksha
```

- for getting all exams

```bash
curl http://localhost:8000/pariksha
```

- for getting a specific exam

```bash
curl http://localhost:8000/pariksha/{YOUR_EXAM_ID}
```
