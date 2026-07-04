#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Condor2026 / SpectrumSecurity

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🔪 DIABOLIC FRANCE v1.0 - SURVEILLANCE CRIMINELLE                            ║
║  ═══════════════════════════════════════════════════════════════════════════  ║
║  🚨 Surveillance: Homicides · Violences · Braquages · Narcotrafic · Gangs     ║
║  🏴 Couvre toute la France métropolitaine + Outre-mer                         ║
║  🔄 150+ User-Agents · Auto-discovery URLs · Anti-blocage                     ║
║  📈 Graphiques interactifs · Dashboard web · Export JSON/CSV/HTML             ║
║  🌍 3 langues: Español · Français · Italiano                                  ║
║  📄 Pagination réelle sur toutes les vues                                     ║
║                                                                               ║
║  🛡️ "L'union fait la force" - Devise française                                ║
║                                                                               ║
║     - By Condor2026                                                           ║
║                                         •SpectrumSecurity•                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import hashlib
import random
import requests
import re
import csv
import io
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diabolic_france.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES GLOBALES
# ============================================================================

VERSION = "1.0"
PUERTO = 5016
ARCHIVO_DATOS = 'diabolic_france.json'
ARCHIVO_CACHE = 'url_cache_crime.json'
ARCHIVO_ESTADO = 'estado_fuentes_crime.json'
ARCHIVO_BACKUP = 'diabolic_france_backup.json'
PAGINAS_BUSQUEDA = 3
TIMEOUT = 25
MAX_INTENTOS = 3
DELAY_MIN = 0.8
DELAY_MAX = 2.0

# ============================================================================
# IDIOMAS
# ============================================================================

IDIOMA_ACTUAL = None

TEXTOS = {
    'es': {
        'app_name': 'DIABOLIC FRANCE v1.0',
        'menu_title': 'MENÚ PRINCIPAL',
        'cmd_buscar': 'Buscar crímenes y delitos',
        'cmd_analisis': 'Análisis completo criminalidad',
        'cmd_conexiones': 'Patrones y tendencias delictivas',
        'cmd_evolucion': 'Evolución mensual de crímenes',
        'cmd_web': 'Iniciar servidor web',
        'cmd_ultimos': 'Últimos 20 crímenes',
        'cmd_exportar': 'Exportar datos',
        'cmd_verificar': 'Verificar fuentes',
        'cmd_tipos': 'Distribución por tipo de crimen',
        'cmd_estadisticas': 'Estadísticas avanzadas',
        'cmd_limpiar': 'Limpiar duplicados',
        'cmd_stats_rapidas': 'Estadísticas rápidas',
        'cmd_salir': 'Salir',
        'stats_total': 'Total crímenes',
        'incidentes': 'crímenes',
        'fuentes': 'fuentes activas',
        'departamentos': 'departamentos',
        'servidor_web': 'Servidor web iniciado',
        'hasta_pronto': '¡Hasta pronto!',
        'opcion_invalida': 'Opción no válida',
        'actualizando': 'ACTUALIZANDO DATOS CRIMINALES',
        'analisis_completo': 'ANÁLISIS COMPLETO CRIMINALIDAD',
        'conexiones': 'PATRONES DELICTIVOS',
        'evolucion_mensual': 'EVOLUCIÓN DE CRÍMENES',
        'exportando': 'EXPORTANDO DATOS',
        'verificando': 'VERIFICANDO FUENTES',
        'limpiando': 'LIMPIANDO BASE',
        'estadisticas_avanzadas': 'ESTADÍSTICAS AVANZADAS',
        'stats_rapidas': 'ESTADÍSTICAS RÁPIDAS',
        'sin_datos': 'Sin datos suficientes',
        'procesando': 'Procesando...',
        'tipo_mas_comun': 'Crimen más común',
        'dia_mas_activo': 'Día más violento',
        'fuente_mas_activa': 'Fuente más activa',
        'departamento_critico': 'Departamento crítico',
        'tendencia': 'Tendencia criminal',
        'severidad': 'Severidad'
    },
    'fr': {
        'app_name': 'DIABOLIC FRANCE v1.0',
        'menu_title': 'MENU PRINCIPAL',
        'cmd_buscar': 'Rechercher crimes et délits',
        'cmd_analisis': 'Analyse complète criminalité',
        'cmd_conexiones': 'Modèles criminels',
        'cmd_evolucion': 'Évolution mensuelle des crimes',
        'cmd_web': 'Démarrer serveur web',
        'cmd_ultimos': '20 derniers crimes',
        'cmd_exportar': 'Exporter données',
        'cmd_verificar': 'Vérifier sources',
        'cmd_tipos': 'Distribution par type de crime',
        'cmd_estadisticas': 'Statistiques avancées',
        'cmd_limpiar': 'Nettoyer doublons',
        'cmd_stats_rapidas': 'Statistiques rapides',
        'cmd_salir': 'Quitter',
        'stats_total': 'Total crimes',
        'incidentes': 'crimes',
        'fuentes': 'sources actives',
        'departamentos': 'départements',
        'servidor_web': 'Serveur web démarré',
        'hasta_pronto': 'Au revoir!',
        'opcion_invalida': 'Option invalide',
        'actualizando': 'MISE À JOUR CRIMINELLE',
        'analisis_completo': 'ANALYSE CRIMINELLE COMPLÈTE',
        'conexiones': 'MODÈLES CRIMINELS',
        'evolucion_mensual': 'ÉVOLUTION DES CRIMES',
        'exportando': 'EXPORTATION',
        'verificando': 'VÉRIFICATION SOURCES',
        'limpiando': 'NETTOYAGE',
        'estadisticas_avanzadas': 'STATISTIQUES AVANCÉES',
        'stats_rapidas': 'STATISTIQUES RAPIDES',
        'sin_datos': 'Pas assez de données',
        'procesando': 'Traitement...',
        'tipo_mas_comun': 'Crime le plus commun',
        'dia_mas_activo': 'Jour le plus violent',
        'fuente_mas_activa': 'Source la plus active',
        'departamento_critico': 'Département critique',
        'tendencia': 'Tendance criminelle',
        'severidad': 'Sévérité'
    },
    'it': {
        'app_name': 'DIABOLIC FRANCE v1.0',
        'menu_title': 'MENU PRINCIPALE',
        'cmd_buscar': 'Cerca crimini e reati',
        'cmd_analisis': 'Analisi completa criminalità',
        'cmd_conexiones': 'Modelli criminali',
        'cmd_evolucion': 'Evoluzione mensile crimini',
        'cmd_web': 'Avvia server web',
        'cmd_ultimos': 'Ultimi 20 crimini',
        'cmd_exportar': 'Esporta dati',
        'cmd_verificar': 'Verifica fonti',
        'cmd_tipos': 'Distribuzione per tipo',
        'cmd_estadisticas': 'Statistiche avanzate',
        'cmd_limpiar': 'Pulisci duplicati',
        'cmd_stats_rapidas': 'Statistiche rapide',
        'cmd_salir': 'Esci',
        'stats_total': 'Totale crimini',
        'incidentes': 'crimini',
        'fuentes': 'fonti attive',
        'departamentos': 'dipartimenti',
        'servidor_web': 'Server web avviato',
        'hasta_pronto': 'Arrivederci!',
        'opcion_invalida': 'Opzione non valida',
        'actualizando': 'AGGIORNAMENTO DATI CRIMINALI',
        'analisis_completo': 'ANALISI COMPLETA CRIMINALITÀ',
        'conexiones': 'MODELLI CRIMINALI',
        'evolucion_mensual': 'EVOLUZIONE CRIMINI',
        'exportando': 'ESPORTAZIONE',
        'verificando': 'VERIFICA FONTI',
        'limpiando': 'PULIZIA',
        'estadisticas_avanzadas': 'STATISTICHE AVANZATE',
        'stats_rapidas': 'STATISTICHE RAPIDE',
        'sin_datos': 'Dati insufficienti',
        'procesando': 'Elaborazione...',
        'tipo_mas_comun': 'Crimine più comune',
        'dia_mas_activo': 'Giorno più violento',
        'fuente_mas_activa': 'Fonte più attiva',
        'departamento_critico': 'Dipartimento critico',
        'tendencia': 'Andamento criminale',
        'severidad': 'Severità'
    }
}

def t(clave):
    return TEXTOS[IDIOMA_ACTUAL].get(clave, clave)

# ============================================================================
# COLORES PROFESIONALES
# ============================================================================

