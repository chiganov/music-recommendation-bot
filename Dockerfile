FROM python:3.7-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app /app/app

ENV PYTHONPATH=/app
CMD ["python", "/app/app/main.py"]
