<script lang="ts">
	import Icon from '@iconify/svelte';
	import { themeState } from '$lib/states/theme.svelte';

	function handleLightModeClick() {
		themeState.toggle();
	}

	const supportedLanguages = [
		{ code: 'en', name: 'English' },
		{ code: 'es', name: 'Spanish' },
		{ code: 'fr', name: 'French' },
		{ code: 'de', name: 'German' },
		{ code: 'zh-CN', name: 'Chinese (Simplified)' },
		{ code: 'ja', name: 'Japanese' },
		{ code: 'ko', name: 'Korean' },
		{ code: 'hi', name: 'Hindi' },
		{ code: 'ar', name: 'Arabic' }
	];

	let currentLang = $state('en');

	$effect(() => {
		const match = document.cookie.match(/googtrans=\/en\/([^;]+)/);
		if (match && match[1]) {
			currentLang = match[1];
		}
	});

	function handleLanguageChange(event: Event) {
		const langCode = (event.target as HTMLSelectElement).value;
		if (langCode === 'en') {
			document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
			document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=.${location.hostname}; path=/;`;
		} else {
			document.cookie = `googtrans=/en/${langCode}; path=/`;
			document.cookie = `googtrans=/en/${langCode}; domain=.${location.hostname}; path=/`;
		}
		window.location.reload();
	}
</script>

<svelte:head>
	<title>HushMap | Settings</title>
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
				
				<div class="shrink-0 p-2 min-h-[44px] flex items-center justify-center">
					<!-- Custom Styled Dropdown -->
					<div class="glass-panel rounded-xl border border-white/10 overflow-hidden flex flex-col w-48 transition-all hover:border-neon-primary/40 bg-surface0 relative">
						<select 
							bind:value={currentLang}
							class="bg-transparent font-display text-sm md:text-base p-3 border-none outline-none focus:ring-0 cursor-pointer w-full font-medium"
							style="color: {themeState.isLight ? '#4c4f69' : '#ffffff'} !important; appearance: none; -webkit-appearance: none;"
							onchange={handleLanguageChange}
						>
							<option value="en" class="bg-crust" style="color: {themeState.isLight ? '#4c4f69' : '#ffffff'} !important;">English</option>
							{#each supportedLanguages.filter(l => l.code !== 'en') as lang}
								<option value={lang.code} class="bg-crust" style="color: {themeState.isLight ? '#4c4f69' : '#ffffff'} !important;">{lang.name}</option>
							{/each}
						</select>
						
						<!-- Dropdown Arrow -->
						<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
							<Icon icon="mdi:chevron-down" style="color: {themeState.isLight ? '#4c4f69' : '#ffffff'} !important;" />
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</div>
