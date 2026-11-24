<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

/** Testlerin geliştirme verisinden yalıtıldığını doğrular. Projede kalabilir. */
class IzolasyonTest extends TestCase
{
    use RefreshDatabase;

    public function test_testler_testing_veritabaninda_ve_bellekte_calisir(): void
    {
        $this->assertSame('testing', DB::connection()->getDatabaseName());
        $this->assertSame('array', config('cache.default'));
        $this->assertSame('array', config('session.driver'));
        $this->assertSame('sync', config('queue.default'));

        User::factory()->create();
        $this->assertSame(1, User::count());
    }
}
