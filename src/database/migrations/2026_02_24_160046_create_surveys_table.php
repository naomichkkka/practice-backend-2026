<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('surveys', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();
            $table->enum('status', ['draft','published','closed'])->default('draft');
            $table->foreignId('author_id')->constrained('users')->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::dropIfExists('surveys');
    }
};