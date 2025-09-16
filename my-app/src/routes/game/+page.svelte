<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { uniqueNamesGenerator, adjectives, colors, animals } from 'unique-names-generator';

  let nisitId: string = '';
  let password: string = '';
  let leaderboard: any[] = [];
  let timeLeft: number = 45;
  let disabled: boolean = false;

  // Random unique display names for IDs
  let nameMap: Record<string, string> = {};

  const getDisplayName = (id: string) => {
    if (!nameMap[id]) {
      nameMap[id] = uniqueNamesGenerator({
        dictionaries: [adjectives, colors, animals],
        separator: '-',
        style: 'capital',
        length: 2
      });
    }
    return nameMap[id];
  };

  onMount(() => {
    nisitId = get(page).url.searchParams.get('nisitId') || '';
    if (!nisitId) {
      window.location.href = '/';
      return;
    }
    startTimer();
    fetchLeaderboard();
  });

  const startTimer = () => {
    const timer = setInterval(() => {
      timeLeft--;
      if (timeLeft <= 0) {
        clearInterval(timer);
        disabled = true;
        alert("Time's up! You cannot submit anymore.");
      }
    }, 1000);
  };

  // Custom crack time formatter: micro → second → minute → hour → day → month → year → century
  const formatCrackTimeExtended = (seconds: number) => {
    const units = [
      { label: 'century', value: 60 * 60 * 24 * 365.25 * 100 },
      { label: 'year', value: 60 * 60 * 24 * 365.25 },
      { label: 'month', value: 60 * 60 * 24 * 30 },
      { label: 'day', value: 60 * 60 * 24 },
      { label: 'hour', value: 60 * 60 },
      { label: 'minute', value: 60 },
      { label: 'second', value: 1 },
      { label: 'millisecond', value: 1e-3 },
      { label: 'microsecond', value: 1e-6 }
    ];

    let remaining = seconds;
    const result: string[] = [];

    for (const u of units) {
      if (remaining >= u.value) {
        const qty = Math.floor(remaining / u.value);
        remaining -= qty * u.value;
        result.push(`${qty} ${u.label}${qty > 1 ? 's' : ''}`);
      }
    }

    if (result.length === 0) {
      return `${(seconds * 1e6).toFixed(0)} microseconds`;
    }

    return result.join(' ');
  };

  const submitPassword = async () => {
    if (!password) return alert("Enter a password");
    try {
      const res = await axios.post("https://potential-disco-9x69r9ggg5p29x95-8000.app.github.dev/submit_password/", {
        nisitId,
        password
      });

      const crackTimeFormatted = formatCrackTimeExtended(res.data.estimated_time_sec);

      alert(`⏳ Estimated crack time: ${crackTimeFormatted}\n🏆 Rank: ${res.data.rank}`);

      const winner = res.data.rank === 1 ? true : false;
      goto(`/reward?nisitId=${nisitId}&winner=${winner}`);

    } catch (err: any) {
      if (err.response) alert(err.response.data.detail);
      else alert("Error connecting to backend.");
    }
  };

  const fetchLeaderboard = async () => {
    const res = await axios.get("https://potential-disco-9x69r9ggg5p29x95-8000.app.github.dev/leaderboard/");
    leaderboard = res.data;
  };
</script>

<div class="min-h-screen bg-gradient-to-r from-purple-400 to-pink-400 p-6 flex justify-center items-start">
  <div class="w-full max-w-xl bg-white p-6 rounded-xl shadow-lg">
    <h1 class="text-2xl font-bold mb-4 text-center">Hello, Nisit {nisitId}!</h1>
    <p class="text-center mb-4 text-lg font-semibold">Time left: {timeLeft}s</p>

    <input
      type="text"
      placeholder="Enter password (max 8)"
      bind:value={password}
      class="border p-2 rounded w-full mb-2"
      {disabled}
      maxlength="8"
    />
    <button
      on:click={submitPassword}
      class="bg-purple-600 text-white p-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
      {disabled}
    >
      Submit
    </button>

    <h2 class="text-xl font-bold mb-2 text-center mt-4">Leaderboard</h2>
    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="bg-gray-200">
          <th class="border p-2">Rank</th>
          <th class="border p-2">Player</th>
          <th class="border p-2">Crack Time</th>
        </tr>
      </thead>
      <tbody>
        {#each leaderboard as item, i}
          <tr>
            <td class="border p-2">{i + 1}</td>
            <td class="border p-2">{getDisplayName(item.nisitId)}</td>
            <td class="border p-2">{formatCrackTimeExtended(item.time_sec)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
