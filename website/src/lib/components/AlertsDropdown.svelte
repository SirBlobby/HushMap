<script lang="ts">
	import Icon from '@iconify/svelte';
	import { alertsState } from '$lib/states/alerts.svelte';
	import { slide, fade } from 'svelte/transition';

	let isOpen = $state(false);
</script>

<div class="relative">
	<!-- Notification Bell -->
	<button onclick={() => isOpen = !isOpen} class="relative w-12 h-12 glass-panel flex items-center justify-center rounded-xl border border-white/10 hover:bg-white/10 transition-colors group {isOpen ? 'bg-white/10 ring-1 ring-neon-alert' : ''}">
		<Icon icon="mdi:bell-outline" class="text-2xl text-slate-300 group-hover:text-white" />
		<!-- Badge -->
		{#if alertsState.activeAlerts.length > 0}
			<span class="absolute top-2 right-2 w-2.5 h-2.5 bg-neon-alert rounded-full shadow-[0_0_8px_rgba(255,7,58,0.8)] animate-pulse border border-slate-900"></span>
		{/if}
	</button>

	<!-- Dropdown Panel -->
	{#if isOpen}
		<div class="absolute top-14 left-0 w-80 glass-panel rounded-2xl shadow-2xl border border-white/10 overflow-hidden z-30 animate-in fade-in slide-in-from-top-2">
			<div class="px-4 py-3 border-b border-white/10 bg-black/40 flex justify-between items-center">
				<h3 class="font-display font-medium text-white text-sm">Active Noise Alerts</h3>
				<span class="text-xs text-slate-400 bg-white/5 py-0.5 px-2 rounded-full">{alertsState.activeAlerts.length} New</span>
			</div>

			<div class="max-h-64 overflow-y-auto">
				{#each alertsState.activeAlerts as alert (alert.id)}
					<div class="w-full text-left p-4 border-b border-white/5 hover:bg-white/5 transition-colors flex items-start gap-3 group relative">
						<Icon icon="mdi:alert-rhombus-outline" class="text-neon-alert text-xl mt-0.5" />
						<div class="flex-1 pr-6">
							<p class="text-sm font-medium text-red-200">Spike Detected: {alert.level} dB</p>
							<p class="text-xs text-red-400/80 mt-1">{alert.loc}</p>
							<p class="text-[10px] text-slate-500 font-mono mt-2">{alert.time}</p>
						</div>
						<button
							onclick={(e) => { e.stopPropagation(); alertsState.dismissAlert(alert.id); }}
							class="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"
							aria-label="Close alert"
						>
							<Icon icon="mdi:close" class="text-lg" />
						</button>
					</div>
				{/each}

				{#if alertsState.activeAlerts.length === 0}
					<div class="p-6 text-center text-slate-500">
						<Icon icon="mdi:check-circle-outline" class="text-3xl text-neon-primary mx-auto mb-2 opacity-50" />
						<p class="text-sm">Campus is quiet right now.</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<!-- Floating Toast Notifications -->
<!-- Displays globally without needing menu interaction to fulfill user requirement -->
<div class="fixed top-24 left-6 md:left-8 z-50 flex flex-col gap-3 pointer-events-none">
	{#each alertsState.activeAlerts.slice(0, 3) as alert (alert.id)}
		<div transition:slide={{ duration: 300 }} class="glass-panel w-72 rounded-xl p-4 shadow-2xl border-l-2 border-l-neon-alert pointer-events-auto flex items-start gap-3 animate-in slide-in-from-left-4" style="box-shadow: var(--shadow-glow-alert)">
			<Icon icon="mdi:alert-circle-outline" class="text-neon-alert text-2xl mt-0.5 shrink-0 animate-pulse" />
			<div class="flex-1">
				<div class="flex justify-between items-start">
					<p class="text-sm font-bold text-white tracking-wide">NOISE SPIKE: {alert.level} dB</p>
					<button
						onclick={() => alertsState.dismissAlert(alert.id)}
						class="text-slate-400 hover:text-white -mr-1 -mt-1 p-1 transition-colors"
					>
						<Icon icon="mdi:close" class="text-sm" />
					</button>
				</div>
				<p class="text-xs text-red-200 mt-1 font-medium">{alert.loc}</p>
				<p class="text-[10px] text-slate-400 font-mono mt-2">{alert.time}</p>
			</div>
		</div>
	{/each}
</div>
