import rasterio
from rasterio.windows import Window
from rasterio.warp import transform
import numpy as np
import time
import matplotlib.pyplot as plt

start_time = time.time()
thermal_image_path = "C:\\Users\\samuk\\Documents\\Ohjelmointi\\Web\\Thermal-data-viewer\\ImageRadianceConvert\\LC08_L1TP_107035_20150806_20200908_02_T1_B10.TIF"

# --- SÄÄDÄ NÄITÄ ARVOJA VAPAASTI ---
WINDOW_WIDTH = 250 
WINDOW_HEIGHT = 250  
# -------------------------------------

with rasterio.open(thermal_image_path) as src:
    print(f"Photo opened, size: {src.width}x{src.height} pixels. CRS: {src.crs}")

    # 1. Tokion keskipiste (WGS84), johon ikkuna halutaan keskittää
    tokio_lon, tokio_lat = 139.76, 35.68
    
    # Muunnetaan keskipiste kuvan omaan CRS-järjestelmään 
    xs, ys = transform('EPSG:4326', src.crs, [tokio_lon], [tokio_lat])
    center_east, center_north = xs[0], ys[0]
    
    # Haetaan keskipisteen pikseli-indeksit
    center_row, center_col = src.index(center_east, center_north)
    
    # 2. Leikataan ikkuna (keskitettynä Tokion ylle)
    col_off = center_col - (WINDOW_WIDTH // 2)
    row_off = center_row - (WINDOW_HEIGHT // 2)
    window = Window(col_off=col_off, row_off=row_off, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    # Luetaan lämpötilamatriisi
    dn_matrix = src.read(1, window=window)

    # 3. LASKETAAN IKKUNAN TARKAT MAANTIETEELLISET RAJAT
    # rasterio.windows.bounds hakee absoluuttiset reunat kuvan omassa projisoinnissa
    left, bottom, right, top = rasterio.windows.bounds(window, src.transform)
    
    # Muunnetaan vasen yläkulma (left, top) ja oikea alakulma (right, bottom) WGS84:ksi
    wgs_lons, wgs_lats = transform(src.crs, 'EPSG:4326', [left, right], [top, bottom])
    
    start_lng = wgs_lons[0]  # Vasen reuna (Länsi)
    end_lng = wgs_lons[1]    # Oikea reuna (Itä)
    
    start_lat = wgs_lats[0]  # Yläreuna (Pohjoinen)
    end_lat = wgs_lats[1]    # Alareuna (Etelä)

    # Lasketaan tarkat askelkoot per solu front-endiä varten
    lat_step = (start_lat - end_lat) / WINDOW_HEIGHT
    lng_step = (end_lng - start_lng) / WINDOW_WIDTH
    
    print("\n=== KOPIOI NÄMÄ ARVOT SUORAAN REACTIIN ===")
    print(f"const START_LAT = {start_lat};")
    print(f"const START_LNG = {start_lng};")
    print(f"const LAT_STEP = {lat_step};")
    print(f"const LNG_STEP = {lng_step};")
    print("===========================================\n")
    
    # Radiance- ja Celsius-muunnokset
    radiance = (0.0003342 * dn_matrix) + 0.1
    K1 = 774.89  
    K2 = 1321.08  
    
    with np.errstate(divide='ignore', invalid='ignore'):
        kelvin = K2 / np.log((K1 / radiance) + 1)
        celsius_calc = kelvin - 273.15
        celsius = np.where(celsius_calc < -50, np.nan, celsius_calc)
    
    # Tallennetaan kuvapreview
    plt.figure(figsize=(10, 10))
    plt.imshow(celsius, cmap='inferno', vmin=20, vmax=45)
    plt.axis('off')
    preview_filename = "tokio_lasersilma_preview.png"
    plt.savefig(preview_filename, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    # Save for backend
    np.save("tokio_celsius.npy", celsius)

print(f"Preview valmis: {preview_filename}")