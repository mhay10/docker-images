FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install script dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy python script
COPY app.py .

# Expose port server runs on
EXPOSE 4000

# Command to run server
CMD ["python", "app.py"]