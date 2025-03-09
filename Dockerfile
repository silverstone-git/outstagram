FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./lib /app/lib
COPY ./src /app/src
COPY ./main.py /app/main.py
COPY ./__init__.py /app/__init__.py

EXPOSE 8671

CMD ["fastapi", "run", "/app/main.py", "--port", "8671"]

