<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	let { onClose }: { onClose: () => void } = $props();

	type CallState = 'idle' | 'listening' | 'processing' | 'speaking';
	let callState = $state<CallState>('idle');
	
	let ws: WebSocket | null = null;
	let stream: MediaStream | null = null;
	let audioContext: AudioContext | null = null;
	let processor: ScriptProcessorNode | null = null;
	let currentAudio: HTMLAudioElement | null = null;

	let hasSpoken = false;
	let silenceTime = 0;
	let errorMessage = $state<string>('');
	let hardwareSampleRate = 16000;
	
	// Visualizer data
	let currentRms = $state<number>(0);
	
	function cleanupMic() {
		try {
			if (processor) {
				processor.disconnect();
				processor = null;
			}
			if (stream) {
				stream.getTracks().forEach((track) => track.stop());
				stream = null;
			}
			if (audioContext && audioContext.state !== 'closed') {
				if (typeof audioContext.close === 'function') {
					audioContext.close();
				}
				audioContext = null;
			}
		} catch(e) {
			console.warn('Silent mic cleanup error:', e);
		}
	}

	function playTTS(url: string) {
		callState = 'speaking';
		currentAudio = new Audio(url + "?t=" + Date.now());
		currentRms = 0.06; // Set a much smaller safe static visualizer size
		currentAudio.onended = () => {
			currentRms = 0;
			if (callState === 'speaking') {
				// AI is done talking, start listening automatically!
				startListeningPhase();
			}
		};
		// Some browsers require explicit play tracking
		const playPromise = currentAudio.play();
		if (playPromise !== undefined) {
			playPromise.catch(e => {
				console.error('Audio play blocked:', e);
				errorMessage = 'Audio playback blocked by browser.';
				endCall();
			});
		}
	}

	async function startListeningPhase() {
		if (callState === 'idle') return;
		callState = 'listening';
		hasSpoken = false;
		silenceTime = 0;
		errorMessage = '';
		currentRms = 0;

		try {
			// Synchronous audio context resume
			if (audioContext && audioContext.state === 'suspended') {
				await audioContext.resume();
			}

			if (!stream) {
				stream = await navigator.mediaDevices.getUserMedia({ audio: true });
				if (!audioContext) return;
				
				const source = audioContext.createMediaStreamSource(stream);
				processor = audioContext.createScriptProcessor(2048, 1, 1);
				
				processor.onaudioprocess = (e) => {
					if (!ws || ws.readyState !== WebSocket.OPEN || callState !== 'listening') return;
					
					const float32 = e.inputBuffer.getChannelData(0);
					const int16 = new Int16Array(float32.length);
					let sumSq = 0;
					
					for (let i = 0; i < float32.length; i++) {
						const s = Math.max(-1, Math.min(1, float32[i]));
						int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
						sumSq += s * s;
					}
					
					ws.send(int16.buffer);

					const rms = Math.sqrt(sumSq / float32.length);
					currentRms = rms; // Drive the visualizer UI

					if (rms > 0.035) {
						hasSpoken = true;
						silenceTime = 0;
					} else if (hasSpoken) {
						silenceTime += float32.length / hardwareSampleRate;
						if (silenceTime > 1.2) {
							finishUtterance();
						}
					}
				};

				const dummy = audioContext.createGain();
				dummy.gain.value = 0;
				source.connect(processor);
				processor.connect(dummy);
				dummy.connect(audioContext.destination);
			}
		} catch (err: any) {
			console.error('Mic error:', err);
			errorMessage = err.message || 'Microphone blocked';
			endCall();
		}
	}

	function finishUtterance() {
		callState = 'processing';
		currentRms = 0;
		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify({ event: 'stop_listening', sample_rate: hardwareSampleRate }));
		}
		// Do NOT cleanup hardware mic here as the session is perfectly continuous!
	}

	function startCall() {
		if (callState !== 'idle') return;
		callState = 'listening'; // transition state instantly
		
		try {
			// MUST CREATE AUDIO CONTEXT SYNCHRONOUSLY IN CLICK HANDLER
			const AC = window.AudioContext || (window as any).webkitAudioContext;
			audioContext = new AC();
			hardwareSampleRate = audioContext.sampleRate;
		} catch (e: any) {
			errorMessage = "Audio system initialization failed: " + e.message;
			return;
		}

		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const host = window.location.hostname;
		ws = new WebSocket(`${protocol}//${host}:8000/ws/voice`);

		ws.onmessage = (e) => {
			const data = JSON.parse(e.data);
			if (data.event === 'tts_ready') {
				playTTS(`${window.location.protocol}//${host}:8000/api/tts-audio`);
			} else if (data.event === 'error') {
				console.error('Agent Error:', data.msg);
				errorMessage = data.msg;
				endCall();
			}
		};

		ws.onclose = () => {
			if (callState !== 'idle') endCall();
		};

		startListeningPhase();
	}

	function endCall() {
		callState = 'idle';
		currentRms = 0;
		cleanupMic();
		if (ws) {
			ws.close();
			ws = null;
		}
		if (currentAudio) {
			currentAudio.pause();
			currentAudio = null;
		}
	}

	function handleAction() {
		if (callState === 'idle') {
			startCall();
		} else if (callState === 'listening') {
			// Force manual send
			hasSpoken = true;
			finishUtterance();
		} else {
			endCall();
			onClose();
		}
	}

	function handleHangUp() {
		endCall();
		onClose();
	}

	onMount(() => {
		// Auto-start the call when modal opens
		startCall();
	});

	onDestroy(() => {
		endCall();
	});
