<script lang="ts">
	import Icon from '@iconify/svelte';
	import { themeState } from '$lib/states/theme.svelte';

	function handleLightModeClick() {
		themeState.toggle();
	}
</script>

<svelte:head>
	<title>EchoNode | Settings</title>
	<script>
		window.googleTranslateElementInit = function() {
			new window.google.translate.TranslateElement({
				pageLanguage: 'en',
				layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE
			}, 'google_translate_element');
		};
	</script>
	<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit" async defer></script>
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
				Appearance and Accesibility
			</h2>
			
			<div class="flex flex-col md:flex-row md:items-center justify-between p-4 md:p-6 bg-mantle/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors gap-4">
				<div class="pr-4">
					<h3 class="font-display font-medium text-white text-lg flex items-center gap-2">
						<Icon icon="mdi:theme-light-dark" class="text-neon-primary" />
						Light / Dark Mode
					</h3>
				</div>
				
				<button onclick={handleLightModeClick} class="shrink-0 px-5 py-2.5 bg-surface0 rounded-xl border border-white/10 hover:border-yellow-400/50 hover:text-yellow-400 hover:bg-surface1 transition-all flex items-center justify-center gap-2 font-medium">
					<Icon icon={themeState.isLight ? "mdi:weather-night" : "mdi:weather-sunny"} class="text-lg" />
					{themeState.isLight ? "Enable Dark Mode" : "Enable Light Mode"}
				</button>
			</div>

			<div class="flex flex-col md:flex-row md:items-center justify-between p-4 md:p-6 bg-mantle/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors gap-4 mt-4">
				<div class="pr-4">
					<h3 class="font-display font-medium text-white text-lg flex items-center gap-2">
						<Icon icon="mdi:contrast-circle" class="text-neon-primary" />
						High Contrast Mode
					</h3>
				</div>
				
				<button onclick={() => themeState.toggleHighContrast()} class="shrink-0 px-5 py-2.5 bg-surface0 rounded-xl border border-white/10 hover:border-white/20 transition-all flex items-center justify-center gap-2 font-medium">
					<Icon icon={themeState.isHighContrast ? "mdi:toggle-switch" : "mdi:toggle-switch-off-outline"} class="text-2xl {themeState.isHighContrast ? 'text-neon-primary' : 'text-slate-400'}" />
					{themeState.isHighContrast ? "Enabled" : "Disabled"}
				</button>
			</div>

			<div class="flex flex-col md:flex-row md:items-center justify-between p-4 md:p-6 bg-mantle/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors gap-4 mt-4">
				<div class="pr-4">
					<h3 class="font-display font-medium text-white text-lg flex items-center gap-2">
						<Icon icon="mdi:eye-outline" class="text-neon-primary" />
						Color Blind Friendly
					</h3>
				</div>
				
				<button onclick={() => themeState.toggleColorBlind()} class="shrink-0 px-5 py-2.5 bg-surface0 rounded-xl border border-white/10 hover:border-white/20 transition-all flex items-center justify-center gap-2 font-medium">
					<Icon icon={themeState.isColorBlindFriendly ? "mdi:toggle-switch" : "mdi:toggle-switch-off-outline"} class="text-2xl {themeState.isColorBlindFriendly ? 'text-neon-primary' : 'text-slate-400'}" />
					{themeState.isColorBlindFriendly ? "Enabled" : "Disabled"}
				</button>
			</div>

			<div class="flex flex-col md:flex-row md:items-center justify-between p-4 md:p-6 bg-mantle/40 rounded-xl border border-white/5 hover:border-white/10 transition-colors gap-4 mt-4">
				<div class="pr-4">
					<h3 class="font-display font-medium text-white text-lg flex items-center gap-2"><Icon icon="mdi:translate" class="text-neon-primary" /> Global Translation</h3>
				</div>
				
				<div class="shrink-0 p-2 bg-surface0 border border-white/10 rounded-xl overflow-hidden min-h-[44px] flex items-center justify-center">
					<div id="google_translate_element" class="scale-90 origin-right"></div>
				</div>
			</div>
		</section>
	</div>
</div>
