import adapter from '@sveltejs/adapter-static';


const config = {
	compilerOptions: {

		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter({
			pages: '../backend/static',
			assets: '../backend/static',
			fallback: 'index.html',
			strict: false
		})
	}
};

export default config;
