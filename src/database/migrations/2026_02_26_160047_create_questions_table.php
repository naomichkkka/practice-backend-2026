<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('questions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('survey_id')->constrained('surveys')->onDelete('cascade');
            $table->string('text');
            $table->enum('type', ['single','multiple','text']);
            $table->integer('order')->default(1);
        });
    }

    public function down()
    {
        Schema::dropIfExists('questions');
    }
};