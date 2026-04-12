<script lang="ts">
	import AICallModal from './AICallModal.svelte';

	let isModalOpen = $state(false);

	function handleClick() {
		isModalOpen = true;
	}

	function closeModal() {
		isModalOpen = false;
	}
</script>

<div class="voice-btn-wrapper z-40">
	<div class="halo-ring halo-ring-1"></div>
	<div class="halo-ring halo-ring-2"></div>
	<div class="halo-ring halo-ring-3"></div>
	<div class="wave-container">
		<div class="wave wave-1"></div>
		<div class="wave wave-2"></div>
		<div class="wave wave-3"></div>
	</div>
	<button
		id="voice-assistant-btn"
		class="voice-btn {isModalOpen ? 'pressed' : ''}"
		onclick={handleClick}
		aria-label="Voice Assistant"
		title="Voice Assistant"
	>
		<svg
			xmlns="http://www.w3.org/2000/svg"
			viewBox="0 0 24 24"
			fill="none"
			class="chat-icon {isModalOpen ? 'icon-active' : ''}"
		>
			<path
				d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z"
				fill="currentColor"
			/>
			<circle cx="8" cy="10" r="1.2" fill="white" opacity="0.9" />
			<circle cx="12" cy="10" r="1.2" fill="white" opacity="0.9" />
			<circle cx="16" cy="10" r="1.2" fill="white" opacity="0.9" />
		</svg>
	</button>
</div>

