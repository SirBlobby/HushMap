<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	// Make sure you have $app/environment or similar if you need active states, 
	// for now we use simple routing links using sveltekit's native anchor tags.
	import Icon from '@iconify/svelte';
	import { page } from '$app/stores';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="h-screen w-full overflow-hidden bg-black text-slate-200 flex flex-col md:flex-row relative">
	
	<!-- Floating Sidebar (Desktop) / Bottom Bar (Mobile) -->
	<nav class="absolute md:static bottom-4 left-1/2 md:left-4 -translate-x-1/2 md:translate-x-0 md:my-auto z-50 rounded-3xl glass-panel md:w-16 w-11/12 md:h-auto py-3 md:py-6 px-4 md:px-0 flex md:flex-col items-center justify-around md:justify-center gap-6 shadow-2xl border-white/10 md:mr-4 overflow-hidden relative">
		<!-- Shell Pattern Background -->
		<div class="absolute inset-0 pointer-events-none opacity-[0.08] z-0" style="background-image: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2228%22 height=%2249%22 viewBox=%220 0 28 49%22%3E%3Cg fill-rule=%22evenodd%22%3E%3Cg id=%22hexagons%22 fill=%22%23ffffff%22 fill-opacity=%221%22 fill-rule=%22nonzero%22%3E%3Cpath d=%22M13.99 9.25l13 7.5v15l-13 7.5L1 31.75v-15l12.99-7.5zM3 17.9v12.7l10.99 6.34 11-6.35V17.9l-11-6.34L3 17.9zM0 15l12.98-7.5V0h-2v6.35L0 12.69v2.3zm0 18.5L12.98 41v8h-2v-6.85L0 35.81v-2.3zM15 0v7.5L27.99 15H28v-2.31h-.01L17 6.35V0h-2zm0 49v-8l12.99-7.5H28v2.31h-.01L17 42.15V49h-2z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E'); background-repeat: repeat;"></div>
		
		<!-- Nav Item: Live Map -->
		<a href="/" class="relative flex items-center justify-center p-3 rounded-2xl transition-all duration-300 hover:bg-white/10 group {$page.url.pathname === '/' ? 'text-neon-blue drop-shadow-[0_0_10px_rgba(0,243,255,0.6)] bg-white/5' : 'text-slate-400 hover:text-white'}">
			<Icon icon="mdi:map" class="text-2xl" />
			<span class="absolute left-full ml-4 px-2 py-1 bg-black/80 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none md:block hidden border border-white/10">Live Map</span>
		</a>

		<!-- Nav Item: History Map -->
		<a href="/history" class="relative flex items-center justify-center p-3 rounded-2xl transition-all duration-300 hover:bg-white/10 group {$page.url.pathname === '/history' ? 'text-neon-blue drop-shadow-[0_0_10px_rgba(0,243,255,0.6)]' : 'text-slate-400 hover:text-white'}">
			<Icon icon="mdi:history" class="text-2xl" />
			<span class="absolute left-full ml-4 px-2 py-1 bg-black/80 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none md:block hidden border border-white/10">History</span>
		</a>

		<!-- Nav Item: Settings -->
		<a href="/settings" class="relative flex items-center justify-center p-3 rounded-2xl transition-all duration-300 hover:bg-white/10 group {$page.url.pathname === '/settings' ? 'text-neon-blue drop-shadow-[0_0_10px_rgba(0,243,255,0.6)]' : 'text-slate-400 hover:text-white'}">
			<Icon icon="mdi:cog-outline" class="text-2xl" />
			<span class="absolute left-full ml-4 px-2 py-1 bg-black/80 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none md:block hidden border border-white/10">Settings</span>
		</a>
	</nav>

	<!-- Main Content Area -->
	<main class="flex-1 relative w-full h-full overflow-hidden">
		{@render children()}
	</main>
</div>
