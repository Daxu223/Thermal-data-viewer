import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Rectangle, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { fetchHeatmapData } from './services/heatmapApi';
import type { HeatmapData }  from './services/heatmapApi';

// TODO: These should update dynamically based off the thermal conversion script.
const START_LAT = 35.71354654335892;
const START_LNG = 139.7177582184755;
const LAT_STEP = 0.00026701422376652315;
const LNG_STEP = 0.0003356355227203949;

const getHeatColor = (temp: number, min: number, max: number): string => {
  const ratio = (temp - min) / (max - min);
  const hue = (1 - ratio) * 240;
  return `hsl(${hue}, 100%, 50%)`;
}

const App = () => {
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getData = async () => {
      try {
        setIsLoading(true);
        const data = await fetchHeatmapData();
        setHeatmapData(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch heatmap data');
      } finally {
        setIsLoading(false);
      }
    };

    getData();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error || !heatmapData) {
    return <p>Something went wrong :3</p>
  }

  // Data was loaded, so we can display the map
  const { min_temp, max_temp, data, resolution } = heatmapData;

  return (
    <div>
      <header>
        <h1>Lämpökartta</h1>
        <p style={{ margin: '5px 0 0 0', fontSize: '0.9rem', color: '#aaa' }}>
          Resoluutio: {resolution} | Maksimi: {max_temp}°C | Minimi: {min_temp}°C
        </p>
      </header>

      <div>
        <MapContainer center={[START_LAT, START_LNG]} zoom={14} style={{ height: '80vh', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {data.map((row, rowIndex) =>
            row.map((temp, colIndex) => {
              const northWest : [number, number] = [
                START_LAT - rowIndex * LAT_STEP,
                START_LNG + colIndex * LNG_STEP
              ];
              const southEast : [number, number] = [
                START_LAT - (rowIndex + 1) * LAT_STEP,
                START_LNG + (colIndex + 1)* LNG_STEP
              ];

              const cellBounds : [[number, number], [number, number]] = [northWest, southEast];
              const color = getHeatColor(temp, min_temp, max_temp);

              return (
                <Rectangle
                  key={`${rowIndex}-${colIndex}`}
                  bounds={cellBounds}
                  pathOptions={{ fillColor: color, fillOpacity: 0.7, color: 'none', weight: 0.5 }}
                >
                  <Tooltip sticky>
                    <span>Lämpötila: <strong>{temp.toFixed(1)}°C</strong></span>
                  </Tooltip>
                </Rectangle>
              );
            })
          )}
        </MapContainer>
      </div>
    </div>
  );
}

export default App
