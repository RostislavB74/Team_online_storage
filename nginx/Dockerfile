# Use official Nginx image from Docker Hub
FROM nginx:alpine

# Copy the Nginx configuration file
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the static files from the Django container (static files should be collected)
# COPY ./staticfiles /staticfiles
COPY ./project_1444/media /mediafiles

# Expose port 80 for HTTP traffic
EXPOSE 8080
