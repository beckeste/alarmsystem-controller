# Verwende das offizielle Nginx-Image
FROM nginx:alpine

# Kopiere die statische Website und die nginx-Konfiguration
COPY index.html /usr/share/nginx/html/index.html
COPY app.js /usr/share/nginx/html/app.js
COPY nginx.conf /etc/nginx/nginx.conf