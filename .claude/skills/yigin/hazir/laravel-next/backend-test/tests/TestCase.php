<?php

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;
use RuntimeException;

abstract class TestCase extends BaseTestCase
{
    /**
     * Koruma: testler yalnızca "testing" veritabanında çalışır.
     *
     * setUpTraits(), RefreshDatabase gibi trait'lerden ÖNCE çalışır; böylece yanlış ayarda
     * veritabanı sıfırlanmadan test durur. (Test sınıfının kendi setUp() metodu bunun için
     * geç kalır: RefreshDatabase o zamana kadar çalışmış olur.)
     */
    protected function setUpTraits()
    {
        $baglanti = config('database.default');
        $veritabani = config("database.connections.{$baglanti}.database");

        if ($veritabani !== 'testing') {
            throw new RuntimeException(
                "Testler yalnızca 'testing' veritabanında çalışır; şu an: {$baglanti}/{$veritabani}. "
                .'phpunit.xml içindeki <env ... force="true"/> satırlarını kontrol edin.'
            );
        }

        return parent::setUpTraits();
    }
}
