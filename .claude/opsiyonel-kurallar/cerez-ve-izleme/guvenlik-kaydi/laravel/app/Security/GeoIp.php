<?php

namespace App\Security;

use GeoIp2\Database\Reader;
use Throwable;

/**
 * IP adresinden ülke ve şehir bulur (DB-IP Lite, CC BY 4.0, https://db-ip.com).
 * Veritabanı dosyası `php artisan geoip:indir` ile storage/app/geoip/ altına indirilir.
 * Dosya yoksa, IP özel ağdaysa veya bulunamazsa ülke ve şehir boş döner; kayıt yine yazılır.
 */
final class GeoIp
{
    private static ?Reader $okuyucu = null;

    private static bool $denendi = false;

    public static function dosya(): string
    {
        return storage_path('app/geoip/dbip-city-lite.mmdb');
    }

    /** @return array{ulke: ?string, sehir: ?string} */
    public static function bul(?string $ip): array
    {
        $bos = ['ulke' => null, 'sehir' => null];
        if ($ip === null || ! filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
            return $bos;
        }

        $okuyucu = self::okuyucu();
        if ($okuyucu === null) {
            return $bos;
        }

        try {
            $kayit = $okuyucu->city($ip);

            return ['ulke' => $kayit->country->isoCode, 'sehir' => $kayit->city->name];
        } catch (Throwable) {
            return $bos;
        }
    }

    private static function okuyucu(): ?Reader
    {
        if (! self::$denendi) {
            self::$denendi = true;
            if (is_file(self::dosya())) {
                try {
                    self::$okuyucu = new Reader(self::dosya());
                } catch (Throwable) {
                    self::$okuyucu = null;
                }
            }
        }

        return self::$okuyucu;
    }
}
