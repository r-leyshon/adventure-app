# Build stage
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd -m shiny-user

# Set the working directory
WORKDIR /app

# Copy installed dependencies from builder stage, 3rd party installs go in
# site-packages, shiny and other CLI tools like shiny go in bin.
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages 
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy only necessary files
COPY app.py .
COPY www ./www

# Change ownership of the app directory
RUN chown -R shiny-user:shiny-user /app

# Switch to non-root user
USER shiny-user

# Expose the port
EXPOSE 8000/tcp 

# Run the application
CMD ["shiny", "run", "/app/app.py", "--host", "0.0.0.0", "--port", "8000"]
