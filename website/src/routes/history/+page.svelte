<script lang="ts">
	import Icon from '@iconify/svelte';
	import MapControls from '$lib/components/MapControls.svelte';
	import InteractiveMap from '$lib/components/InteractiveMap.svelte';
	import { onDestroy, onMount } from 'svelte';

	// Time state
	const NOW = Date.now();
	const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;
	let playbackTime = $state(NOW);
	
	let isPlaying = $state(false);
	let playInterval: any;

	function togglePlay() {
		isPlaying = !isPlaying;
		if (isPlaying) {
			// Auto replay from beginning if at the end
			if (playbackTime >= NOW) {
				playbackTime = NOW - TWENTY_FOUR_HOURS;
			}
			playInterval = setInterval(() => {
				// Advance 15 minutes per tick
				playbackTime += 15 * 60 * 1000;
				if (playbackTime >= NOW) {
					playbackTime = NOW;
					isPlaying = false;
					clearInterval(playInterval);
				}
			}, 200); // Ticks every 200ms
		} else {
			clearInterval(playInterval);
		}
	}

	onDestroy(() => {
		if (playInterval) clearInterval(playInterval);
	});

	// Derived values for the UI
	let progressPercent = $derived(((playbackTime - (NOW - TWENTY_FOUR_HOURS)) / TWENTY_FOUR_HOURS) * 100);
	
	let formattedTime = $derived.by(() => {
		const d = new Date(playbackTime);
		return d.toLocaleString('en-US', {
			weekday: 'short',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			timeZone: 'America/New_York'
		}) + ' EST';
	});

</script>

<svelte:head>
	<title>EchoNode | History</title>
</svelte:head>

<div class="relative w-full h-full bg-crust border-l border-white/5">
	<!-- Map Engine Engine -->
	<InteractiveMap {playbackTime} />

	<MapControls showDropdown={true} />

	<!-- Top Bar / History Mode Overlay -->
	<header class="absolute top-6 left-6 md:left-8 z-10">
		<div class="glass-panel flex items-center justify-between md:justify-start gap-4 px-6 py-3 rounded-2xl shadow-lg border-l-2 border-l-neon-blue drop-shadow-[0_0_10px_rgba(0,243,255,0.2)] h-12">
			<div>
				<h1 class="font-display font-semibold text-white tracking-wider flex items-center gap-2">
					<Icon icon="mdi:history" class="text-neon-blue drop-shadow-[0_0_5px_rgba(0,243,255,0.8)] text-lg" />
					HISTORICAL DATA
				</h1>
			</div>
		</div>
	</header>

	<!-- Time Control Bottom Bar -->
	<div class="absolute bottom-24 md:bottom-8 left-4 md:left-8 right-4 md:right-8 z-10 flex justify-center">
		<div class="glass-panel rounded-2xl p-6 border-l-2 border-l-neon-primary w-full max-w-4xl" style="box-shadow: var(--shadow-glow-primary)">
			
			<div class="flex items-center justify-between mb-2">
				<h2 class="font-display font-medium text-lg text-white">Playback Controls</h2>
				<span class="text-neon-blue font-mono text-sm tracking-wider drop-shadow-[0_0_5px_rgba(0,243,255,0.5)]">{formattedTime}</span>
			</div>
			
			<div class="flex items-center gap-6 mt-6">
				<button onclick={togglePlay} class="w-12 h-12 rounded-full bg-neon-blue/10 hover:bg-neon-blue/20 flex items-center justify-center text-neon-blue transition-colors border border-neon-blue/30 shrink-0 focus:outline-none">
					<Icon icon={isPlaying ? "mdi:pause" : "mdi:play"} class="text-2xl" />
				</button>
				
				<!-- Slider Track -->
				<div class="flex-1 relative h-8 flex items-center group">
					<div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden absolute pointer-events-none">
						<div class="h-full bg-neon-blue shadow-[0_0_10px_rgba(0,243,255,0.8)]" style="width: {progressPercent}%"></div>
					</div>
					
					<!-- Native Range Input (Hidden visual, overlay over the track) -->
					<input 
						type="range" 
						min={NOW - TWENTY_FOUR_HOURS} 
						max={NOW} 
						bind:value={playbackTime}
						oninput={() => { if (isPlaying) togglePlay(); }}
						class="w-full absolute opacity-0 cursor-pointer h-full z-20"
					/>
					
					<!-- Custom Thumb (visually synced to the input value) -->
					<div class="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)] border-2 border-neon-blue group-hover:scale-125 transition-transform pointer-events-none z-10" style="left: calc({progressPercent}% - 8px)"></div>
				</div>
				
				<div class="text-xs text-slate-400 font-mono shrink-0">
					<p>24H Window</p>
				</div>
			</div>
		</div>
	</div>
</div>
