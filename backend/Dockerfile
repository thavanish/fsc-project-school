FROM python:3.11-slim

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN pip install --no-cache-dir dlib-bin face-recognition-models


RUN pip install --no-cache-dir --no-deps face-recognition==1.3.0

COPY . .
RUN mkdir -p data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