class Color:
    BLACK = '\033[30m'
    RED = '\033[91m'
    DARK_RED = '\033[31m'
    GREEN = '\033[92m'
    DARK_GREEN = '\033[32m'
    YELLOW = '\033[93m'
    DARK_YELLOW = '\033[33m'
    BLUE = '\033[94m'
    DARK_BLUE = '\033[34m'
    MAGENTA = '\033[95m'
    DARK_MAGENTA = '\033[35m'
    CYAN = '\033[96m'
    DARK_CYAN = '\033[36m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    RESET = '\033[0m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_GRAY = '\033[100m'
    BG_DARK_RED = '\033[101m'
    BG_DARK_GREEN = '\033[102m'
    BG_DARK_YELLOW = '\033[103m'
    BG_DARK_BLUE = '\033[104m'
    BG_DARK_MAGENTA = '\033[105m'
    BG_DARK_CYAN = '\033[106m'

def cprint(texto, color=None, bold=False, dim=False, italic=False, underline=False, blink=False, bg=False, end='\n'):
    styles = []
    if bold:
        styles.append(Color.BOLD)
    if dim:
        styles.append(Color.DIM)
    if italic:
        styles.append(Color.ITALIC)
    if underline:
        styles.append(Color.UNDERLINE)
    if blink:
        styles.append(Color.BLINK)
    
    color_map = {
        'black': Color.BLACK, 'red': Color.RED, 'dark_red': Color.DARK_RED,
        'green': Color.GREEN, 'dark_green': Color.DARK_GREEN, 'yellow': Color.YELLOW,
        'dark_yellow': Color.DARK_YELLOW, 'blue': Color.BLUE, 'dark_blue': Color.DARK_BLUE,
        'magenta': Color.MAGENTA, 'dark_magenta': Color.DARK_MAGENTA, 'cyan': Color.CYAN,
        'dark_cyan': Color.DARK_CYAN, 'white': Color.WHITE, 'gray': Color.GRAY,
        'light_gray': Color.LIGHT_GRAY
    }
    
    bg_map = {
        'black': Color.BG_BLACK, 'red': Color.BG_RED, 'green': Color.BG_GREEN,
        'yellow': Color.BG_YELLOW, 'blue': Color.BG_BLUE, 'magenta': Color.BG_MAGENTA,
        'cyan': Color.BG_CYAN, 'white': Color.BG_WHITE, 'gray': Color.BG_GRAY,
        'dark_red': Color.BG_DARK_RED, 'dark_green': Color.BG_DARK_GREEN,
        'dark_yellow': Color.BG_DARK_YELLOW, 'dark_blue': Color.BG_DARK_BLUE,
        'dark_magenta': Color.BG_DARK_MAGENTA, 'dark_cyan': Color.BG_DARK_CYAN
    }
    
    col = color_map.get(color, '') if color else ''
    bg_col = bg_map.get(bg if isinstance(bg, str) else None, '') if bg else ''
    
    style_str = ''.join(styles)
    print(f"{bg_col}{style_str}{col}{texto}{Color.RESET}", end=end)

# ============================================================================
# USER-AGENTS (150+ completos)
# ============================================================================

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.62 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.58 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.129 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.62 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0.1',
    'Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36 Edg/125.0.6422.60',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36 Edg/125.0.6422.42',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36 Edg/124.0.6367.118',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36 Edg/124.0.6367.91',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.62 Safari/537.36 Edg/124.0.6367.62',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36 Edg/125.0.6422.60',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/110.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36 OPR/110.0.5322.60',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36 OPR/109.0.5322.118',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Android 14; Mobile; rv:126.0) Gecko/126.0 Firefox/126.0',
    'Mozilla/5.0 (Android 14; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0',
    'Mozilla/5.0 (Android 13; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0',
    'Mozilla/5.0 (Android 13; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
    'Mozilla/5.0 (compatible; DuckDuckBot-Https/1.1; https://duckduckgo.com/duckduckbot)',
    'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
]

def get_random_ua():
    return random.choice(USER_AGENTS)

def get_random_delay():
    return random.uniform(DELAY_MIN, DELAY_MAX)

# ============================================================================
# PALABRAS CLAVE CRIMINALES
# ============================================================================

PALABRAS_CLAVE_CRIMEN = [
    'meurtre', 'homicide', 'assassinat', 'tué', 'morte', 'corps retrouvé',
    'viol', 'agression sexuelle', 'violence sexuelle',
    'braquage', 'hold-up', 'vol à main armée', 'arme', 'fusillade',
    'cambriolage', 'vol', 'effraction',
    'narcotrafic', 'drogue', 'cocaïne', 'héroïne', 'stupéfiants', 'deal',
    'gang', 'bande', 'règlement de comptes',
    'attentat', 'terrorisme', 'djihadiste', 'radicalisé',
    'kidnapping', 'enlèvement', 'séquestration',
    'incendie criminel', 'pyromane',
    'féminicide', 'violence conjugale'
]

# ============================================================================
# TIPOS DE CRIMEN
# ============================================================================

TIPOS_CRIMEN = {
    'homicide': {'icono': '🔪', 'color': '#cc0000', 'nombre': 'Homicide/Meurtre', 'es': 'Homicidio', 'fr': 'Homicide', 'it': 'Omicidio'},
    'violence': {'icono': '👊', 'color': '#ff6600', 'nombre': 'Violence/Agression', 'es': 'Violencia', 'fr': 'Violence', 'it': 'Violenza'},
    'viol': {'icono': '⚠️', 'color': '#990000', 'nombre': 'Viol/Agression sexuelle', 'es': 'Violación', 'fr': 'Viol', 'it': 'Stupro'},
    'braquage': {'icono': '🔫', 'color': '#ff4444', 'nombre': 'Braquage/Hold-up', 'es': 'Atraco', 'fr': 'Braquage', 'it': 'Rapina'},
    'cambriolage': {'icono': '🚪', 'color': '#ffaa00', 'nombre': 'Cambriolage/Vol', 'es': 'Robo', 'fr': 'Cambriolage', 'it': 'Furto'},
    'narcotrafic': {'icono': '💊', 'color': '#ff00ff', 'nombre': 'Narcotrafic/Drogue', 'es': 'Narcotráfico', 'fr': 'Narcotrafic', 'it': 'Narcotraffico'},
    'gang': {'icono': '👥', 'color': '#880000', 'nombre': 'Gang/Règlement comptes', 'es': 'Pandilla', 'fr': 'Gang', 'it': 'Gang'},
    'terrorisme': {'icono': '💣', 'color': '#000000', 'nombre': 'Terrorisme/Attentat', 'es': 'Terrorismo', 'fr': 'Terrorisme', 'it': 'Terrorismo'},
    'other': {'icono': '❓', 'color': '#888888', 'nombre': 'Autre crime', 'es': 'Otro crimen', 'fr': 'Autre crime', 'it': 'Altro crimine'}
}

# ============================================================================
# FUENTES
# ============================================================================

