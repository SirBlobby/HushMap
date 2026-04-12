<script lang="ts">
	import { mapState } from '$lib/states/map.svelte';
	import { themeState } from '$lib/states/theme.svelte';
	import Icon from '@iconify/svelte';
	import { onMount, onDestroy } from 'svelte';

	let Chart: any;

	let chartCanvas: HTMLCanvasElement;
	let chartInstance: any;

	function closePopup() {
		mapState.selectedLocation = null;
		mapState.flyHome();
	}

	function getChartColor(db: number, isLight: boolean, isCB: boolean) {
		if (db === 0) return '#888888';
		if (db < 40) return isCB ? '#0072b2' : isLight ? '#1e66f5' : '#89b4fa';
		if (db < 55) return isCB ? '#56b4e9' : isLight ? '#179299' : '#94e2d5';
		if (db < 65) return isCB ? '#f0e442' : isLight ? '#df8e1d' : '#f9e2af';
		if (db < 80) return isCB ? '#ffb000' : isLight ? '#fe640b' : '#fab387';
		return isCB ? '#e66100' : isLight ? '#d20f39' : '#f38ba8';
	}

	function getStatusLabel(db: number) {
		if (db === 0) return 'No Data';
		if (db < 40) return 'Ideal';
		if (db < 55) return 'Great';
		if (db < 65) return 'Manageable';
		if (db < 80) return 'Disruptive';
		return 'Harmful';
	}


	let current2hAvg = $derived.by(() => {
		if (!mapState.selectedLocation) return 0;
		const now = Date.now();
		const twoHoursAgo = now - 2 * 60 * 60 * 1000;
		const points = mapState.historyData.filter(d =>
			d.room_id === mapState.selectedLocation?.id &&
			new Date(d.date.endsWith('Z') ? d.date : d.date + 'Z').getTime() >= twoHoursAgo
		);
		if (points.length === 0) return 0;
		const sum = points.reduce((acc, p) => acc + p.db, 0);
		return Math.round(sum / points.length);
	});

	let statusColor = $derived(getChartColor(current2hAvg, themeState.isLight, themeState.isColorBlindFriendly));
	let statusLabel = $derived(getStatusLabel(current2hAvg));

	function drawChart() {
		if (!Chart || !chartCanvas || !mapState.selectedLocation) return;
		if (chartInstance) chartInstance.destroy();


		const locData = mapState.historyData.filter(d => d.room_id === mapState.selectedLocation?.id)
			.map(d => ({
				x: new Date(d.date.endsWith('Z') ? d.date : d.date + 'Z'),
				y: d.db
			}))
			.sort((a, b) => a.x.getTime() - b.x.getTime());

		const isLight = themeState.isLight;
		const isCB = themeState.isColorBlindFriendly;

		const ctx = chartCanvas.getContext('2d');
		let gradientLine = statusColor;
		let gradientFill = statusColor + '33';

		if (ctx) {
			gradientLine = ctx.createLinearGradient(0, 0, 0, 200);
			gradientLine.addColorStop(0, getChartColor(85, isLight, isCB));
			gradientLine.addColorStop(0.35, getChartColor(65, isLight, isCB));
			gradientLine.addColorStop(0.45, getChartColor(55, isLight, isCB));
			gradientLine.addColorStop(0.6, getChartColor(40, isLight, isCB));
			gradientLine.addColorStop(1, getChartColor(0, isLight, isCB));

			gradientFill = ctx.createLinearGradient(0, 0, 0, 200);
			gradientFill.addColorStop(0, getChartColor(85, isLight, isCB) + '55');
			gradientFill.addColorStop(0.35, getChartColor(65, isLight, isCB) + '44');
			gradientFill.addColorStop(0.45, getChartColor(55, isLight, isCB) + '33');
			gradientFill.addColorStop(0.6, getChartColor(40, isLight, isCB) + '22');
			gradientFill.addColorStop(1, getChartColor(0, isLight, isCB) + '00');
		}

		chartInstance = new Chart(chartCanvas, {
			type: 'line',
			data: {
				datasets: [{
					label: 'Loudness (dB)',
					data: locData,
					borderColor: gradientLine,
					backgroundColor: gradientFill,
					borderWidth: 3,
					fill: true,
					segment: {
						borderColor: ctx => getChartColor(ctx.p1.parsed.y, isLight, isCB)
					},
					tension: 0.5,
					pointRadius: 0,
					pointHoverRadius: 6
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				interaction: { mode: 'nearest', axis: 'x', intersect: false },
				animation: {
					y: { duration: 2000, easing: 'easeOutElastic' },
					x: { duration: 1000, easing: 'easeOutQuart' }
				},
				scales: {
					x: {
						type: 'time',
						time: { unit: 'hour' },
						grid: { display: false, color: isLight ? '#e5e7eb' : '#313244' },
						ticks: { color: isLight ? '#6b7280' : '#a6adc8' }
					},
					y: {
						min: 0, max: 100,
						grid: { color: isLight ? '#e5e7eb' : '#313244' },
						ticks: { color: isLight ? '#6b7280' : '#a6adc8' }
					}
				},
				plugins: {
					legend: { display: false },
					tooltip: {
						mode: 'index',
						intersect: false,
						backgroundColor: isLight ? 'rgba(255,255,255,0.9)' : 'rgba(30,30,46,0.9)',
						titleColor: isLight ? '#111827' : '#cdd6f4',
						bodyColor: isLight ? '#111827' : '#cdd6f4',
					}
				}
			}
		});
	}

	$effect(() => {
		if (mapState.selectedLocation && mapState.historyData) {
			drawChart();
		}
	});

	onMount(async () => {
		const chartModule = await import('chart.js/auto');
		const chartjsAdapter = await import('chartjs-adapter-date-fns');
		Chart = chartModule.default;
		if (mapState.selectedLocation) drawChart();
	});

	onDestroy(() => {
		if (chartInstance) chartInstance.destroy();
	});
</script>

{#if mapState.selectedLocation}
<div class="absolute right-4 md:right-8 top-24 md:top-8 z-50 w-11/12 md:w-96 glass-panel rounded-3xl overflow-hidden border border-white/10 flex flex-col pointer-events-auto transition-all duration-300" style="box-shadow: 0 0 20px {statusColor}88, 0 25px 50px -12px rgba(0,0,0,0.5); border-left: 2px solid {statusColor};">
	<!-- Header -->
	<div class="px-6 py-5 border-b border-white/10 relative">
		<button onclick={closePopup} class="absolute right-4 top-4 w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-colors">
			<Icon icon="mdi:close" class="text-xl" />
		</button>
		<h2 class="font-display font-semibold text-2xl text-white mb-1">{mapState.selectedLocation.name}</h2>
		<div class="flex items-center gap-2">
			<div class="w-3 h-3 rounded-full shadow-[0_0_8px_currentColor]" style="color: {statusColor}; background-color: {statusColor};"></div>
			<span class="text-sm font-medium" style="color: {statusColor}">{statusLabel}</span>
			<span class="text-slate-400 text-sm ml-1">· {current2hAvg} dB Avg (Last 2h)</span>
		</div>
	</div>

	<!-- Usually quiet logic -->
	<div class="px-6 py-4 bg-mantle/30 flex items-start gap-3">
		<Icon icon="mdi:information" class="text-neon-blue mt-0.5 text-lg" />
		<div>
			<h3 class="text-sm font-medium text-white">Usually quiet this time of day</h3>
			<p class="text-xs text-slate-400 mt-1 leading-relaxed">Historical data shows this location typically averages less noise around this time.</p>
		</div>
	</div>

	<!-- Chart area -->
	<div class="p-6">
		<h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Past 24 Hours</h3>
		<div class="h-48 w-full">
			<canvas bind:this={chartCanvas}></canvas>
		</div>
	</div>
</div>
{/if}
