import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
import os
import logging
import numpy as np
from matplotlib.lines import Line2D
from fpdf import FPDF
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='population_analysis.log'
)

# Constants
BESIKTAS_AREA = 18.34  # km²
TURKEY_AREA = 783562  # km²
GREEN_SPACE_PER_CAPITA_STANDARD = 9  # m²/person (WHO recommendation)

# Get absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../../../'))
output_dir = os.path.join(project_root, 'outputs')
os.makedirs(os.path.join(output_dir, 'maps'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'reports'), exist_ok=True)

class TurkishPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Fontların bulunduğu tam yol
        fonts_path = os.path.join(project_root, 'assets', 'fonts')
        
        try:
            # Fontları ekleme
            self.add_font('DejaVu', '', os.path.join(fonts_path, 'DejaVuSansCondensed.ttf'), uni=True)
            self.add_font('DejaVu', 'B', os.path.join(fonts_path, 'DejaVuSansCondensed-Bold.ttf'), uni=True)
            self.add_font('DejaVu', 'I', os.path.join(fonts_path, 'DejaVuSansCondensed-Oblique.ttf'), uni=True)
        except Exception as e:
            logging.error(f"Font yükleme hatası: {str(e)}")
            try:
                self.add_font('Arial', '', 'arial.ttf')
                logging.warning("DejaVu fontları bulunamadı, Arial kullanılıyor")
            except:
                logging.error("Hiçbir font yüklenemedi, PDF oluşturulamayabilir")

        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('DejaVu', 'B', 16)
        self.cell(0, 10, 'Beşiktaş Nüfus ve Yeşil Alan Analizi', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

def create_comprehensive_visualization(green_coords, green_info_melted, besiktas_pop, national_pop, green_space_per_capita):
    """Gelişmiş görselleştirmeler oluşturur ve kaydeder"""
    try:
        sns.set_theme()
        plt.style.use('seaborn-v0_8')
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 20), constrained_layout=True)
        gs = fig.add_gridspec(4, 3)
        
        # Plot 1: Population Comparison
        ax1 = fig.add_subplot(gs[0, 0])
        pop_data = pd.DataFrame({
            'Region': ['Beşiktaş', 'Türkiye'],
            'Population': [besiktas_pop['total_population'].values[0], national_pop['Total Population'].values[0]]
        })
        bars = ax1.bar(pop_data['Region'], pop_data['Population'], color=['#2e8b57', '#4682b4'])
        ax1.set_title('Nüfus Karşılaştırması', fontsize=14, pad=20)
        ax1.set_ylabel('Nüfus', fontsize=12)
        ax1.ticklabel_format(style='plain', axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=12)
        
        # Plot 2: Population Density
        ax2 = fig.add_subplot(gs[0, 1])
        density_data = pd.DataFrame({
            'Region': ['Beşiktaş', 'Türkiye'],
            'Density': [
                besiktas_pop['population_density'].values[0],
                national_pop['population_density'].values[0]
            ]
        })
        bars = ax2.bar(density_data['Region'], density_data['Density'], color=['#3cb371', '#6495ed'])
        ax2.set_title('Nüfus Yoğunluğu Karşılaştırması', fontsize=14, pad=20)
        ax2.set_ylabel('Kişi/km²', fontsize=12)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=12)
        
        # Plot 3: Green Space Types
        ax3 = fig.add_subplot(gs[0, 2])
        green_type_dist = green_coords['type'].value_counts()
        explode = [0.1] + [0]*(len(green_type_dist)-1)
        wedges, texts, autotexts = ax3.pie(
            green_type_dist, 
            labels=green_type_dist.index,
            autopct='%1.1f%%',
            startangle=90,
            explode=explode,
            textprops={'fontsize': 12}
        )
        ax3.set_title('Yeşil Alan Türleri Dağılımı', fontsize=14, pad=20)
        
        # Plot 4: Green Space Per Capita Comparison
        ax4 = fig.add_subplot(gs[1, :])
        if green_space_per_capita is not None:
            ax4.bar(['Beşiktaş'], [green_space_per_capita], color='#2e8b57')
            ax4.axhline(y=GREEN_SPACE_PER_CAPITA_STANDARD, color='r', linestyle='--', linewidth=2)
            ax4.text(0.5, GREEN_SPACE_PER_CAPITA_STANDARD+0.5, 
                    f'WHO Standardı: {GREEN_SPACE_PER_CAPITA_STANDARD} m²/kişi',
                    color='r', ha='center', fontsize=12)
            ax4.set_title('Kişi Başına Düşen Yeşil Alan (2024)', fontsize=14, pad=20)
            ax4.set_ylabel('m²/kişi', fontsize=12)
            
            # Add value label on bar
            ax4.text(0, green_space_per_capita/2, 
                    f'{green_space_per_capita:.2f} m²/kişi',
                    ha='center', va='center', color='white', fontsize=14, fontweight='bold')
        
        # Plot 5: New Parks Over Years (if data available)
        ax5 = fig.add_subplot(gs[2, :])
        park_data = green_info_melted[
            green_info_melted['FAALİYET KONUSU'] == 'Yıl İçinde Yeni Yapılan Park Sayısı'
        ]
        if not park_data.empty:
            years = park_data['year'].astype(str)
            parks = park_data['value']
            
            bars = ax5.bar(years, parks, color='#3cb371')
            ax5.set_title('Yıllara Göre Yeni Yapılan Park Sayısı', fontsize=14, pad=20)
            ax5.set_ylabel('Park Sayısı', fontsize=12)
            ax5.set_xlabel('Yıl', fontsize=12)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}',
                        ha='center', va='bottom', fontsize=12)
        
        # Plot 6: Green Space Area Over Years (if data available)
        ax6 = fig.add_subplot(gs[3, :])
        area_data = green_info_melted[
            green_info_melted['FAALİYET KONUSU'] == 'Yıl İçinde Yapılan Yeşil Alan Miktarı'
        ]
        if not area_data.empty:
            years = area_data['year'].astype(str)
            areas = area_data['value'] / 10000  # Convert to hectares
            
            ax6.plot(years, areas, marker='o', linestyle='-', color='#228b22', linewidth=3, markersize=10)
            ax6.set_title('Yıllara Göre Yapılan Yeşil Alan Miktarı', fontsize=14, pad=20)
            ax6.set_ylabel('Hektar (10,000 m²)', fontsize=12)
            ax6.set_xlabel('Yıl', fontsize=12)
            
            # Add value labels on points
            for x, y in zip(years, areas):
                ax6.text(x, y, f'{y:.1f} ha', ha='center', va='bottom', fontsize=12)
        
        # Save the figure
        output_path = os.path.join(output_dir, 'maps', 'comprehensive_population_greenspace_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        logging.error(f"Görselleştirme oluşturma hatası: {str(e)}", exc_info=True)
        return None
    
def generate_population_pdf_report(results: dict, visualization_path: str) -> str:
    """Generate PDF report for population and green space analysis"""
    try:
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
        
        # Population metrics
        pop = results['population']
        pdf.cell(0, 8, f"Beşiktaş Nüfusu: {pop['besiktas_total']:,}", ln=True)
        pdf.cell(0, 8, f"Kentsel Nüfus Oranı: {pop['urban_percentage']:.1f}%", ln=True)
        pdf.cell(0, 8, f"Beşiktaş Nüfus Yoğunluğu: {pop['besiktas_density']:,.1f} kişi/km²", ln=True)
        pdf.cell(0, 8, f"Türkiye Nüfus Yoğunluğu: {pop['turkey_density']:,.1f} kişi/km²", ln=True)
        pdf.ln(10)
        
        # Green space metrics
        green = results['green_spaces']
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, "Yeşil Alan Metrikleri", ln=True)
        pdf.set_font('DejaVu', '', 12)
        
        pdf.cell(0, 8, f"Yeşil Alan Tür Sayısı: {green['total_types']}", ln=True)
        pdf.cell(0, 8, f"Park Sayısı: {green['park_count']}", ln=True)
        pdf.cell(0, 8, f"Kişi Başına Yeşil Alan: {green['green_space_per_capita']} m²/kişi", ln=True)
        
        if green['meets_who_standard'] is not None:
            status = "Evet" if green['meets_who_standard'] else "Hayır"
            pdf.cell(0, 8, f"WHO Standardını Karşılama: {status}", ln=True)
        
        pdf.cell(0, 8, f"2024'te Yapılan Yeni Park Sayısı: {green['new_parks_2024']}", ln=True)
        
        if green.get('sample_distances'):
            pdf.cell(0, 8, "Örnek Yeşil Alan Mesafeleri:", ln=True)
            for dist in green['sample_distances']:
                pdf.cell(0, 8, f"- {dist:.2f} km", ln=True)
        
        pdf.ln(10)
        
        # Add visualization to the report
        if visualization_path and os.path.exists(visualization_path):
            pdf.add_page()
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, "Nüfus ve Yeşil Alan Görselleştirmesi", ln=True)
            pdf.image(visualization_path, x=10, y=30, w=180)
            pdf.ln(140)
        
        # Conclusions section
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, "Sonuçlar ve Öneriler", ln=True)
        pdf.set_font('DejaVu', '', 12)
        
        conclusions = [
            "Beşiktaş'ın nüfus ve yeşil alan analizinden çıkan temel bulgular:",
            "",
            f"1. İlçede toplam {pop['besiktas_total']:,} nüfus bulunmaktadır.",
            f"2. Nüfus yoğunluğu {pop['besiktas_density']:,.1f} kişi/km²'dir.",
            f"3. Kişi başına düşen yeşil alan {green['green_space_per_capita']} m²'dir.",
            f"4. WHO standardı{' karşılanmaktadır' if green['meets_who_standard'] else ' karşılanmamaktadır' if green['meets_who_standard'] is not None else ' bilinmemektedir'}.",
            "",
            "Öneriler:",
            "",
            "• Yeşil alanların artırılması",
            "• Park sayısının çoğaltılması",
            "• Mevcut yeşil alanların korunması",
            "• Kentsel dönüşüm projelerinde yeşil alan planlaması"
        ]
        
        for line in conclusions:
            pdf.multi_cell(0, 8, line)
            pdf.ln(5)
        
        # Save the PDF
        report_path = os.path.join(output_dir, 'reports', 'besiktas_population_green_space_analysis.pdf')
        pdf.output(report_path)
        return report_path
        
    except Exception as e:
        logging.error(f"PDF oluşturma hatası: {str(e)}", exc_info=True)
        return ""

