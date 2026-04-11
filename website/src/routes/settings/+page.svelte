<script lang="ts">
	import Icon from '@iconify/svelte';
	import { themeState } from '$lib/states/theme.svelte';

	function handleLightModeClick() {
		themeState.toggle();
	}
</script>

<svelte:head>
	<title>EchoNode | Settings</title>
</svelte:head>

<div class="relative w-full h-full bg-crust border-l border-white/5 p-6 md:p-12 overflow-y-auto duration-500 transition-colors">
	<!-- Background Mesh -->
	<div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-surface0/30 via-crust to-crust z-0 pointer-events-none transition-colors duration-500"></div>

	<div class="relative z-10 max-w-4xl mx-auto">
		<header class="mb-10">
			<h1 class="font-display font-semibold text-3xl text-white tracking-wider flex items-center gap-3">
				<Icon icon="mdi:cog" class="text-slate-300" />
				SYSTEM SETTINGS
			</h1>
			<p class="text-sm text-slate-400 mt-2">Configure your interface preferences.</p>
		</header>

		<section class="glass-panel p-6 md:p-8 rounded-2xl border-white/10 shadow-xl">
			<h2 class="font-display text-xl text-white mb-6 flex items-center gap-2 border-b border-white/10 pb-3">
				<Icon icon="mdi:palette-outline" class="text-neon-blue" />
				Appearance
			</h2>
			
			<div class="flex flex-col md:flex-row md:items-center justify-between p-4 md:p-6 bg-mantle/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors gap-4">
				<div class="pr-4">
					<h3 class="font-display font-medium text-white text-lg">Light / Dark Mode</h3>
				</div>
				
				<button onclick={handleLightModeClick} class="shrink-0 px-5 py-2.5 bg-surface0 rounded-xl border border-white/10 hover:border-yellow-400/50 hover:text-yellow-400 hover:bg-surface1 transition-all flex items-center justify-center gap-2 font-medium">
					<Icon icon={themeState.isLight ? "mdi:weather-night" : "mdi:weather-sunny"} class="text-lg" />
					{themeState.isLight ? "Enable Dark Mode" : "Enable Light Mode"}
				</button>
			</div>
		</section>
	</div>
</div>
