<script lang="ts">
	import Icon from '@iconify/svelte';

	let isOpen = $state(false);

	const mockAlerts = [
		{ id: 1, loc: 'McKeldin 2nd Floor', level: 78, time: '2 mins ago' },
		{ id: 2, loc: 'ESJ Atrium', level: 82, time: '15 mins ago' }
	];
</script>

<div class="relative">
	<!-- Notification Bell -->
	<button onclick={() => isOpen = !isOpen} class="relative w-12 h-12 glass-panel flex items-center justify-center rounded-xl border border-white/10 hover:bg-white/10 transition-colors group {isOpen ? 'bg-white/10 ring-1 ring-neon-alert' : ''}">
		<Icon icon="mdi:bell-outline" class="text-2xl text-slate-300 group-hover:text-white" />
		<!-- Badge -->
		{#if mockAlerts.length > 0}
			<span class="absolute top-2 right-2 w-2.5 h-2.5 bg-neon-alert rounded-full shadow-[0_0_8px_rgba(255,7,58,0.8)] animate-pulse border border-slate-900"></span>
		{/if}
	</button>

	<!-- Dropdown Panel -->
	{#if isOpen}
		<div class="absolute top-14 left-0 w-80 glass-panel rounded-2xl shadow-2xl border border-white/10 overflow-hidden z-30 animate-in fade-in slide-in-from-top-2">
			<div class="px-4 py-3 border-b border-white/10 bg-black/40 flex justify-between items-center">
				<h3 class="font-display font-medium text-white text-sm">Active Noise Alerts</h3>
				<span class="text-xs text-slate-400 bg-white/5 py-0.5 px-2 rounded-full">{mockAlerts.length} New</span>
			</div>
			
			<div class="max-h-64 overflow-y-auto">
				{#each mockAlerts as alert}
					<button class="w-full text-left p-4 border-b border-white/5 hover:bg-white/5 transition-colors flex items-start gap-3">
						<Icon icon="mdi:alert-rhombus-outline" class="text-neon-alert text-xl mt-0.5" />
						<div class="flex-1">
							<p class="text-sm font-medium text-red-200">Spike Detected: {alert.level} dB</p>
							<p class="text-xs text-red-400/80 mt-1">{alert.loc}</p>
						</div>
						<p class="text-[10px] text-slate-500 font-mono mt-1">{alert.time}</p>
					</button>
				{/each}
				
				{#if mockAlerts.length === 0}
					<div class="p-6 text-center text-slate-500">
						<Icon icon="mdi:check-circle-outline" class="text-3xl text-neon-primary mx-auto mb-2 opacity-50" />
						<p class="text-sm">Campus is quiet right now.</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
