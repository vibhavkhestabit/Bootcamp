# Use python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements (assumes requirements.txt is in week6/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (src, models, data) into the container
COPY . .

# Expose port
EXPOSE 8000

# Run the API from the root using the "src" package path
CMD ["uvicorn", "src.deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]