def print_statistical_results(results):
    """İstatistiksel sonuçları düzenli bir şekilde yazdırır"""
    print("\n" + "="*60)
    print("BEŞİKTAŞ NÜFUS VE YEŞİL ALAN İSTATİSTİKLERİ")
    print("="*60)
    
    pop = results['population']
    green = results['green_spaces']
    
    # Nüfus bilgileri
    print("\nNÜFUS ANALİZİ:")
    print(f"- Beşiktaş Nüfusu: {pop['besiktas_total']:,}")
    print(f"- Kentsel Nüfus Oranı: {pop['urban_percentage']:.1f}%")
    print(f"- Beşiktaş Nüfus Yoğunluğu: {pop['besiktas_density']:,.1f} kişi/km²")
    print(f"- Türkiye Nüfus Yoğunluğu: {pop['turkey_density']:,.1f} kişi/km²")
    
    # Yeşil alan bilgileri
    print("\nYEŞİL ALAN ANALİZİ:")
    print(f"- Yeşil Alan Tür Sayısı: {green['total_types']}")
    print(f"- Park Sayısı: {green['park_count']}")
    print(f"- Kişi Başına Yeşil Alan: {green['green_space_per_capita']} m²/kişi")
    print(f"- WHO Standardını Karşılama: {'Evet' if green['meets_who_standard'] else 'Hayır' if green['meets_who_standard'] is not None else 'Bilinmiyor'}")
    print(f"- 2024'te Yapılan Yeni Park Sayısı: {green['new_parks_2024']}")
    
    if green.get('sample_distances'):
        print(f"- Örnek Yeşil Alan Mesafeleri: {', '.join(f'{d:.2f} km' for d in green['sample_distances'])}")
    
    print("\n" + "="*60)

