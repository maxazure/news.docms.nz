FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

EXPOSE 8009

CMD ["gunicorn", "--bind", "0.0.0.0:8009", "app:app"]