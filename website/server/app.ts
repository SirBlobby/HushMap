import { createServer } from 'node:http';
import { handler } from '../build/handler.js';

const port = process.env.PORT || 3000;
const server = createServer(handler as any);

server.listen(port, () => {
	console.log(`Bun Server is listening on http://localhost:${port}`);
});