</script>

<div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
	<div class="glass-panel bg-crust/95 border border-white/10 rounded-3xl p-8 max-w-sm w-full shadow-2xl flex flex-col items-center">
		
		<!-- Header -->
		<h2 class="text-white text-xl font-display font-medium mb-1">Live AI Assistant</h2>
		<p class="text-slate-400 text-sm mb-8 font-medium">
			{#if callState === 'idle'}
				Disconnected
			{:else if callState === 'listening'}
				<span class="text-neon-primary animate-pulse">Listening...</span>
			{:else if callState === 'processing'}
				<span class="text-blue-400 animate-pulse">Agent is thinking...</span>
			{:else if callState === 'speaking'}
				<span class="text-white">Agent is speaking...</span>
			{/if}
		</p>

		<!-- Visualizer Circle -->
		<div class="relative w-32 h-32 flex items-center justify-center mb-10">
			<!-- Animated rings based on RMS volume -->
			{#if callState === 'listening' || callState === 'speaking'}
				<div 
					class="absolute inset-0 rounded-full transition-all duration-75 {callState === 'speaking' ? 'animate-pulse' : ''}"
					class:bg-neon-primary={callState === 'listening'}
					class:bg-blue-500={callState === 'speaking'}
					style={`opacity: ${0.15 + (currentRms * 6)}; transform: scale(${1 + (currentRms * 8)});`}
				></div>
				<div 
					class="absolute inset-2 rounded-full transition-all duration-150 {callState === 'speaking' ? 'animate-pulse' : ''}"
					class:bg-neon-primary={callState === 'listening'}
					class:bg-blue-400={callState === 'speaking'}
					style={`opacity: ${0.25 + (currentRms * 8)}; transform: scale(${1 + (currentRms * 6)});`}
				></div>
			{/if}
			
			<div class="z-10 w-20 h-20 rounded-full bg-surface0 border-[3px] shadow-inner flex items-center justify-center
				{callState === 'listening' ? 'border-neon-primary' : callState === 'processing' ? 'border-blue-500 border-dashed animate-spin-slow' : callState === 'speaking' ? 'border-blue-400' : 'border-surface1'}">
				{#if callState === 'processing'}
					<!-- Searching/Thinking icon -->
					<svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-blue-400" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2A10 10 0 1 0 22 12A10 10 0 0 0 12 2Zm0 18a8 8 0 1 1 8-8A8 8 0 0 1 12 20Z" opacity="0.3"/><path fill="currentColor" d="M12 2a10 10 0 0 0-10 10h2a8 8 0 0 1 8-8Z"/></svg>
				{:else}
					<!-- Mic icon -->
					<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" class="text-white">
						<path fill="currentColor" d="M12 14q-1.25 0-2.125-.875T9 11V5q0-1.25.875-2.125T12 2t2.125.875T15 5v6q0 1.25-.875 2.125T12 14m-1 7v-3.075q-2.6-.35-4.3-2.325T5 11h2q0 2.075 1.463 3.538T12 16t3.538-1.463T17 11h2q0 2.625-1.7 4.6t-4.3 2.325V21z"/>
					</svg>
				{/if}
			</div>
		</div>

		{#if errorMessage}
			<div class="bg-red-500/20 text-red-300 text-sm p-3 rounded mb-6 text-center border border-red-500/50 w-full shadow px-4">
				{errorMessage}
			</div>
		{/if}

		<!-- Controls -->
		<div class="flex gap-4 w-full justify-center">
			{#if callState === 'idle'}
				<button 
					onclick={handleAction}
					class="bg-blue-600 hover:bg-blue-500 text-white py-3 px-6 rounded-xl font-display font-medium shadow-lg transition-colors flex-1 border border-white/5">
					Start Call
				</button>
			{:else if callState === 'listening'}
				<button 
					onclick={handleAction}
					title="Force process audio"
					class="bg-surface0 hover:bg-surface1 border border-white/10 text-neon-primary rounded-xl p-4 font-display font-medium shadow-lg transition-colors">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M2.01 21L23 12L2.01 3L2 10l15 2l-15 2z"/></svg>
				</button>
			{/if}
			
			<button 
				onclick={handleHangUp}
				class="bg-red-600 hover:bg-red-500 text-white py-3 px-6 rounded-xl font-display font-medium shadow-lg transition-colors flex-1 flex items-center justify-center gap-2 border border-red-500/50">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"><path fill="currentColor" d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9c-.98.49-1.87 1.12-2.66 1.85c-.18.18-.43.28-.7.28c-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 0 1 0-1.4C3.36 8.42 7.46 6.5 12 6.5s8.64 1.92 11.71 5.18c.39.39.39 1.02 0 1.41l-2.48 2.48c-.18.18-.43.29-.71.29c-.27 0-.52-.11-.7-.28c-.79-.74-1.69-1.36-2.67-1.85c-.33-.16-.56-.5-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/></svg>
				Hang Up
			</button>
		</div>
	</div>
</div>

<style>
	.animate-fade-in {
		animation: fadeIn 0.2s ease-out forwards;
	}
	
	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	.animate-spin-slow {
		animation: spin 3s linear infinite;
	}
	
	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}
</style>
