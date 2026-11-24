<?php

namespace App\Security;

/**
 * User-Agent başlığından işletim sistemi, tarayıcı ve cihaz ailesini çıkarır.
 * Dış bağımlılık yoktur; yalnızca aileyi bulur (sürüm yok). Ham başlık ayrıca saklanır.
 */
final class UserAgent
{
    private const BOT = '/bot|spider|crawl|slurp|curl|wget|python-requests|httpclient|go-http|postman/i';

    /** @return array{isletim_sistemi: ?string, tarayici: ?string, cihaz: string} */
    public static function coz(?string $ua): array
    {
        $ua = (string) $ua;

        $isletimSistemi = match (true) {
            $ua === '' => null,
            (bool) preg_match('/Windows NT/i', $ua) => 'Windows',
            (bool) preg_match('/iPhone|iPad|iPod/i', $ua) => 'iOS',
            (bool) preg_match('/Android/i', $ua) => 'Android',
            (bool) preg_match('/CrOS/i', $ua) => 'ChromeOS',
            (bool) preg_match('/Mac OS X|Macintosh/i', $ua) => 'macOS',
            (bool) preg_match('/Linux/i', $ua) => 'Linux',
            default => null,
        };

        $tarayici = match (true) {
            $ua === '' => null,
            (bool) preg_match(self::BOT, $ua) => 'bot/araç',
            (bool) preg_match('/Edg(e|A|iOS)?\//', $ua) => 'Edge',
            (bool) preg_match('/OPR\/|Opera/', $ua) => 'Opera',
            (bool) preg_match('/SamsungBrowser/', $ua) => 'Samsung Internet',
            (bool) preg_match('/Firefox\/|FxiOS/', $ua) => 'Firefox',
            (bool) preg_match('/Chrome\/|CriOS/', $ua) => 'Chrome',
            (bool) preg_match('/Safari\//', $ua) => 'Safari',
            default => null,
        };

        $cihaz = match (true) {
            (bool) preg_match(self::BOT, $ua) => 'bot',
            (bool) preg_match('/iPad|Tablet/i', $ua) => 'tablet',
            (bool) preg_match('/Mobi|iPhone|Android/i', $ua) => 'mobil',
            default => 'masaustu',
        };

        return ['isletim_sistemi' => $isletimSistemi, 'tarayici' => $tarayici, 'cihaz' => $cihaz];
    }

    /** E-postayı maskeler: ayse@ornek.com → a***@ornek.com. E-posta değilse ilk harf + ***. */
    public static function maskele(?string $kimlik): ?string
    {
        if ($kimlik === null || $kimlik === '') {
            return null;
        }
        if (str_contains($kimlik, '@')) {
            [$ad, $alan] = explode('@', $kimlik, 2);

            return mb_substr($ad, 0, 1).'***@'.$alan;
        }

        return mb_substr($kimlik, 0, 1).'***';
    }
}
