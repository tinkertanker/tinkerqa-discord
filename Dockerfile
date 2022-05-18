FROM python:3.9-slim

RUN apt-get update && apt-get install -y python3-pip
RUN pip install poetry>=1.0.0

COPY . /app

WORKDIR /app

RUN poetry install

ENTRYPOINT ["python", "bot.py"]