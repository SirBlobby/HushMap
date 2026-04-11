FROM oven/bun:latest AS builder

WORKDIR /app

# Install dependencies
COPY website/package.json website/bun.lock ./
RUN bun install --frozen-lockfile

# Build the SvelteKit application
COPY website/ .
RUN bun run build

# Setup the production environment
FROM oven/bun:latest

WORKDIR /app

# Copy production dependencies configuration and install
COPY --from=builder /app/package.json /app/bun.lock ./
RUN bun install --production --frozen-lockfile

# Copy the build output and the custom Bun server
COPY --from=builder /app/build ./build
COPY --from=builder /app/server ./server

EXPOSE 3000

CMD ["bun", "run", "server/app.ts"]
