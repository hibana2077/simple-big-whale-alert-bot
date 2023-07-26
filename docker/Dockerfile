FROM python:3.10-alpine3.17

RUN apk add py3-pip

ENV PYTHONUNBUFFERED=1
ENV ALCHEMYTOKEN="yourkey"
ENV DISCORDWEBHOOK="yourwebhook"
ENV THRESHOLD=10000

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ../src .

CMD ["python", "main.py", "-at", "$ALCHEMYTOKEN", "-dw", "$DISCORDWEBHOOK", "-t", "$THRESHOLD"]