def analyze_population_and_greenspace():
    """Nüfus ve yeşil alan verilerini analiz eder"""
    try:
        # Örnek veriler
        besiktas_pop = pd.DataFrame({
            'district': ['Beşiktaş'],
            'total_population': [167264],
            'urban_population': [167264]
        })
        
        national_pop = pd.DataFrame({
            'Year': [2023],
            'Age Group': ['Total'],
            'Total Population': [85372377]
        })
        
        green_coords = pd.DataFrame({
            'TUR': ['Karayolu', 'Kamu', 'Park', 'Cadde', 'Park', 'Park', 'Park'],
            'MAHAL_ADI': ['15 TEMMUZ ŞEHİTLER KÖPRÜSÜ', 'YILDIZ HAMİDİYE CAMİ', 
                         'YAHYA KEMAL PARKI', 'BARBAROS BULVARI', 'BEBEK ÇINARLI', 
                         'KURUÇEŞME PARKI', 'DİKİLİTAŞ PARKI'],
            'ILCE': ['BEŞİKTAŞ'] * 7,
            'LATITUDE': [41.059106, 41.049119, 41.048573, 41.051962, 41.076656, 
                         41.061357, 41.056036],
            'LONGITUDE': [29.016272, 29.010108, 29.008816, 29.008831, 29.042859,
                          29.038104, 29.0045]
        })
        
        green_info = pd.DataFrame({
            'FAALİYET KONUSU': [
                'Yıl İçinde Yeni Yapılan Park Sayısı',
                'Yıl İçinde Yapılan Yeşil Alan Miktarı',
                'Kişi Başına Düşen Aktif Yeşil Alan Miktarı'
            ],
            'BİRİM': ['Adet', 'm2', 'm2/kişi'],
            'yil_2024': [27, 1004825, 7.94]
        })

        # Veri işleme
        besiktas_pop['population_density'] = besiktas_pop['total_population'] / BESIKTAS_AREA
        national_pop['population_density'] = national_pop['Total Population'] / TURKEY_AREA
        
        green_coords = green_coords.rename(columns={
            'TUR': 'type',
            'MAHAL_ADI': 'name',
            'ILCE': 'district',
            'LATITUDE': 'lat',
            'LONGITUDE': 'lon'
        })
        
        # Yeşil alan mesafeleri
        distances = []
        if len(green_coords) > 1:
            sample_coords = green_coords.head(5)
            for i in range(len(sample_coords)-1):
                point1 = (sample_coords.iloc[i]['lat'], sample_coords.iloc[i]['lon'])
                point2 = (sample_coords.iloc[i+1]['lat'], sample_coords.iloc[i+1]['lon'])
                distances.append(geodesic(point1, point2).km)
        
        # Yeşil alan bilgilerini işle
        green_info_melted = green_info.melt(id_vars=['FAALİYET KONUSU', 'BİRİM'], 
                                          var_name='year', 
                                          value_name='value')
        green_info_melted['year'] = green_info_melted['year'].str.replace('yil_', '').astype(int)
        
        # Kişi başına yeşil alan
        green_space_per_capita = green_info_melted[
            (green_info_melted['FAALİYET KONUSU'] == 'Kişi Başına Düşen Aktif Yeşil Alan Miktarı') & 
            (green_info_melted['year'] == 2024)
        ].iloc[0]['value'] if not green_info_melted[
            (green_info_melted['FAALİYET KONUSU'] == 'Kişi Başına Düşen Aktif Yeşil Alan Miktarı') & 
            (green_info_melted['year'] == 2024)
        ].empty else None
        
        # Yeni park sayısı
        new_parks = green_info_melted[
            (green_info_melted['FAALİYET KONUSU'] == 'Yıl İçinde Yeni Yapılan Park Sayısı') & 
            (green_info_melted['year'] == 2024)
        ].iloc[0]['value'] if not green_info_melted[
            (green_info_melted['FAALİYET KONUSU'] == 'Yıl İçinde Yeni Yapılan Park Sayısı') & 
            (green_info_melted['year'] == 2024)
        ].empty else None
        
        # Görselleştirme oluştur
        visualization_path = create_comprehensive_visualization(
            green_coords, green_info_melted, besiktas_pop, national_pop, green_space_per_capita
        )
        
        # Sonuçları hazırla
        results = {
            'population': {
                'besiktas_total': besiktas_pop['total_population'].sum(),
                'urban_percentage': 100.0,
                'besiktas_density': besiktas_pop['population_density'].values[0],
                'turkey_density': national_pop['population_density'].mean()
            },
            'green_spaces': {
                'total_types': len(green_coords['type'].unique()),
                'park_count': len(green_coords[green_coords['type'] == 'Park']),
                'green_space_per_capita': green_space_per_capita,
                'new_parks_2024': new_parks,
                'meets_who_standard': green_space_per_capita >= GREEN_SPACE_PER_CAPITA_STANDARD if green_space_per_capita else None,
                'sample_distances': distances if distances else None
            },
            'visualization_path': visualization_path
        }
        
        # İstatistikleri yazdır
        print_statistical_results(results)
        
        # PDF raporu oluştur
        report_path = generate_population_pdf_report(results, visualization_path)
        
        # Çıktı bilgisi
        print("\nOLUŞTURULAN ÇIKTILAR:")
        print(f"- Görselleştirme: {visualization_path if visualization_path else 'Oluşturulamadı'}")
        print(f"- PDF Rapor: {report_path if report_path else 'Oluşturulamadı'}")
        
        return results
        
    except Exception as e:
        logging.error(f"Analiz hatası: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_population_and_greenspace()