FUENTES_BASE = [
    {'nombre': 'Le Monde - Faits divers', 'url': 'https://www.lemonde.fr/faits-divers/', 'base': 'https://www.lemonde.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'Le Figaro - Faits divers', 'url': 'https://www.lefigaro.fr/faits-divers', 'base': 'https://www.lefigaro.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'Libération - Faits divers', 'url': 'https://www.liberation.fr/faits-divers/', 'base': 'https://www.liberation.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': '20 Minutes - Faits divers', 'url': 'https://www.20minutes.fr/faits-divers', 'base': 'https://www.20minutes.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'France Info - Faits divers', 'url': 'https://www.francetvinfo.fr/faits-divers/', 'base': 'https://www.francetvinfo.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'Le Parisien - Faits divers', 'url': 'https://www.leparisien.fr/faits-divers/', 'base': 'https://www.leparisien.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'Le Point - Faits divers', 'url': 'https://www.lepoint.fr/faits-divers/', 'base': 'https://www.lepoint.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'L\'Express - Faits divers', 'url': 'https://www.lexpress.fr/actualite/faits-divers/', 'base': 'https://www.lexpress.fr', 'departement': 'Paris', 'activo': True},
    {'nombre': 'France 3 Régions - Faits divers', 'url': 'https://france3-regions.francetvinfo.fr/faits-divers', 'base': 'https://france3-regions.francetvinfo.fr', 'departement': 'National', 'activo': True},
    {'nombre': 'Actu.fr - Faits divers', 'url': 'https://actu.fr/faits-divers', 'base': 'https://actu.fr', 'departement': 'National', 'activo': True},
    {'nombre': 'La Provence - Faits divers', 'url': 'https://www.laprovence.com/actu/faits-divers', 'base': 'https://www.laprovence.com', 'departement': 'Bouches-du-Rhône', 'activo': True},
    {'nombre': 'Le Progrès - Faits divers', 'url': 'https://www.leprogres.fr/faits-divers', 'base': 'https://www.leprogres.fr', 'departement': 'Rhône', 'activo': True},
    {'nombre': 'Sud Ouest - Faits divers', 'url': 'https://www.sudouest.fr/faits-divers', 'base': 'https://www.sudouest.fr', 'departement': 'Gironde', 'activo': True},
    {'nombre': 'Ouest-France - Faits divers', 'url': 'https://www.ouest-france.fr/faits-divers', 'base': 'https://www.ouest-france.fr', 'departement': 'Ille-et-Vilaine', 'activo': True},
    {'nombre': 'La Dépêche - Faits divers', 'url': 'https://www.ladepeche.fr/faits-divers', 'base': 'https://www.ladepeche.fr', 'departement': 'Haute-Garonne', 'activo': True},
    {'nombre': 'Nice-Matin - Faits divers', 'url': 'https://www.nicematin.com/faits-divers', 'base': 'https://www.nicematin.com', 'departement': 'Alpes-Maritimes', 'activo': True},
    {'nombre': 'Midi Libre - Faits divers', 'url': 'https://www.midilibre.fr/faits-divers', 'base': 'https://www.midilibre.fr', 'departement': 'Hérault', 'activo': True},
    {'nombre': 'La Voix du Nord - Faits divers', 'url': 'https://www.lavoixdunord.fr/faits-divers', 'base': 'https://www.lavoixdunord.fr', 'departement': 'Nord', 'activo': True},
    {'nombre': 'France Info Outre-mer - Faits divers', 'url': 'https://la1ere.francetvinfo.fr/faits-divers/', 'base': 'https://la1ere.francetvinfo.fr', 'departement': 'Outre-mer', 'activo': True},
]

# ============================================================================
# GESTOR DE DATOS
# ============================================================================

class GestorDatos:
    def __init__(self):
        self.archivo = ARCHIVO_DATOS
        self.datos = self.cargar()
    
    def cargar(self):
        """Carga el archivo JSON o crea uno nuevo con la estructura correcta"""
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Asegurar que tiene la estructura correcta
                    if 'crimes' not in data:
                        data['crimes'] = []
                    if 'ultima_actualizacion' not in data:
                        data['ultima_actualizacion'] = None
                    if 'estadisticas_historicas' not in data:
                        data['estadisticas_historicas'] = {}
                    return data
            except Exception as e:
                logger.error(f"Error cargando {self.archivo}: {e}")
                # Si hay error, crear estructura nueva
                return {'crimes': [], 'ultima_actualizacion': None, 'estadisticas_historicas': {}}
        else:
            # Si no existe, crear el archivo
            data = {'crimes': [], 'ultima_actualizacion': None, 'estadisticas_historicas': {}}
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data
    
    def guardar(self):
        """Guarda los datos en el archivo JSON"""
        self.datos['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=2, ensure_ascii=False)
        logger.info(f"Datos guardados: {len(self.datos['crimes'])} crimes")
    
    def agregar_crimes(self, nuevos):
        """Agrega nuevos crímenes evitando duplicados"""
        if not nuevos:
            return 0
        ids_existentes = {c['id'] for c in self.datos['crimes']}
        contador = 0
        for n in nuevos:
            if n['id'] not in ids_existentes:
                self.datos['crimes'].append(n)
                ids_existentes.add(n['id'])
                contador += 1
        if contador > 0:
            self._actualizar_historicas(nuevos)
            self.guardar()
        return contador
    
    def _actualizar_historicas(self, nuevos):
        """Actualiza estadísticas históricas"""
        historicas = self.datos.get('estadisticas_historicas', {})
        for c in nuevos:
            fecha = c.get('fecha', '')
            if fecha and len(fecha) >= 7:
                mes = fecha[:7]
                tipo = c.get('tipo', 'other')
                dep = c.get('departement', 'France')
                if mes not in historicas:
                    historicas[mes] = {'total': 0, 'tipos': {}, 'departements': {}}
                historicas[mes]['total'] += 1
                historicas[mes]['tipos'][tipo] = historicas[mes]['tipos'].get(tipo, 0) + 1
                historicas[mes]['departements'][dep] = historicas[mes]['departements'].get(dep, 0) + 1
        self.datos['estadisticas_historicas'] = historicas
    
    def detectar_tipo_crimen(self, texto):
        """Detecta el tipo de crimen basado en palabras clave"""
        tl = texto.lower()
        if any(p in tl for p in ['meurtre', 'homicide', 'assassinat', 'tué', 'morte']):
            return 'homicide'
        if any(p in tl for p in ['viol', 'agression sexuelle']):
            return 'viol'
        if any(p in tl for p in ['violence', 'agression', 'bagarre', 'rixe', 'couteau']):
            return 'violence'
        if any(p in tl for p in ['braquage', 'hold-up', 'fusillade', 'arme à feu']):
            return 'braquage'
        if any(p in tl for p in ['cambriolage', 'vol', 'effraction']):
            return 'cambriolage'
        if any(p in tl for p in ['narcotrafic', 'drogue', 'cocaïne', 'stupéfiants']):
            return 'narcotrafic'
        if any(p in tl for p in ['gang', 'bande', 'règlement de comptes']):
            return 'gang'
        if any(p in tl for p in ['attentat', 'terrorisme', 'djihadiste']):
            return 'terrorisme'
        return 'other'
    
    def calcular_severidad(self, texto):
        """Calcula la severidad del crimen del 1 al 10"""
        tl = texto.lower()
        score = 0
        if any(p in tl for p in ['meurtre', 'homicide', 'assassinat', 'terrorisme', 'attentat']):
            score += 4
        if any(p in tl for p in ['viol', 'braquage', 'fusillade']):
            score += 3
        if any(p in tl for p in ['gang', 'narcotrafic', 'arme']):
            score += 2
        return min(10, score)
    
    def estadisticas(self):
        """Genera estadísticas de los crímenes"""
        crimes = self.datos.get('crimes', [])
        stats = {
            'total': len(crimes),
            'departements': defaultdict(int),
            'tipos': defaultdict(int),
            'fuentes': defaultdict(int),
            'ultimos_7dias': 0,
            'ultimos_30dias': 0,
            'ultimos_90dias': 0,
            'tendencia': defaultdict(int),
            'severidad_promedio': 0.0
        }
        hoy = datetime.now()
        hace_7d = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
        hace_30d = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        hace_90d = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')
        suma_severidad = 0.0
        count_severidad = 0
        
        for c in crimes:
            if c.get('departement'):
                stats['departements'][c['departement']] += 1
            if c.get('tipo'):
                stats['tipos'][c['tipo']] += 1
            if c.get('fuente'):
                stats['fuentes'][c['fuente']] += 1
            if c.get('severidad'):
                suma_severidad += c['severidad']
                count_severidad += 1
            fecha = c.get('fecha', '')
            if fecha:
                if fecha >= hace_7d:
                    stats['ultimos_7dias'] += 1
                if fecha >= hace_30d:
                    stats['ultimos_30dias'] += 1
                if fecha >= hace_90d:
                    stats['ultimos_90dias'] += 1
                if len(fecha) >= 7:
                    stats['tendencia'][fecha[:7]] += 1
        
        if count_severidad > 0:
            stats['severidad_promedio'] = suma_severidad / count_severidad
        return stats
    
    def evolucion_mensual(self):
        """Devuelve la evolución mensual de crímenes"""
        meses = {}
        for c in self.datos.get('crimes', []):
            if c.get('fecha') and len(c['fecha']) >= 7:
                meses[c['fecha'][:7]] = meses.get(c['fecha'][:7], 0) + 1
        return dict(sorted(meses.items()))
    
    def limpiar_duplicados(self):
        """Elimina crímenes duplicados"""
        ids_vistos = set()
        limpios = []
        dup = 0
        for c in self.datos.get('crimes', []):
            if c['id'] not in ids_vistos:
                ids_vistos.add(c['id'])
                limpios.append(c)
            else:
                dup += 1
        self.datos['crimes'] = limpios
        if dup > 0:
            self.guardar()
        return dup
    
    def estadisticas_rapidas(self):
        """Devuelve estadísticas rápidas para el menú"""
        stats = self.estadisticas()
        if stats['total'] == 0:
            return {}
        
        tipo_mas_comun = max(stats['tipos'].items(), key=lambda x: x[1]) if stats['tipos'] else ('Ninguno', 0)
        porcentaje = (tipo_mas_comun[1] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        dias = defaultdict(int)
        for c in self.datos.get('crimes', []):
            if c.get('fecha'):
                dias[c['fecha'][:10]] += 1
        dia_mas_activo = max(dias.items(), key=lambda x: x[1]) if dias else ('Ninguno', 0)
        
        fuente_mas_activa = max(stats['fuentes'].items(), key=lambda x: x[1]) if stats['fuentes'] else ('Ninguna', 0)
        dep_critico = max(stats['departements'].items(), key=lambda x: x[1]) if stats['departements'] else ('Ninguno', 0)
        
        tendencia = 0
        if len(stats['tendencia']) >= 2:
            meses = sorted(stats['tendencia'].keys())
            ultimo = stats['tendencia'][meses[-1]]
            anterior = stats['tendencia'][meses[-2]]
            if anterior > 0:
                tendencia = ((ultimo - anterior) / anterior) * 100
        
        return {
            'tipo_mas_comun': tipo_mas_comun[0],
            'tipo_mas_comun_count': tipo_mas_comun[1],
            'tipo_mas_comun_porcentaje': porcentaje,
            'dia_mas_activo': dia_mas_activo[0],
            'dia_mas_activo_count': dia_mas_activo[1],
            'fuente_mas_activa': fuente_mas_activa[0],
            'fuente_mas_activa_count': fuente_mas_activa[1],
            'departamento_critico': dep_critico[0],
            'departamento_critico_count': dep_critico[1],
            'tendencia': tendencia
        }
    
    def exportar_json(self):
        """Exporta todos los datos a JSON"""
        return json.dumps(self.datos, indent=2, ensure_ascii=False)
    
    def exportar_csv(self):
        """Exporta los crímenes a CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Titre', 'Date', 'Département', 'Type Crime', 'Source', 'Severite'])
        for c in self.datos.get('crimes', []):
            writer.writerow([c['id'], c['titulo'].replace('\n', ' '), c['fecha'], 
                           c.get('departement', ''), c.get('tipo', ''), c['fuente'], 
                           c.get('severidad', 0)])
        return output.getvalue()
    
    def exportar_html(self):
        """Exporta un informe HTML"""
        stats = self.estadisticas()
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>DIABOLIC FRANCE - Rapport Criminel</title>
<style>
body{{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:20px}}
h1{{color:#cc0000;text-align:center}}
h2{{color:#ff6666;margin-top:30px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:20px 0}}
.stat-card{{background:#1a1a1a;padding:15px;border-radius:8px;text-align:center;border-left:4px solid #cc0000}}
.stat-number{{font-size:2em;color:#cc0000;font-weight:bold}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{border:1px solid #333;padding:8px;text-align:left}}
th{{background:#333;color:#ff6666}}
</style>
</head>
<body>
<h1>🔪 DIABOLIC FRANCE - Rapport Criminel</h1>
<p style="text-align:center">Généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<div class="stats">
<div class="stat-card"><div>Total crimes</div><div class="stat-number">{stats['total']}</div></div>
<div class="stat-card"><div>7 derniers jours</div><div class="stat-number">{stats['ultimos_7dias']}</div></div>
<div class="stat-card"><div>30 derniers jours</div><div class="stat-number">{stats['ultimos_30dias']}</div></div>
<div class="stat-card"><div>Sources actives</div><div class="stat-number">{len(stats['fuentes'])}</div></div>
</div>
<h2>📍 Top départements criminogènes</h2>
<table><tr><th>Département</th><th>Nombre de crimes</th></tr>"""
        for dep, cnt in sorted(stats['departements'].items(), key=lambda x: x[1], reverse=True)[:10]:
            html += f"<tr><td>{dep}</td><td>{cnt}</td></tr>"
        html += "</table><h2>🔪 Types de crimes</h2><table><tr><th>Type</th><th>Icone</th><th>Nombre</th></tr>"
        for tip, cnt in sorted(stats['tipos'].items(), key=lambda x: x[1], reverse=True):
            icono = TIPOS_CRIMEN.get(tip, {}).get('icono', '❓')
            nombre = TIPOS_CRIMEN.get(tip, {}).get('nombre', tip)
            html += f"<tr><td>{nombre}</td><td>{icono}</td><td>{cnt}</td></tr>"
        html += "</table><h2>📈 Évolution mensuelle</h2><table><tr><th>Mois</th><th>Crimes</th></tr>"
        for mes, cnt in sorted(stats['tendencia'].items()):
            html += f"<tr><td>{mes}</td><td>{cnt}</td></tr>"
        html += f"""</table>
<h2>📰 Derniers crimes (20)</h2>
<table><tr><th>Date</th><th>Département</th><th>Type</th><th>Titre</th><th>Source</th></tr>"""
        for c in self.datos.get('crimes', [])[-20:][::-1]:
            html += f"<tr><td>{c['fecha']}</td><td>{c.get('departement', '?')}</td><td>{c.get('tipo', '?')}</td><td>{c['titulo'][:100]}...</td><td>{c['fuente']}</td></tr>"
        html += "</table></body></html>"
        return html

# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def mostrar_banner_inicial():
    print(f"""
{Color.RED}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    ██████╗ ██╗ █████╗ ██████╗  ██████╗ ██╗     ██╗ ██████╗                    ║
║    ██╔══██╗██║██╔══██╗██╔══██╗██╔═══██╗██║     ██║██╔════╝                    ║
║    ██║  ██║██║███████║██████╔╝██║   ██║██║     ██║██║                         ║
║    ██║  ██║██║██╔══██║██╔══██╗██║   ██║██║     ██║██║                         ║
║    ██████╔╝██║██║  ██║███████║╚██████╔╝███████╗██║╚██████╗                    ║
║    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝                    ║
║                                                                               ║
║   🔪 DIABOLIC FRANCE v{VERSION} - SURVEILLANCE CRIMINELLE                         ║
║   ══════════════════════════════════════════════════════════════════════════  ║
║   🚨 Surveillance: Homicides · Violences · Braquages · Narcotrafic · Gangs    ║
║   🔄 150+ User-Agents · Auto-discovery · Anti-blocage · Pagination réelle     ║
║   📈 Graphiques interactifs · Dashboard web · 3 langues (ES/FR/IT)            ║
║                                                                               ║
║   🛡️  "L'union fait la force" - Devise française                              ║
║                                                                               ║
║                                         - By Condor2026                       ║
║                                         •SpectrumSecurity•                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")

def mostrar_stats_rapidas():
    """Muestra estadísticas rápidas en la terminal"""
    stats = gestor_global.estadisticas()
    rapidas = gestor_global.estadisticas_rapidas()
    if not rapidas:
        cprint(f"\n⚠️ {t('sin_datos')}", 'yellow')
        return
    
    print(f"\n{Color.RED}{'═' * 60}{Color.RESET}")
    print(f"{Color.BOLD}{Color.WHITE}  ⚡ {t('stats_rapidas')} - DIABOLIC FRANCE{Color.RESET}")
    print(f"{Color.RED}{'═' * 60}{Color.RESET}")
    
    tipo_nombre = TIPOS_CRIMEN.get(rapidas['tipo_mas_comun'], {}).get(IDIOMA_ACTUAL, rapidas['tipo_mas_comun'])
    print(f"  {Color.YELLOW}🔪 {t('tipo_mas_comun')}:{Color.RESET} {tipo_nombre} ({rapidas['tipo_mas_comun_count']} - {rapidas['tipo_mas_comun_porcentaje']:.1f}%)")
    print(f"  {Color.YELLOW}📅 {t('dia_mas_activo')}:{Color.RESET} {rapidas['dia_mas_activo']} ({rapidas['dia_mas_activo_count']})")
    print(f"  {Color.YELLOW}📰 {t('fuente_mas_activa')}:{Color.RESET} {rapidas['fuente_mas_activa']} ({rapidas['fuente_mas_activa_count']})")
    print(f"  {Color.YELLOW}🏴 {t('departamento_critico')}:{Color.RESET} {rapidas['departamento_critico']} ({rapidas['departamento_critico_count']})")
    
    tendencia_icono = "▲" if rapidas['tendencia'] > 0 else "▼" if rapidas['tendencia'] < 0 else "■"
    tendencia_color = Color.GREEN if rapidas['tendencia'] > 0 else Color.RED if rapidas['tendencia'] < 0 else Color.GRAY
    print(f"  {Color.YELLOW}📈 {t('tendencia')}:{Color.RESET} {tendencia_color}{tendencia_icono} {abs(rapidas['tendencia']):.1f}%{Color.RESET}")
    
    severidad = stats.get('severidad_promedio', 0)
    print(f"  {Color.YELLOW}💀 {t('severidad')}:{Color.RESET} {severidad:.1f}/10")
    print(f"{Color.RED}{'═' * 60}{Color.RESET}")

def mostrar_menu_principal():
    """Muestra el menú principal"""
    stats = gestor_global.estadisticas()
    activas = len([f for f in fuentes_global if f.get('activo', True)])
    
    print(f"""
{Color.RED}{'=' * 55}{Color.RESET}
{Color.BOLD}{Color.WHITE}  🔪 DIABOLIC FRANCE v{VERSION}{Color.RESET}
{Color.RED}{'=' * 55}{Color.RESET}
  📊 {t('stats_total')}: {stats['total']}
  📰 {t('fuentes')}: {activas} / {len(fuentes_global)}
  🏴 {t('departamentos')}: {len(stats['departements'])}
  💀 Severidad: {stats.get('severidad_promedio', 0):.1f}/10
{Color.RED}{'=' * 55}{Color.RESET}

{Color.YELLOW}{'=' * 55}{Color.RESET}
{Color.CYAN}  📋 {t('menu_title')}{Color.RESET}
{Color.YELLOW}{'=' * 55}{Color.RESET}
{Color.GREEN}  1. 🔍 {t('cmd_buscar')}
{Color.GREEN}  2. 📊 {t('cmd_analisis')}
{Color.GREEN}  3. 🔗 {t('cmd_conexiones')}
{Color.GREEN}  4. 📈 {t('cmd_evolucion')}
{Color.GREEN}  5. 🌐 {t('cmd_web')}
{Color.GREEN}  6. 📰 {t('cmd_ultimos')}
{Color.GREEN}  7. 📥 {t('cmd_exportar')}
{Color.GREEN}  8. 🔍 {t('cmd_verificar')}
{Color.GREEN}  9. 📊 {t('cmd_tipos')}
{Color.GREEN} 10. 📈 {t('cmd_estadisticas')}
{Color.GREEN} 11. 🧹 {t('cmd_limpiar')}
{Color.GREEN} 12. ⚡ {t('cmd_stats_rapidas')}
{Color.RED} 13. 🗑️ {t('cmd_salir')}{Color.RESET}
{Color.YELLOW}{'=' * 55}{Color.RESET}
""")

def menu():
    """Bucle principal del menú"""
    global gestor_global, fuentes_global
    while True:
        mostrar_menu_principal()
        opc = input(f"{Color.CYAN}➤ {Color.YELLOW}Opción: {Color.RESET}")
        
        if opc == '1':
            cprint(f"\n🔍 {t('procesando')}", 'cyan', bold=True)
            # Verificar fuentes primero
            verificador = VerificadorFuentes()
            fuentes_global = verificador.verificar_todas(fuentes_global)
            # Extraer crímenes
            extractor = ExtractorNoticias(fuentes_global)
            nuevos = extractor.extraer_todas(paginas=PAGINAS_BUSQUEDA)
            agregados = gestor_global.agregar_crimes(nuevos)
            cprint(f"\n✅ {agregados} {t('incidentes')} nouveaux", 'green', bold=True)
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '2':
            stats = gestor_global.estadisticas()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📊 {t('analisis_completo')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            cprint(f"\n📈 {t('stats_total')}: {stats['total']}", 'white')
            cprint(f"   7d: {stats['ultimos_7dias']} | 30d: {stats['ultimos_30dias']} | 90d: {stats['ultimos_90dias']}", 'white')
            cprint(f"\n💀 Severidad promedio: {stats.get('severidad_promedio', 0):.1f}/10", 'cyan')
            cprint(f"\n📍 TOP départements criminogènes:", 'yellow')
            for dep, cnt in sorted(stats['departements'].items(), key=lambda x: x[1], reverse=True)[:10]:
                barra = '█' * min(int(cnt / max(stats['departements'].values()) * 30), 30) if stats['departements'] else ''
                cprint(f"   {dep:25} {cnt:4} {barra}", 'cyan')
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '3':
            stats = gestor_global.estadisticas()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"🔗 {t('conexiones')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            cprint(f"\n📰 TOP fuentes criminales:", 'yellow')
            for f, cnt in sorted(stats['fuentes'].items(), key=lambda x: x[1], reverse=True)[:10]:
                barra = '█' * min(int(cnt / max(stats['fuentes'].values()) * 30), 30) if stats['fuentes'] else ''
                cprint(f"   {f:30} {cnt:4} {barra}", 'cyan')
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '4':
            evolucion = gestor_global.evolucion_mensual()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📈 {t('evolucion_mensual')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            if evolucion:
                max_val = max(evolucion.values())
                for mes, cnt in list(evolucion.items())[-12:]:
                    barra = '█' * int(cnt / max_val * 30) if max_val > 0 else ''
                    cprint(f"   {mes}  {cnt:4} {barra}", 'cyan')
            else:
                cprint(f"   {Color.GRAY}{t('sin_datos')}{Color.RESET}")
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '5':
            cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
            cprint(f"   🔪 Dashboard criminal con paginación real", 'cyan')
            cprint(f"   🌍 3 langues: ES/FR/IT", 'cyan')
            cprint(f"   💀 Barra de severidad por crimen", 'cyan')
            cprint(f"   {Color.GRAY}Ctrl+C para volver al menú{Color.RESET}")
            app.run(host='127.0.0.1', port=PUERTO, debug=False)
            
        elif opc == '6':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📰 {t('cmd_ultimos')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            crimes = gestor_global.datos.get('crimes', [])[-20:][::-1]
            if crimes:
                for i, c in enumerate(crimes, 1):
                    tipo_nombre = TIPOS_CRIMEN.get(c.get('tipo', 'other'), {}).get(IDIOMA_ACTUAL, c.get('tipo', 'other'))
                    icono = TIPOS_CRIMEN.get(c.get('tipo', 'other'), {}).get('icono', '❓')
                    severidad_icono = "🔴" if c.get('severidad', 0) > 7 else "🟠" if c.get('severidad', 0) > 4 else "🟡"
                    cprint(f"\n{i:2d}. {icono} {c['titulo'][:100]}...", 'white')
                    cprint(f"      📅 {c['fecha']} | 📍 {c.get('departement','?')} | 📰 {c['fuente']} | {severidad_icono} Severidad: {c.get('severidad',0)}/10", 'gray')
            else:
                cprint(f"   {Color.GRAY}{t('sin_datos')}{Color.RESET}")
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '7':
            cprint(f"\n📥 {t('exportando')}", 'cyan', bold=True)
            cprint(f"\n{Color.YELLOW}Formatos: 1=JSON 2=CSV 3=HTML{Color.RESET}")
            fmt = input(f"{Color.CYAN}➤ Elige: {Color.RESET}")
            if fmt == '1':
                with open('diabolic_export.json', 'w', encoding='utf-8') as f:
                    f.write(gestor_global.exportar_json())
                cprint(f"✅ Exportado a diabolic_export.json", 'green')
            elif fmt == '2':
                with open('diabolic_export.csv', 'w', encoding='utf-8') as f:
                    f.write(gestor_global.exportar_csv())
                cprint(f"✅ Exportado a diabolic_export.csv", 'green')
            elif fmt == '3':
                with open('diabolic_export.html', 'w', encoding='utf-8') as f:
                    f.write(gestor_global.exportar_html())
                cprint(f"✅ Exportado a diabolic_export.html", 'green')
            else:
                cprint(f"❌ {t('opcion_invalida')}", 'red')
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '8':
            cprint(f"\n🔍 {t('verificando')}", 'cyan', bold=True)
            verificador = VerificadorFuentes()
            fuentes_global = verificador.verificar_todas(fuentes_global)
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '9':
            stats = gestor_global.estadisticas()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📊 {t('cmd_tipos')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            if stats['tipos']:
                for tip, cnt in sorted(stats['tipos'].items(), key=lambda x: x[1], reverse=True):
                    icono = TIPOS_CRIMEN.get(tip, {}).get('icono', '❓')
                    nombre = TIPOS_CRIMEN.get(tip, {}).get(IDIOMA_ACTUAL, tip)
                    barra = '█' * min(int(cnt / max(stats['tipos'].values()) * 30), 30) if stats['tipos'] else ''
                    cprint(f"   {icono} {nombre:20} {cnt:4} {barra}", 'cyan')
            else:
                cprint(f"   {Color.GRAY}{t('sin_datos')}{Color.RESET}")
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '10':
            stats = gestor_global.estadisticas()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📈 {t('estadisticas_avanzadas')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            cprint(f"\n📊 Total crímenes: {stats['total']}", 'white')
            cprint(f"   Últimos 7 días: {stats['ultimos_7dias']}", 'white')
            cprint(f"   Últimos 30 días: {stats['ultimos_30dias']}", 'white')
            cprint(f"   Últimos 90 días: {stats['ultimos_90dias']}", 'white')
            cprint(f"\n🔪 Tipos de crimen detectados: {len(stats['tipos'])}", 'yellow')
            cprint(f"📍 Departamentos afectados: {len(stats['departements'])}", 'yellow')
            cprint(f"📰 Fuentes activas: {len(stats['fuentes'])}", 'yellow')
            cprint(f"\n💀 Severidad promedio: {stats.get('severidad_promedio', 0):.1f}/10", 'cyan')
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '11':
            cprint(f"\n🧹 {t('limpiando')}", 'cyan', bold=True)
            duplicados = gestor_global.limpiar_duplicados()
            cprint(f"✅ Eliminados {duplicados} duplicados", 'green')
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '12':
            mostrar_stats_rapidas()
            input(f"\n{Color.GRAY}Enter para continuar...{Color.RESET}")
            
        elif opc == '13':
            cprint(f"\n👋 {t('hasta_pronto')}", 'red', bold=True)
            break
            
        else:
            cprint(f"\n❌ {t('opcion_invalida')}", 'red')
            time.sleep(1)

# ============================================================================
# VERIFICADOR DE FUENTES
# ============================================================================

class VerificadorFuentes:
    def __init__(self):
        self.discoverer = URLAutoDiscoverer()
        self.estado_file = ARCHIVO_ESTADO
        self.estado = self.cargar_estado()
    
    def cargar_estado(self):
        if os.path.exists(self.estado_file):
            try:
                with open(self.estado_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def guardar_estado(self):
        with open(self.estado_file, 'w', encoding='utf-8') as f:
            json.dump(self.estado, f, indent=2)
    
    def verificar_fuente(self, fuente, aplicar_discovery=True):
        nombre = fuente['nombre']
        for intento in range(MAX_INTENTOS):
            try:
                headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
                r = requests.get(fuente['url'], timeout=TIMEOUT, headers=headers, allow_redirects=True)
                if r.status_code == 200:
                    fuente['activo'] = True
                    return fuente, True
                else:
                    time.sleep(get_random_delay())
            except:
                time.sleep(get_random_delay())
        
        if aplicar_discovery:
            nueva_url = self.discoverer.discover_url(fuente)
            if nueva_url != fuente['url']:
                fuente['url'] = nueva_url
                for intento in range(MAX_INTENTOS):
                    try:
                        headers = {'User-Agent': get_random_ua()}
                        r = requests.get(nueva_url, timeout=TIMEOUT, headers=headers)
                        if r.status_code == 200:
                            fuente['activo'] = True
                            return fuente, True
                    except:
                        continue
        
        fuente['activo'] = False
        return fuente, False
    
    def verificar_todas(self, fuentes, mostrar_progreso=True):
        cprint(f"\n{'='*80}", 'red', bold=True)
        cprint(f"🔍 {t('verificando')}", 'red', bold=True, bg=True)
        cprint(f"{'='*80}", 'red', bold=True)
        
        verificadas = []
        activas = 0
        auto = 0
        total = len(fuentes)
        
        for i, fuente in enumerate(fuentes, 1):
            if mostrar_progreso:
                pct = (i/total)*100
                barra = '█' * int(i*40/total) + '░' * (40 - int(i*40/total))
                sys.stdout.write(f"\r   📊 Progreso: [{barra}] {i}/{total} ({pct:.1f}%)")
                sys.stdout.flush()
            
            cprint(f"\n📰 [{i}/{total}] {fuente['nombre']}", 'yellow', bold=True, end=' ')
            url_orig = fuente['url']
            fv, exito = self.verificar_fuente(fuente.copy(), True)
            
            if exito:
                activas += 1
                if fv['url'] != url_orig:
                    auto += 1
                    cprint(f"✅ OK (Auto-discovery)", 'green')
                else:
                    cprint(f"✅ OK", 'green')
            else:
                cprint(f"❌ INACTIVE", 'red')
            
            verificadas.append(fv)
            time.sleep(0.1)
        
        print()
        cprint(f"\n{'='*80}", 'green', bold=True)
        cprint(f"📊 RÉSULTATS:", 'green', bold=True)
        cprint(f"   Sources actives: {activas} / {total}", 'white')
        cprint(f"   Auto-discovery appliqué: {auto} URLs trouvées", 'cyan')
        cprint(f"{'='*80}", 'green', bold=True)
        
        self.guardar_estado()
        return verificadas

# ============================================================================
# AUTO-DISCOVERY DE URLs
# ============================================================================

class URLAutoDiscoverer:
    def __init__(self):
        self.cache_file = ARCHIVO_CACHE
        self.cache = self.load_cache()
        self.common_paths = [
            'faits-divers', 'faits_divers', 'actualite', 'actualites',
            'justice', 'police', 'gendarmerie', 'criminalite',
            'delinquance', 'arrestation', 'interpellation',
            'enquete', 'crime', 'crimes', 'violence'
        ]
    
    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def probar_url(self, url):
        try:
            headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
            r = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                texto = soup.get_text().lower()
                if any(kw in texto for kw in ['meurtre', 'violence', 'crime', 'braquage']):
                    return True
            return False
        except:
            return False
    
    def discover_url(self, fuente):
        nombre = fuente['nombre']
        base_url = fuente['base']
        original_url = fuente['url']
        
        if nombre in self.cache and self.cache[nombre].get('url'):
            cached_url = self.cache[nombre]['url']
            cprint(f"   📦 Cache trouvée: {cached_url}", 'gray', dim=True)
            if self.probar_url(cached_url):
                return cached_url
        
        cprint(f"   🔍 Recherche URL alternative...", 'cyan', dim=True)
        
        for path in self.common_paths:
            urls_to_try = [
                f"{base_url.rstrip('/')}/{path}",
                f"{base_url.rstrip('/')}/{path}/",
                f"{base_url.rstrip('/')}/{path}.html",
                f"{base_url.rstrip('/')}/rubrique/{path}",
                f"{base_url.rstrip('/')}/theme/{path}",
                f"{base_url.rstrip('/')}/category/{path}",
            ]
            
            for test_url in urls_to_try[:5]:
                if self.probar_url(test_url):
                    cprint(f"   ✅ URL trouvée: {test_url}", 'green')
                    self.cache[nombre] = {'url': test_url, 'found_date': datetime.now().isoformat()}
                    self.save_cache()
                    return test_url
                time.sleep(0.2)
        
        cprint(f"   ⚠️ URL alternative non trouvée", 'yellow')
        return original_url

# ============================================================================
# EXTRACTOR DE NOTICIAS CRIMINALES
# ============================================================================

class ExtractorNoticias:
    def __init__(self, fuentes):
        self.fuentes = fuentes
        self.session = self._crear_sesion()
    
    def _crear_sesion(self):
        session = requests.Session()
        retry = Retry(total=2, read=2, connect=2, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def fetch_url(self, url):
        for intento in range(MAX_INTENTOS):
            try:
                headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
                response = self.session.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    time.sleep(get_random_delay()*2)
                else:
                    time.sleep(get_random_delay())
            except:
                time.sleep(get_random_delay())
        return None
    
    def extraer_de_fuente(self, fuente, paginas=PAGINAS_BUSQUEDA):
        crimes = []
        url_base = fuente['url']
        
        for pagina in range(1, paginas + 1):
            if pagina == 1:
                url = url_base
            else:
                patrones = [
                    url_base.rstrip('/') + f'/page/{pagina}/',
                    url_base.rstrip('/') + f'?page={pagina}',
                    url_base.rstrip('/') + f'&page={pagina}',
                    url_base.rstrip('/') + f'/pagina/{pagina}',
                    url_base.rstrip('/') + f'?p={pagina}',
                ]
                url = None
                for pat in patrones:
                    test = self.fetch_url(pat)
                    if test:
                        url = pat
                        break
                if not url:
                    break
            
            try:
                cprint(f"   📄 Page {pagina}... ", 'gray', end='')
                response = self.fetch_url(url)
                
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    elementos = []
                    elementos.extend(soup.find_all('article'))
                    elementos.extend(soup.find_all('div', class_=re.compile(r'article|story|post|news|entry', re.I)))
                    elementos.extend(soup.find_all(['h1', 'h2', 'h3', 'h4']))
                    
                    encontrados = 0
                    gestor_temp = GestorDatos()
                    crimes_pagina = []
                    
                    for elem in elementos[:30]:
                        texto = elem.get_text().strip()
                        if len(texto) < 40:
                            continue
                        
                        tl = texto.lower()
                        if any(kw in tl for kw in PALABRAS_CLAVE_CRIMEN):
                            fecha_elem = soup.find('time')
                            fecha = datetime.now().strftime('%Y-%m-%d')
                            if fecha_elem and fecha_elem.get('datetime'):
                                fecha = fecha_elem.get('datetime')[:10]
                            
                            dep = fuente['departement']
                            for d in ['Paris', 'Bouches-du-Rhône', 'Rhône', 'Gironde', 'Haute-Garonne', 
                                      'Ille-et-Vilaine', 'Finistère', 'Bas-Rhin', 'Alpes-Maritimes', 'Nord',
                                      'Outre-mer', 'National']:
                                if d.lower() in tl:
                                    dep = d
                                    break
                            
                            tipo = gestor_temp.detectar_tipo_crimen(texto)
                            severidad = gestor_temp.calcular_severidad(texto)
                            
                            crimes.append({
                                'id': hashlib.md5(texto.encode()).hexdigest()[:16],
                                'titulo': texto[:500],
                                'fecha': fecha,
                                'departement': dep,
                                'tipo': tipo,
                                'fuente': fuente['nombre'],
                                'severidad': severidad
                            })
                            encontrados += 1
                    
                    cprint(f"✓ {encontrados} crimes trouvés", 'green')
                    if encontrados == 0 and pagina > 2:
                        break
                else:
                    cprint(f"✗ Pas de réponse", 'red')
                    break
            except Exception as e:
                cprint(f"✗ Erreur: {str(e)[:30]}", 'red')
            
            time.sleep(get_random_delay())
        
        return crimes
    
    def extraer_todas(self, paginas=PAGINAS_BUSQUEDA):
        cprint(f"\n{'='*80}", 'red', bold=True)
        cprint(f"🔪 DIABOLIC FRANCE - SURVEILLANCE CRIMINELLE", 'red', bold=True, bg=True)
        cprint(f"{'='*80}", 'red', bold=True)
        
        todas = []
        fuentes_activas = [f for f in self.fuentes if f.get('activo', True)]
        total_act = len(fuentes_activas)
        
        if total_act == 0:
            cprint(f"\n⚠️ {t('sin_datos')}", 'yellow')
            return todas
        
        for idx, fuente in enumerate(fuentes_activas, 1):
            pct = (idx/total_act)*100
            barra = '█' * int(idx*40/total_act) + '░' * (40 - int(idx*40/total_act))
            sys.stdout.write(f"\r   🔪 Analyse: [{barra}] {idx}/{total_act} ({pct:.1f}%)")
            sys.stdout.flush()
            
            cprint(f"\n\n📰 {fuente['nombre']}", 'yellow', bold=True)
            cprint(f"   📍 Département: {fuente['departement']}", 'gray', dim=True)
            
            crimes_f = self.extraer_de_fuente(fuente, paginas)
            todas.extend(crimes_f)
            cprint(f"   📊 Total source: {len(crimes_f)} crimes", 'cyan')
        
        print()
        
        unicos = {}
        for c in todas:
            if c['id'] not in unicos:
                unicos[c['id']] = c
        
        resultado = list(unicos.values())
        
        cprint(f"\n{'='*80}", 'green', bold=True)
        cprint(f"🔪 RÉSULTAT FINAL:", 'green', bold=True)
        cprint(f"   Crimes trouvés: {len(resultado)}", 'white')
        cprint(f"   Sources actives: {total_act}", 'white')
        cprint(f"   Auto-discovery appliqué", 'cyan')
        cprint(f"{'='*80}", 'green', bold=True)
        
        input(f"\n{Color.GRAY}Presiona Enter para volver al menú...{Color.RESET}")
        
        return resultado

# ============================================================================
# SERVIDOR WEB (DASHBOARD CRIMINAL)
# ============================================================================

app = Flask(__name__)
gestor_global = None
fuentes_global = None

WEB_TEXTS = {
    'es': {
        'subtitle': 'Monitoreo criminal en tiempo real - Francia',
        'stats_total': 'Total crímenes', 'fuentes': 'fuentes activas',
        'actualizar': 'Actualizar', 'todo': 'Todo', 'days': 'días',
        'prev': '← Anterior', 'next': 'Siguiente →', 'page': 'Página',
        'items': 'crímenes', 'last_news': 'Últimos crímenes',
        'severidad': 'Severidad'
    },
    'fr': {
        'subtitle': 'Surveillance criminelle en temps réel - France',
        'stats_total': 'Total crimes', 'fuentes': 'sources actives',
        'actualizar': 'Mettre à jour', 'todo': 'Tout', 'days': 'jours',
        'prev': '← Précédent', 'next': 'Suivant →', 'page': 'Page',
        'items': 'crimes', 'last_news': 'Derniers crimes',
        'severidad': 'Sévérité'
    },
    'it': {
        'subtitle': 'Monitoraggio criminale in tempo reale - Francia',
        'stats_total': 'Totale crimini', 'fuentes': 'fonti attive',
        'actualizar': 'Aggiorna', 'todo': 'Tutto', 'days': 'giorni',
        'prev': '← Precedente', 'next': 'Successivo →', 'page': 'Pagina',
        'items': 'crimini', 'last_news': 'Ultimi crimini',
        'severidad': 'Severità'
    }
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>🔪 DIABOLIC FRANCE</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:linear-gradient(135deg,#0a0a0a,#1a0a2a);color:#e0e0e0;font-family:sans-serif;padding:20px}
        .container{max-width:1200px;margin:0 auto}
        .header{background:linear-gradient(135deg,#1a0a2a,#2a0a2a);padding:30px;border-radius:20px;text-align:center;margin-bottom:30px;border:1px solid #cc0000}
        h1{color:#cc0000}.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:20px 0}
        .stat-card{background:#111;padding:20px;border-radius:15px;text-align:center;border-left:4px solid #cc0000}
        .stat-number{font-size:2.5em;color:#cc0000;font-weight:bold}
        .btn{background:#222;color:#cc0000;border:2px solid #cc0000;padding:10px 20px;border-radius:40px;margin:5px;cursor:pointer;text-decoration:none;display:inline-block}
        .btn:hover{background:#cc0000;color:#000}
        .filtros{display:flex;gap:10px;justify-content:center;margin:20px 0;flex-wrap:wrap}
        .filtro-btn{background:#1a1a1a;color:#ccc;border:2px solid #333;padding:8px 20px;border-radius:30px;text-decoration:none}
        .filtro-btn.active,.filtro-btn:hover{background:#cc0000;color:#000}
        .charts-row{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin:20px 0}
        .chart-container{background:#111;border-radius:15px;padding:20px}
        .pagination{display:flex;justify-content:center;gap:15px;margin:20px 0}
        .page-link{background:#222;color:#cc0000;padding:8px 16px;border-radius:8px;text-decoration:none}
        .crime-card{background:#0a0a0a;margin:10px 0;padding:15px;border-radius:10px;border-left:4px solid #cc0000}
        .severity-bar{height:4px;background:#333;margin-top:10px;border-radius:2px;overflow:hidden}
        .severity-fill{height:100%;background:#cc0000;width:0%}
        @media(max-width:768px){.stats-grid{grid-template-columns:repeat(2,1fr)}.charts-row{grid-template-columns:1fr}}
    </style>
</head>
<body>
<div class="container">
    <div class="header"><h1>🔪 DIABOLIC FRANCE</h1><p>{{ texts.subtitle }}</p></div>
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-number">{{ stats.total }}</div><div>{{ texts.stats_total }}</div></div>
        <div class="stat-card"><div class="stat-number">{{ stats.ultimos_7dias }}</div><div>⚡ 7 {{ texts.days }}</div></div>
        <div class="stat-card"><div class="stat-number">{{ stats.ultimos_30dias }}</div><div>🔥 30 {{ texts.days }}</div></div>
        <div class="stat-card"><div class="stat-number">{{ periodicos_activos }}</div><div>📰 {{ texts.fuentes }}</div></div>
    </div>
    <div style="text-align:center">
        <form action="/actualizar" method="post" style="display:inline"><button class="btn">🔄 {{ texts.actualizar }}</button></form>
        <a href="/exportar/json" class="btn">📥 JSON</a><a href="/exportar/csv" class="btn">📥 CSV</a>
        <a href="/exportar/html" class="btn">📄 HTML</a>
        <a href="?lang=es" class="btn">🇪🇸</a><a href="?lang=fr" class="btn">🇫🇷</a><a href="?lang=it" class="btn">🇮🇹</a>
    </div>
    <div class="filtros">
        <a href="/?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='todo' %}active{% endif %}">📅 {{ texts.todo }}</a>
        <a href="/filtro/7d?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='7d' %}active{% endif %}">⚡ 7d</a>
        <a href="/filtro/30d?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='30d' %}active{% endif %}">🔥 30d</a>
        <a href="/filtro/90d?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='90d' %}active{% endif %}">📊 90d</a>
    </div>
    <div class="charts-row">
        <div class="chart-container"><canvas id="depChart"></canvas></div>
        <div class="chart-container"><canvas id="typeChart"></canvas></div>
    </div>
    <div class="pagination">
        {% if page > 1 %}<a href="?page={{ page-1 }}&lang={{ lang }}&filtro={{ filtro }}" class="page-link">← {{ texts.prev }}</a>{% endif %}
        <span>{{ texts.page }} {{ page }} / {{ total_pages }}</span>
        {% if page < total_pages %}<a href="?page={{ page+1 }}&lang={{ lang }}&filtro={{ filtro }}" class="page-link">{{ texts.next }} →</a>{% endif %}
    </div>
    <div class="chart-container">
        <h3>📰 {{ texts.last_news }}</h3>
        {% for c in crimes_paginados %}
        <div class="crime-card">
            <div><strong>{{ c.titulo[:150] }}...</strong></div>
            <div style="color:#888;font-size:0.9em">📍 {{ c.departement }} | 📅 {{ c.fecha }} | 📰 {{ c.fuente }} | 🔪 {{ tipos_crimen[c.tipo][lang] if c.tipo in tipos_crimen and lang in tipos_crimen[c.tipo] else c.tipo }}</div>
            <div class="severity-bar"><div class="severity-fill" style="width: {{ c.severidad * 10 }}%"></div></div>
        </div>
        {% endfor %}
    </div>
</div>
<script>
    new Chart(document.getElementById('depChart'),{type:'bar',data:{labels:{{ condados_labels|tojson }}, datasets:[{label:'Crimes',data:{{ condados_data|tojson }},backgroundColor:'#cc0000'}]}});
    new Chart(document.getElementById('typeChart'),{type:'doughnut',data:{labels:{{ tipos_labels|tojson }}, datasets:[{data:{{ tipos_data|tojson }},backgroundColor:['#cc0000','#ff6600','#990000','#ff4444','#ffaa00','#ff00ff','#880000','#000000','#888888']}]}});
</script>
</body>
</html>
'''

@app.route('/')
def home():
    lang = request.args.get('lang', IDIOMA_ACTUAL or 'fr')
    page = int(request.args.get('page', 1))
    filtro = request.args.get('filtro', 'todo')
    per_page = 12
    
    crimes = gestor_global.datos.get('crimes', [])
    if filtro == '7d':
        hace = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        crimes = [c for c in crimes if c.get('fecha', '') >= hace]
    elif filtro == '30d':
        hace = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        crimes = [c for c in crimes if c.get('fecha', '') >= hace]
    elif filtro == '90d':
        hace = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        crimes = [c for c in crimes if c.get('fecha', '') >= hace]
    
    total_items = len(crimes)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    start = (page - 1) * per_page
    paginated = crimes[start:start + per_page] if crimes else []
    
    stats = gestor_global.estadisticas()
    condados_labels = list(stats['departements'].keys())[:6]
    condados_data = list(stats['departements'].values())[:6]
    tipos_labels = [TIPOS_CRIMEN.get(t, {}).get('icono', '❓') + ' ' + TIPOS_CRIMEN.get(t, {}).get(lang, t) for t in list(stats['tipos'].keys())[:6]]
    tipos_data = list(stats['tipos'].values())[:6]
    periodicos_activos = len([f for f in fuentes_global if f.get('activo', True)])
    
    return render_template_string(HTML_TEMPLATE, version=VERSION, lang=lang, texts=WEB_TEXTS.get(lang, WEB_TEXTS['fr']),
                                  stats=stats, periodicos_activos=periodicos_activos, filtro=filtro,
                                  condados_labels=condados_labels, condados_data=condados_data,
                                  tipos_labels=tipos_labels, tipos_data=tipos_data,
                                  crimes_paginados=paginated, page=page, total_pages=total_pages,
                                  tipos_crimen=TIPOS_CRIMEN)

@app.route('/filtro/<periodo>')
def filtro_route(periodo):
    lang = request.args.get('lang', IDIOMA_ACTUAL or 'fr')
    return home()

@app.route('/actualizar', methods=['POST'])
def actualizar():
    global gestor_global, fuentes_global
    cprint(f"\n{'='*80}", 'red', bold=True)
    cprint(f"🔪 {t('actualizando')}", 'red', bold=True, bg=True)
    cprint(f"{'='*80}", 'red', bold=True)
    
    verificador = VerificadorFuentes()
    fuentes_global = verificador.verificar_todas(fuentes_global)
    extractor = ExtractorNoticias(fuentes_global)
    nuevos = extractor.extraer_todas(paginas=PAGINAS_BUSQUEDA)
    agregados = gestor_global.agregar_crimes(nuevos)
    
    cprint(f"\n✅ {agregados} {t('incidentes')} nouveaux", 'green', bold=True)
    return home()

@app.route('/exportar/json')
def exportar_json():
    return Response(gestor_global.exportar_json(), mimetype='application/json',
                    headers={'Content-Disposition': 'attachment; filename=diabolic_france.json'})

@app.route('/exportar/csv')
def exportar_csv():
    return Response(gestor_global.exportar_csv(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=diabolic_france.csv'})

@app.route('/exportar/html')
def exportar_html():
    return Response(gestor_global.exportar_html(), mimetype='text/html',
                    headers={'Content-Disposition': 'attachment; filename=diabolic_france.html'})

# ============================================================================
# SELECCIÓN DE IDIOMA
# ============================================================================

def seleccionar_idioma():
    global IDIOMA_ACTUAL
    print(f"""
{Color.RED}╔════════════════════════════════════════════════════════════════════╗
║   🔪 DIABOLIC FRANCE v{VERSION} - SURVEILLANCE CRIMINELLE                 ║
╚════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")
    print(f"{Color.YELLOW}┌{'─' * 40}┐{Color.RESET}")
    print(f"{Color.YELLOW}│  🌍 SELECCIONE IDIOMA / CHOISISSEZ LA LANGUE  │{Color.RESET}")
    print(f"{Color.YELLOW}├{'─' * 40}┤{Color.RESET}")
    print(f"{Color.YELLOW}│  {Color.GREEN}[1] Español{Color.YELLOW}                      │{Color.RESET}")
    print(f"{Color.YELLOW}│  {Color.GREEN}[2] Français{Color.YELLOW}                     │{Color.RESET}")
    print(f"{Color.YELLOW}│  {Color.GREEN}[3] Italiano{Color.YELLOW}                     │{Color.RESET}")
    print(f"{Color.YELLOW}└{'─' * 40}┘{Color.RESET}")
    
    while True:
        opc = input(f"\n{Color.CYAN}➤ Opción: {Color.RESET}")
        if opc == '1':
            IDIOMA_ACTUAL = 'es'
            print(f"{Color.GREEN}✅ Español seleccionado{Color.RESET}")
            break
        elif opc == '2':
            IDIOMA_ACTUAL = 'fr'
            print(f"{Color.GREEN}✅ Français sélectionné{Color.RESET}")
            break
        elif opc == '3':
            IDIOMA_ACTUAL = 'it'
            print(f"{Color.GREEN}✅ Italiano selezionato{Color.RESET}")
            break
    time.sleep(0.5)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    seleccionar_idioma()
    mostrar_banner_inicial()
    
    gestor_global = GestorDatos()
    fuentes_global = FUENTES_BASE.copy()
    
    stats = gestor_global.estadisticas()
    cprint(f"\n{Color.GREEN}📊 Base de données: {stats['total']} crimes stockés{Color.RESET}")
    cprint(f"{Color.YELLOW}⏳ Dernière mise à jour: {gestor_global.datos.get('ultima_actualizacion', 'Jamais')}{Color.RESET}")
    cprint(f"{Color.CYAN}📰 Sources configurées: {len(fuentes_global)} médias français{Color.RESET}")
    
    print(f"\n{Color.CYAN}┌{'─' * 40}┐{Color.RESET}")
    print(f"{Color.CYAN}│{Color.WHITE}  Mode d'exécution:{' ' * 25}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}├{'─' * 40}┤{Color.RESET}")
    print(f"{Color.CYAN}│{Color.GREEN}  [1] Terminal (recommandé){' ' * 17}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}│{Color.GREEN}  [2] Web (dashboard criminel){' ' * 11}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}└{'─' * 40}┘{Color.RESET}")
    
    modo = input(f"\n{Color.CYAN}➤ {Color.YELLOW}Choisissez: {Color.RESET}")
    
    if modo == '2':
        cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
        cprint(f"   🔪 Dashboard criminal con gráficos", 'cyan')
        cprint(f"   🌍 3 langues: ES/FR/IT", 'cyan')
        cprint(f"   {Color.GRAY}Ctrl+C para volver al menú{Color.RESET}")
        app.run(host='127.0.0.1', port=PUERTO, debug=False)
    else:
        menu()
