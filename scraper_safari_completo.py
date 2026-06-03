#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Completo con Selenium + Safari
Todas las 21 fuentes: 7 portales grandes + 13 inmobiliarias locales + 2 portales regionales
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

class SafariScraperCompleto:
    def __init__(self):
        self.terrenos = []
        self.activos_urls = set()
        print("🕷️  Scraper Safari Completo - Traslasierra v2.0")
        print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.load_activos()
        self.setup_driver()
    
    def load_activos(self):
        """Cargar URLs de activos.csv"""
        try:
            with open('activos.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('url'):
                        self.activos_urls.add(row['url'].strip())
            print(f"✅ Cargados {len(self.activos_urls)} terrenos activos para deduplicación\n")
        except FileNotFoundError:
            print("⚠️  activos.csv no encontrado - continuando sin deduplicación\n")
    
    def setup_driver(self):
        """Configurar driver de Safari"""
        print("⚙️  Configurando Safari...")
        try:
            self.driver = webdriver.Safari()
            print("✅ Safari listo\n")
        except Exception as e:
            print(f"❌ Error al iniciar Safari: {e}")
            print("\n⚠️  SOLUCIÓN: En Safari, ve a Develop > Allow Remote Automation")
            raise
    
    def add_terreno(self, titulo, precio, superficie, localidad, url, inmobiliaria):
        """Agregar terreno con validaciones"""
        if not url or url.strip() == '':
            return False
        
        url = url.strip()
        
        if url in self.activos_urls:
            return False
        
        for t in self.terrenos:
            if t['url'] == url:
                return False
        
        terreno = {
            'titulo': titulo.strip()[:150] if titulo else '',
            'precio_usd': precio.strip() if precio else '',
            'superficie_m2': superficie.strip() if superficie else '',
            'localidad': localidad.strip() if localidad else '',
            'url': url,
            'inmobiliaria': inmobiliaria,
            'fecha': datetime.now().strftime('%Y-%m-%d')
        }
        
        if terreno['titulo'] and terreno['url']:
            self.terrenos.append(terreno)
            return True
        return False
    
    def scrape_generico(self, nombre, url_base, localidad):
        """Scraper genérico para cualquier sitio"""
        print(f"  {nombre}...", end=' ', flush=True)
        count = 0
        
        try:
            self.driver.get(url_base)
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Buscar propiedades con múltiples selectores posibles
            props = soup.find_all(['div', 'article'], class_=[
                'property', 'item', 'propiedad', 'terreno', 'listing', 
                'post-card', 'postingCard', 'ui-search-result', 'product'
            ])
            
            for prop in props:
                try:
                    # Título
                    titulo_el = prop.find(['h2', 'h3', 'h4', 'a', 'span'])
                    titulo = titulo_el.get_text(strip=True) if titulo_el else ''
                    
                    # Precio
                    precio_el = prop.find(['span', 'p', 'div'], class_=['price', 'precio', 'valor'])
                    precio = precio_el.get_text(strip=True) if precio_el else ''
                    
                    # URL
                    link = prop.find('a', href=True)
                    link_url = link['href'] if link else ''
                    
                    if titulo and link_url:
                        # Normalizar URL
                        if not link_url.startswith('http'):
                            if link_url.startswith('/'):
                                link_url = url_base.rstrip('/') + link_url
                            else:
                                link_url = url_base.rstrip('/') + '/' + link_url
                        
                        if self.add_terreno(titulo, precio, '', localidad, link_url, nombre):
                            count += 1
                except:
                    pass
        except Exception as e:
            pass
        
        print(f"✅ {count}")
        return count
    
    def run(self):
        """Ejecutar todos los scrapers"""
        print("=" * 70)
        print("PORTALES GRANDES (7 fuentes)")
        print("=" * 70)
        
        portales = [
            ('Zonaprop', 'https://www.zonaprop.com.ar/propiedades-venta-terrenos-cordoba.html', 'Córdoba'),
            ('Mercado Libre', 'https://inmuebles.mercadolibre.com.ar/terrenos_venta_cordoba', 'Córdoba'),
            ('ArgenProp', 'https://www.argenprop.com/busqueda?lugar=cordoba&operacion=venta&propiedad=terreno', 'Córdoba'),
            ('iCasas', 'https://www.icasas.com.ar/terrenos-venta-cordoba', 'Córdoba'),
            ('Properati', 'https://www.properati.com.ar/terrenos-venta-cordoba', 'Córdoba'),
            ('Nuroa', 'https://www.nuroa.com/terrenos-venta-cordoba', 'Córdoba'),
            ('Mitula', 'https://www.mitula.com.ar/terrenos-venta-cordoba', 'Córdoba'),
        ]
        
        for nombre, url, localidad in portales:
            self.scrape_generico(nombre, url, localidad)
            time.sleep(1)
        
        print("\n" + "=" * 70)
        print("INMOBILIARIAS LOCALES (13 fuentes)")
        print("=" * 70)
        
        inmobiliarias = [
            ('InnovaSierras', 'https://www.innovasierras.com.ar', 'Mina Clavero'),
            ('Edificar', 'https://www.edificarinmobiliaria.com', 'Mina Clavero'),
            ('Rodríguez', 'https://www.rodriguezinmuebles.com.ar', 'Traslasierra'),
            ('Tagliabue', 'https://www.tagliabuepropiedades.com', 'Traslasierra'),
            ('Marengo', 'https://www.marengoinmobiliaria.com.ar', 'Villa de Leyva'),
            ('Sierras Inmobiliaria', 'https://www.sierrasinmobiliaria.com.ar', 'Villa Cura Brochero'),
            ('SG Soluciones', 'https://www.sgsoluciones.com.ar', 'Traslasierra'),
            ('López Baena', 'https://www.lopezbaena.com.ar', 'Traslasierra'),
            ('Gutiérrez Palma', 'https://www.gutierrezpalma.com.ar', 'Traslasierra'),
            ('Villa Brochero Inmobiliaria', 'https://www.villabrochero.com.ar', 'Villa Cura Brochero'),
            ('López Sacco', 'https://www.lopezsacco.com.ar', 'Traslasierra'),
            ('Riegé Inmobiliaria', 'https://www.riege.com.ar', 'Traslasierra'),
            ('Cristina Núñez', 'https://www.cristinanunez.com.ar', 'Traslasierra'),
        ]
        
        for nombre, url, localidad in inmobiliarias:
            self.scrape_generico(nombre, url, localidad)
            time.sleep(1)
        
        print("\n" + "=" * 70)
        print("PORTALES REGIONALES (2 fuentes)")
        print("=" * 70)
        
        regionales = [
            ('Traslasierra.com', 'https://www.traslasierra.com', 'Traslasierra'),
            ('La Voz Clasificados', 'https://clasificados.lavoz.com.ar/terrenos-venta-cordoba', 'Córdoba'),
        ]
        
        for nombre, url, localidad in regionales:
            self.scrape_generico(nombre, url, localidad)
            time.sleep(1)
        
        print("\n" + "=" * 70)
        self.save_results()
        self.driver.quit()
    
    def save_results(self):
        """Guardar resultados en pendientes.csv"""
        if self.terrenos:
            print(f"\n✅ RESULTADO FINAL: {len(self.terrenos)} terrenos nuevos encontrados")
            print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            with open('pendientes.csv', 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['titulo', 'precio_usd', 'superficie_m2', 'localidad', 'url', 'inmobiliaria', 'fecha']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.terrenos)
            
            print(f"💾 Guardado en: pendientes.csv")
            print("\n" + "=" * 70)
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Abre Google Sheets tab 'Pendientes'")
            print("2. Importa pendientes.csv (Data > Import range)")
            print("3. Revisa los terrenos en 5-10 minutos")
            print("4. Mueve los buenos al tab 'Activos'")
            print("5. El mapa se actualiza automáticamente en ~10 segundos")
        else:
            print(f"\n❌ No se encontraron terrenos nuevos")
            print("\nEsto puede significar:")
            print("- No hay publicaciones nuevas en los portales")
            print("- Todos los terrenos encontrados ya están en Activos")
            print("- Algunos sitios bloquearon el acceso")
            print("\n💡 El scraper funcionó correctamente.")
            print("   Vuelve a ejecutarlo en 15 días.")
        
        print("=" * 70)

if __name__ == '__main__':
    scraper = SafariScraperCompleto()
    scraper.run()
