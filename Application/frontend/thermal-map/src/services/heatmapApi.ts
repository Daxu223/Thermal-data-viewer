// TODO
const BASE_URL = "http://localhost:8000/api";

// Tee interface backendistä saatavaa dataa varten
export interface HeatmapData {
    max_temp: number;
    min_temp: number;
    resolution: string;
    data: number[][]; // This is the 2D array of temp values from backend
}
// Hae data promisella backendistä ja tallenna se responseen
export const fetchHeatmapData = async (): Promise<HeatmapData> => {
    try {
        const response = await fetch(`${BASE_URL}/temperature`);

        // Muuta response jsoniksi ja palaute data App komponenttiin
        const data: HeatmapData = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching heatmap data:", error);
        throw error;
    }
}

