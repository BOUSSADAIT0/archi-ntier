FROM nginx:alpine

# Copier la configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers du frontend
COPY . /usr/share/nginx/html/

# Exposer le port 80
EXPOSE 80 