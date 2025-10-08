FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

# Copy the SSL certificate (already in backend folder)
COPY ca-certificate.crt /app/ca-certificate.crt

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY . .

ENV FLASK_APP=app.py 
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
