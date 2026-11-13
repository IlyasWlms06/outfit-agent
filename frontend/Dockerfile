# nginx image die al als non-root user draait (luistert op poort 8080)
FROM nginxinc/nginx-unprivileged:alpine

# Onze instellingen: website tonen en /api en /fotos doorsturen naar de backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Website kopiëren
COPY index.html script.js style.css /usr/share/nginx/html/

EXPOSE 8080
