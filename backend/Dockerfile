FROM python:3.11-slim

WORKDIR /app

COPY ./backend/requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./backend /app

CMD ["sleep", "infinity"]
