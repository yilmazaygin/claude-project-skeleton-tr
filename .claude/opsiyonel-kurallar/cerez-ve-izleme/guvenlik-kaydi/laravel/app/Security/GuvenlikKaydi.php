<?php

namespace App\Security;

use Illuminate\Auth\Events\Failed;
use Illuminate\Auth\Events\Lockout;
use Illuminate\Auth\Events\Login;
use Illuminate\Auth\Events\Logout;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Auth\Events\PasswordResetLinkSent;
use Illuminate\Events\Dispatcher;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Throwable;

/**
 * Laravel'in kimlik doğrulama olaylarını guvenlik_kaydi tablosuna yazar.
 * AppServiceProvider::boot() içinde kaydedilir: Event::subscribe(GuvenlikKaydi::class);
 * (Sınıf app/Listeners dışında durur; böylece otomatik olay keşfiyle iki kez kaydedilmez.)
 *
 * IP, Laravel'in trustProxies ayarına göre okunur. Yalnızca Docker iç ağları güvenilir
 * sayılmalıdır; '*' ziyaretçinin uydurduğu X-Forwarded-For değerine de güvenir (PARCALAR.md).
 */
final class GuvenlikKaydi
{
    public function girisBasarisiz(Failed $olay): void
    {
        $kimlik = $olay->credentials['email'] ?? $olay->credentials['username'] ?? null;
        $this->yaz('giris.basarisiz', $olay->user?->getAuthIdentifier(), $kimlik);
    }

    public function girisBasarili(Login $olay): void
    {
        $this->yaz('giris.basarili', $olay->user->getAuthIdentifier());
    }

    public function kilitlendi(Lockout $olay): void
    {
        $kimlik = $olay->request->input('email') ?? $olay->request->input('username');
        $this->yaz('giris.kilitlendi', null, is_string($kimlik) ? $kimlik : null, $olay->request);
    }

    public function cikis(Logout $olay): void
    {
        $this->yaz('cikis', $olay->user?->getAuthIdentifier());
    }

    public function sifirlamaIstendi(PasswordResetLinkSent $olay): void
    {
        $this->yaz('parola.sifirlama_istendi', $olay->user->getAuthIdentifier());
    }

    public function parolaDegisti(PasswordReset $olay): void
    {
        $this->yaz('parola.degisti', $olay->user->getAuthIdentifier());
    }

    /** @return array<class-string, string> */
    public function subscribe(Dispatcher $olaylar): array
    {
        return [
            Failed::class => 'girisBasarisiz',
            Login::class => 'girisBasarili',
            Lockout::class => 'kilitlendi',
            Logout::class => 'cikis',
            PasswordResetLinkSent::class => 'sifirlamaIstendi',
            PasswordReset::class => 'parolaDegisti',
        ];
    }

    private function yaz(string $olay, mixed $kullaniciId, ?string $kimlik = null, ?Request $istek = null): void
    {
        $istek ??= request();
        $ip = $istek->ip();
        $ua = $istek->userAgent();
        $konum = GeoIp::bul($ip);
        $cihaz = UserAgent::coz($ua);

        try {
            DB::table('guvenlik_kaydi')->insert([
                'olay' => $olay,
                'kullanici_id' => $kullaniciId === null ? null : (string) $kullaniciId,
                'denenen_kimlik' => UserAgent::maskele($kimlik),
                'ip' => $ip,
                'ulke' => $konum['ulke'],
                'sehir' => $konum['sehir'],
                'user_agent' => $ua === null ? null : mb_substr($ua, 0, 512),
                'isletim_sistemi' => $cihaz['isletim_sistemi'],
                'tarayici' => $cihaz['tarayici'],
                'cihaz' => $cihaz['cihaz'],
            ]);
        } catch (Throwable $hata) {
            // Güvenlik kaydı yazılamazsa giriş akışı bozulmaz; hata uygulama günlüğüne düşer.
            Log::error('guvenlik_kaydi yazılamadı', ['olay' => $olay, 'hata' => $hata->getMessage()]);
        }
    }
}
