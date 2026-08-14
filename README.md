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
- PARIKSHA_ADMIN_SECRET

### For CORS
- OUTSTAGRAM_ALLOWED_ORIGIN_1
- OUTSTAGRAM_ALLOWED_ORIGIN_2

### For S3
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
- S3_BUCKET
- S3_ENDPOINT
- S3_REGION

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
- media_url (url, media_type)
- exam
- examsection
- question
- topic
- sectionquestionlink



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

- for unliking
```bash

curl -X DELETE \
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

- for creating an exam (structured with sections)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d \
  '{
    "exam_title": "Physics GATE 2026",
    "exam_json_str": "{\"legacy_support\": true}",
    "sections": [
      {
        "name": "Quantum Mechanics",
        "questions": ["uuid-of-a-question"],
        "marking": {
          "positive": 2.0,
          "negative": 0.66
        },
        "max_attempts": 10
      }
    ]
  }' \
  http://localhost:8000/pariksha
```

- for getting all exams (paginated)

```bash
curl http://localhost:8000/pariksha?page=1
```

**Note:** The `/pariksha` endpoint is paginated, sorted by upload date (latest first), and returns a list of exams without the `exam_json_str` or `sections` fields. To get the full exam details, use the endpoint below.

- for getting a specific exam

```bash
curl http://localhost:8000/pariksha/{YOUR_EXAM_ID}
```

### Question Bank API

- `GET /api/question_bank/topics`: Fetch available topics. Supports optional `?group=<group_name>` to return topics structured by group.
- `GET /api/question_bank/groups`: Fetch all available topic groups.
- `GET /api/question_bank/sample?topic=<slug>&count=<n>&proportions=<easy,medium,hard>`: Sample random questions server-side, with optional weighted sampling based on difficulty proportions.
- `POST /api/question_bank/topics/{slug}`: Append new questions (may create duplicates). Protected by an `PARIKSHA_ADMIN_SECRET` bearer token.
- `PATCH /api/question_bank/topics/{slug}`: Append unique questions only (idempotent). Protected by an `PARIKSHA_ADMIN_SECRET` bearer token.
- `DELETE /api/question_bank/topics/{slug}`: Clear all questions for a topic. Protected by an `PARIKSHA_ADMIN_SECRET` bearer token.

- for adding questions to a topic

```bash
curl -X POST \
  http://localhost:8000/api/question_bank/topics/quantum_mechanics \
  -H "Authorization: Bearer PARIKSHA_ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d \
  '[
    {
      "type": "MCQ",
      "question": "What is the commutator $[x, p]$?",
      "options": [{"label": 1, "value": "$i\\hbar$"}, {"label": 2, "value": "$0$"}],
      "answer_label": 1,
      "explanation": "Fundamental commutation relation"
    }
  ]'
```
