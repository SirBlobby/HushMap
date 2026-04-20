<script lang="ts">
    import Icon from '@iconify/svelte';
</script>

<div class="min-h-screen pt-24 pb-32 px-6 flex flex-col items-center">
    <div class="max-w-4xl w-full">
        <!-- Header Section -->
        <div class="text-center mb-16 relative">
            <h1 class="text-5xl md:text-6xl font-bold mb-6 text-white drop-shadow-[0_0_15px_rgba(0,243,255,0.8)]">
                HushMap
            </h1>
            <div class="inline-flex items-center justify-center gap-2 mb-6 px-4 py-2 bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border border-yellow-500/50 rounded-full shadow-[0_0_15px_rgba(234,179,8,0.3)]">
                <Icon icon="mdi:trophy" class="text-xl text-yellow-400" />
                <span class="text-lg font-semibold text-yellow-400">Best UI/UX Bitcamp 2026</span>
            </div>
            <p class="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
                A real-time study buddy platform integrating vision AI, speech recognition, and map data to optimize campus space utilization.
            </p>
        </div>

        <!-- Problem Section -->
        <div class="glass-panel p-10 rounded-3xl border border-white/10 mb-16 relative overflow-hidden group">
            <div class="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <h2 class="text-3xl font-semibold mb-8 text-white flex items-center gap-3">
                <span class="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
                The Problem: Campus Noise and Crowds
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                    <h3 class="text-xl font-medium text-white mb-2">Sensory Overload</h3>
                    <p class="text-slate-400">Unexpectedly loud environments can trigger severe sensory overload for neurodivergent students or other students with high sensitivity.</p>
                </div>
                <div>
                    <h3 class="text-xl font-medium text-white mb-2">Awkward Confrontation</h3>
                    <p class="text-slate-400">Neither librarians nor other students want to initiate uncomfortable confrontations when noise levels spike.</p>
                </div>
                <div>
                    <h3 class="text-xl font-medium text-white mb-2">Wasted Time</h3>
                    <p class="text-slate-400">Students burn time walking to study spots only to find them packed and loud, wishing they knew before leaving their dorm.</p>
                </div>
            </div>
        </div>

        <!-- Solution Section -->
        <div class="glass-panel p-10 rounded-3xl border border-white/10 mb-16 relative overflow-hidden group">
            <div class="absolute inset-0 bg-gradient-to-br from-neon-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <h2 class="text-3xl font-semibold mb-8 text-white flex items-center gap-3">
                <span class="w-2 h-2 rounded-full bg-neon-blue shadow-[0_0_8px_rgba(0,243,255,0.8)]"></span>
                Our Solution: HushMap
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                <div>
                    <h3 class="text-xl font-medium text-neon-blue mb-2">Real-Time Mapping</h3>
                    <p class="text-slate-400">We track noise levels across campus as they happen.</p>
                </div>
                <div>
                    <h3 class="text-xl font-medium text-neon-blue mb-2">Historical Trends</h3>
                    <p class="text-slate-400">We analyze past data to predict the best times to study.</p>
                </div>
                <div>
                    <h3 class="text-xl font-medium text-neon-blue mb-2">Active Control</h3>
                    <p class="text-slate-400">We use smart devices to keep noise levels within acceptable limits.</p>
                </div>
            </div>

            <!-- Features -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                <!-- 1 -->
                <div class="bg-white/5 p-6 rounded-2xl border border-white/10">
                    <h4 class="text-lg font-semibold text-white mb-3">1. The Interactive Map</h4>
                    <ul class="space-y-2 text-sm text-slate-400">
                        <li><strong class="text-slate-300">24hr Data Storage:</strong> Database with the past 24 hrs' worth of sound volume data saved for analysis.</li>
                        <li><strong class="text-slate-300">Live Updates:</strong> Real-time updates directly from campus-wide noise sensors.</li>
                        <li><strong class="text-slate-300">Noise Legend:</strong> Visual legend and graph describing noise levels and thresholds.</li>
                    </ul>
                </div>
                <!-- 2 -->
                <div class="bg-white/5 p-6 rounded-2xl border border-white/10">
                    <h4 class="text-lg font-semibold text-white mb-3">2. TerpAI</h4>
                    <ul class="space-y-2 text-sm text-slate-400">
                        <li><strong class="text-slate-300">Multichannel Access:</strong> Talk to Terp AI assistant in the website or in person with the sensors.</li>
                        <li><strong class="text-slate-300">Study Recommendations:</strong> TerpAI will let you know the best spots to study based on current noise data.</li>
                    </ul>
                </div>
                <!-- 3 -->
                <div class="bg-white/5 p-6 rounded-2xl border border-white/10">
                    <h4 class="text-lg font-semibold text-white mb-3">3. Accessibility Settings</h4>
                    <p class="text-sm text-slate-400 mb-2">HushMap ensures usability for all students through integrated accessibility tools.</p>
                    <ul class="space-y-2 text-sm text-slate-400">
                        <li><strong class="text-slate-300">Color Blind Mode:</strong> Optimized palette for color vision deficiencies.</li>
                        <li><strong class="text-slate-300">Language Translation:</strong> Multi-language support for international users.</li>
                        <li><strong class="text-slate-300">High Contrast Mode:</strong> Enhanced legibility for low-vision accessibility.</li>
                    </ul>
                </div>
                <!-- 4 -->
                <div class="bg-white/5 p-6 rounded-2xl border border-white/10">
                    <h4 class="text-lg font-semibold text-white mb-3">4. The On-site Librarians</h4>
                    <ul class="space-y-2 text-sm text-slate-400">
                        <li><strong class="text-slate-300">Automated Noise Management:</strong> Nodes monitor noise levels and react to noise spikes by telling students to quiet down.</li>
                        <li><strong class="text-slate-300">Interactive Assistance:</strong> Students can interact directly by asking the librarians questions in real-time.</li>
                        <li><strong class="text-slate-300">Privacy & Analytics:</strong> No audio recorded—only noise data. Camera footage determines occupancy by comparing seats vs. people.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Tech Stack Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
            <!-- Frontend -->
            <div class="glass-panel p-8 rounded-3xl border border-white/10 relative overflow-hidden group">
                <div class="absolute inset-0 bg-gradient-to-br from-neon-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <h2 class="text-2xl font-semibold mb-4 text-white flex items-center gap-3">
                    <span class="w-2 h-2 rounded-full bg-neon-blue shadow-[0_0_8px_rgba(0,243,255,0.8)]"></span>
                    Frontend
                </h2>
                <ul class="space-y-3 text-slate-400">
                    <li class="flex items-center gap-2"><span class="text-neon-blue">▹</span> SvelteKit 5</li>
                    <li class="flex items-center gap-2"><span class="text-neon-blue">▹</span> Tailwind CSS 4</li>
                    <li class="flex items-center gap-2"><span class="text-neon-blue">▹</span> MapLibre GL JS</li>
                    <li class="flex items-center gap-2"><span class="text-neon-blue">▹</span> Chart.js</li>
                </ul>
            </div>

            <!-- Backend -->
            <div class="glass-panel p-8 rounded-3xl border border-white/10 relative overflow-hidden group">
                <div class="absolute inset-0 bg-gradient-to-br from-neon-purple/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <h2 class="text-2xl font-semibold mb-4 text-white flex items-center gap-3">
                    <span class="w-2 h-2 rounded-full bg-neon-purple shadow-[0_0_8px_rgba(188,19,254,0.8)]"></span>
                    Backend
                </h2>
                <ul class="space-y-3 text-slate-400">
                    <li class="flex items-center gap-2"><span class="text-neon-purple">▹</span> Python & FastAPI</li>
                    <li class="flex items-center gap-2"><span class="text-neon-purple">▹</span> WebSockets</li>
                    <li class="flex items-center gap-2"><span class="text-neon-purple">▹</span> MongoDB / In-Memory Mock Data</li>
                </ul>
            </div>

            <!-- AI Features -->
            <div class="glass-panel p-8 rounded-3xl border border-white/10 relative overflow-hidden group md:col-span-2">
                <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <h2 class="text-2xl font-semibold mb-4 text-white flex items-center gap-3">
                    <span class="w-2 h-2 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]"></span>
                    AI Integration
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <ul class="space-y-3 text-slate-400">
                        <li class="flex items-center gap-2"><span class="text-white">▹</span> Terp AI (Primary Conversational Agent)</li>
                        <li class="flex items-center gap-2"><span class="text-white">▹</span> Gemini 2.5 Flash (Seamless Fallback)</li>
                        <li class="flex items-center gap-2"><span class="text-white">▹</span> Faster-Whisper (On-device Speech-to-Text)</li>
                    </ul>
                    <ul class="space-y-3 text-slate-400">
                        <li class="flex items-center gap-2"><span class="text-white">▹</span> ElevenLabs (Text-to-Speech Voice)</li>
                        <li class="flex items-center gap-2"><span class="text-white">▹</span> Yolo v8 Vision (Room Image Analysis)</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Project Team Section -->
        <div class="glass-panel p-10 rounded-3xl border border-white/10 text-center relative overflow-hidden group">
            <div class="absolute inset-0 bg-gradient-to-t from-neon-purple/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <h2 class="text-3xl font-semibold mb-6 text-white">Project Team</h2>
            <div class="flex flex-wrap justify-center gap-6 text-lg text-slate-300">
                <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10 shadow-[0_0_10px_rgba(188,19,254,0.2)]">Gagan (Adith) Manjunatha</span>
                <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10 shadow-[0_0_10px_rgba(188,19,254,0.2)]">Sameera Nageshwar</span>
                <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10 shadow-[0_0_10px_rgba(188,19,254,0.2)]">Jolie Wu</span>
                <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10 shadow-[0_0_10px_rgba(188,19,254,0.2)]">Sarayu Jilludumudi</span>
            </div>
        </div>
    </div>
</div>