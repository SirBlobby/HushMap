<script lang="ts">
	import Icon from "@iconify/svelte";
	import AlertsDropdown from "$lib/components/AlertsDropdown.svelte";
	import MapControls from "$lib/components/MapControls.svelte";
	import InteractiveMap from "$lib/components/InteractiveMap.svelte";
</script>

<svelte:head>
	<title>EchoNode | Live Map</title>
</svelte:head>

<div class="relative w-full h-full bg-crust border-l border-white/5">
	<InteractiveMap />

	<MapControls showDropdown={true} />

	<div class="absolute top-6 left-6 md:left-8 z-10 flex gap-4 items-center">
		<div
			class="glass-panel flex items-center gap-4 px-6 py-3 rounded-2xl shadow-lg border-l-2 border-l-neon-primary h-12"
			style="box-shadow: var(--shadow-glow-primary)"
		>
			<h1
				class="font-display font-semibold text-white tracking-wider flex items-center gap-2"
			>
				<Icon
					icon="mdi:access-point-network"
					class="text-neon-primary text-lg"
					style="filter: drop-shadow(var(--shadow-glow-primary))"
				/>
				LIVE DATA
			</h1>
		</div>
		<AlertsDropdown />
	</div>
</div>
