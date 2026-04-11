<script lang="ts">
	import Icon from '@iconify/svelte';
	import MapControls from '$lib/components/MapControls.svelte';
	import InteractiveMap from '$lib/components/InteractiveMap.svelte';
</script>

<svelte:head>
	<title>EchoNode | History</title>
</svelte:head>

<div class="relative w-full h-full bg-crust border-l border-white/5">
	<!-- Map Engine Engine -->
	<InteractiveMap />

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
				<span class="text-neon-blue font-mono text-sm tracking-wider drop-shadow-[0_0_5px_rgba(0,243,255,0.5)]">Tue, Oct 14 - 14:00</span>
			</div>
			
			<div class="flex items-center gap-6 mt-6">
				<button class="w-12 h-12 rounded-full bg-neon-blue/10 hover:bg-neon-blue/20 flex items-center justify-center text-neon-blue transition-colors border border-neon-blue/30 shrink-0">
					<Icon icon="mdi:play" class="text-2xl" />
				</button>
				
				<!-- Slider Track -->
				<div class="flex-1 relative group cursor-pointer h-8 flex items-center">
					<div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
						<div class="h-full bg-neon-blue w-[60%] shadow-[0_0_10px_rgba(0,243,255,0.8)]"></div>
					</div>
					<!-- Slider Thumb -->
					<div class="absolute top-1/2 left-[60%] -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)] border-2 border-neon-blue group-hover:scale-125 transition-transform"></div>
				</div>
				
				<div class="text-xs text-slate-400 font-mono shrink-0">
					<p>24H Window</p>
				</div>
			</div>
		</div>
	</div>

</div>
