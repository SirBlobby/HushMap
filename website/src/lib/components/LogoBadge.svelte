<script lang="ts">
	import { themeState } from '$lib/states/theme.svelte';
	import logoDark from '$lib/assets/logo/HushMapLogo_dark.png';
	import logoLight from '$lib/assets/logo/HushMapLogo_light.png';

	let expanded = $state(false);
	let collapseTimer: ReturnType<typeof setTimeout>;

	function handleClick() {
		if (expanded) {
			expanded = false;
			clearTimeout(collapseTimer);
		} else {
			expanded = true;
			clearTimeout(collapseTimer);
			collapseTimer = setTimeout(() => {
				expanded = false;
			}, 3000);
		}
	}
</script>

<button
	id="logo-badge-btn"
	class="logo-badge {expanded ? 'expanded' : ''}"
	onclick={handleClick}
	aria-label="HushMap logo"
>
	<div class="halo halo-1"></div>
	<div class="halo halo-2"></div>
	<div class="halo halo-3"></div>

	<div class="badge-inner">
		<div class="logo-wrap">
			<img
				src={themeState.isLight ? logoLight : logoDark}
				alt="HushMap"
				class="logo-img"
			/>
		</div>
		<span class="badge-title">HushMap</span>
	</div>
</button>

<style>
	.logo-badge {
		position: fixed;
		top: 1rem;
		left: 50%;
		transform: translateX(-50%) scale(1);
		z-index: 55;
		cursor: pointer;
		background: none;
		border: none;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	.logo-badge.expanded {
		transform: translateX(-50%) translateY(28px) scale(1.3);
	}

	.badge-inner {
		position: relative;
		z-index: 2;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		background: rgba(30, 30, 46, 0.65);
		backdrop-filter: blur(14px);
		-webkit-backdrop-filter: blur(14px);
		border: 1px solid rgba(243, 139, 168, 0.25);
		border-radius: 20px;
		padding: 7px 16px 8px;
		box-shadow:
			0 2px 16px rgba(0, 0, 0, 0.4),
			inset 0 1px 0 rgba(255, 255, 255, 0.08);
		transition: border-color 0.4s ease, box-shadow 0.4s ease;
	}

	:global(.light-theme) .badge-inner {
		background: rgba(239, 241, 245, 0.75);
		border-color: rgba(234, 118, 203, 0.3);
	}

	.logo-badge:hover .badge-inner {
		border-color: rgba(243, 139, 168, 0.55);
	}

	.logo-wrap {
		width: 76px;
		height: 46px;
		border-radius: 12px;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.logo-img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		border-radius: 10px;
	}

	.badge-title {
		font-family: 'Comic Relief', 'Comic Neue', 'Comic Sans MS', cursive, sans-serif;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: #f38ba8;
		animation: title-color-shift 5s ease-in-out infinite;
		line-height: 1;
	}

	:global(.light-theme) .badge-title {
		color: #ea76cb;
	}

	.halo {
		position: absolute;
		border-radius: 50%;
		pointer-events: none;
		top: 50%;
		left: 50%;
	}

	.halo-1 {
		width: 70px;
		height: 70px;
		margin-top: -35px;
		margin-left: -35px;
		background: conic-gradient(
			from 0deg,
			#f38ba8,
			#fab387,
			#f9e2af,
			#94e2d5,
			#89b4fa,
			#f38ba8
		);
		opacity: 0;
		filter: blur(10px);
		transition: opacity 0.4s ease;
		animation: halo-spin 5s linear infinite;
	}

	.halo-2 {
		width: 90px;
		height: 90px;
		margin-top: -45px;
		margin-left: -45px;
		background: conic-gradient(
			from 180deg,
			#89b4fa,
			#94e2d5,
			#f9e2af,
			#fab387,
			#f38ba8,
			#89b4fa
		);
		opacity: 0;
		filter: blur(16px);
		transition: opacity 0.4s ease;
		animation: halo-spin-reverse 8s linear infinite;
	}

	.halo-3 {
		width: 114px;
		height: 114px;
		margin-top: -57px;
		margin-left: -57px;
		background: conic-gradient(
			from 90deg,
			#f9e2af,
			#f38ba8,
			#89b4fa,
			#94e2d5,
			#fab387,
			#f9e2af
		);
		opacity: 0;
		filter: blur(22px);
		transition: opacity 0.4s ease;
		animation: halo-spin 12s linear infinite;
	}

	.logo-badge.expanded .halo-1 { opacity: 0.28; }
	.logo-badge.expanded .halo-2 { opacity: 0.16; }
	.logo-badge.expanded .halo-3 { opacity: 0.09; }

	@keyframes halo-spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	@keyframes halo-spin-reverse {
		from { transform: rotate(360deg); }
		to { transform: rotate(0deg); }
	}

	@keyframes title-color-shift {
		0%, 100% { color: #f38ba8; }
		20%       { color: #fab387; }
		40%       { color: #f9e2af; }
		60%       { color: #94e2d5; }
		80%       { color: #89b4fa; }
	}
</style>