{#if isModalOpen}
	<AICallModal onClose={closeModal} />
{/if}

<style>
	.voice-btn-wrapper {
		position: fixed;
		bottom: 5.5rem;
		left: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 64px;
		height: 64px;
	}

	@media (min-width: 768px) {
		.voice-btn-wrapper {
			bottom: 1.75rem;
			left: 1.5rem;
		}
	}

	.halo-ring {
		position: absolute;
		border-radius: 50%;
		pointer-events: none;
		animation: halo-pulse 3s ease-in-out infinite;
	}

	.halo-ring-1 {
		width: 80px;
		height: 80px;
		background: conic-gradient(
			from 0deg,
			#f38ba8,
			#fab387,
			#f9e2af,
			#94e2d5,
			#89b4fa,
			#f38ba8
		);
		border-radius: 50%;
		opacity: 0.35;
		filter: blur(6px);
		animation: halo-spin 4s linear infinite, halo-pulse 3s ease-in-out infinite;
	}

	.halo-ring-2 {
		width: 94px;
		height: 94px;
		background: conic-gradient(
			from 180deg,
			#89b4fa,
			#94e2d5,
			#f9e2af,
			#fab387,
			#f38ba8,
			#89b4fa
		);
		border-radius: 50%;
		opacity: 0.22;
		filter: blur(10px);
		animation: halo-spin-reverse 6s linear infinite, halo-pulse 3s ease-in-out infinite 0.4s;
	}

	.halo-ring-3 {
		width: 108px;
		height: 108px;
		background: conic-gradient(
			from 90deg,
			#f9e2af,
			#f38ba8,
			#89b4fa,
			#94e2d5,
			#fab387,
			#f9e2af
		);
		border-radius: 50%;
		opacity: 0.14;
		filter: blur(14px);
		animation: halo-spin 9s linear infinite, halo-pulse 3s ease-in-out infinite 0.8s;
	}

	.wave-container {
		position: absolute;
		width: 64px;
		height: 64px;
		border-radius: 50%;
		pointer-events: none;
		overflow: visible;
	}

	.wave {
		position: absolute;
		inset: 0;
		border-radius: 50%;
		border: 2px solid transparent;
	}

	.wave-1 {
		background: transparent;
		box-shadow: 0 0 0 0 rgba(243, 139, 168, 0.6);
		animation: wave-expand 2.5s ease-out infinite;
	}

	.wave-2 {
		background: transparent;
		box-shadow: 0 0 0 0 rgba(137, 180, 250, 0.5);
		animation: wave-expand 2.5s ease-out infinite 0.7s;
	}

	.wave-3 {
		background: transparent;
		box-shadow: 0 0 0 0 rgba(148, 226, 213, 0.4);
		animation: wave-expand 2.5s ease-out infinite 1.4s;
	}

	.voice-btn {
		position: relative;
		z-index: 2;
		width: 56px;
		height: 56px;
		border-radius: 50%;
		border: none;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #1e1e2e 0%, #313244 100%);
		box-shadow:
			0 0 0 2px rgba(243, 139, 168, 0.5),
			0 0 24px rgba(243, 139, 168, 0.35),
			0 0 48px rgba(137, 180, 250, 0.2),
			inset 0 1px 0 rgba(255, 255, 255, 0.12);
		transition:
			transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1),
			box-shadow 0.3s ease;
		animation: btn-glow-shift 4s ease-in-out infinite;
	}

	.voice-btn::before {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: 50%;
		background: conic-gradient(
			from var(--hue, 0deg),
			rgba(243, 139, 168, 0.15),
			rgba(250, 179, 135, 0.1),
			rgba(249, 226, 175, 0.1),
			rgba(148, 226, 213, 0.15),
			rgba(137, 180, 250, 0.15),
			rgba(243, 139, 168, 0.15)
		);
		animation: halo-spin 6s linear infinite;
		z-index: -1;
	}

	.voice-btn:hover {
		transform: scale(1.12);
		box-shadow:
			0 0 0 2px rgba(243, 139, 168, 0.8),
			0 0 30px rgba(243, 139, 168, 0.5),
			0 0 60px rgba(137, 180, 250, 0.3),
			0 0 80px rgba(148, 226, 213, 0.2),
			inset 0 1px 0 rgba(255, 255, 255, 0.18);
	}

	.voice-btn.pressed {
		transform: scale(0.93);
		box-shadow:
			0 0 0 3px rgba(148, 226, 213, 0.9),
			0 0 35px rgba(148, 226, 213, 0.6),
			0 0 70px rgba(137, 180, 250, 0.4),
			inset 0 1px 0 rgba(255, 255, 255, 0.2);
	}

	.chat-icon {
		width: 26px;
		height: 26px;
		color: #f38ba8;
		transition: color 0.3s ease, transform 0.3s ease;
		filter: drop-shadow(0 0 6px rgba(243, 139, 168, 0.7));
		animation: icon-color-shift 4s ease-in-out infinite;
	}

	.chat-icon.icon-active {
		color: #94e2d5;
		filter: drop-shadow(0 0 8px rgba(148, 226, 213, 0.9));
		transform: scale(1.1);
	}

	@keyframes halo-spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	@keyframes halo-spin-reverse {
		from { transform: rotate(360deg); }
		to { transform: rotate(0deg); }
	}

	@keyframes halo-pulse {
		0%, 100% { opacity: var(--base-opacity, 0.3); transform: scale(1) rotate(0deg); }
		50% { opacity: calc(var(--base-opacity, 0.3) * 1.6); transform: scale(1.05) rotate(180deg); }
	}

	@keyframes wave-expand {
		0% {
			box-shadow: 0 0 0 0 currentColor;
			opacity: 0.8;
		}
		100% {
			box-shadow: 0 0 0 28px transparent;
			opacity: 0;
		}
	}

	@keyframes btn-glow-shift {
		0%, 100% {
			box-shadow:
				0 0 0 2px rgba(243, 139, 168, 0.5),
				0 0 24px rgba(243, 139, 168, 0.35),
				0 0 48px rgba(137, 180, 250, 0.2),
				inset 0 1px 0 rgba(255, 255, 255, 0.12);
		}
		25% {
			box-shadow:
				0 0 0 2px rgba(250, 179, 135, 0.5),
				0 0 24px rgba(250, 179, 135, 0.35),
				0 0 48px rgba(243, 139, 168, 0.2),
				inset 0 1px 0 rgba(255, 255, 255, 0.12);
		}
		50% {
			box-shadow:
				0 0 0 2px rgba(137, 180, 250, 0.5),
				0 0 24px rgba(137, 180, 250, 0.35),
				0 0 48px rgba(148, 226, 213, 0.2),
				inset 0 1px 0 rgba(255, 255, 255, 0.12);
		}
		75% {
			box-shadow:
				0 0 0 2px rgba(148, 226, 213, 0.5),
				0 0 24px rgba(148, 226, 213, 0.35),
				0 0 48px rgba(249, 226, 175, 0.2),
				inset 0 1px 0 rgba(255, 255, 255, 0.12);
		}
	}

	@keyframes icon-color-shift {
		0%, 100% { color: #f38ba8; filter: drop-shadow(0 0 6px rgba(243, 139, 168, 0.7)); }
		25% { color: #fab387; filter: drop-shadow(0 0 6px rgba(250, 179, 135, 0.7)); }
		50% { color: #89b4fa; filter: drop-shadow(0 0 6px rgba(137, 180, 250, 0.7)); }
		75% { color: #94e2d5; filter: drop-shadow(0 0 6px rgba(148, 226, 213, 0.7)); }
	}
</style>
