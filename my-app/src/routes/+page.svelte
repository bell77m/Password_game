<script lang="ts">
  import { goto } from '$app/navigation';
  import axios from 'axios';

  let nisitId: string = '';
  let errorMsg: string = '';

  const startGame = async () => {
    errorMsg = '';

    if (!nisitId) {
      errorMsg = "Enter your Nisit ID first";
      return;
    }

    // Simple validation: 10-digit ID
    if (!/^\d{10}$/.test(nisitId)) {
      errorMsg = "Nisit ID must be 10 digits";
      return;
    }

    try {
      // Check if Nisit ID already played
      const res = await axios.get(`https://potential-disco-9x69r9ggg5p29x95-8000.app.github.dev/check_status/${nisitId}`);

      if (res.data.played) {
        errorMsg = "You have already played the game. Cannot play again.";
      } else {
        goto(`/game?nisitId=${nisitId}`);
      }
    } catch (err) {
      console.error(err);
      errorMsg = "Error connecting to backend.";
    }
  };
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-purple-400 to-pink-400">
  <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md text-center">
    <h1 class="text-2xl font-bold mb-4">Password Competition</h1>
    <input
      type="text"
      placeholder="Enter Nisit ID"
      bind:value={nisitId}
      class="border p-2 rounded w-full mb-4"
      maxlength="10"
    />
    {#if errorMsg}
      <p class="text-red-600 mb-2">{errorMsg}</p>
    {/if}
    <button
      on:click={startGame}
      class="bg-purple-600 text-white p-2 rounded w-full hover:bg-purple-700"
    >
      Start Game
    </button>
  </div>
</div>
