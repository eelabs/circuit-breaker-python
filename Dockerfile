FROM python:3.8

WORKDIR /app

ENV REDIS_HOST=redis

CMD ["make"]