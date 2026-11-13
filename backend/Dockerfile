# Python image (slim = kleiner)
FROM python:3.13-slim
WORKDIR /app

# Eerst requirements kopiëren voor caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Code en data kopiëren
COPY . .

# Run als non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
