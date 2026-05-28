FROM python:3.11

# dlib needs cmake + a C++ compiler, and face_recognition builds it from source.
# This takes ~10 minutes on first build — it's a one-time cost.
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dlib first so Docker can cache that layer separately.
# Rebuilding the app code won't retrigger the dlib compile.
RUN pip install --no-cache-dir dlib==19.24.2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The data directory holds the face encodings pickle file.
RUN mkdir -p data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
