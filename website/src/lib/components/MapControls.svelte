<script lang="ts">
	import { mapState, UMD_LOCATIONS } from '$lib/states/map.svelte';

	let { showDropdown = true } = $props<{ showDropdown?: boolean }>();

	const legendItems = [
		{ label: 'Harmful (80+ dB)', color: '#f38ba8' },
		{ label: 'Disruptive (65-79 dB)', color: '#fab387' },
		{ label: 'Manageable (55-64 dB)', color: '#f9e2af' },
		{ label: 'Great (40-54 dB)', color: '#94e2d5' },
		{ label: 'Ideal (0-39 dB)', color: '#89b4fa' }
	];
</script>

<div class="absolute top-6 right-6 md:right-8 z-20 flex flex-col gap-3 items-end">
    <div class="glass-panel p-4 md:p-5 rounded-2xl border-l-2 border-l-neon-primary flex flex-col gap-3" style="box-shadow: var(--shadow-glow-primary)">
		<h3 class="font-display font-medium text-white text-xs md:text-sm tracking-wider uppercase mb-1 border-b border-white/5 pb-2">Noise Levels</h3>
		<div class="flex flex-col gap-2.5">
			{#each legendItems as item}
				<div class="flex items-center gap-3">
					<div class="w-3.5 h-3.5 rounded shadow-sm shrink-0 border border-white/20" style="background-color: {item.color}; box-shadow: 0 0 8px {item.color}60"></div>
					<span class="text-xs font-mono text-slate-300 font-medium whitespace-nowrap">{item.label}</span>
				</div>
			{/each}
		</div>
	</div>

	{#if showDropdown}
	<div class="glass-panel rounded-xl border-l-2 border-l-neon-primary overflow-hidden flex flex-col w-64" style="box-shadow: var(--shadow-glow-primary)">
		<select class="bg-transparent text-white font-display text-sm p-4 border-none outline-none focus:ring-0 cursor-pointer w-full font-medium" onchange={(e) => {
			const val = (e.target as HTMLSelectElement).value;
			if (val === 'default') {
				mapState.flyHome();
			} else if (val) {
				const loc = UMD_LOCATIONS.find((l: { name: string; lat: number; lng: number }) => l.name === val);
				if (loc) {
					mapState.flyTo(loc.lng, loc.lat, 18);
				}
			}
		}}>
			<option value="default" class="bg-crust text-white font-semibold text-center hidden md:block">Jump to Campus Area</option>
			{#each UMD_LOCATIONS as loc}
				<option value={loc.name} class="bg-crust text-white">{loc.name}</option>
			{/each}
		</select>
	</div>
	{/if}
</div>
