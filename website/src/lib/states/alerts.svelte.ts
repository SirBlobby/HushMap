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

            if (room.db >= 65) {
                const roomDate = new Date(room.date.endsWith('Z') ? room.date : room.date + 'Z').getTime();


                if (now - roomDate < 300000) {
                    const lastAlert = this.alertHistory.get(room.room_id) || 0;


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
