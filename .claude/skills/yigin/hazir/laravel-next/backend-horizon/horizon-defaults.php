<?php

/*
 * backend/config/horizon.php içindeki 'defaults' ve 'environments' girdileri, aşağıdaki
 * iki girdiyle değiştirilir. (php artisan horizon:install o dosyayı oluşturur.)
 * Bu dosyanın kendisi kullanılmaz; yalnızca geçerli PHP olsun diye 'return' içindedir.
 *
 * İkisi birlikte değişmelidir: Horizon yalnızca 'environments' içinde adı geçen
 * supervisor'ları çalıştırır; 'defaults' tek başına hiçbir worker başlatmaz.
 *
 * Kısa işler ile uzun işler ayrı supervisor'larda çalışır; biri öbürünü bekletmez.
 * Uzun iş göndermek için: SomeJob::dispatch()->onQueue('long');
 *
 * Kural: en uzun timeout (900), REDIS_QUEUE_RETRY_AFTER (960) değerinden küçük olmalıdır.
 * Bu değer compose dosyalarındaki x-laravel-env bloğundadır. Biri değişince öbürü ve
 * compose'daki horizon servisinin stop_grace_period değeri de aynı işte değişir.
 */

return [

'defaults' => [
    'supervisor-default' => [
        'connection' => 'redis',
        'queue' => ['high', 'default', 'low'],
        'balance' => 'auto',
        'autoScalingStrategy' => 'time',
        'minProcesses' => 1,
        'maxProcesses' => 4,
        'maxTime' => 3600,
        'maxJobs' => 0,
        'memory' => 256,
        'tries' => 3,
        'timeout' => 120,
        'nice' => 0,
    ],

    'supervisor-long' => [
        'connection' => 'redis',
        'queue' => ['long'],
        'balance' => 'simple',
        'minProcesses' => 1,
        'maxProcesses' => 2,
        'maxTime' => 3600,
        'maxJobs' => 0,
        'memory' => 512,
        'tries' => 3,
        'timeout' => 900,
        'nice' => 0,
    ],
],

'environments' => [
    'production' => [
        'supervisor-default' => [
            'maxProcesses' => 8,
            'balanceMaxShift' => 1,
            'balanceCooldown' => 3,
        ],
        'supervisor-long' => [
            'maxProcesses' => 2,
        ],
    ],

    'local' => [
        'supervisor-default' => [
            'maxProcesses' => 3,
        ],
        'supervisor-long' => [
            'maxProcesses' => 1,
        ],
    ],
],

];
