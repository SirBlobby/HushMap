<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { browser } from '$app/environment';
	import { mapState, UMD_LOCATIONS } from '$lib/states/map.svelte';
	import { themeState } from '$lib/states/theme.svelte';
	import 'maplibre-gl/dist/maplibre-gl.css';

	function addMapLayers(map: any, isLight: boolean) {
    if (!map.getSource('study-locations')) {
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
    }

    if (!map.getLayer('study-locations-labels')) {
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
                'text-color': isLight ? '#1e1e2e' : '#ffffff',
                'text-halo-color': isLight ? '#ffffff' : '#000000',
                'text-halo-width': 2
            }
        });
    }
	}

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
			const isLight = themeState.isLight;
			const style = isLight 
				? 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'
				: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';
			untrack(() => {
				mapInstance.setStyle(style);
				mapInstance.once('style.load', () => addMapLayers(mapInstance, isLight));
			});
		}
	});

	onMount(() => {
    if (!browser || !mapContainer) return;

    let map: any;

    (async () => {
        const { Map, NavigationControl } = await import('maplibre-gl');

        map = new Map({
            container: mapContainer!,
            style: themeState.isLight
                ? 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'
                : 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            center: [-76.9425, 38.9859],
            zoom: 16.5,
            pitch: 0,
            bearing: 0,
            attributionControl: false
        });

        map.addControl(new NavigationControl({ visualizePitch: true }), 'bottom-right');
        mapInstance = map;

        map.on('load', () => addMapLayers(map, themeState.isLight));
		})();

		return () => {
			map?.remove();
		};
	});
</script>

<div class="absolute inset-0 z-0 bg-crust transition-colors duration-500">
    <div bind:this={mapContainer} class="absolute inset-0 z-0 {themeState.isLight ? 'opacity-100' : 'mix-blend-luminosity opacity-90'} transition-all duration-500" style="width: 100%; height: 100%;"></div>
    {#if !themeState.isLight}
    <div class="absolute inset-0 pointer-events-none mix-blend-color bg-crust opacity-100 z-10 transition-all duration-500"></div>
    {/if}
</div>

	<style>
	:global(.maplibregl-ctrl-group) {
	background: var(--color-panel-glass) !important; /* already switches per theme */
	backdrop-filter: blur(12px) !important;
	border: 1px solid color-mix(in srgb, var(--color-surface1) 30%, transparent) !important;
	box-shadow: var(--shadow-glow-primary) !important;
	border-radius: 12px !important;
	overflow: hidden;
	}
	:global(.maplibregl-ctrl-group button) {
	width: 40px !important;
	height: 40px !important;
	border-bottom: 1px solid color-mix(in srgb, var(--color-surface1) 20%, transparent) !important;
	}
	:global(.maplibregl-ctrl-icon) {
	filter: opacity(0.8) !important;
	filter: drop-shadow(0 0 1px #000000) !important;
	}
	:global(.maplibregl-ctrl-group button:hover) {
		background: rgba(255, 255, 255, 0.1) !important;
	}
</style>
