<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('responses', function (Blueprint $table) {
            $table->id(); // уникальный ID
            $table->foreignId('survey_id')->constrained('surveys')->onDelete('cascade'); // к какому опросу относится
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');   // кто прошёл опрос
        });
    }

    public function down()
    {
        Schema::dropIfExists('responses');
    }
};