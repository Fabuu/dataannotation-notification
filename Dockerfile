# Use official Python image which supports ARM64 (Raspberry Pi)
FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
# This step is critical for ARM64 to ensure correct binaries are downloaded
RUN playwright install --with-deps chromium

COPY bot.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
