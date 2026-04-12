import { UMD_LOCATIONS } from "./map.svelte";

export interface Alert {
    id: string;
    locId: string;
    loc: string;
    level: number;
    time: string;
    timestamp: number;
}

class AlertsState {
    activeAlerts = $state<Alert[]>([]);
    alertHistory = new Map<string, number>();

    processLiveReadings(latestReadings: any[]) {
        const now = Date.now();
        
        for (const room of latestReadings) {
            // Only fire if the reading is >= 65dB (Disruptive or Harmful)
            if (room.db >= 65) {
                const roomDate = new Date(room.date.endsWith('Z') ? room.date : room.date + 'Z').getTime();
                
                // Ensure the reading is recent (within 5 minutes, 300000ms), to prevent alerting on stale data on initial load
                if (now - roomDate < 300000) {
                    const lastAlert = this.alertHistory.get(room.room_id) || 0;
                    
                    // Cooldown: Don't alert for the same location within 3 minutes (180000ms)
                    if (now - lastAlert > 180000) {
                        const locData = UMD_LOCATIONS.find(l => l.id === room.room_id);
                        const locName = locData ? locData.name : room.room_id;
                        
                        const d = new Date(roomDate);
                        const timeStr = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' }) + ' EST';

                        this.activeAlerts.unshift({
                            id: Math.random().toString(36).substring(2, 9),
                            locId: room.room_id,
                            loc: locName,
                            level: Number(room.db.toFixed(1)),
                            time: timeStr,
                            timestamp: now
                        });
                        
                        // Keep a max of 10 alerts logic
                        if (this.activeAlerts.length > 20) {
                            this.activeAlerts.pop();
                        }

                        this.alertHistory.set(room.room_id, now);
                    }
                }
            }
        }
    }

    dismissAlert(id: string) {
        this.activeAlerts = this.activeAlerts.filter(a => a.id !== id);
    }
    
    clearAll() {
        this.activeAlerts = [];
    }
}

export const alertsState = new AlertsState();
