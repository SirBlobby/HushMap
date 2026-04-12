<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Icon from '@iconify/svelte';
	
	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let hiddenCanvas: HTMLCanvasElement;
	let stream: MediaStream | null = null;
	let intervalId: any;
	
	let roomStatus = $state('unknown');
	let peopleCount = $state(0);
	let chairsCount = $state(0);
	let availableChairsCount = $state(0);
	
	onMount(async () => {
		hiddenCanvas = document.createElement('canvas');
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: true });
			if (videoElement) {
				videoElement.srcObject = stream;
				videoElement.play();
			}
		} catch (err) {
			console.error("Camera access denied or unavailable", err);
		}
		
		intervalId = setInterval(processFrame, 1500);
	});
	
	onDestroy(() => {
		if (intervalId) clearInterval(intervalId);
		if (stream) {
			stream.getTracks().forEach(track => track.stop());
		}
	});
	
	async function processFrame() {
		if (!videoElement || videoElement.readyState !== videoElement.HAVE_ENOUGH_DATA) return;
		
		const width = videoElement.videoWidth;
		const height = videoElement.videoHeight;
		
		hiddenCanvas.width = width;
		hiddenCanvas.height = height;
		const ctx = hiddenCanvas.getContext('2d');
		if (!ctx) return;
		
		ctx.drawImage(videoElement, 0, 0, width, height);
		
		hiddenCanvas.toBlob(async (blob) => {
			if (!blob) return;
			const formData = new FormData();
			formData.append('file', blob, 'frame.jpg');
			
			try {
				const response = await fetch('http://localhost:8000/api/vision/room-status', {
					method: 'POST',
					body: formData
				});
				if (response.ok) {
					const data = await response.json();
					roomStatus = data.room_status;
					peopleCount = data.counts?.people || 0;
					chairsCount = data.counts?.chairs || 0;
					availableChairsCount = data.counts?.available_chairs || 0;
					
					drawOverlay(data, width, height);
				}
			} catch (e) {
				console.error("Failed to process vision frame:", e);
			}
		}, 'image/jpeg');
	}
	
	function drawOverlay(data: any, videoWidth: number, videoHeight: number) {
		if (!canvasElement) return;
		
		const rect = canvasElement.getBoundingClientRect();
		canvasElement.width = rect.width;
		canvasElement.height = rect.height;
		
		const ctx = canvasElement.getContext('2d');
		if (!ctx) return;
		
		ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
		
		const scaleX = canvasElement.width / videoWidth;
		const scaleY = canvasElement.height / videoHeight;
		
		ctx.scale(scaleX, scaleY);
		
		const people = data.details?.people || [];
		const chairs = data.details?.chairs || [];
		const pairs = data.pairs || [];
		
		ctx.lineWidth = 3;
		
		people.forEach((p: any) => {
			ctx.strokeStyle = '#1e66f5'; // blue for people
			ctx.strokeRect(p.box[0], p.box[1], p.box[2] - p.box[0], p.box[3] - p.box[1]);
		});
		
		chairs.forEach((c: any) => {
			ctx.strokeStyle = '#40a02b'; // green for chairs
			ctx.strokeRect(c.box[0], c.box[1], c.box[2] - c.box[0], c.box[3] - c.box[1]);
		});
		
		// Draw connecting lines between pairs
		ctx.strokeStyle = '#df8e1d'; // orange/yellow
		ctx.setLineDash([5, 5]);
		ctx.beginPath();
		pairs.forEach((pair: any) => {
			const person = people[pair.person_index];
			const chair = chairs[pair.chair_index];
			if (person && chair) {
				ctx.moveTo(person.centroid[0], person.centroid[1]);
				ctx.lineTo(chair.centroid[0], chair.centroid[1]);
			}
		});
		ctx.stroke();
		ctx.setLineDash([]); // Reset line dash
	}
</script>

<svelte:window on:resize={() => {
	// Re-process layout or clear overlay on resize if needed
	if (canvasElement) {
		const ctx = canvasElement.getContext('2d');
		if (ctx) ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
	}
}} />

<div class="h-full w-full flex flex-col md:flex-row items-center justify-center p-6 gap-6 pt-20 md:pt-6 md:pl-24 overflow-y-auto">
	<div class="relative w-full max-w-4xl rounded-3xl overflow-hidden glass-panel border border-white/10 shadow-2xl flex-shrink-0">
		<video bind:this={videoElement} class="w-full h-auto object-cover block" playsinline muted></video>
		<canvas bind:this={canvasElement} class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
	</div>
	
	<div class="w-full max-w-md glass-panel rounded-3xl border border-white/10 p-6 flex flex-col gap-4 shadow-xl shrink-0">
		<h2 class="font-display font-semibold text-2xl text-white mb-2 flex items-center gap-2">
			<Icon icon="mdi:cctv" class="text-neon-blue" /> Live Vision
		</h2>
		
		<div class="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/10">
			<span class="text-slate-400 font-medium text-sm">Status</span>
			<span class="font-bold text-lg {roomStatus === 'full' ? 'text-red-400' : roomStatus === 'available' ? 'text-green-400' : 'text-slate-400'} capitalize">
				{roomStatus}
			</span>
		</div>
		
		<div class="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/10">
			<span class="text-slate-400 font-medium text-sm flex items-center gap-2"><Icon icon="mdi:account" /> People</span>
			<span class="font-bold text-xl text-white">{peopleCount}</span>
		</div>
		
		<div class="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/10">
			<span class="text-slate-400 font-medium text-sm flex items-center gap-2"><Icon icon="mdi:chair-school" /> Available Chairs</span>
			<span class="font-bold text-xl text-white">{availableChairsCount} / {chairsCount}</span>
		</div>
	</div>
</div>

<style>
	:global(.glass-panel) {
		background: var(--color-panel-glass);
		backdrop-filter: blur(12px);
	}
</style>