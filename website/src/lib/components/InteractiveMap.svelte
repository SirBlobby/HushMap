<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { browser } from '$app/environment';
	import { mapState, UMD_LOCATIONS } from '$lib/states/map.svelte';
	import { themeState } from '$lib/states/theme.svelte';
	import 'maplibre-gl/dist/maplibre-gl.css';

	let mapContainer: HTMLDivElement | undefined = $state();
	let mapInstance: any = $state();

	// Watch and react to mapState updates using a Svelte 5 $effect
	$effect(() => {
		const target = mapState.targetFlyTo;
		if (mapInstance && target) {
			untrack(() => {
				mapInstance.flyTo({
					center: [target.lng, target.lat],
					zoom: target.zoom,
					essential: true,
					duration: 1500
				});
			});
		}
	});

	$effect(() => {
		if (mapInstance) {
			const style = themeState.isLight 
				? 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'
				: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';
			untrack(() => { mapInstance.setStyle(style); });
		}
	});

	onMount(async () => {
		if (!browser || !mapContainer) return;
		
		const { Map, NavigationControl } = await import('maplibre-gl');

		const map = new Map({
			container: mapContainer,
			style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
			center: [-76.9425, 38.9859], // UMD McKeldin Mall
			zoom: 15.5,
			pitch: 0,
			bearing: 0,
			attributionControl: false
		});

		map.addControl(new NavigationControl({
			visualizePitch: true
		}), 'bottom-right');

		mapInstance = map;

		map.on('load', () => {
			map.addSource('study-locations', {
				type: 'geojson',
				data: {
					type: 'FeatureCollection',
					features: UMD_LOCATIONS.map(loc => ({
						type: 'Feature',
						geometry: { type: 'Point', coordinates: [loc.lng, loc.lat] },
						properties: { name: loc.name }
					}))
				}
			});

			map.addLayer({
				id: 'study-locations-labels',
				type: 'symbol',
				source: 'study-locations',
				layout: {
					'text-field': ['get', 'name'],
					'text-size': 13,
					'text-variable-anchor': ['top', 'bottom', 'left', 'right'],
					'text-radial-offset': 1,
					'text-justify': 'center'
				},
				paint: {
					'text-color': '#ffffff',
					'text-halo-color': '#000000',
					'text-halo-width': 2
				}
			});
		});

		return () => {
			map.remove();
		};
	});
</script>

<div class="absolute inset-0 z-0 bg-crust transition-colors duration-500">
	<div bind:this={mapContainer} class="absolute inset-0 z-0 {themeState.isLight ? 'mix-blend-normal opacity-100 filter brightness-105 contrast-125 grayscale' : 'mix-blend-luminosity opacity-90'} transition-all duration-500" style="width: 100%; height: 100%;"></div>
	<!-- Color Screen Wash -->
	<div class="absolute inset-0 pointer-events-none {themeState.isLight ? 'mix-blend-screen bg-white opacity-20' : 'mix-blend-color bg-crust opacity-100'} z-10 transition-all duration-500"></div>
</div>

	<style>
	:global(.maplibregl-ctrl-group) {
		background: rgba(15, 23, 42, 0.8) !important;
		backdrop-filter: blur(12px) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
		border-left: 2px solid var(--color-neon-primary) !important;
		box-shadow: var(--shadow-glow-primary) !important;
		border-radius: 12px !important;
		overflow: hidden;
	}
	:global(.maplibregl-ctrl-group button) {
		width: 40px !important;
		height: 40px !important;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
	}
	:global(.maplibregl-ctrl-group button:last-child) {
		border-bottom: none !important;
	}
	:global(.maplibregl-ctrl-icon) {
		filter: invert(1) opacity(0.8) !important;
	}
	:global(.maplibregl-ctrl-group button:hover) {
		background: rgba(255, 255, 255, 0.1) !important;
	}
</style>
