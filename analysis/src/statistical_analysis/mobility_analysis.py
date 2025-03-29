import geopandas as gpd
import logging
import os
import matplotlib.pyplot as plt
import contextily as ctx
from datetime import datetime
from fpdf import FPDF
import pandas as pd
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TurkishPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Script'in bulunduğu dizin: analysis/src/statistical_analysis
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Proje kök dizinine çıkmak için 3 seviye yukarı çıkıyoruz
        project_root = os.path.abspath(os.path.join(script_dir, '../../../'))
        
        # Fontların bulunduğu tam yol
        fonts_path = os.path.join(project_root, 'assets', 'fonts')
        
        try:
            # Fontları ekleme
            self.add_font('DejaVu', '', os.path.join(fonts_path, 'DejaVuSansCondensed.ttf'), uni=True)
            self.add_font('DejaVu', 'B', os.path.join(fonts_path, 'DejaVuSansCondensed-Bold.ttf'), uni=True)
            self.add_font('DejaVu', 'I', os.path.join(fonts_path, 'DejaVuSansCondensed-Oblique.ttf'), uni=True)
        except Exception as e:
            logging.error(f"Font yükleme hatası: {str(e)}")
            # Alternatif font deneyebilirsiniz
            try:
                self.add_font('Arial', '', 'arial.ttf')
                logging.warning("DejaVu fontları bulunamadı, Arial kullanılıyor")
            except:
                logging.error("Hiçbir font yüklenemedi, PDF oluşturulamayabilir")

        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('DejaVu', 'B', 16)
        self.cell(0, 10, 'Beşiktaş Mobilite Altyapı Analizi', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

def calculate_path_length(gdf: gpd.GeoDataFrame) -> float:
    """Calculate total length of paths in kilometers"""
    try:
        if gdf.crs is None:
            gdf.crs = "EPSG:4326"
        projected = gdf.to_crs("EPSG:3857")
        return projected.geometry.length.sum() / 1000
    except Exception as e:
        logging.error(f"Path length calculation error: {str(e)}")
        return 0.0

def create_mobility_map(bike_paths: gpd.GeoDataFrame, micromobility: gpd.GeoDataFrame) -> str:
    """Create a map visualization"""
    try:
        os.makedirs('outputs/maps', exist_ok=True)
        fig, ax = plt.subplots(figsize=(12, 10))
        
        bike_paths_proj = bike_paths.to_crs("EPSG:3857")
        micromobility_proj = micromobility.to_crs("EPSG:3857")
        
        if 'PRJ_ASAMA' in bike_paths.columns:
            bike_paths_proj.plot(column='PRJ_ASAMA', ax=ax, linewidth=2, legend=True)
        else:
            bike_paths_proj.plot(ax=ax, color='blue', linewidth=2)
        
        micromobility_proj.plot(ax=ax, color='red', markersize=30, marker='o')
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
        
        plt.title('Beşiktaş Mobilite Altyapısı', fontsize=16)
        output_path = 'outputs/maps/mobility_infrastructure.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
    except Exception as e:
        logging.error(f"Map creation error: {str(e)}")
        return ""

def create_bike_path_charts(bike_paths: gpd.GeoDataFrame) -> list:
    """Create data visualization charts"""
    try:
        os.makedirs('outputs/maps', exist_ok=True)
        output_paths = []
        
        # Chart 1: Bike path types
        if 'PRJ_ASAMA' in bike_paths.columns:
            plt.figure(figsize=(10, 6))
            path_types = bike_paths['PRJ_ASAMA'].value_counts()
            path_types.plot(kind='pie', autopct='%1.1f%%')
            plt.title('Bisiklet Yolu Türleri', fontsize=14)
            plt.ylabel('')
            chart_path = 'outputs/maps/bike_path_types.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            output_paths.append(chart_path)
        
        # Chart 2: Construction years
        if 'YAPIM_YILI' in bike_paths.columns:
            plt.figure(figsize=(12, 7))
            years = bike_paths['YAPIM_YILI'].value_counts().sort_index()
            ax = years.plot(kind='bar', color='seagreen')
            plt.title('Yapım Yılına Göre Bisiklet Yolları', fontsize=14)
            plt.xlabel('Yıl')
            plt.ylabel('Sayı')
            plt.xticks(rotation=45)
            for i, v in enumerate(years):
                ax.text(i, v + 0.1, str(v), ha='center', fontsize=9)
            chart_path = 'outputs/maps/bike_paths_by_year.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            output_paths.append(chart_path)
        
        return output_paths
    except Exception as e:
        logging.error(f"Chart creation error: {str(e)}")
        return []

def generate_pdf_report(results: dict, map_path: str, chart_paths: list) -> str:
    """Generate PDF report with Turkish character support"""
    try:
        os.makedirs('outputs/reports', exist_ok=True)
        pdf = TurkishPDF()
        pdf.add_page()
        
        # Set Turkish-friendly font
        pdf.set_font('DejaVu', '', 12)
        
        # Report metadata
        pdf.cell(0, 10, f"Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.ln(10)
        
        # Key metrics section
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, "Temel Metrikler", ln=True)
        pdf.set_font('DejaVu', '', 12)
        
        metrics = [
            f"Toplam bisiklet yolu uzunluğu: {results.get('total_bike_path_km', 0):.2f} km",
            f"Mikromobilite istasyon sayısı: {results.get('micromobility_stations', 0)}",
            f"Bisiklet yolu segment sayısı: {results.get('bike_path_count', 0)}",
            f"Ortalama yol uzunluğu: {results.get('avg_path_length_km', 0):.2f} km"
        ]
        
        for metric in metrics:
            pdf.cell(0, 8, metric, ln=True)
        
        pdf.ln(10)
        
        # Bike path types section
        if 'bike_path_types' in results:
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, "Bisiklet Yolu Türleri", ln=True)
            pdf.set_font('DejaVu', '', 12)
            
            for path_type, count in results['bike_path_types'].items():
                pdf.cell(0, 8, f"- {path_type}: {count}", ln=True)
            
            pdf.ln(10)
        
        # Construction years section
        if 'construction_years' in results:
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, "Yapım Yılları", ln=True)
            pdf.set_font('DejaVu', '', 12)
            
            for year, count in sorted(results['construction_years'].items()):
                pdf.cell(0, 8, f"- {year}: {count}", ln=True)
            
            pdf.ln(10)
        
        # Add map to the report
        if os.path.exists(map_path):
            pdf.add_page()
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, "Mobilite Altyapı Haritası", ln=True)
            pdf.image(map_path, x=10, y=30, w=180)
            pdf.ln(140)
        
        # Add charts to the report
        for chart_path in chart_paths:
            if os.path.exists(chart_path):
                pdf.add_page()
                pdf.set_font('DejaVu', 'B', 14)
                
                if "types" in chart_path:
                    pdf.cell(0, 10, "Bisiklet Yolu Türleri Dağılımı", ln=True)
                elif "year" in chart_path:
                    pdf.cell(0, 10, "Yıllara Göre Bisiklet Yolları", ln=True)
                
                pdf.image(chart_path, x=10, y=30, w=180)
                pdf.ln(140)
        
        # Conclusions and recommendations
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, "Sonuçlar ve Öneriler", ln=True)
        pdf.set_font('DejaVu', '', 12)
        
        conclusions = [
            "Beşiktaş'ın mobilite altyapısı analizinden çıkan temel bulgular:",
            "",
            f"1. İlçede toplam {results.get('total_bike_path_km', 0):.2f} km bisiklet yolu bulunmaktadır.",
            f"2. {results.get('micromobility_stations', 0)} adet mikromobilite istasyonu mevcuttur.",
            "3. Bisiklet yolu ağında bağlantıların artırılması gerekmektedir."
        ]
        
        for conclusion in conclusions:
            pdf.multi_cell(0, 8, conclusion)
        
        pdf.ln(5)
        
        recommendations = [
            "Öneriler:",
            "",
            "• Mevcut bisiklet yolları arasındaki bağlantıların güçlendirilmesi",
            "• Mikromobilite istasyonlarının yaygınlaştırılması",
            "• Güvenli bisiklet yollarının artırılması",
            "• Bisiklet kullanımını teşvik edici programlar geliştirilmesi"
        ]
        
        for recommendation in recommendations:
            pdf.multi_cell(0, 8, recommendation)
        
        # Save the PDF
        output_path = 'outputs/reports/besiktas_mobility_analysis.pdf'
        pdf.output(output_path)
        return output_path
        
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        return ""

