# Laravel için PHP-FPM. Build bağlamı proje köküdür.
# dev: kod ./backend klasöründen bağlanır. prod: kod imaja kopyalanır.

FROM php:8.4-fpm-alpine AS base
RUN apk add --no-cache icu-libs libzip libpq \
 && apk add --no-cache --virtual .build-deps $PHPIZE_DEPS icu-dev libzip-dev postgresql-dev \
 && docker-php-ext-install -j"$(nproc)" intl zip pdo_pgsql pcntl bcmath opcache \
 && pecl install redis \
 && docker-php-ext-enable redis \
 && apk del .build-deps
# Yükleme sınırı nginx'teki client_max_body_size (20m) ile aynıdır; biri değişince öbürü de değişir.
RUN printf "upload_max_filesize=20M\npost_max_size=20M\n" > "$PHP_INI_DIR/conf.d/uploads.ini"
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /var/www/html

FROM base AS dev
# www-data kullanıcısı bilgisayardaki kullanıcıyla aynı kimliği alır.
# Böylece storage ve vendor altındaki dosyalar bilgisayarda da düzenlenebilir.
ARG UID=1000
ARG GID=1000
RUN apk add --no-cache shadow \
 && groupmod -o -g "$GID" www-data \
 && usermod -o -u "$UID" -g "$GID" www-data
ENV COMPOSER_HOME=/tmp/composer
# exec ile verilen komutlar (composer, artisan) root değil www-data olarak çalışır;
# böylece ./backend altında root sahibi dosya oluşmaz.
USER www-data

FROM base AS prod
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
COPY backend/ ./
# İndirilen paketler build önbelleğinde tutulur; sonraki build'ler ağa daha az bağımlıdır
# (GitHub indirmeleri zaman zaman 504 verir).
RUN --mount=type=cache,target=/tmp/composer-cache \
    COMPOSER_CACHE_DIR=/tmp/composer-cache composer install --no-dev --optimize-autoloader --no-interaction --no-progress \
 && chown -R www-data:www-data storage bootstrap/cache
USER www-data
