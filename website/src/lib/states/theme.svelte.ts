import { browser } from '$app/environment';

class ThemeState {
	isLight = $state(false);

	toggle() {
		this.isLight = !this.isLight;
		if (browser) {
			if (this.isLight) {
				document.documentElement.classList.add('light-theme');
			} else {
				document.documentElement.classList.remove('light-theme');
			}
		}
	}
}

export const themeState = new ThemeState();
