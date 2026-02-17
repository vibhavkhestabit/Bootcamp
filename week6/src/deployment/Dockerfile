# Use python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
# (We assume the Docker build context is the root project folder)
COPY . .

# Expose port
EXPOSE 8000

# Run the API
# NOTE: We adjust the path assuming deployment/api.py is inside the container
CMD ["uvicorn", "deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]