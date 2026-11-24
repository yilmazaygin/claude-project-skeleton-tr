# Postgres yedek servisi (yedekleme kuralı). Build bağlamı proje köküdür.
# postgres imajı pg_dump/pg_restore'u projenin Postgres sürümüyle aynı getirir; rclone uzak kopya içindir.
FROM postgres:17-alpine
RUN apk add --no-cache rclone tzdata
COPY docker/yedek/baslat.sh docker/yedek/yedekle.sh docker/yedek/geri-yukle-sina.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/baslat.sh /usr/local/bin/yedekle.sh /usr/local/bin/geri-yukle-sina.sh
ENTRYPOINT ["/usr/local/bin/baslat.sh"]
