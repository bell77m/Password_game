<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { get } from 'svelte/store';

  let winner: boolean = false;
  let rewardMessage: string = '';
  let collected: boolean = false;
  let nisitId: string = '';

  // Rewards with probability weights
  const winnerRewards = [
    { reward: "🎉 UNO", weight: 5},
    { reward: "🏆 Inhaler", weight: 5},
    { reward: "🍢 Snack x2", weight: 88},
    { reward: "✏️ Pencil sets", weight: 2},
  ];

  const loserRewards = [
    { reward: "🍬 Candy", weight: 85},
    { reward: "🍢 Snack", weight: 10},
    { reward: "🖊️ Pen", weight: 5 },
  ];

  // Weighted random selection
  function getWeightedReward(isWinner: boolean): string {
    const rewards = isWinner ? winnerRewards : loserRewards;
    const totalWeight = rewards.reduce((sum, r) => sum + r.weight, 0);
    let rand = Math.random() * totalWeight;

    for (const r of rewards) {
      if (rand < r.weight) return r.reward;
      rand -= r.weight;
    }
    return rewards[0].reward; // fallback
  }

  onMount(() => {
    const params = get(page).url.searchParams;
    winner = params.get('winner') === 'true';
    nisitId = params.get('nisitId') || '';
    rewardMessage = getWeightedReward(winner);
  });

  const collectReward = async () => {
    try {
      const res = await axios.post(
        `https://potential-disco-9x69r9ggg5p29x95-8000.app.github.dev/collect_reward/${nisitId}`,
        { reward: rewardMessage }
      );
      alert(res.data.message);
      collected = true;
    } catch (err: any) {
      if (err.response) alert(err.response.data.detail);
      else alert("Error connecting to backend");
    }
  };
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-purple-400 to-pink-400">
  <div class="bg-white p-8 rounded-xl shadow-lg text-center w-full max-w-md">
    <h1 class="text-3xl font-bold mb-4">
      {winner ? '🎉 You are the Winner! 🎉' : '😢 Already Played'}
    </h1>
    <p class="text-lg mb-4">{rewardMessage}</p>
    <button 
      class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
      on:click={collectReward}
      disabled={collected || !nisitId}
    >
      {collected ? "Reward Collected" : "Collect Reward"}
    </button>
    <a href="/" class="inline-block mt-4 bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">Go Home</a>
  </div>
</div>
