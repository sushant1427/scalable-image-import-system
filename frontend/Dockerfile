FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config from project root
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend static files
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/style.css /usr/share/nginx/html/style.css
COPY frontend/app.js /usr/share/nginx/html/app.js

