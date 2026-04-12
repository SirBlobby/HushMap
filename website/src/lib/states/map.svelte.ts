export interface StudyLocation {
	id: string;
	name: string;
	hasFloors: boolean;
	floors?: string[];
	lng: number;
	lat: number;
}

export const UMD_LOCATIONS: StudyLocation[] = [
	{ id: 'esj', name: 'Edward St. John (ESJ)', hasFloors: true, floors: ['Floor 1', 'Floor 2', 'Floor 3'], lng: -76.94209511596014, lat: 38.987133359608755 },
	{ id: 'mckeldin', name: 'McKeldin Library', hasFloors: true, floors: ['Floor 1', 'Floor 2', 'Floor 3', 'Floor 4', 'Floor 5', 'Floor 6', 'Floor 7'], lng: -76.94494907523277, lat: 38.986021017749366 },
	{ id: 'hornbake', name: 'Hornbake Library', hasFloors: false, lng: -76.94161787005467, lat: 38.988233373664826 },
	{ id: 'stem', name: 'STEM Library', hasFloors: false, lng: -76.93942003731279, lat: 38.988991437126195 },
	{ id: 'clarice', name: 'Clarice Library', hasFloors: false, lng: -76.9500912552473, lat: 38.990547823732285 },
	{ id: 'yahentamitsi', name: 'Yahentamitsi', hasFloors: false, lng: -76.9448027183373, lat: 38.99108961575231 },
	{ id: 'iribe', name: 'Iribe', hasFloors: false, lng: -76.93643838603555, lat: 38.98933701397555 },
	{ id: 'reckord', name: 'Reckord Armory', hasFloors: false, lng: -76.93897470250619, lat: 38.98609556181066 },
	{ id: 'stamp', name: 'Stamp Student Union', hasFloors: true, floors: ['Basement', 'Floor 1', 'Floor 2'], lng: -76.94473083972326, lat: 38.988130238874874 }
];

export const DEFAULT_VIEW = { lng: -76.94259561477574, lat: 38.98813763708658, zoom: 15.5 };

class MapState {

	targetFlyTo = $state<{ lng: number; lat: number; zoom: number; timestamp: number } | null>(null);

	selectedLocation = $state<StudyLocation | null>(null);
	historyData = $state<any[]>([]);
	historyLoading = $state<boolean>(false);
	historyPlaybackTime = $state<number>(Date.now());

	flyTo(lng: number, lat: number, zoom: number = 18) {
		this.targetFlyTo = { lng, lat, zoom, timestamp: Date.now() };
	}

	flyHome() {
		this.flyTo(DEFAULT_VIEW.lng, DEFAULT_VIEW.lat, DEFAULT_VIEW.zoom);
	}

	async fetchHistoryData() {
		this.historyLoading = true;
		try {

			const res = await fetch('http://127.0.0.1:8000/api/study-rooms/history');
			if (res.ok) {
				const json = await res.json();
				this.historyData = json.data;
			}
		} catch (e) {
			console.error("Failed to fetch history data", e);
		} finally {
			this.historyLoading = false;
		}
	}
}

export const mapState = new MapState();
