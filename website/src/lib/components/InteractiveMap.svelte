<script lang="ts">
	import { onMount, untrack, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { mapState, UMD_LOCATIONS } from '$lib/states/map.svelte';
	import { themeState } from '$lib/states/theme.svelte';
	import 'maplibre-gl/dist/maplibre-gl.css';

    let { playbackTime = null } = $props<{ playbackTime?: number | null }>();

    let studyRoomsData: any[] = [];
    let refreshInterval: any;

    async function fetchStudyRoomData() {
        try {
            const res = await fetch('http://localhost:8000/api/study-rooms/history');
            if (res.ok) {
                const json = await res.json();
                studyRoomsData = json.data;
                updateMapData();
            }
        } catch (e) {
            console.error("Failed to fetch study room data", e);
        }
    }

    function updateMapData() {
        if (!mapInstance || !mapInstance.getSource('study-locations')) return;

        // Group history by location using room_id
        const latestByLoc = new Map();
        for (const room of studyRoomsData) {
            // Use room_id as the key, fallback to coordinates if room_id is missing for some reason
            const key = room.room_id || room.location.coordinates.join(',');
            
            // Ensure date is treated as UTC
            const roomDateString = room.date.endsWith('Z') ? room.date : room.date + 'Z';
            const roomDate = new Date(roomDateString);

            // Filter out points strictly in the future of our playback time
            if (playbackTime && roomDate.getTime() > playbackTime) continue;

            if (!latestByLoc.has(key)) {
                latestByLoc.set(key, room);
            } else {
                const existing = latestByLoc.get(key);
                const existingDate = new Date(existing.date.endsWith('Z') ? existing.date : existing.date + 'Z');
                if (roomDate > existingDate) {
                    latestByLoc.set(key, room);
                }
            }
        }

        const features = Array.from(latestByLoc.values()).map((room: any) => {
            // Find the corresponding UMD_LOCATION to get the name
            let matchingLoc = null;
            if (room.room_id) {
                matchingLoc = UMD_LOCATIONS.find(loc => loc.id === room.room_id);
            } else {
                matchingLoc = UMD_LOCATIONS.find(loc => 
                    Math.abs(loc.lng - room.location.coordinates[0]) < 0.0001 &&
                    Math.abs(loc.lat - room.location.coordinates[1]) < 0.0001
                );
            }
            
            const locName = matchingLoc ? matchingLoc.name : 'Unknown Location';

            return {
                type: 'Feature',
                geometry: room.location,
                properties: {
                    room_id: room.room_id,
                    db: room.db,
                    name: `${locName}\n${room.db.toFixed(1)} dB`,
                    date: room.date
                }
            };
        });

        // Add features for UMD_LOCATIONS that don't have sensor data yet
        UMD_LOCATIONS.forEach(loc => {
            const hasData = features.some(f => f.properties.room_id === loc.id);

            if (!hasData) {
                features.push({
                    type: 'Feature',
                    geometry: { type: 'Point', coordinates: [loc.lng, loc.lat] },
                    properties: {
                        room_id: loc.id,
                        db: 0, // 0 db for no data
                        name: loc.name,
                        date: new Date().toISOString()
                    }
                });
            }
        });

        mapInstance.getSource('study-locations').setData({
            type: 'FeatureCollection',
            features: features
        });
    }

	function addMapLayers(map: any, isLight: boolean) {
    if (!map.getSource('study-locations')) {
        map.addSource('study-locations', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: []
            }
        });
    }

    // Add a layer for the circles based on db level
    if (!map.getLayer('study-locations-circles')) {
        map.addLayer({
            id: 'study-locations-circles',
            type: 'circle',
            source: 'study-locations',
            paint: {
                'circle-radius': [
                    'case',
                    ['==', ['get', 'db'], 0], 5, // Small radius for 0 dB (no data)
                    [
                        'interpolate',
                        ['linear'],
                        ['get', 'db'],
                        40, 10,
                        60, 20,
                        80, 40
                    ]
                ],
                'circle-color': [
                    'case',
                    ['==', ['get', 'db'], 0], '#888888', // Gray for no data
                    [
                        'interpolate',
                        ['linear'],
                        ['get', 'db'],
                        40, '#00ff00',
                        60, '#ffff00',
                        80, '#ff0000'
                    ]
                ],
                'circle-opacity': 0.6,
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff'
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

    fetchStudyRoomData();
    refreshInterval = setInterval(fetchStudyRoomData, 10000); // refresh every 10s

    let map: any;

    (async () => {
        const { Map, NavigationControl, Popup } = await import('maplibre-gl');

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

        // Create a popup, but don't add it to the map yet.
        const popup = new Popup({
            closeButton: false,
            closeOnClick: false,
            className: 'custom-map-popup'
        });

        map.on('mouseenter', 'study-locations-circles', (e: any) => {
            map.getCanvas().style.cursor = 'pointer';

            const coordinates = e.features[0].geometry.coordinates.slice();
            const props = e.features[0].properties;
            
            // Format the date
            let timeStr = 'No data';
            if (props.db > 0 && props.date) {
                const dateStr = props.date.endsWith('Z') ? props.date : props.date + 'Z';
                const date = new Date(dateStr);
                timeStr = date.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' }) + ' EST';
            }

            let status = 'Unknown';
            let statusColor = '#888888';
            if (props.db === 0) {
                status = 'No Data';
            } else if (props.db < 50) {
                status = 'Quiet';
                statusColor = '#00ff00';
            } else if (props.db < 70) {
                status = 'Moderate';
                statusColor = '#ffff00';
            } else {
                status = 'Loud / Busy';
                statusColor = '#ff0000';
            }

            const rawName = props.name.split('\\n')[0].split('\n')[0]; // Handle both literal and escaped newlines

            const html = `
                <div class="px-3 py-2 bg-crust/90 backdrop-blur-md border border-white/10 rounded-xl shadow-[0_0_15px_rgba(0,0,0,0.5)] min-w-[150px] text-text">
                    <h3 class="font-display font-bold text-sm mb-1 text-white border-b border-white/10 pb-1">${rawName}</h3>
                    <div class="flex items-center gap-2 mt-2">
                        <div class="w-2 h-2 rounded-full shadow-[0_0_5px_${statusColor}]" style="background-color: ${statusColor}"></div>
                        <span class="text-xs font-semibold" style="color: ${statusColor}">${status}</span>
                    </div>
                    <p class="text-xs text-subtext0 mt-1">Noise: <span class="font-mono text-white">${props.db > 0 ? props.db.toFixed(1) + ' dB' : 'N/A'}</span></p>
                    <p class="text-[10px] text-surface2 mt-2 font-mono">Last updated: ${timeStr}</p>
                </div>
            `;

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            popup.setLngLat(coordinates)
                .setHTML(html)
                .addTo(map);
        });

        map.on('mouseleave', 'study-locations-circles', () => {
            map.getCanvas().style.cursor = '';
            popup.remove();
        });

        map.on('load', () => {
            addMapLayers(map, themeState.isLight);
            updateMapData();
        });
		})();

		return () => {
            if (refreshInterval) clearInterval(refreshInterval);
			map?.remove();
		};
	});

    $effect(() => {
        if (playbackTime !== undefined) {
            updateMapData();
        }
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
	:global(.custom-map-popup .maplibregl-popup-content) {
		background: transparent !important;
		padding: 0 !important;
		box-shadow: none !important;
		border-radius: 12px;
	}
	:global(.custom-map-popup .maplibregl-popup-tip) {
		border-top-color: rgba(24, 24, 37, 0.9) !important; /* matches bg-crust */
	}
</style>