def analyze_mobility() -> dict:
    """Main analysis function"""
    try:
        bike_paths = gpd.read_file('data/processed/besiktas_bike_paths.geojson')
        micromobility = gpd.read_file('data/processed/besiktas_micromobility.geojson')
        
        total_length = calculate_path_length(bike_paths)
        
        results = {
            'total_bike_path_km': round(total_length, 2),
            'micromobility_stations': len(micromobility),
            'bike_path_count': len(bike_paths),
            'avg_path_length_km': round(total_length / len(bike_paths), 2) if len(bike_paths) > 0 else 0
        }
        
        if 'PRJ_ASAMA' in bike_paths.columns:
            results['bike_path_types'] = bike_paths['PRJ_ASAMA'].value_counts().to_dict()
        
        if 'YAPIM_YILI' in bike_paths.columns:
            results['construction_years'] = bike_paths['YAPIM_YILI'].value_counts().to_dict()
        
        return results
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        return {}

if __name__ == "__main__":
    logging.info("Mobilite analizi başlatılıyor")
    
    results = analyze_mobility()
    logging.info(f"Analiz tamamlandı, {len(results)} metrik hesaplandı")
    
    try:
        bike_paths = gpd.read_file('data/processed/besiktas_bike_paths.geojson')
        micromobility = gpd.read_file('data/processed/besiktas_micromobility.geojson')
        
        map_path = create_mobility_map(bike_paths, micromobility)
        logging.info(f"Harita oluşturuldu: {map_path}")
        
        chart_paths = create_bike_path_charts(bike_paths)
        logging.info(f"{len(chart_paths)} grafik oluşturuldu")
        
        report_path = generate_pdf_report(results, map_path, chart_paths)
        logging.info(f"PDF rapor oluşturuldu: {report_path}")
        
    except Exception as e:
        logging.error(f"Görselleştirme hatası: {str(e)}")
    
    # Console output
    print("\nBeşiktaş Mobilite Altyapı Analiz Sonuçları")
    print("="*50)
    print(f"Toplam bisiklet yolu uzunluğu: {results.get('total_bike_path_km', 0):.2f} km")
    print(f"Mikromobilite istasyon sayısı: {results.get('micromobility_stations', 0)}")
    print(f"Bisiklet yolu segment sayısı: {results.get('bike_path_count', 0)}")
    print(f"Ortalama yol uzunluğu: {results.get('avg_path_length_km', 0):.2f} km")
    
    if 'bike_path_types' in results:
        print("\nBisiklet Yolu Türleri:")
        for path_type, count in results['bike_path_types'].items():
            print(f"- {path_type}: {count}")
    
    if 'construction_years' in results:
        print("\nYapım Yılları:")
        for year, count in sorted(results['construction_years'].items()):
            print(f"- {year}: {count}")
    
    print("\nÇıktılar:")
    print(f"- Rapor: {report_path if 'report_path' in locals() else 'Oluşturulamadı'}")
    print(f"- Harita: {map_path if 'map_path' in locals() else 'Oluşturulamadı'}")
    print(f"- Grafikler: {len(chart_paths) if 'chart_paths' in locals() else 0} adet")