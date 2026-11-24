# Canlı nginx. Build bağlamı proje köküdür. Yerelde kullanılmaz; yerelde ayar dosyası bağlanır.
FROM nginx:1.28-alpine
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY backend/public /var/www/html/public
