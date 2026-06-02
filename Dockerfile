FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Runtime configuration
ENV APP_ENV=prod
ENV OBSIDIA_API_HOST=0.0.0.0
ENV OBSIDIA_API_PORT=8000

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "apps.obsidia_api.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
