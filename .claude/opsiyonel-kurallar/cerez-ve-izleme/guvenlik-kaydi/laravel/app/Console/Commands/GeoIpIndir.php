<?php

namespace App\Console\Commands;

use App\Security\GeoIp;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

/**
 * DB-IP Lite şehir veritabanını indirir (CC BY 4.0, https://db-ip.com).
 * Dosya her ay yenilenir; scheduler eki varsa routes/console.php içinde ayda bir çalışır:
 *   Schedule::command('geoip:indir')->monthlyOn(3, '04:00');
 * Dosya bellekte açılmaz; diske indirilip akış halinde açılır (yaklaşık 130 MB).
 */
class GeoIpIndir extends Command
{
    protected $signature = 'geoip:indir';

    protected $description = 'DB-IP Lite şehir veritabanını storage/app/geoip/ altına indirir';

    public function handle(): int
    {
        $hedef = GeoIp::dosya();
        if (! is_dir(dirname($hedef))) {
            mkdir(dirname($hedef), 0775, true);
        }
        $gz = $hedef.'.gz.tmp';

        // Ayın dosyası ilk günlerde henüz yayımlanmamış olabilir; önce bu ay, sonra geçen ay denenir.
        foreach ([now(), now()->subMonthNoOverflow()] as $tarih) {
            $url = 'https://download.db-ip.com/free/dbip-city-lite-'.$tarih->format('Y-m').'.mmdb.gz';
            $yanit = Http::timeout(300)->sink($gz)->get($url);
            if ($yanit->successful()) {
                if (! copy('compress.zlib://'.$gz, $hedef.'.tmp')) {
                    @unlink($gz);
                    $this->error('Arşiv açılamadı.');

                    return self::FAILURE;
                }
                rename($hedef.'.tmp', $hedef);
                @unlink($gz);
                $this->info('İndirildi: '.$url.' → '.$hedef.' ('.round(filesize($hedef) / 1048576).' MB)');

                return self::SUCCESS;
            }
        }

        @unlink($gz);
        $this->error('DB-IP Lite indirilemedi.');

        return self::FAILURE;
    }
}
