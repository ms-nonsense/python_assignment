FROM python:3.10-slim-bullseye
ENV PYTHONUNBUFFERED 1

WORKDIR /financial

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD [ "python", "app.py"]
