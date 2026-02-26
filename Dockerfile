FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY run_app.sh .
COPY auto-restore.py ./
COPY docker-setup_vector_db.py ./
COPY docker-entrypoint.sh ./

# Make scripts executable
RUN chmod +x run_app.sh docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p app/chat_history/prompts

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=5)" || exit 1

# Run the application with auto-restore
CMD ["./docker-entrypoint.sh"] 