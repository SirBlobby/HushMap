import { browser } from '$app/environment';

class ThemeState {
	isLight = $state(false);
	isHighContrast = $state(false);
	isColorBlindFriendly = $state(false);

	constructor() {
		if (browser) {
			this.isLight = localStorage.getItem('theme') === 'light';
			this.isHighContrast = localStorage.getItem('highContrast') === 'true';
			this.isColorBlindFriendly = localStorage.getItem('colorBlind') === 'true';
			this.updateDOM();
		}
	}

	toggle() {
		this.isLight = !this.isLight;
		if (browser) {
			localStorage.setItem('theme', this.isLight ? 'light' : 'dark');
			this.updateDOM();
		}
	}

	toggleHighContrast() {
		this.isHighContrast = !this.isHighContrast;
		if (browser) {
			localStorage.setItem('highContrast', this.isHighContrast ? 'true' : 'false');
			this.updateDOM();
		}
	}

	toggleColorBlind() {
		this.isColorBlindFriendly = !this.isColorBlindFriendly;
		if (browser) {
			localStorage.setItem('colorBlind', this.isColorBlindFriendly ? 'true' : 'false');
			this.updateDOM();
		}
	}

	private updateDOM() {
		if (browser) {
			if (this.isLight) {
				document.documentElement.classList.add('light-theme');
			} else {
				document.documentElement.classList.remove('light-theme');
			}

			if (this.isHighContrast) {
				document.documentElement.classList.add('high-contrast');
			} else {
				document.documentElement.classList.remove('high-contrast');
			}

			if (this.isColorBlindFriendly) {
				document.documentElement.classList.add('color-blind');
			} else {
				document.documentElement.classList.remove('color-blind');
			}
		}
	}
}

export const themeState = new ThemeState();
