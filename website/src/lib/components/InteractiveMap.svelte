<script lang="ts">
	import { onMount, untrack, onDestroy } from "svelte";
	import { browser } from "$app/environment";
	import { mapState, UMD_LOCATIONS } from "$lib/states/map.svelte";
	import { themeState } from "$lib/states/theme.svelte";
	import { alertsState } from "$lib/states/alerts.svelte";
	import LocationPopup from "$lib/components/LocationPopup.svelte";
	import "maplibre-gl/dist/maplibre-gl.css";

	let { playbackTime = null } = $props<{ playbackTime?: number | null }>();

	let studyRoomsData: any[] = [];
	let refreshInterval: any;

	async function fetchStudyRoomData() {
		try {
			const res = await fetch(
				"http://localhost:8000/api/study-rooms/history",
			);
			if (res.ok) {
				const json = await res.json();
				studyRoomsData = json.data;
				mapState.historyData = json.data;
				updateMapData();
			}
		} catch (e) {
			console.error("Failed to fetch study room data", e);
		}
	}

	function updateMapData() {
		if (!mapInstance || !mapInstance.getSource("study-locations")) return;


		const latestByLoc = new Map();
		for (const room of studyRoomsData) {

			const key = room.room_id || room.location.coordinates.join(",");


			const roomDateString = room.date.endsWith("Z")
				? room.date
				: room.date + "Z";
			const roomDate = new Date(roomDateString);


			if (playbackTime && roomDate.getTime() > playbackTime) continue;

			if (!latestByLoc.has(key)) {
				latestByLoc.set(key, room);
			} else {
				const existing = latestByLoc.get(key);
				const existingDate = new Date(
					existing.date.endsWith("Z")
						? existing.date
						: existing.date + "Z",
				);
				if (roomDate > existingDate) {
					latestByLoc.set(key, room);
				}
			}
		}

		const latestRooms = Array.from(latestByLoc.values());

		if (playbackTime == null || playbackTime === undefined) {
			alertsState.processLiveReadings(latestRooms);
		}

		const features = latestRooms.map((room: any) => {

			let matchingLoc = null;
			if (room.room_id) {
				matchingLoc = UMD_LOCATIONS.find(
					(loc) => loc.id === room.room_id,
				);
			} else {
				matchingLoc = UMD_LOCATIONS.find(
					(loc) =>
						Math.abs(loc.lng - room.location.coordinates[0]) <
							0.0001 &&
						Math.abs(loc.lat - room.location.coordinates[1]) <
							0.0001,
				);
			}

			const locName = matchingLoc ? matchingLoc.name : "Unknown Location";

			return {
				type: "Feature",
				geometry: room.location,
				properties: {
					room_id: room.room_id,
					db: room.db,
					people: room.people || 0,
					name: locName,
					date: room.date,
				},
			};
		});


		UMD_LOCATIONS.forEach((loc) => {
			const hasData = features.some(
				(f) => f.properties.room_id === loc.id,
			);

			if (!hasData) {
				features.push({
					type: "Feature",
					geometry: {
						type: "Point",
						coordinates: [loc.lng, loc.lat],
					},
					properties: {
						room_id: loc.id,
						db: 0,
						people: 0,
						name: loc.name,
						date: new Date().toISOString(),
					},
				});
			}
		});

		mapInstance.getSource("study-locations").setData({
			type: "FeatureCollection",
			features: features,
		});

		if (popupInstance && hoveredFeatureId) {
			const freshFeature = features.find((f: any) => f.properties.room_id === hoveredFeatureId);
			if (freshFeature && popupInstance.isOpen && popupInstance.isOpen()) {
				popupInstance.setHTML(getPopupHTML(freshFeature.properties));
			}
		}
	}

	function addMapLayers(map: any, isLight: boolean, isCB: boolean) {
		if (!map.getSource("study-locations")) {
			map.addSource("study-locations", {
				type: "geojson",
				data: {
					type: "FeatureCollection",
					features: [],
				},
			});
		}

		const colorExpr = [
			"case",
			["==", ["get", "db"], 0],
			"#888888",
			[
				"step",
				["get", "db"],
				isCB ? "#0072b2" : isLight ? "#1e66f5" : "#89b4fa",
				40,
				isCB ? "#56b4e9" : isLight ? "#179299" : "#94e2d5",
				55,
				isCB ? "#f0e442" : isLight ? "#df8e1d" : "#f9e2af",
				65,
				isCB ? "#ffb000" : isLight ? "#fe640b" : "#fab387",
				80,
				isCB ? "#e66100" : isLight ? "#d20f39" : "#f38ba8",
			],
		];

		if (!map.getLayer("study-locations-glow")) {
			map.addLayer({
				id: "study-locations-glow",
				type: "circle",
				source: "study-locations",
				paint: {
					"circle-radius": [
						"case",
						["==", ["get", "db"], 0],
						10,
						20
					],
					"circle-color": colorExpr,
					"circle-opacity": 0.5,
					"circle-blur": 1.5,
				},
			});
		}

		if (!map.getLayer("study-locations-circles")) {
			map.addLayer({
				id: "study-locations-circles",
				type: "circle",
				source: "study-locations",
				paint: {
					"circle-radius": [
						"case",
						["==", ["get", "db"], 0],
						5,
						10
					],
					"circle-color": colorExpr,
					"circle-opacity": 0.95,
					"circle-stroke-width": 0,
				},
			});
		}

		if (!map.getLayer("study-locations-labels")) {
			map.addLayer({
				id: "study-locations-labels",
				type: "symbol",
				source: "study-locations",
				layout: {
					"text-field": ["get", "name"],
					"text-size": 13,
					"text-variable-anchor": ["top", "bottom", "left", "right"],
					"text-radial-offset": 1,
					"text-justify": "center",
					"text-allow-overlap": true,
					"text-ignore-placement": true,
				},
				paint: {
					"text-color": isLight ? "#1e1e2e" : "#ffffff",
					"text-halo-color": isLight ? "#ffffff" : "#000000",
					"text-halo-width": 2,
				},
			});
		}
	}

	let mapContainer: HTMLDivElement | undefined = $state();
	let mapInstance: any = $state();
	let popupInstance: any = null;
	let hoveredFeatureId: string | null = null;

	function getPopupHTML(props: any) {
		let timeStr = "No data";
		if (props.db > 0 && props.date) {
			const dateStr = props.date.endsWith("Z") ? props.date : props.date + "Z";
			const date = new Date(dateStr);
			timeStr = date.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour: "2-digit", minute: "2-digit" }) + " EST";
		}

		let status = "Unknown";
		let statusColor = "#888888";
		const isLight = themeState.isLight;
		const isCB = themeState.isColorBlindFriendly;

		if (props.db === 0) {
			status = "No Data";
		} else if (props.db < 40) {
			status = "Ideal";
			statusColor = isCB ? "#0072b2" : isLight ? "#1e66f5" : "#89b4fa";
		} else if (props.db < 55) {
			status = "Great";
			statusColor = isCB ? "#56b4e9" : isLight ? "#179299" : "#94e2d5";
		} else if (props.db < 65) {
			status = "Manageable";
			statusColor = isCB ? "#f0e442" : isLight ? "#df8e1d" : "#f9e2af";
		} else if (props.db < 80) {
			status = "Disruptive";
			statusColor = isCB ? "#ffb000" : isLight ? "#fe640b" : "#fab387";
		} else {
			status = "Harmful";
			statusColor = isCB ? "#e66100" : isLight ? "#d20f39" : "#f38ba8";
		}

		const rawName = props.name.split("\\n")[0].split("\n")[0];
		
		let occStatus = "Quiet";
		let occColor = "#94e2d5";
		if (props.people > 60) {
			occStatus = "Packed";
			occColor = "#f38ba8";
		} else if (props.people > 25) {
			occStatus = "Moderate";
			occColor = "#f9e2af";
		} else if (props.people === 0 && props.db === 0) {
			occStatus = "No Data";
			occColor = "#888888";
		}

		return `
			<div class="px-3 py-2 bg-crust/90 backdrop-blur-md border border-white/10 rounded-xl shadow-[0_0_15px_rgba(0,0,0,0.5)] min-w-[150px] text-text">
				<h3 class="font-display font-bold text-sm mb-1 text-white border-b border-white/10 pb-1">${rawName}</h3>
				<div class="flex items-center gap-2 mt-2">
					<div class="w-2 h-2 rounded-full shadow-[0_0_5px_${statusColor}]" style="background-color: ${statusColor}"></div>
					<span class="text-xs font-semibold" style="color: ${statusColor}">${status}</span>
				</div>
				<p class="text-xs text-subtext0 mt-1">Noise: <span class="font-mono text-white">${props.db > 0 ? props.db.toFixed(1) + " dB" : "N/A"}</span></p>
				<p class="text-xs text-subtext0 mt-1 flex items-center gap-1">
					Occupancy: <span class="font-mono" style="color: ${occColor}">${props.people}</span> 
					<span class="text-[10px]" style="color: ${occColor}">(${occStatus})</span>
				</p>
				<p class="text-[10px] text-surface2 mt-2 font-mono">Last updated: ${timeStr}</p>
			</div>
		`;
	}


	$effect(() => {
		const target = mapState.targetFlyTo;
		if (mapInstance && target) {
			untrack(() => {
				mapInstance.flyTo({
					center: [target.lng, target.lat],
					zoom: target.zoom,
					essential: true,
					duration: 1500,
				});
			});
		}
	});

	$effect(() => {
		if (mapInstance) {
			const isLight = themeState.isLight;
			const style = isLight
				? "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
				: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
			untrack(() => {
				mapInstance.setStyle(style);
				mapInstance.once("style.load", () => {
					addMapLayers(
						mapInstance,
						isLight,
						themeState.isColorBlindFriendly,
					);
				});
			});
		}
	});

	$effect(() => {
		if (mapInstance) {
			const isLight = themeState.isLight;
			const isCB = themeState.isColorBlindFriendly;
			untrack(() => {
				const colorExpr = [
					"case",
					["==", ["get", "db"], 0],
					"#888888",
					[
						"step",
						["get", "db"],
						isCB
							? "#0072b2"
							: isLight
								? "#1e66f5"
								: "#89b4fa",
						40,
						isCB
							? "#56b4e9"
							: isLight
								? "#179299"
								: "#94e2d5",
						55,
						isCB
							? "#f0e442"
							: isLight
								? "#df8e1d"
								: "#f9e2af",
						65,
						isCB
							? "#ffb000"
							: isLight
								? "#fe640b"
								: "#fab387",
						80,
						isCB
							? "#e66100"
							: isLight
								? "#d20f39"
								: "#f38ba8",
					],
				];
				if (mapInstance.getLayer("study-locations-glow")) {
					mapInstance.setPaintProperty("study-locations-glow", "circle-color", colorExpr);
				}
				if (mapInstance.getLayer("study-locations-circles")) {
					mapInstance.setPaintProperty("study-locations-circles", "circle-color", colorExpr);
				}
			});
		}
	});

	onMount(() => {
		if (!browser || !mapContainer) return;

		fetchStudyRoomData();
		refreshInterval = setInterval(fetchStudyRoomData, 10000);

		let map: any;

		(async () => {
			const { Map, NavigationControl, Popup } = await import(
				"maplibre-gl"
			);

			map = new Map({
				container: mapContainer!,
				style: themeState.isLight
					? "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
					: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
				center: [-76.94259561477574, 38.98813763708658],
				zoom: 15.5,
				pitch: 0,
				bearing: 0,
				attributionControl: false,
			});

			map.addControl(
				new NavigationControl({ visualizePitch: true }),
				"bottom-right",
			);
			mapInstance = map;

			popupInstance = new Popup({
				closeButton: false,
				closeOnClick: false,
				className: "custom-map-popup",
			});

			map.on("mouseenter", "study-locations-circles", (e: any) => {
				map.getCanvas().style.cursor = "pointer";

				const coordinates = e.features[0].geometry.coordinates.slice();
				const props = e.features[0].properties;

				hoveredFeatureId = props.room_id;

				while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
					coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
				}

				popupInstance.setLngLat(coordinates).setHTML(getPopupHTML(props)).addTo(map);
			});

			map.on("mouseleave", "study-locations-circles", () => {
				map.getCanvas().style.cursor = "";
				hoveredFeatureId = null;
				popupInstance.remove();
			});

			map.on("click", "study-locations-circles", (e: any) => {
				const id = e.features[0].properties.room_id;
				const loc = UMD_LOCATIONS.find(l => l.id === id);
				if (loc) {
					mapState.selectedLocation = loc;
					mapState.flyTo(loc.lng, loc.lat, 17.5);
				}
			});

			map.on("load", () => {
				addMapLayers(
					map,
					themeState.isLight,
					themeState.isColorBlindFriendly,
				);
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
	<div
		bind:this={mapContainer}
		class="absolute inset-0 z-0 opacity-100 transition-all duration-500"
		style="width: 100%; height: 100%;"
	></div>
</div>

<LocationPopup />

<style>
	:global(.maplibregl-ctrl-group) {
		background: var(
			--color-panel-glass
		) !important;
		backdrop-filter: blur(12px) !important;
		border: 1px solid
			color-mix(in srgb, var(--color-surface1) 30%, transparent) !important;
		border-left: 2px solid var(--color-neon-primary) !important;
		box-shadow: var(--shadow-glow-primary) !important;
		border-radius: 12px !important;
		overflow: hidden;
	}
	:global(.maplibregl-ctrl-group button) {
		width: 40px !important;
		height: 40px !important;
		border-bottom: 1px solid
			color-mix(in srgb, var(--color-surface1) 20%, transparent) !important;
	}
	:global(.maplibregl-ctrl-icon) {
		filter: var(--map-icon-filter, invert(1) opacity(0.9))
			drop-shadow(0 0 1px rgba(0, 0, 0, 0.5)) !important;
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
		border-top-color: rgba(
			24,
			24,
			37,
			0.9
		) !important;
	}
</style>
