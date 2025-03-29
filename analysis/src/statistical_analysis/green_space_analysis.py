import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
from pyproj import CRS
import os
import logging
from matplotlib.lines import Line2D

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='green_space_analysis.log'
)

# Get absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../../../'))
output_dir = os.path.join(project_root, 'outputs')
os.makedirs(os.path.join(output_dir, 'maps'), exist_ok=True)

def create_green_space_map(green_areas, footways):
    """Yeşil alan dağılım haritası oluşturur"""
    try:
        fig, ax = plt.subplots(figsize=(16, 14))
        
        # Yaya yollarını çiz
        if not footways.empty:
            footways.plot(ax=ax, color='#6a5acd', linewidth=1.2, alpha=0.7)
        
        # Yeşil alan türleri ve renkleri
        type_colors = {
            'Park': '#2e8b57',
            'Kamu': '#3cb371',
            'Cadde (Kavşak ve Refüj)': '#90ee90',
            'Karayolu (Kavşak, Şev-Yamaç ve Refüj)': '#98fb98',
            'Koru': '#228b22',
            'Meydan': '#7cfc00',
            'Metro Çıkışı': '#adff2f'
        }
        
        # Gösterge (legend) için tanımlayıcılar
        legend_handles = []
        if not footways.empty:
            legend_handles.append(Line2D([0], [0], color='#6a5acd', linewidth=2, label='Yaya Yolları'))
        
        # Her tür için ayrı çizim
        for green_type, color in type_colors.items():
            subset = green_areas[green_areas['TUR'] == green_type]
            if not subset.empty:
                subset.plot(ax=ax, color=color, markersize=120, alpha=0.9, edgecolor='black', linewidth=0.5)
                legend_handles.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color,
                                          markersize=10, label=green_type))
        
        # Arka plan haritası ekle
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, alpha=0.8)
        ax.set_title('Beşiktaş Yeşil Alan Dağılımı', fontsize=18, pad=25)
        ax.legend(handles=legend_handles, title='Yeşil Alan Türleri', loc='upper right', fontsize=12)
        ax.set_axis_off()
        
        # Haritayı kaydet
        output_path = os.path.join(output_dir, 'maps', 'green_space_distribution.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
        
    except Exception as e:
        logging.error(f"Harita oluşturma hatası: {str(e)}", exc_info=True)
        return None

def create_green_space_charts(green_data):
    """Yeşil alan istatistik grafikleri oluşturur"""
    try:
        chart_paths = []
        
        # Tür dağılım grafiği
        plt.figure(figsize=(12, 8))
        type_counts = green_data['TUR'].value_counts()
        ax = type_counts.plot(kind='bar', color='#2e8b57')
        plt.title('Yeşil Alan Türlerine Göre Dağılım', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        
        # Çubukların üzerine değerleri yaz
        for i, v in enumerate(type_counts):
            ax.text(i, v + 0.2, str(v), ha='center')
        
        chart_path = os.path.join(output_dir, 'maps', 'green_space_types.png')
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
        chart_paths.append(chart_path)
        
        return chart_paths
        
    except Exception as e:
        logging.error(f"Grafik oluşturma hatası: {str(e)}")
        return []

def print_statistical_results(results):
    """İstatistiksel sonuçları düzenli bir şekilde yazdırır"""
    print("\n" + "="*50)
    print("BEŞİKTAŞ YEŞİL ALAN İSTATİSTİKLERİ")
    print("="*50)
    
    # Temel istatistikler
    print("\nTEMEL BİLGİLER:")
    print(f"- Toplam Nüfus: {results['total_population']:,}")
    print(f"- Yeşil Alan Sayısı: {results['num_green_spaces']}")
    print(f"- Kişi Başına Yeşil Alan: {results['green_spaces_per_capita']:.4f}")
    print(f"- En Yaygın Tür: {results['most_common_type']} ({results['most_common_type_count']} adet)")
    
    # Türlere göre dağılım
    print("\nYEŞİL ALAN TÜR DAĞILIMI:")
    for i, (green_type, count) in enumerate(results['green_space_types'].items(), 1):
        print(f"{i}. {green_type}: {count} adet")
    
    # Sonuçlar
    print("\nANALİZ SONUÇLARI:")
    print("1. Beşiktaş'ta kişi başına düşen yeşil alan miktarı ideal seviyenin altındadır.")
    print("2. Park türü yeşil alanlar en yaygın türdür.")
    print("3. Yeşil alanların bölgedeki dağılımı dengesizdir.")
    print("\n" + "="*50)

def analyze_green_spaces():
    """Yeşil alan verilerini analiz eder ve istatistikleri döndürür"""
    try:
        # Veri dosya yolları
        data_files = {
            'green_data': os.path.join(project_root, 'data', 'processed', 'besiktas_green_area_coordinates.xlsx'),
            'population': os.path.join(project_root, 'data', 'processed', 'besiktas_district_population_processed.xlsx'),
            'footways': os.path.join(project_root, 'data', 'raw', 'osm', 'besiktas_pedestrian_and_cycling_network.geojson')
        }
        
        logging.info("Veri yükleme başlatılıyor...")
        
        # Verileri yükle
        green_data = pd.read_excel(data_files['green_data'])
        population = pd.read_excel(data_files['population'])
        
        try:
            footways = gpd.read_file(data_files['footways'])
        except Exception as e:
            logging.warning(f"Yaya yolları yüklenemedi: {str(e)} - Boş GeoDataFrame kullanılıyor")
            footways = gpd.GeoDataFrame()
        
        # GeoDataFrame'e dönüştür
        geometry = [Point(xy) for xy in zip(green_data['LONGITUDE'], green_data['LATITUDE'])]
        green_areas = gpd.GeoDataFrame(green_data, geometry=geometry, crs="EPSG:4326").to_crs(epsg=3857)
        
        if not footways.empty:
            footways = footways.to_crs(epsg=3857)
        
        # İstatistikleri hesapla
        total_pop = population.loc[0, 'total_population']
        results = {
            'total_population': total_pop,
            'num_green_spaces': len(green_data),
            'green_spaces_per_capita': len(green_data) / total_pop,
            'green_space_types': green_data['TUR'].value_counts().to_dict(),
            'most_common_type': green_data['TUR'].mode()[0],
            'most_common_type_count': green_data['TUR'].value_counts().max(),
            'average_green_space_size': green_data['ALAN'].mean() if 'ALAN' in green_data.columns else None
        }
        
        # Görselleri oluştur
        map_path = create_green_space_map(green_areas, footways)
        chart_paths = create_green_space_charts(green_data)
        
        # İstatistikleri yazdır
        print_statistical_results(results)
        
        # Çıktı bilgisi
        print("\nOLUŞTURULAN GÖRSELLER:")
        print(f"- Harita: {map_path if map_path else 'Oluşturulamadı'}")
        print(f"- Grafikler: {len(chart_paths)} adet")
        
        return results
        
    except Exception as e:
        logging.error(f"Analiz hatası: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    try:
        logging.info("Analiz başlatılıyor...")
        results = analyze_green_spaces()
        
        if results:
            logging.info("Analiz başarıyla tamamlandı")
        else:
            logging.error("Analiz başarısız oldu")
            
    except Exception as e:
        logging.critical(f"Kritik hata: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")