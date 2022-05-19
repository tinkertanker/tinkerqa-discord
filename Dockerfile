FROM python:3.9-slim

RUN apt-get update && apt-get install -y python3-pip
RUN pip install poetry>=1.0.0

COPY . /app
WORKDIR /app
# workaround: https://github.com/python-poetry/poetry/issues/234
RUN poetry config virtualenvs.create false
RUN poetry install


ENTRYPOINT ["python", "bot.py"]
