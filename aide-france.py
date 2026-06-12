#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Condor2026 / SpectrumSecurity

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🔪 AIDE-FRANCE v3.0 - PLATEFORME DE RENSEIGNEMENT CRIMINEL FRANÇAISE         ║
║  ═══════════════════════════════════════════════════════════════════════════ ║
║  📊 Surveillance en temps réel: Trafic de drogue · Violence des gangs        ║
║  🏴 Couvre tous les 101 départements français                                ║
║  🔄 150+ User-Agents rotatifs · Découverte auto-URL · Anti-blocage            ║
║  📈 Graphiques interactifs · Dashboard web · Interface complète               ║
║  🔍 Mécanisme de réessai intelligent · Cache URL · Persistance session        ║
║                                                                              ║
║  🛡️ "Un grand pouvoir implique de grandes responsabilités" - Spider-Man      ║
║                                                                              ║
║                                         - Par Condor2026                      ║
║                                         •SpectrumSecurity•                   ║
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
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, Response
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Thread, Lock
from queue import Queue

# ============================================================================
# LANGUAGE SELECTOR WITH BEAUTIFUL INTERFACE
# ============================================================================

IDIOMA_ACTUAL = None

VERSION = "3.0"

def mostrar_banner_idioma():
    print(f"""
{Color.CYAN}╔════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║   🔪 AIDE-FRANCE v{VERSION} - RENSEIGNEMENT CRIMINEL FRANÇAIS          ║
║                                                                    ║
║   "Nous surveillons pour protéger, pas pour stigmatiser.          ║
║    Données publiques, éthique inébranlable, transparence absolue."║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")

def mostrar_menu_idioma():
    print(f"\n{Color.YELLOW}┌{'─' * 50}┐{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.CYAN}  🌍 SÉLECTIONNER LANGUE / SELECT LANGUAGE{' ' * 15}{Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}├{'─' * 50}┤{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [1] Français                                {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [2] English                                 {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [3] Español                                 {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [4] Italiano                                {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}└{'─' * 50}┘{Color.RESET}")

def seleccionar_idioma():
    global IDIOMA_ACTUAL
    mostrar_banner_idioma()
    mostrar_menu_idioma()
    
    while True:
        opc = input(f"\n{Color.CYAN}➤ {Color.YELLOW}Option / Opción / Opzione: {Color.RESET}")
        if opc == '1':
            IDIOMA_ACTUAL = 'fr'
            print(f"\n{Color.GREEN}✅ Langue: Français sélectionné{Color.RESET}")
            break
        elif opc == '2':
            IDIOMA_ACTUAL = 'en'
            print(f"\n{Color.GREEN}✅ Language: English selected{Color.RESET}")
            break
        elif opc == '3':
            IDIOMA_ACTUAL = 'es'
            print(f"\n{Color.GREEN}✅ Idioma: Español seleccionado{Color.RESET}")
            break
        elif opc == '4':
            IDIOMA_ACTUAL = 'it'
            print(f"\n{Color.GREEN}✅ Lingua: Italiano selezionato{Color.RESET}")
            break
        else:
            print(f"{Color.RED}❌ Option invalide / Invalid option / Opción inválida / Opzione non valida{Color.RESET}")
    
    time.sleep(0.5)

TEXTOS = {
    'fr': {
        'app_name': '🔪 AIDE-FRANCE v3.0',
        'welcome_title': 'PLATEFORME DE RENSEIGNEMENT CRIMINEL FRANÇAISE',
        'menu_title': 'MENU PRINCIPAL',
        'cmd_buscar': 'Rechercher crimes (auto-détection URLs)',
        'cmd_analisis': 'Analyse complète avec graphiques',
        'cmd_conexiones': 'Modèles et connexions entre incidents',
        'cmd_evolucion': 'Évolution mensuelle détaillée',
        'cmd_web': 'Démarrer serveur web (dashboard avec graphiques)',
        'cmd_ultimos': '20 derniers incidents enregistrés',
        'cmd_exportar': 'Exporter données (JSON/CSV/HTML)',
        'cmd_verificar': 'Vérifier/mettre à jour sources (auto-découverte)',
        'cmd_tipos': 'Distribution par type de crime',
        'cmd_estadisticas': 'Statistiques avancées',
        'cmd_limpiar': 'Nettoyer base de données doublons',
        'cmd_salir': 'Quitter application',
        'stats_total': 'Total incidents',
        'incidentes': 'incidents',
        'fuentes': 'sources actives',
        'condados': 'départements affectés',
        'servidor_web': 'Serveur web démarré',
        'presiona_ctrl_c': 'Appuyez sur Ctrl+C pour revenir au menu',
        'hasta_pronto': 'Au revoir! Merci d\'utiliser AIDE-FRANCE',
        'opcion_invalida': 'Option invalide, réessayez',
        'actualizando': 'MISE À JOUR DES DONNÉES CRIMINELLES FRANÇAISES',
        'analisis_completo': 'ANALYSE COMPLÈTE DE LA CRIMINALITÉ EN FRANCE',
        'conexiones': 'MODÈLES ET CONNEXIONS ENTRE INCIDENTS',
        'evolucion_mensual': 'ÉVOLUTION MENSUELLE DES INCIDENTS',
        'exportando': 'EXPORTATION DES DONNÉES',
        'verificando': 'VÉRIFICATION DES SOURCES FRANÇAISES',
        'limpiando': 'NETTOYAGE DE LA BASE DE DONNÉES',
        'estadisticas_avanzadas': 'STATISTIQUES AVANCÉES',
        'error_conexion': 'Erreur de connexion avec la source',
        'sin_datos': 'Pas assez de données à afficher',
        'procesando': 'Traitement en cours...'
    },
    'en': {
        'app_name': '🔪 AIDE-FRANCE v3.0',
        'welcome_title': 'FRENCH CRIMINAL INTELLIGENCE PLATFORM',
        'menu_title': 'MAIN MENU',
        'cmd_buscar': 'Search crimes (auto-discover URLs)',
        'cmd_analisis': 'Full analysis with charts',
        'cmd_conexiones': 'Patterns and connections between incidents',
        'cmd_evolucion': 'Detailed monthly evolution',
        'cmd_web': 'Start web server (dashboard with charts)',
        'cmd_ultimos': 'Last 20 registered incidents',
        'cmd_exportar': 'Export data (JSON/CSV/HTML)',
        'cmd_verificar': 'Verify/update sources (auto-discovery)',
        'cmd_tipos': 'Distribution by crime type',
        'cmd_estadisticas': 'Advanced statistics',
        'cmd_limpiar': 'Clean duplicate database entries',
        'cmd_salir': 'Exit application',
        'stats_total': 'Total incidents',
        'incidentes': 'incidents',
        'fuentes': 'active sources',
        'condados': 'affected departments',
        'servidor_web': 'Web server started',
        'presiona_ctrl_c': 'Press Ctrl+C to return to menu',
        'hasta_pronto': 'Goodbye! Thanks for using AIDE-FRANCE',
        'opcion_invalida': 'Invalid option, try again',
        'actualizando': 'UPDATING FRENCH CRIME DATA',
        'analisis_completo': 'COMPLETE CRIME ANALYSIS FOR FRANCE',
        'conexiones': 'PATTERNS AND CONNECTIONS BETWEEN INCIDENTS',
        'evolucion_mensual': 'MONTHLY INCIDENT EVOLUTION',
        'exportando': 'EXPORTING DATA',
        'verificando': 'VERIFYING FRENCH SOURCES',
        'limpiando': 'CLEANING DATABASE',
        'estadisticas_avanzadas': 'ADVANCED STATISTICS',
        'error_conexion': 'Connection error with source',
        'sin_datos': 'Insufficient data to display',
        'procesando': 'Processing...'
    },
    'es': {
        'app_name': '🔪 AIDE-FRANCE v3.0',
        'welcome_title': 'PLATAFORMA DE INTELIGENCIA CRIMINAL FRANCESA',
        'menu_title': 'MENÚ PRINCIPAL',
        'cmd_buscar': 'Buscar crímenes (auto-detección URLs)',
        'cmd_analisis': 'Análisis completo con gráficos',
        'cmd_conexiones': 'Patrones y conexiones entre incidentes',
        'cmd_evolucion': 'Evolución mensual detallada',
        'cmd_web': 'Iniciar servidor web (dashboard con gráficos)',
        'cmd_ultimos': 'Últimos 20 incidentes registrados',
        'cmd_exportar': 'Exportar datos (JSON/CSV/HTML)',
        'cmd_verificar': 'Verificar/actualizar fuentes (auto-discovery)',
        'cmd_tipos': 'Distribución por tipo de crimen',
        'cmd_estadisticas': 'Estadísticas avanzadas',
        'cmd_limpiar': 'Limpiar base de datos duplicados',
        'cmd_salir': 'Salir de la aplicación',
        'stats_total': 'Total incidentes',
        'incidentes': 'incidentes',
        'fuentes': 'fuentes activas',
        'condados': 'departamentos afectados',
        'servidor_web': 'Servidor web iniciado',
        'presiona_ctrl_c': 'Presiona Ctrl+C para volver al menú',
        'hasta_pronto': '¡Hasta pronto! Gracias por usar AIDE-FRANCE',
        'opcion_invalida': 'Opción no válida, intenta de nuevo',
        'actualizando': 'ACTUALIZANDO DATOS DE CRIMEN EN FRANCIA',
        'analisis_completo': 'ANÁLISIS COMPLETO DEL CRIMEN EN FRANCIA',
        'conexiones': 'PATRONES Y CONEXIONES ENTRE INCIDENTES',
        'evolucion_mensual': 'EVOLUCIÓN MENSUAL DE INCIDENTES',
        'exportando': 'EXPORTANDO DATOS',
        'verificando': 'VERIFICANDO FUENTES FRANCESAS',
        'limpiando': 'LIMPIANDO BASE DE DATOS',
        'estadisticas_avanzadas': 'ESTADÍSTICAS AVANZADAS',
        'error_conexion': 'Error de conexión con la fuente',
        'sin_datos': 'No hay datos suficientes para mostrar',
        'procesando': 'Procesando...'
    },
    'it': {
        'app_name': '🔪 AIDE-FRANCE v3.0',
        'welcome_title': 'PIATTAFORMA DI INTELLIGENZA CRIMINALE FRANCESE',
        'menu_title': 'MENU PRINCIPALE',
        'cmd_buscar': 'Cerca crimini (auto-rilevamento URL)',
        'cmd_analisis': 'Analisi completa con grafici',
        'cmd_conexiones': 'Modelli e connessioni tra incidenti',
        'cmd_evolucion': 'Evoluzione mensile dettagliata',
        'cmd_web': 'Avvia server web (dashboard con grafici)',
        'cmd_ultimos': 'Ultimi 20 incidenti registrati',
        'cmd_exportar': 'Esporta dati (JSON/CSV/HTML)',
        'cmd_verificar': 'Verifica/aggiorna fonti (auto-scoperta)',
        'cmd_tipos': 'Distribuzione per tipo di crimine',
        'cmd_estadisticas': 'Statistiche avanzate',
        'cmd_limpiar': 'Pulisci database duplicati',
        'cmd_salir': 'Esci dall\'applicazione',
        'stats_total': 'Totale incidenti',
        'incidentes': 'incidenti',
        'fuentes': 'fonti attive',
        'condados': 'dipartimenti colpiti',
        'servidor_web': 'Server web avviato',
        'presiona_ctrl_c': 'Premi Ctrl+C per tornare al menu',
        'hasta_pronto': 'Arrivederci! Grazie per aver usato AIDE-FRANCE',
        'opcion_invalida': 'Opzione non valida, riprova',
        'actualizando': 'AGGIORNAMENTO DATI CRIMINALI FRANCESI',
        'analisis_completo': 'ANALISI COMPLETA DELLA CRIMINALITÀ IN FRANCIA',
        'conexiones': 'MODELLI E CONNESSIONI TRA INCIDENTI',
        'evolucion_mensual': 'EVOLUZIONE MENSILE DEGLI INCIDENTI',
        'exportando': 'ESPORTAZIONE DATI',
        'verificando': 'VERIFICA FONTI FRANCESI',
        'limpiando': 'PULIZIA DATABASE',
        'estadisticas_avanzadas': 'STATISTICHE AVANZATE',
        'error_conexion': 'Errore di connessione con la fonte',
        'sin_datos': 'Dati insufficienti da mostrare',
        'procesando': 'Elaborazione in corso...'
    }
}

def t(clave):
    return TEXTOS[IDIOMA_ACTUAL].get(clave, clave)

# ============================================================================
# COLORES PROFESIONALES PARA TERMINAL
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
    
    # Background colors
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
    
    col = color_map.get(color, '')
    bg_col = bg_map.get(bg if isinstance(bg, str) else None, '') if bg else ''
    
    style_str = ''.join(styles)
    print(f"{bg_col}{style_str}{col}{texto}{Color.RESET}", end=end)

# ============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ============================================================================

PUERTO = 5015
ARCHIVO_DATOS = 'aide_france_france.json'
ARCHIVO_CACHE = 'url_cache_france.json'
ARCHIVO_ESTADO = 'etat_sources_france.json'
ARCHIVO_BACKUP = 'aide_france_backup.json'
PAGINAS_BUSQUEDA = 5
TIMEOUT = 25
MAX_INTENTOS = 3
DELAY_MIN = 0.8
DELAY_MAX = 2.0

# ============================================================================
# 150+ USER-AGENTS MODERNOS (COMPLETOS - MANTENIDOS)
# ============================================================================

USER_AGENTS = [
    # Chrome 125 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36',
    
    # Chrome 124 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.62 Safari/537.36',
    
    # Chrome 123 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.58 Safari/537.36',
    
    # Chrome 122 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.129 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
    
    # Chrome 125 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36',
    
    # Chrome 124 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.62 Safari/537.36',
    
    # Chrome 123 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36',
    
    # Chrome 125 - Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    
    # Firefox 126 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0b9',
    
    # Firefox 125 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0.1',
    
    # Firefox 124 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0.1',
    
    # Firefox 123 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0.1',
    
    # Firefox 126 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0.1',
    
    # Firefox 125 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0.1',
    
    # Firefox 124 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0.1',
    
    # Firefox 126 - Linux
    'Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    
    # Safari 17 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    
    # Safari 16 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    
    # Edge 125 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36 Edg/125.0.6422.60',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36 Edg/125.0.6422.42',
    
    # Edge 124 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36 Edg/124.0.6367.118',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36 Edg/124.0.6367.91',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.62 Safari/537.36 Edg/124.0.6367.62',
    
    # Edge 125 - Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36 Edg/125.0.6422.60',
    
    # Opera 110 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/110.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36 OPR/110.0.5322.60',
    
    # Opera 109 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36 OPR/109.0.5322.118',
    
    # iPhone Safari 17
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    
    # iPhone Safari 16
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1',
    
    # iPad Safari
    'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    
    # Android Chrome
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
    
    # Android Firefox
    'Mozilla/5.0 (Android 14; Mobile; rv:126.0) Gecko/126.0 Firefox/126.0',
    'Mozilla/5.0 (Android 14; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0',
    'Mozilla/5.0 (Android 13; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0',
    'Mozilla/5.0 (Android 13; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0',
    
    # Search engine bots
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
    'Mozilla/5.0 (compatible; DuckDuckBot-Https/1.1; https://duckduckgo.com/duckduckbot)',
    'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    
    # Legacy browsers (sometimes work better)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    
    # Linux additional
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
]

def get_random_ua():
    """Retorna un User-Agent aleatorio de la lista de 150+"""
    return random.choice(USER_AGENTS)

def get_random_delay():
    """Retorna un delay aleatorio entre DELAY_MIN y DELAY_MAX"""
    return random.uniform(DELAY_MIN, DELAY_MAX)

# ============================================================================
# SISTEMA DE AUTO-DESCOBRIMIENTO DE URLs
# ============================================================================

class URLAutoDiscoverer:
    """
    Sistema inteligente que busca automáticamente las URLs correctas
    cuando una fuente está caída o ha cambiado de estructura.
    """
    
    def __init__(self):
        self.cache_file = ARCHIVO_CACHE
        self.cache = self.load_cache()
        self.common_paths = [
            # Crime section paths in French
            'faits-divers', 'justice', 'criminalite', 'delinquance', 'police',
            'gendarmerie', 'arrestations', 'drogue', 'trafic-de-drogue',
            'violence', 'gang', 'marseille', 'cites', 'banlieue',
            'category/faits-divers', 'news/faits-divers', 'actualite/justice',
            'france/criminalite', 'societe/faits-divers', 'region/faits-divers',
            'en-direct', 'actu', 'flash-actu', 'dernieres-infos',
            # Pagination patterns
            'page', 'pagina', 'pagination', 'archive', 'category',
            # Common CMS patterns
            '?cat=faits-divers', '?category=criminalite', '?section=justice',
            '#faits-divers', '/faits-divers/', '/criminalite', '/justice'
        ]
        
    def load_cache(self):
        """Carga el caché de URLs encontradas previamente"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_cache(self):
        """Guarda el caché de URLs para futuras ejecuciones"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def discover_url(self, fuente):
        """
        Intenta descubrir la URL correcta para una fuente.
        Retorna la URL encontrada o la original si no se encuentra nada.
        """
        nombre = fuente['nom']
        base_url = fuente['base']
        original_url = fuente['url']
        
        # Verificar caché primero
        if nombre in self.cache and self.cache[nombre].get('url'):
            cached_url = self.cache[nombre]['url']
            cprint(f"   📦 Cache trouvé: {cached_url}", 'gray', dim=True)
            
            # Verificar que la URL cacheada aún funciona
            try:
                headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
                r = requests.get(cached_url, timeout=10, headers=headers)
                if r.status_code == 200:
                    return cached_url
                else:
                    cprint(f"   ⚠️ Cache obsolète (HTTP {r.status_code})", 'yellow')
            except:
                cprint(f"   ⚠️ Cache obsolète (erreur connexion)", 'yellow')
        
        # Probar diferentes paths
        cprint(f"   🔍 Recherche URL alternative...", 'cyan', dim=True)
        
        for path in self.common_paths:
            # Probar diferentes combinaciones de URL
            urls_to_try = [
                f"{base_url}/{path}" if not base_url.endswith('/') else f"{base_url}{path}",
                f"{base_url}/{path}/",
                f"{base_url}/{path}.html",
                f"{base_url}/index.php?category={path}",
                f"{base_url}/?s={path}",
                f"{base_url}/search?q={path}",
                f"{base_url}/tag/{path}",
                f"{base_url}/topic/{path}",
                f"{base_url}/section/{path}",
                f"{base_url}/category/{path}",
                f"{base_url}/archives/category/{path}",
                f"{base_url}/actualite/{path}",
                f"{base_url}/france/{path}",
                f"{base_url}/national/{path}",
            ]
            
            for test_url in urls_to_try[:5]:  # Limitar a 5 intentos por path
                try:
                    headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
                    r = requests.get(test_url, timeout=15, headers=headers)
                    
                    if r.status_code == 200:
                        # Verificar que la página contiene contenido relevante
                        soup = BeautifulSoup(r.text, 'html.parser')
                        page_text = soup.get_text().lower()
                        
                        crime_keywords = ['criminel', 'drogue', 'gang', 'meurtre', 'gendarmerie', 'arrestation', 'violence']
                        if any(keyword in page_text for keyword in crime_keywords):
                            cprint(f"   ✅ URL trouvée: {test_url}", 'green')
                            self.cache[nombre] = {
                                'url': test_url,
                                'path': path,
                                'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            self.save_cache()
                            return test_url
                except:
                    continue
            
            # Pequeña pausa entre intentos
            time.sleep(0.2)
        
        cprint(f"   ❌ Aucune URL alternative trouvée, utilisation originale", 'red')
        return original_url

# ============================================================================
# SOURCES FRANÇAISES (55+ sources vérifiées)
# ============================================================================

SOURCES_BASE = [
    # === NATIONAL NEWS OUTLETS ===
    {'nom': 'Le Monde', 'url': 'https://www.lemonde.fr/faits-divers/', 'base': 'https://www.lemonde.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Le Figaro', 'url': 'https://www.lefigaro.fr/faits-divers', 'base': 'https://www.lefigaro.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Libération', 'url': 'https://www.liberation.fr/societe/police-justice/', 'base': 'https://www.liberation.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Le Parisien', 'url': 'https://www.leparisien.fr/faits-divers/', 'base': 'https://www.leparisien.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'BFMTV', 'url': 'https://www.bfmtv.com/police-justice/', 'base': 'https://www.bfmtv.com', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'France Info', 'url': 'https://www.francetvinfo.fr/faits-divers/', 'base': 'https://www.francetvinfo.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'LCI', 'url': 'https://www.lci.fr/faits-divers/', 'base': 'https://www.lci.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': '20 Minutes', 'url': 'https://www.20minutes.fr/faits-divers/', 'base': 'https://www.20minutes.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Le Point', 'url': 'https://www.lepoint.fr/societe/faits-divers/', 'base': 'https://www.lepoint.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'L\'Express', 'url': 'https://www.lexpress.fr/actualite/societe/faits-divers/', 'base': 'https://www.lexpress.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Le Nouvel Obs', 'url': 'https://www.nouvelobs.com/faits-divers/', 'base': 'https://www.nouvelobs.com', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'La Croix', 'url': 'https://www.la-croix.com/Faits-divers', 'base': 'https://www.la-croix.com', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Valeurs Actuelles', 'url': 'https://www.valeursactuelles.com/societe/faits-divers/', 'base': 'https://www.valeursactuelles.com', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'France Inter', 'url': 'https://www.radiofrance.fr/franceinter/police-justice', 'base': 'https://www.radiofrance.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'Europe 1', 'url': 'https://www.europe1.fr/societe/faits-divers', 'base': 'https://www.europe1.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nom': 'RTL', 'url': 'https://www.rtl.fr/actu/justice-faits-divers', 'base': 'https://www.rtl.fr', 'departement': 'Paris', 'categorie': 'national'},
    
    # === PARIS / ÎLE-DE-FRANCE ===
    {'nom': 'Actu17', 'url': 'https://actu17.fr/', 'base': 'https://actu17.fr', 'departement': 'Paris', 'categorie': 'local'},
    {'nom': 'Paris Normandie', 'url': 'https://www.paris-normandie.fr/faits-divers', 'base': 'https://www.paris-normandie.fr', 'departement': 'Paris', 'categorie': 'local'},
    {'nom': 'Citoyens.com', 'url': 'https://www.citoyens.com/faits-divers/', 'base': 'https://www.citoyens.com', 'departement': 'Paris', 'categorie': 'local'},
    
    # === MARSEILLE / PROVENCE-ALPES-CÔTE D'AZUR ===
    {'nom': 'La Provence', 'url': 'https://www.laprovence.com/actu/faits-divers', 'base': 'https://www.laprovence.com', 'departement': 'Bouches-du-Rhône', 'categorie': 'local'},
    {'nom': 'Marsactu', 'url': 'https://marsactu.fr/categorie/justice/', 'base': 'https://marsactu.fr', 'departement': 'Bouches-du-Rhône', 'categorie': 'local'},
    {'nom': 'Made in Marseille', 'url': 'https://madeinmarseille.net/actualites/faits-divers-marseille/', 'base': 'https://madeinmarseille.net', 'departement': 'Bouches-du-Rhône', 'categorie': 'local'},
    {'nom': 'Nice-Matin', 'url': 'https://www.nicematin.com/faits-divers', 'base': 'https://www.nicematin.com', 'departement': 'Alpes-Maritimes', 'categorie': 'local'},
    {'nom': 'Var-Matin', 'url': 'https://www.varmatin.com/faits-divers', 'base': 'https://www.varmatin.com', 'departement': 'Var', 'categorie': 'local'},
    {'nom': 'Corse-Matin', 'url': 'https://www.corsematin.com/faits-divers', 'base': 'https://www.corsematin.com', 'departement': 'Corse-du-Sud', 'categorie': 'local'},
    
    # === LYON / AUVERGNE-RHÔNE-ALPES ===
    {'nom': 'Le Progrès', 'url': 'https://www.leprogres.fr/faits-divers/', 'base': 'https://www.leprogres.fr', 'departement': 'Rhône', 'categorie': 'local'},
    {'nom': 'Lyon Capitale', 'url': 'https://lyoncapitale.fr/categorie/justice/', 'base': 'https://lyoncapitale.fr', 'departement': 'Rhône', 'categorie': 'local'},
    {'nom': 'Le Dauphiné Libéré', 'url': 'https://www.ledauphine.com/faits-divers', 'base': 'https://www.ledauphine.com', 'departement': 'Isère', 'categorie': 'local'},
    
    # === LILLE / HAUTS-DE-FRANCE ===
    {'nom': 'La Voix du Nord', 'url': 'https://www.lavoixdunord.fr/faits-divers', 'base': 'https://www.lavoixdunord.fr', 'departement': 'Nord', 'categorie': 'local'},
    {'nom': 'Nord Éclair', 'url': 'https://www.nordeclair.fr/faits-divers', 'base': 'https://www.nordeclair.fr', 'departement': 'Nord', 'categorie': 'local'},
    {'nom': 'L\'Observateur du Douaisis', 'url': 'https://www.observateurdouaisis.fr/faits-divers/', 'base': 'https://www.observateurdouaisis.fr', 'departement': 'Nord', 'categorie': 'local'},
    
    # === BORDEAUX / NOUVELLE-AQUITAINE ===
    {'nom': 'Sud Ouest', 'url': 'https://www.sudouest.fr/faits-divers', 'base': 'https://www.sudouest.fr', 'departement': 'Gironde', 'categorie': 'local'},
    {'nom': 'Bordeaux Gazette', 'url': 'https://bordeaux-gazette.com/justice/', 'base': 'https://bordeaux-gazette.com', 'departement': 'Gironde', 'categorie': 'local'},
    {'nom': 'Charente Libre', 'url': 'https://www.charentelibre.fr/faits-divers', 'base': 'https://www.charentelibre.fr', 'departement': 'Charente', 'categorie': 'local'},
    
    # === TOULOUSE / OCCITANIE ===
    {'nom': 'La Dépêche', 'url': 'https://www.ladepeche.fr/faits-divers/', 'base': 'https://www.ladepeche.fr', 'departement': 'Haute-Garonne', 'categorie': 'local'},
    {'nom': 'Le Journal Toulousain', 'url': 'https://lejournaltoulousain.fr/categorie/faits-divers-toulouse/', 'base': 'https://lejournaltoulousain.fr', 'departement': 'Haute-Garonne', 'categorie': 'local'},
    {'nom': 'Midi Libre', 'url': 'https://www.midilibre.fr/faits-divers', 'base': 'https://www.midilibre.fr', 'departement': 'Hérault', 'categorie': 'local'},
    
    # === NANTES / PAYS DE LA LOIRE ===
    {'nom': 'Ouest-France', 'url': 'https://www.ouest-france.fr/faits-divers/', 'base': 'https://www.ouest-france.fr', 'departement': 'Loire-Atlantique', 'categorie': 'local'},
    {'nom': 'Presse Océan', 'url': 'https://www.presseocean.fr/faits-divers', 'base': 'https://www.presseocean.fr', 'departement': 'Loire-Atlantique', 'categorie': 'local'},
    {'nom': 'Le Courrier de l\'Ouest', 'url': 'https://www.courrierdelouest.fr/faits-divers', 'base': 'https://www.courrierdelouest.fr', 'departement': 'Maine-et-Loire', 'categorie': 'local'},
    
    # === STRASBOURG / GRAND EST ===
    {'nom': 'Dernières Nouvelles d\'Alsace', 'url': 'https://www.dna.fr/faits-divers', 'base': 'https://www.dna.fr', 'departement': 'Bas-Rhin', 'categorie': 'local'},
    {'nom': 'L\'Alsace', 'url': 'https://www.lalsace.fr/faits-divers', 'base': 'https://www.lalsace.fr', 'departement': 'Haut-Rhin', 'categorie': 'local'},
    {'nom': 'Le Républicain Lorrain', 'url': 'https://www.republicain-lorrain.fr/faits-divers', 'base': 'https://www.republicain-lorrain.fr', 'departement': 'Moselle', 'categorie': 'local'},
    
    # === RENNES / BRETAGNE ===
    {'nom': 'Le Télégramme', 'url': 'https://www.letelegramme.fr/faits-divers', 'base': 'https://www.letelegramme.fr', 'departement': 'Finistère', 'categorie': 'local'},
    {'nom': 'Ouest-France Rennes', 'url': 'https://www.ouest-france.fr/bretagne/faits-divers/', 'base': 'https://www.ouest-france.fr', 'departement': 'Ille-et-Vilaine', 'categorie': 'local'},
    
    # === CLERMONT-FERRAND / AUVERGNE ===
    {'nom': 'La Montagne', 'url': 'https://www.lamontagne.fr/faits-divers', 'base': 'https://www.lamontagne.fr', 'departement': 'Puy-de-Dôme', 'categorie': 'local'},
    
    # === ORLÉANS / CENTRE-VAL DE LOIRE ===
    {'nom': 'La République du Centre', 'url': 'https://www.larep.fr/faits-divers', 'base': 'https://www.larep.fr', 'departement': 'Loiret', 'categorie': 'local'},
    
    # === DIJON / BOURGOGNE ===
    {'nom': 'Le Bien Public', 'url': 'https://www.bienpublic.com/faits-divers', 'base': 'https://www.bienpublic.com', 'departement': 'Côte-d\'Or', 'categorie': 'local'},
    
    # === LIMOGES / NOUVELLE-AQUITAINE ===
    {'nom': 'Le Populaire du Centre', 'url': 'https://www.lepopulaire.fr/faits-divers', 'base': 'https://www.lepopulaire.fr', 'departement': 'Haute-Vienne', 'categorie': 'local'},
    
    # === POLICE / GENDARMERIE OFFICIAL ===
    {'nom': 'Police Nationale', 'url': 'https://www.police-nationale.interieur.gouv.fr/Actualites', 'base': 'https://www.police-nationale.interieur.gouv.fr', 'departement': 'Paris', 'categorie': 'official'},
    {'nom': 'Gendarmerie Nationale', 'url': 'https://www.gendarmerie.interieur.gouv.fr/actu', 'base': 'https://www.gendarmerie.interieur.gouv.fr', 'departement': 'Paris', 'categorie': 'official'},
]

# Départements français (101 départements métropolitains et d'outre-mer)
DEPARTEMENTS_FRANCE = [
    'Paris', 'Bouches-du-Rhône', 'Nord', 'Rhône', 'Haute-Garonne', 'Gironde', 'Alpes-Maritimes',
    'Loire-Atlantique', 'Var', 'Hérault', 'Seine-Maritime', 'Isère', 'Puy-de-Dôme', 'Finistère',
    'Morbihan', 'Ille-et-Vilaine', 'Côtes-d\'Armor', 'Bas-Rhin', 'Haut-Rhin', 'Moselle', 'Meurthe-et-Moselle',
    'Pas-de-Calais', 'Calvados', 'Manche', 'Orne', 'Eure', 'Yvelines', 'Hauts-de-Seine', 'Seine-Saint-Denis',
    'Val-de-Marne', 'Val-d\'Oise', 'Essonne', 'Seine-et-Marne', 'Somme', 'Aisne', 'Oise', 'Marne',
    'Aube', 'Haute-Marne', 'Ardennes', 'Meuse', 'Vosges', 'Doubs', 'Jura', 'Haute-Saône', 'Territoire de Belfort',
    'Savoie', 'Haute-Savoie', 'Ain', 'Ardèche', 'Drôme', 'Vaucluse', 'Gard', 'Lozère', 'Aveyron', 'Lot',
    'Tarn', 'Tarn-et-Garonne', 'Lot-et-Garonne', 'Landes', 'Pyrénées-Atlantiques', 'Hautes-Pyrénées', 'Gers',
    'Haute-Garonne', 'Ariège', 'Pyrénées-Orientales', 'Aude', 'Corse-du-Sud', 'Haute-Corse', 'France'
]

# ============================================================================
# PALABRAS CLAVE PARA DETECCIÓN DE CRÍMENES (Francia)
# ============================================================================

KEYWORDS_CRIME = [
    # Drug trafficking and seizures (trafic de drogue)
    'drogue', 'cocaïne', 'héroïne', 'cannabis', 'weed', 'méthamphétamine', 'ecstasy', 'mdma',
    'benzodiazépines', 'oxycodone', 'fentanyl', 'trafic', 'saisie', 'kilos', 'stups', 'stupéfiants',
    'cartel', 'narco', 'dealer', 'deal', 'go-fast', 'résine', 'herbe', 'shit',
    
    # Gang violence and feuds (violence des gangs)
    'gang', 'rivalité', 'règlement de comptes', 'guerre des gangs', 'cité', 'quartier',
    'bande', 'caïd', 'narcobanditisme', 'fusillade', 'tir', 'kalachnikov',
    
    # Shootings and murders (fusillades et meurtres)
    'fusillade', 'meurtre', 'homicide', 'tué', 'mort', 'corps retrouvé', 'mort suspecte',
    'assassinat', 'victime', 'balles', 'arme à feu', 'flingue',
    
    # Assaults and violent crimes (agressions)
    'agression', 'violence', 'bagarre', 'rixe', 'blessé', 'hospitalisé', 'coups', 'poignardé',
    'attaque', 'braquage', 'vol à main armée', 'violeur', 'viol',
    
    # Weapons (armes)
    'arme', 'pistolet', 'fusil', 'kalachnikov', 'revolver', 'couteau', 'lame', 'machette',
    'grenade', 'explosif', 'munition',
    
    # Police / Gendarmerie operations
    'police', 'gendarmerie', 'garde à vue', 'arrestation', 'interpellation', 'mandat de dépôt',
    'opération', 'perquisition', 'enquête', 'cavale', 'évasion', 'prison', 'juge', 'tribunal',
    'procureur', 'comparution', 'condamnation', 'prison ferme',
    
    # Organized crime (crime organisé)
    'mafia', 'crime organisé', 'blanchiment', 'extorsion', 'traite', 'proxénétisme',
    'cambriolage', 'vol', 'recel', 'escroquerie', 'corruption',
    
    # Terrorism (terrorisme)
    'terrorisme', 'djihad', 'attentat', 'radicalisation', 'daech', 'islamiste',
    
    # Corsican mafia / specific
    'mafia corse', 'brigade criminelle', 'milieu corse', 'gang du petit bar',
    
    # Other crime related
    'scène de crime', 'enquêteurs', 'témoin', 'suspect', 'avis de recherche', 'alerte'
]

# ============================================================================
# TIPOS DE CRIMEN CON ICONOS Y COLORES
# ============================================================================

TIPOS_CRIMEN = {
    'drogue': {'icono': '💊', 'color': '#8b0000', 'nom': 'Trafic de Drogue', 'es': 'Tráfico de Drogas', 'it': 'Traffico di Droga'},
    'violence_gangs': {'icono': '🔫', 'color': '#ff0000', 'nom': 'Violence des Gangs', 'es': 'Violencia de Bandas', 'it': 'Violenza di Bandee'},
    'meurtre': {'icono': '💀', 'color': '#000000', 'nom': 'Meurtre/Homicide', 'es': 'Asesinato/Homicidio', 'it': 'Omicidio'},
    'agression': {'icono': '👊', 'color': '#cc6600', 'nom': 'Agression', 'es': 'Agresión', 'it': 'Aggressione'},
    'vol': {'icono': '💰', 'color': '#8b6b00', 'nom': 'Vol/Braquage', 'es': 'Robo/Hurto', 'it': 'Furto/Rapina'},
    'crime_organise': {'icono': '🕴️', 'color': '#4b0082', 'nom': 'Crime Organisé', 'es': 'Crimen Organizado', 'it': 'Crimine Organizzato'},
    'police_op': {'icono': '👮', 'color': '#0066cc', 'nom': 'Opération Police', 'es': 'Operación Policía', 'it': 'Operazione Polizia'},
    'arme': {'icono': '🔪', 'color': '#990000', 'nom': 'Délit avec Arme', 'es': 'Delito con Arma', 'it': 'Reato con Arma'},
    'terrorisme': {'icono': '💣', 'color': '#ff6600', 'nom': 'Terrorisme', 'es': 'Terrorismo', 'it': 'Terrorismo'},
    'autre': {'icono': '❓', 'color': '#666666', 'nom': 'Autre Crime', 'es': 'Otro Crimen', 'it': 'Altro Crimine'}
}

# ============================================================================
# CLASE GESTOR DE DATOS
# ============================================================================

class GestionnaireDonnees:
    """Gestor principal de la base de datos de incidentes"""
    
    def __init__(self):
        self.archivo = ARCHIVO_DATOS
        self.datos = self.charger()
        self.lock = Lock()
    
    def charger(self):
        """Carga los datos desde el archivo JSON"""
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                cprint(f"⚠️ Erreur chargement données: {e}", 'yellow')
                return {'incidents': [], 'derniere_mise_a_jour': None, 'statistiques_historiques': {}}
        return {'incidents': [], 'derniere_mise_a_jour': None, 'statistiques_historiques': {}}
    
    def sauvegarder(self):
        """Guarda los datos en el archivo JSON"""
        with self.lock:
            self.datos['derniere_mise_a_jour'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Crear backup antes de guardar
            if os.path.exists(self.archivo):
                try:
                    with open(ARCHIVO_BACKUP, 'w', encoding='utf-8') as f:
                        json.dump(self.datos, f, indent=2, ensure_ascii=False)
                except:
                    pass
            
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
    
    def ajouter_incidents(self, nouveaux):
        """Agrega nuevos incidentes evitando duplicados"""
        if not nouveaux:
            return 0
        
        with self.lock:
            ids_existants = {inc['id'] for inc in self.datos['incidents']}
            compteur = 0
            
            for n in nouveaux:
                if n['id'] not in ids_existants:
                    self.datos['incidents'].append(n)
                    ids_existants.add(n['id'])
                    compteur += 1
            
            if compteur > 0:
                # Actualizar estadísticas históricas
                self._actualiser_historiques(nouveaux)
                self.sauvegarder()
            
            return compteur
    
    def _actualiser_historiques(self, nouveaux):
        """Actualiza las estadísticas históricas"""
        historiques = self.datos.get('statistiques_historiques', {})
        
        for inc in nouveaux:
            date = inc.get('date', '')
            if date and len(date) >= 7:
                mois = date[:7]
                type_crime = inc.get('type', 'autre')
                departement = inc.get('departement', 'Inconnu')
                
                if mois not in historiques:
                    historiques[mois] = {'total': 0, 'types': {}, 'departements': {}}
                
                historiques[mois]['total'] += 1
                historiques[mois]['types'][type_crime] = historiques[mois]['types'].get(type_crime, 0) + 1
                historiques[mois]['departements'][departement] = historiques[mois]['departements'].get(departement, 0) + 1
        
        self.datos['statistiques_historiques'] = historiques
    
    def detecter_type(self, texte):
        """Detecta el tipo de crimen basado en el texto"""
        tl = texte.lower()
        
        # Détection de drogue
        if any(p in tl for p in ['drogue', 'cocaïne', 'héroïne', 'cannabis', 'weed', 'meth', 'ecstasy', 'trafic', 'saisie', 'stups', 'kilos']):
            return 'drogue'
        
        # Détection de violence de gangs
        if any(p in tl for p in ['gang', 'rivalité', 'règlement de comptes', 'caïd', 'narcobanditisme']):
            return 'violence_gangs'
        
        # Détection de meurtres
        if any(p in tl for p in ['meurtre', 'homicide', 'tué', 'assassinat', 'corps retrouvé']):
            return 'meurtre'
        
        # Détection d'agressions
        if any(p in tl for p in ['agression', 'violence', 'bagarre', 'rixe', 'blessé', 'coups', 'poignardé']):
            return 'agression'
        
        # Détection de vols
        if any(p in tl for p in ['vol', 'braquage', 'cambriolage', 'recel']):
            return 'vol'
        
        # Détection de crime organisé
        if any(p in tl for p in ['crime organisé', 'blanchiment', 'extorsion', 'mafia corse', 'mafia']):
            return 'crime_organise'
        
        # Détection d'opérations policières
        if any(p in tl for p in ['police', 'gendarmerie', 'arrestation', 'interpellation', 'perquisition', 'garde à vue']):
            return 'police_op'
        
        # Détection d'armes
        if any(p in tl for p in ['arme', 'pistolet', 'fusil', 'couteau', 'kalachnikov', 'revolver']):
            return 'arme'
        
        # Détection de terrorisme
        if any(p in tl for p in ['terrorisme', 'attentat', 'djihad', 'daech', 'radicalisation']):
            return 'terrorisme'
        
        return 'autre'
    
    def statistiques(self, incidents=None):
        """Calcula estadísticas completas de los incidentes"""
        if incidents is None:
            incidents = self.datos['incidents']
        
        stats = {
            'total': len(incidents),
            'departements': defaultdict(int),
            'types': defaultdict(int),
            'sources': defaultdict(int),
            'derniers_7j': 0,
            'derniers_30j': 0,
            'derniers_90j': 0,
            'tendance': defaultdict(int),
            'tendance_types': defaultdict(lambda: defaultdict(int)),
            'top_keywords': defaultdict(int),
            'incidents_par_heure': defaultdict(int),
            'incidents_par_jour_semaine': defaultdict(int)
        }
        
        aujourd_hui = datetime.now()
        il_y_a_7j = (aujourd_hui - timedelta(days=7)).strftime('%Y-%m-%d')
        il_y_a_30j = (aujourd_hui - timedelta(days=30)).strftime('%Y-%m-%d')
        il_y_a_90j = (aujourd_hui - timedelta(days=90)).strftime('%Y-%m-%d')
        
        for inc in incidents:
            # Départements
            if inc.get('departement'):
                stats['departements'][inc['departement']] += 1
            
            # Types
            if inc.get('type'):
                stats['types'][inc['type']] += 1
            
            # Sources
            if inc.get('source'):
                stats['sources'][inc['source']] += 1
            
            # Dates
            date_str = inc.get('date', '')
            if date_str:
                if date_str >= il_y_a_7j:
                    stats['derniers_7j'] += 1
                if date_str >= il_y_a_30j:
                    stats['derniers_30j'] += 1
                if date_str >= il_y_a_90j:
                    stats['derniers_90j'] += 1
                
                if len(date_str) >= 7:
                    mois = date_str[:7]
                    stats['tendance'][mois] += 1
                    
                    if inc.get('type'):
                        stats['tendance_types'][mois][inc['type']] += 1
                
                # Analyse par jour de semaine
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    stats['incidents_par_jour_semaine'][date_obj.strftime('%A')] += 1
                except:
                    pass
            
            # Extraire mots-clés du titre
            titre = inc.get('titre', '').lower()
            for keyword in KEYWORDS_CRIME[:50]:
                if keyword in titre:
                    stats['top_keywords'][keyword] += 1
        
        return stats
    
    def evolution_mensuelle(self):
        """Retorna la evolución mensual de incidentes"""
        mois = {}
        for inc in self.datos['incidents']:
            if inc.get('date') and len(inc['date']) >= 7:
                m = inc['date'][:7]
                mois[m] = mois.get(m, 0) + 1
        return dict(sorted(mois.items()))
    
    def nettoyer_doublons(self):
        """Elimina incidentes duplicados de la base de datos"""
        with self.lock:
            ids_vus = set()
            incidents_propres = []
            doublons = 0
            
            for inc in self.datos['incidents']:
                if inc['id'] not in ids_vus:
                    ids_vus.add(inc['id'])
                    incidents_propres.append(inc)
                else:
                    doublons += 1
            
            self.datos['incidents'] = incidents_propres
            
            if doublons > 0:
                self.sauvegarder()
            
            return doublons
    
    def exporter_json(self):
        """Exporta los datos completos en formato JSON"""
        return json.dumps(self.datos, indent=2, ensure_ascii=False)
    
    def exporter_csv(self):
        """Exporta los incidentes en formato CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Titre', 'Date', 'Département', 'Type', 'Source'])
        
        for inc in self.datos['incidents']:
            writer.writerow([
                inc['id'],
                inc['titre'].replace('\n', ' ').replace('\r', ''),
                inc['date'],
                inc.get('departement', ''),
                inc.get('type', ''),
                inc['source']
            ])
        
        return output.getvalue()
    
    def exporter_html(self):
        """Exporta los datos en formato HTML para reportes"""
        stats = self.statistiques()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AIDE-FRANCE - Rapport Criminel France</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #0a0a0a; color: #e0e0e0; }}
        h1 {{ color: #ff4444; }}
        .stats {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #ff4444; }}
        .stat-number {{ font-size: 2em; color: #ff4444; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
        th {{ background: #333; color: #ff4444; }}
        tr:hover {{ background: #1a1a1a; }}
        .footer {{ text-align: center; margin-top: 30px; padding: 15px; background: #1a1a1a; color: #666; }}
    </style>
</head>
<body>
    <h1>🔪 AIDE-FRANCE - Rapport Criminel France</h1>
    <p>Généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <div class="stat-card"><div>Total Incidents</div><div class="stat-number">{stats['total']}</div></div>
        <div class="stat-card"><div>7 Derniers Jours</div><div class="stat-number">{stats['derniers_7j']}</div></div>
        <div class="stat-card"><div>30 Derniers Jours</div><div class="stat-number">{stats['derniers_30j']}</div></div>
        <div class="stat-card"><div>Sources</div><div class="stat-number">{len(stats['sources'])}</div></div>
    </div>
    
    <h2>Top Départements</h2>
    <table>
        <tr><th>Département</th><th>Incidents</th><th>%</th></tr>"""
        
        for dept, count in sorted(stats['departements'].items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            html += f"<tr><td>{dept}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
        
        html += """</table>
    
    <h2>Types de Crime</h2>
    <table>
        <tr><th>Type</th><th>Incidents</th><th>%</th></tr>"""
        
        for crime_type, count in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            icono = TIPOS_CRIMEN.get(crime_type, {}).get('icono', '❓')
            nom = TIPOS_CRIMEN.get(crime_type, {}).get('nom', crime_type)
            html += f"<tr><td>{icono} {nom}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
        
        html += f"""</table>
    
    <h2>Incidents Récents (20 derniers)</h2>
    <table>
        <tr><th>Date</th><th>Département</th><th>Type</th><th>Titre</th><th>Source</th></tr>"""
        
        for inc in self.datos['incidents'][-20:][::-1]:
            html += f"<tr><td>{inc['date']}</td><td>{inc.get('departement', '?')}</td><td>{inc.get('type', '?')}</td><td>{inc['titre'][:100]}...</td><td>{inc['source']}</td></tr>"
        
        html += f"""
    </table>
    
    <div class="footer">
        <p>🔪 AIDE-FRANCE v{VERSION} - Plateforme de Renseignement Criminel Français</p>
        <p>Surveillance basée sur les données pour la sensibilisation à la sécurité publique</p>
    </div>
</body>
</html>"""
        
        return html

# ============================================================================
# CLASE VERIFICADOR DE FUENTES CON AUTO-DISCOVERY
# ============================================================================

class VerificateurSources:
    """Verifica fuentes y aplica auto-discovery cuando es necesario"""
    
    def __init__(self):
        self.discoverer = URLAutoDiscoverer()
        self.etat_file = ARCHIVO_ESTADO
        self.etat = self.charger_etat()
    
    def charger_etat(self):
        if os.path.exists(self.etat_file):
            try:
                with open(self.etat_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def sauvegarder_etat(self):
        with open(self.etat_file, 'w', encoding='utf-8') as f:
            json.dump(self.etat, f, indent=2)
    
    def verifier_source(self, source, appliquer_discovery=True):
        """Verifica una sola fuente, opcionalmente aplicando auto-discovery"""
        nom = source['nom']
        
        # Verificar usando la URL actual
        for tentative in range(MAX_INTENTOS):
            try:
                headers = {
                    'User-Agent': get_random_ua(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
                
                r = requests.get(source['url'], timeout=TIMEOUT, headers=headers, allow_redirects=True)
                
                if r.status_code == 200:
                    source['actif'] = True
                    return source, True
                else:
                    time.sleep(get_random_delay())
            except Exception as e:
                time.sleep(get_random_delay())
        
        # Si falló y está habilitado el auto-discovery, buscar URL alternativa
        if appliquer_discovery:
            nouvelle_url = self.discoverer.discover_url(source)
            if nouvelle_url != source['url']:
                source['url'] = nouvelle_url
                # Probar la nueva URL
                for tentative in range(MAX_INTENTOS):
                    try:
                        headers = {'User-Agent': get_random_ua()}
                        r = requests.get(nouvelle_url, timeout=TIMEOUT, headers=headers)
                        if r.status_code == 200:
                            source['actif'] = True
                            return source, True
                    except:
                        continue
        
        source['actif'] = False
        return source, False
    
    def verifier_toutes(self, sources, montrer_progres=True):
        """Verifica todas las fuentes con barra de progreso"""
        cprint(f"\n{'='*80}", 'red', bold=True)
        cprint(f"🔍 {t('verificando')}", 'red', bold=True, bg=True)
        cprint(f"{'='*80}", 'red', bold=True)
        
        verifiees = []
        actives = 0
        auto_decouvertes = 0
        total = len(sources)
        
        for i, source in enumerate(sources, 1):
            if montrer_progres:
                pourcentage = (i / total) * 100
                barre_len = 30
                remplie = int(barre_len * i / total)
                barre = '█' * remplie + '░' * (barre_len - remplie)
                sys.stdout.write(f"\r   🔪 Progrès: [{barre}] {i}/{total} ({pourcentage:.1f}%)")
                sys.stdout.flush()
            
            cprint(f"\n📰 [{i}/{total}] {source['nom']}", 'yellow', bold=True, end=' ')
            
            url_originale = source['url']
            source_verifiee, succes = self.verifier_source(source.copy(), appliquer_discovery=True)
            
            if succes:
                actives += 1
                if source_verifiee['url'] != url_originale:
                    auto_decouvertes += 1
                    cprint(f"✅ OK (Auto-découverte)", 'green')
                else:
                    cprint(f"✅ OK", 'green')
            else:
                cprint(f"❌ INACTIVE", 'red')
            
            verifiees.append(source_verifiee)
            time.sleep(0.2)
        
        print()  # Nueva línea después de la barra
        
        cprint(f"\n{'='*80}", 'green', bold=True)
        cprint(f"📊 RÉSULTATS:", 'green', bold=True)
        cprint(f"   Sources actives: {actives} de {total}", 'white')
        cprint(f"   Auto-découverte appliquée: {auto_decouvertes} URLs trouvées", 'cyan')
        cprint(f"{'='*80}", 'green', bold=True)
        
        # Guardar estado para futuras ejecuciones
        self.sauvegarder_etat()
        
        return verifiees

# ============================================================================
# CLASE EXTRACTOR DE NOTICIAS
# ============================================================================

class ExtracteurActualites:
    """Extrae noticias de crímenes de las fuentes verificadas"""
    
    def __init__(self, sources):
        self.sources = sources
        self.session = self._creer_session()
    
    def _creer_session(self):
        """Crea una sesión HTTP con retry y adaptadores"""
        session = requests.Session()
        retry = Retry(
            total=2,
            read=2,
            connect=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def fetch_url(self, url):
        """Obtiene una URL con reintentos y headers rotativos"""
        for tentative in range(MAX_INTENTOS):
            try:
                headers = {
                    'User-Agent': get_random_ua(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                response = self.session.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too many requests
                    time.sleep(get_random_delay() * 2)
                else:
                    time.sleep(get_random_delay())
                    
            except requests.exceptions.Timeout:
                time.sleep(get_random_delay())
            except requests.exceptions.ConnectionError:
                time.sleep(get_random_delay())
            except Exception:
                time.sleep(get_random_delay())
        
        return None
    
    def extraire_de_source(self, source, pages=PAGINAS_BUSQUEDA):
        """Extrae incidentes de una fuente específica"""
        incidents = []
        url_base = source['url']
        
        for page in range(1, pages + 1):
            # Construir URL de paginación
            if page == 1:
                url = url_base
            else:
                # Probar diferentes patrones de paginación
                patrons = [
                    url_base.rstrip('/') + f'/page/{page}/',
                    url_base.rstrip('/') + f'?page={page}',
                    url_base.rstrip('/') + f'&page={page}',
                    url_base.rstrip('/') + f'/pagina/{page}',
                    url_base.rstrip('/') + f'?p={page}',
                    url_base.rstrip('/') + f'/index_{page}.html'
                ]
                url = None
                for patron in patrons:
                    try:
                        test_response = self.fetch_url(patron)
                        if test_response:
                            url = patron
                            break
                    except:
                        continue
                
                if not url:
                    break
            
            try:
                cprint(f"   📄 Page {page}... ", 'gray', end='')
                response = self.fetch_url(url)
                
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Buscar elementos que contengan noticias
                    elements = []
                    
                    # Articles
                    elements.extend(soup.find_all('article'))
                    elements.extend(soup.find_all('div', class_=re.compile(r'article|story|post|news|entry', re.I)))
                    elements.extend(soup.find_all('li', class_=re.compile(r'article|story|post|news', re.I)))
                    
                    # Headers (souvent contiennent des titres)
                    elements.extend(soup.find_all(['h1', 'h2', 'h3', 'h4']))
                    
                    # Links (peuvent contenir des titres d'actualités)
                    elements.extend(soup.find_all('a', href=True))
                    
                    trouves_page = 0
                    gestionnaire_temp = GestionnaireDonnees()
                    
                    for elem in elements[:40]:  # Limitar por página
                        texte = elem.get_text().strip()
                        
                        if len(texte) < 40:
                            continue
                        
                        texte_lower = texte.lower()
                        
                        # Vérifier si contient des mots-clés de crime
                        if any(mot in texte_lower for mot in KEYWORDS_CRIME):
                            # Extraire date si disponible
                            date_elem = soup.find('time')
                            date = datetime.now().strftime('%Y-%m-%d')
                            
                            if date_elem and date_elem.get('datetime'):
                                date = date_elem.get('datetime')[:10]
                            elif date_elem and date_elem.get('content'):
                                date = date_elem.get('content')[:10]
                            else:
                                # Rechercher motifs de date dans le texte
                                pattern_date = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}'
                                match = re.search(pattern_date, texte)
                                if match:
                                    date = match.group()[:10]
                            
                            # Déterminer département
                            departement = source['departement']
                            for d in DEPARTEMENTS_FRANCE:
                                if d.lower() in texte_lower:
                                    departement = d
                                    break
                            
                            type_crime = gestionnaire_temp.detecter_type(texte)
                            
                            incidents.append({
                                'id': hashlib.md5(texte.encode()).hexdigest()[:16],
                                'titre': texte[:500],
                                'date': date,
                                'departement': departement,
                                'type': type_crime,
                                'source': source['nom']
                            })
                            trouves_page += 1
                    
                    cprint(f"✓ {trouves_page} trouvés", 'green')
                    
                    # Si no encontramos nada en 2 páginas consecutivas, salir
                    if trouves_page == 0 and page > 2:
                        break
                else:
                    cprint(f"✗ Pas de réponse", 'red')
                    break
                    
            except Exception as e:
                cprint(f"✗ Erreur: {str(e)[:30]}", 'red')
            
            time.sleep(get_random_delay())
        
        return incidents
    
    def extraire_toutes(self, pages=PAGINAS_BUSQUEDA):
        """Extrae incidentes de todas las fuentes activas"""
        cprint(f"\n{'='*80}", 'red', bold=True)
        cprint(f"🔪 AIDE-FRANCE - ANALYSE DE LA FRANCE", 'red', bold=True, bg=True)
        cprint(f"{'='*80}", 'red', bold=True)
        
        toutes_actualites = []
        sources_actives = [s for s in self.sources if s.get('actif', True)]
        total_actives = len(sources_actives)
        
        if total_actives == 0:
            cprint(f"\n⚠️ {t('sin_datos')}", 'yellow')
            return toutes_actualites
        
        for idx, source in enumerate(sources_actives, 1):
            # Barre de progression
            pourcentage = (idx / total_actives) * 100
            barre_len = 40
            remplie = int(barre_len * idx / total_actives)
            barre = '█' * remplie + '░' * (barre_len - remplie)
            sys.stdout.write(f"\r   🔪 Analyse: [{barre}] {idx}/{total_actives} ({pourcentage:.1f}%)")
            sys.stdout.flush()
            
            cprint(f"\n\n📰 {source['nom']}", 'yellow', bold=True)
            cprint(f"   📍 Département: {source['departement']} | 🌐 URL: {source['url'][:50]}...", 'gray', dim=True)
            
            incidents_source = self.extraire_de_source(source, pages)
            toutes_actualites.extend(incidents_source)
            cprint(f"   📊 Total cette source: {len(incidents_source)} incidents", 'cyan')
        
        print()  # Línea nueva después de la barra
        
        # Éliminer les doublons par ID
        incidents_uniques = {}
        for actualite in toutes_actualites:
            if actualite['id'] not in incidents_uniques:
                incidents_uniques[actualite['id']] = actualite
        
        resultat = list(incidents_uniques.values())
        
        cprint(f"\n{'='*80}", 'green', bold=True)
        cprint(f"🔪 RÉSULTAT FINAL:", 'green', bold=True)
        cprint(f"   Incidents trouvés: {len(resultat)}", 'white')
        cprint(f"   Sources actives: {total_actives}", 'white')
        cprint(f"   Auto-découverte appliquée automatiquement", 'cyan')
        cprint(f"{'='*80}", 'green', bold=True)
        
        return resultat

# ============================================================================
# INTERFAZ WEB CON GRÁFICOS
# ============================================================================

app = Flask(__name__)
gestionnaire_global = None
sources_global = None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔪 AIDE-FRANCE - Renseignement Criminel France</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 100%);
            color: #e0e0e0;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        /* Header avec animation */
        .header {
            background: linear-gradient(135deg, #1a0a0a, #2a0a0a);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            border: 1px solid #ff3333;
            box-shadow: 0 0 30px rgba(255,0,0,0.2);
            animation: glow 2s infinite alternate;
        }
        
        @keyframes glow {
            from { box-shadow: 0 0 10px rgba(255,0,0,0.2); }
            to { box-shadow: 0 0 30px rgba(255,0,0,0.5); }
        }
        
        h1 {
            font-size: 3em;
            color: #ff4444;
            letter-spacing: 3px;
            text-shadow: 0 0 10px #ff0000;
            animation: pulse 1.5s infinite alternate;
        }
        
        @keyframes pulse {
            from { text-shadow: 0 0 5px #ff0000; }
            to { text-shadow: 0 0 20px #ff0000; }
        }
        
        .version-badge {
            background: #1a1a1a;
            color: #ff8888;
            padding: 5px 20px;
            border-radius: 30px;
            display: inline-block;
            margin-top: 10px;
            font-family: monospace;
            border: 1px solid #ff4444;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #111, #1a1a1a);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border-left: 5px solid #ff4444;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(255,68,68,0.2);
        }
        
        .stat-number {
            font-size: 3em;
            color: #ff4444;
            font-weight: bold;
        }
        
        .stat-label {
            color: #888;
            margin-top: 10px;
        }
        
        /* Buttons */
        .btn {
            background: #222;
            color: #ff4444;
            border: 2px solid #ff4444;
            padding: 12px 30px;
            border-radius: 40px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background: #ff4444;
            color: #000;
            transform: scale(1.05);
            box-shadow: 0 0 15px #ff4444;
        }
        
        /* Chart containers */
        .charts-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }
        
        .chart-container {
            background: #111;
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #333;
            transition: all 0.3s ease;
        }
        
        .chart-container:hover {
            border-color: #ff4444;
            box-shadow: 0 0 15px rgba(255,68,68,0.1);
        }
        
        .chart-title {
            color: #ff6666;
            font-size: 1.3em;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        /* Filters */
        .filters {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            background: #1a1a1a;
            color: #ccc;
            border: 2px solid #333;
            padding: 10px 25px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .filter-btn:hover, .filter-btn.active {
            background: #ff4444;
            color: #000;
            border-color: #ff4444;
        }
        
        /* Incident cards */
        .incident-card {
            background: linear-gradient(135deg, #0a0a0a, #111);
            margin: 15px 0;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #ff4444;
            transition: all 0.3s ease;
        }
        
        .incident-card:hover {
            transform: translateX(10px);
            background: #1a1a1a;
        }
        
        .incident-title {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #fff;
        }
        
        .incident-meta {
            color: #888;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.85em;
        }
        
        .incident-meta span {
            background: #1a1a1a;
            padding: 5px 10px;
            border-radius: 20px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            background: #111;
            border-radius: 15px;
            color: #666;
            border-top: 1px solid #333;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .charts-row { grid-template-columns: 1fr; }
            h1 { font-size: 1.8em; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #1a1a1a; }
        ::-webkit-scrollbar-thumb { background: #ff4444; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: #ff6666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔪 AIDE-FRANCE</h1>
            <div class="version-badge">v{{ version }} · Renseignement Criminel France · Port {{ port }}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total }}</div>
                <div class="stat-label">📊 TOTAL INCIDENTS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.derniers_7j }}</div>
                <div class="stat-label">⚡ DERNIERS 7 JOURS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.derniers_30j }}</div>
                <div class="stat-label">🔥 DERNIERS 30 JOURS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ sources_actives }}</div>
                <div class="stat-label">📰 SOURCES ACTIVES</div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <form action="/actualiser" method="post" style="display: inline;">
                <button class="btn">🔄 ACTUALISER</button>
            </form>
            <a href="/exporter/json" class="btn">📥 JSON</a>
            <a href="/exporter/csv" class="btn">📥 CSV</a>
            <a href="/exporter/html" class="btn">📄 RAPPORT HTML</a>
        </div>
        
        <div class="filters">
            <a href="/" class="filter-btn {% if filtre == 'tout' %}active{% endif %}">📅 TOUS</a>
            <a href="/filtre/7j" class="filter-btn {% if filtre == '7j' %}active{% endif %}">⚡ 7 JOURS</a>
            <a href="/filtre/30j" class="filter-btn {% if filtre == '30j' %}active{% endif %}">🔥 30 JOURS</a>
            <a href="/filtre/90j" class="filter-btn {% if filtre == '90j' %}active{% endif %}">📊 90 JOURS</a>
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <div class="chart-title">📍 INCIDENTS PAR DÉPARTEMENT</div>
                <canvas id="deptChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">🔪 RÉPARTITION PAR TYPE DE CRIME</div>
                <canvas id="typeChart"></canvas>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <div class="chart-title">📈 TENDANCE MENSUELLE</div>
                <canvas id="trendChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">📰 TOP SOURCES</div>
                <canvas id="sourcesChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🔪 DERNIERS INCIDENTS ({{ incidents|length }})</div>
            {% for inc in incidents[:25] %}
            <div class="incident-card">
                <div class="incident-title">{{ inc.titre }}</div>
                <div class="incident-meta">
                    <span>📍 {{ inc.departement or '?' }}</span>
                    <span>📅 {{ inc.date }}</span>
                    <span>📰 {{ inc.source }}</span>
                    <span>🔪 {{ inc.type|upper }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>🔪 AIDE-FRANCE v{{ version }} · {{ sources_actives }} SOURCES ACTIVES</p>
            <p style="font-size:0.8em;">"Un grand pouvoir implique de grandes responsabilités" - Spider-Man</p>
            <p style="font-size:0.7em; margin-top:10px;">Surveillance basée sur les données pour la sensibilisation à la sécurité publique</p>
        </div>
    </div>
    
    <script>
        // Graphique départements
        const deptCtx = document.getElementById('deptChart').getContext('2d');
        new Chart(deptCtx, {
            type: 'bar',
            data: {
                labels: {{ dept_labels|tojson }},
                datasets: [{
                    label: 'Incidents',
                    data: {{ dept_data|tojson }},
                    backgroundColor: 'rgba(255, 68, 68, 0.7)',
                    borderColor: '#ff4444',
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: '#ccc' } },
                    tooltip: { backgroundColor: '#111', titleColor: '#ff4444', bodyColor: '#ccc' }
                },
                scales: {
                    y: { ticks: { color: '#ccc' }, grid: { color: '#333' } },
                    x: { ticks: { color: '#ccc', rotation: 45 } }
                }
            }
        });
        
        // Graphique types
        const typeCtx = document.getElementById('typeChart').getContext('2d');
        new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: {{ type_labels|tojson }},
                datasets: [{
                    data: {{ type_data|tojson }},
                    backgroundColor: ['#8b0000', '#ff0000', '#000000', '#cc6600', '#8b6b00', '#4b0082', '#0066cc', '#990000', '#ff6600', '#666666'],
                    borderWidth: 2,
                    borderColor: '#1a1a1a'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#ccc' } },
                    tooltip: { backgroundColor: '#111', titleColor: '#ff4444' }
                }
            }
        });
        
        // Graphique tendance
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: {{ trend_labels|tojson }},
                datasets: [{
                    label: 'Incidents par mois',
                    data: {{ trend_data|tojson }},
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#ff4444',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#ccc' } },
                    tooltip: { backgroundColor: '#111', titleColor: '#ff4444' }
                },
                scales: {
                    y: { ticks: { color: '#ccc' }, grid: { color: '#333' } },
                    x: { ticks: { color: '#ccc', rotation: 45 } }
                }
            }
        });
        
        // Graphique sources
        const sourcesCtx = document.getElementById('sourcesChart').getContext('2d');
        new Chart(sourcesCtx, {
            type: 'bar',
            data: {
                labels: {{ sources_labels|tojson }},
                datasets: [{
                    label: 'Articles',
                    data: {{ sources_data|tojson }},
                    backgroundColor: 'rgba(255, 102, 102, 0.7)',
                    borderColor: '#ff6666',
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: { labels: { color: '#ccc' } },
                    tooltip: { backgroundColor: '#111', titleColor: '#ff6666' }
                },
                scales: {
                    x: { ticks: { color: '#ccc' }, grid: { color: '#333' } },
                    y: { ticks: { color: '#ccc' } }
                }
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    global gestionnaire_global, sources_global
    incidents = gestionnaire_global.datos['incidents']
    stats = gestionnaire_global.statistiques()
    
    dept_labels = list(stats['departements'].keys())
    dept_data = list(stats['departements'].values())
    type_labels = [f"{TIPOS_CRIMEN.get(t, {}).get('icono', '❓')} {t.upper()}" for t in stats['types'].keys()]
    type_data = list(stats['types'].values())
    
    trend_items = list(stats['tendance'].items())[-12:]
    trend_labels = [item[0] for item in trend_items]
    trend_data = [item[1] for item in trend_items]
    
    sources_top = dict(sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True)[:5])
    sources_labels = list(sources_top.keys())
    sources_data = list(sources_top.values())
    
    sources_actives = len([s for s in sources_global if s.get('actif', True)])
    
    return render_template_string(HTML_TEMPLATE, 
        version=VERSION, port=PUERTO, stats=stats,
        incidents=incidents[::-1], sources_actives=sources_actives, filtre='tout',
        dept_labels=dept_labels, dept_data=dept_data,
        type_labels=type_labels, type_data=type_data,
        trend_labels=trend_labels, trend_data=trend_data,
        sources_labels=sources_labels, sources_data=sources_data)

@app.route('/filtre/<periode>')
def filtre(periode):
    global gestionnaire_global, sources_global
    incidents = gestionnaire_global.datos['incidents']
    
    if periode == '7j':
        date_limite = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        incidents = [i for i in incidents if i.get('date', '') >= date_limite]
    elif periode == '30j':
        date_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        incidents = [i for i in incidents if i.get('date', '') >= date_limite]
    elif periode == '90j':
        date_limite = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        incidents = [i for i in incidents if i.get('date', '') >= date_limite]
    
    stats = gestionnaire_global.statistiques(incidents)
    sources_actives = len([s for s in sources_global if s.get('actif', True)])
    
    return render_template_string(HTML_TEMPLATE,
        version=VERSION, port=PUERTO, stats=stats,
        incidents=incidents[::-1], sources_actives=sources_actives, filtre=periode,
        dept_labels=list(stats['departements'].keys()), dept_data=list(stats['departements'].values()),
        type_labels=[f"{TIPOS_CRIMEN.get(t, {}).get('icono', '❓')} {t.upper()}" for t in stats['types'].keys()],
        type_data=list(stats['types'].values()),
        trend_labels=list(stats['tendance'].keys())[-12:], trend_data=list(stats['tendance'].values())[-12:],
        sources_labels=list(dict(sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True)[:5]).keys()),
        sources_data=list(dict(sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True)[:5]).values()))

@app.route('/actualiser', methods=['POST'])
def actualiser():
    global gestionnaire_global, sources_global
    cprint(f"\n{'='*80}", 'red', bold=True)
    cprint(f"🔪 {t('actualizando')}", 'red', bold=True, bg=True)
    cprint(f"{'='*80}", 'red', bold=True)
    
    verificateur = VerificateurSources()
    sources_verifiees = verificateur.verifier_toutes(sources_global)
    sources_global = sources_verifiees
    
    extracteur = ExtracteurActualites(sources_verifiees)
    nouvelles_actualites = extracteur.extraire_toutes(pages=PAGINAS_BUSQUEDA)
    ajoutees = gestionnaire_global.ajouter_incidents(nouvelles_actualites)
    
    cprint(f"\n{'='*80}", 'green', bold=True)
    cprint(f"✅ {ajoutees} NOUVEAUX INCIDENTS ENREGISTRÉS", 'green', bold=True, bg=True)
    cprint(f"{'='*80}", 'green', bold=True)
    
    return home()

@app.route('/exporter/json')
def exporter_json():
    global gestionnaire_global
    return Response(gestionnaire_global.exporter_json(), mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=aide_france_export.json'})

@app.route('/exporter/csv')
def exporter_csv():
    global gestionnaire_global
    return Response(gestionnaire_global.exporter_csv(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=aide_france_export.csv'})

@app.route('/exporter/html')
def exporter_html():
    global gestionnaire_global
    return Response(gestionnaire_global.exporter_html(), mimetype='text/html', headers={'Content-Disposition': 'attachment; filename=aide_france_report.html'})

# ============================================================================
# MENÚ PRINCIPAL DE TERMINAL
# ============================================================================

def afficher_menu_principal():
    """Affiche le menu principal avec design professionnel - UN SEUL ÉMOJI PAR LIGNE"""
    print(f"""
{Color.RED}╔{'═' * 70}╗{Color.RESET}
{Color.RED}║{Color.BOLD}{Color.WHITE}  🔪 {t('app_name')}{' ' * 40}{Color.RED}║{Color.RESET}
{Color.RED}╠{'═' * 70}╣{Color.RESET}
{Color.RED}║{Color.CYAN}  📊 {t('stats_total')}: {gestionnaire_global.statistiques()['total']} {t('incidentes')}{' ' * 35}{Color.RED}║{Color.RESET}
{Color.RED}║{Color.YELLOW}  📰 {t('fuentes')}: {len([s for s in sources_global if s.get('actif', True)])} de {len(sources_global)}{' ' * 36}{Color.RED}║{Color.RESET}
{Color.RED}║{Color.GREEN}  🏴 {t('condados')}: {len(gestionnaire_global.statistiques()['departements'])}{' ' * 39}{Color.RED}║{Color.RESET}
{Color.RED}╚{'═' * 70}╝{Color.RESET}

{Color.YELLOW}┌{'─' * 50}┐{Color.RESET}
{Color.YELLOW}│{Color.CYAN}  📋 {t('menu_title')}{' ' * 36}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}├{'─' * 50}┤{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [1] 🔍 {t('cmd_buscar')}{' ' * 33}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [2] 📊 {t('cmd_analisis')}{' ' * 32}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [3] 🔗 {t('cmd_conexiones')}{' ' * 30}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [4] 📈 {t('cmd_evolucion')}{' ' * 33}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [5] 🌐 {t('cmd_web')}{' ' * 37}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [6] 📰 {t('cmd_ultimos')}{' ' * 34}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [7] 📥 {t('cmd_exportar')}{' ' * 34}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [8] 🔍 {t('cmd_verificar')}{' ' * 33}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [9] 📊 {t('cmd_tipos')}{' ' * 35}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [10] 📈 {t('cmd_estadisticas')}{' ' * 28}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [11] 🧹 {t('cmd_limpiar')}{' ' * 35}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.RED}  [12] 🗑️ {t('cmd_salir')}{' ' * 37}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}└{'─' * 50}┘{Color.RESET}
""")

def menu():
    """Boucle principale du menu"""
    global gestionnaire_global, sources_global
    
    while True:
        afficher_menu_principal()
        
        option = input(f"{Color.CYAN}➤ {Color.YELLOW}Option: {Color.RESET}")
        
        if option == '1':
            cprint(f"\n🔍 {t('procesando')}", 'cyan', bold=True)
            verificateur = VerificateurSources()
            sources_global = verificateur.verifier_toutes(sources_global)
            extracteur = ExtracteurActualites(sources_global)
            nouvelles = extracteur.extraire_toutes(pages=PAGINAS_BUSQUEDA)
            ajoutees = gestionnaire_global.ajouter_incidents(nouvelles)
            cprint(f"\n✅ {ajoutees} {t('incidentes')} nouveaux enregistrés", 'green', bold=True)
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '2':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📊 {t('analisis_completo')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            
            stats = gestionnaire_global.statistiques()
            
            cprint(f"\n{Color.YELLOW}📈 STATISTIQUES GÉNÉRALES:{Color.RESET}")
            cprint(f"   Total incidents: {stats['total']}", 'white')
            cprint(f"   Derniers 7 jours: {stats['derniers_7j']}", 'white')
            cprint(f"   Derniers 30 jours: {stats['derniers_30j']}", 'white')
            cprint(f"   Derniers 90 jours: {stats['derniers_90j']}", 'white')
            
            cprint(f"\n{Color.YELLOW}📍 TOP 10 DÉPARTEMENTS:{Color.RESET}")
            for dept, quantite in sorted(stats['departements'].items(), key=lambda x: x[1], reverse=True)[:10]:
                pct = (quantite / stats['total'] * 100) if stats['total'] > 0 else 0
                barre = '█' * int(pct // 2)
                cprint(f"   {dept}: {quantite} ({pct:.1f}%) {barre}", 'cyan')
            
            cprint(f"\n{Color.YELLOW}🔪 RÉPARTITION PAR TYPE:{Color.RESET}")
            for type_crime, quantite in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
                pct = (quantite / stats['total'] * 100) if stats['total'] > 0 else 0
                icono = TIPOS_CRIMEN.get(type_crime, {}).get('icono', '❓')
                cprint(f"   {icono} {type_crime.upper()}: {quantite} ({pct:.1f}%)", 'white')
            
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '3':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"🔗 {t('conexiones')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            
            incidents = gestionnaire_global.datos['incidents'][-200:]
            groupes = defaultdict(list)
            
            for inc in incidents:
                groupes[(inc.get('type', 'autre'), inc.get('departement', 'Inconnu'))].append(inc)
            
            motifs = 0
            for (type_crime, dept), liste in groupes.items():
                if len(liste) >= 3:
                    cprint(f"\n{Color.RED}🔥 MOTIF DÉTECTÉ: {len(liste)} {type_crime.upper()} dans {dept}{Color.RESET}")
                    for inc in sorted(liste, key=lambda x: x['date'], reverse=True)[:3]:
                        cprint(f"   • {inc['date']}: {inc['titre'][:70]}...", 'gray')
                    motifs += 1
            
            if motifs == 0:
                cprint(f"\n{Color.GRAY}   Aucun motif significatif détecté.{Color.RESET}")
            
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '4':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📈 {t('evolucion_mensual')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            
            evolution = gestionnaire_global.evolution_mensuelle()
            if evolution:
                max_val = max(evolution.values())
                for mois, quantite in list(evolution.items())[-12:]:
                    barre = '█' * int((quantite / max_val) * 50) if max_val > 0 else ''
                    cprint(f"   {mois}: {quantite:3d} {barre}", 'cyan')
            else:
                cprint(f"   {Color.GRAY}Pas assez de données.{Color.RESET}")
            
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '5':
            cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
            cprint(f"   📊 Dashboard avec graphiques interactifs", 'cyan')
            cprint(f"   🔪 {t('presiona_ctrl_c')}", 'gray')
            app.run(host='127.0.0.1', port=PUERTO, debug=False)
        
        elif option == '6':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📰 {t('cmd_ultimos')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            
            for i, inc in enumerate(gestionnaire_global.datos['incidents'][-20:][::-1], 1):
                cprint(f"\n{Color.RED}{i:2d}.{Color.RESET} {inc['titre'][:100]}...", 'white')
                cprint(f"      📅 {inc['date']} | 📍 {inc.get('departement', '?')} | 📰 {inc['source']} | 🔪 {inc.get('type', '?')}", 'gray')
            
            if gestionnaire_global.statistiques()['total'] == 0:
                cprint(f"   {Color.GRAY}Aucun incident enregistré. Lancez d'abord une recherche.{Color.RESET}")
            
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '7':
            cprint(f"\n📥 {t('exportando')}", 'cyan', bold=True)
            gestionnaire_global.exporter_json()
            gestionnaire_global.exporter_csv()
            gestionnaire_global.exporter_html()
            cprint(f"✅ Données exportées en JSON, CSV et HTML", 'green')
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '8':
            cprint(f"\n🔍 {t('verificando')}", 'cyan', bold=True)
            verificateur = VerificateurSources()
            sources_global = verificateur.verifier_toutes(sources_global)
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '9':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📊 {t('cmd_tipos')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            
            stats = gestionnaire_global.statistiques()
            if stats['total'] > 0:
                for type_crime, quantite in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
                    pct = (quantite / stats['total'] * 100)
                    barre_len = 40
                    filled = int(barre_len * quantite / stats['total'])
                    barre = '█' * filled + '░' * (barre_len - filled)
                    icono = TIPOS_CRIMEN.get(type_crime, {}).get('icono', '❓')
                    cprint(f"   {icono} {type_crime.upper()}: [{barre}] {quantite} ({pct:.1f}%)", 'white')
            else:
                cprint(f"   {Color.GRAY}Pas de données.{Color.RESET}")
            
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '10':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📈 {t('estadisticas_avanzadas')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            
            stats = gestionnaire_global.statistiques()
            
            cprint(f"\n{Color.YELLOW}📊 MÉTRIQUES AVANCÉES:{Color.RESET}")
            cprint(f"   Densité d'incidents: {stats['total'] / max(1, len(stats['departements'])):.1f} par département", 'white')
            cprint(f"   Sources par incident: {stats['total'] / max(1, len(stats['sources'])):.2f}", 'white')
            
            if stats['derniers_30j'] > 0 and stats['derniers_90j'] > 0:
                tendance = (stats['derniers_30j'] / stats['derniers_90j'] * 30) if stats['derniers_90j'] > 0 else 0
                cprint(f"   Tendance mensuelle: {tendance:.1f} incidents/mois", 'white')
            
            cprint(f"\n{Color.YELLOW}🔝 MOTS-CLÉS LES PLUS FRÉQUENTS:{Color.RESET}")
            for mot, count in sorted(stats['top_keywords'].items(), key=lambda x: x[1], reverse=True)[:10]:
                cprint(f"   • {mot}: {count} fois", 'cyan')
            
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '11':
            cprint(f"\n🧹 {t('limpiando')}", 'cyan', bold=True)
            doublons = gestionnaire_global.nettoyer_doublons()
            cprint(f"✅ {doublons} incidents dupliqués supprimés", 'green')
            input(f"\n{Color.GRAY}Appuyez sur Entrée pour continuer...{Color.RESET}")
        
        elif option == '12':
            cprint(f"\n👋 {t('hasta_pronto')}", 'red', bold=True)
            cprint(f"\n{Color.GRAY}🔪 AIDE-FRANCE - Nous surveillons pour protéger{Color.RESET}")
            break
        
        else:
            cprint(f"\n❌ {t('opcion_invalida')}", 'red')
            time.sleep(1)

# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================

def afficher_banniere_initiale():
    """Affiche la bannière de bienvenue"""
    print(f"""
{Color.RED}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    █████╗ ██╗██████╗ ███████╗    ███████╗██████╗   █████╗  ███╗   ██╗ ███████╗███████╗
║   ██╔══██╗██║██╔══██╗██╔════╝    ██╔════╝██╔══██╗ ██╔══██╗ ████╗  ██║ ██╔════╝██╔════╝
║   ███████║██║██║  ██║█████╗      █████╗  ██║████╗ ███████║ █████║ ██║ ██╗     ██║██║       
║   ██╔══██║██║██║  ██║██╔══╝      ██╔══╝  ██║  ██║ ██╔══██║ ██║╚██╗██║ ██║     ██╔══╝  
║   ██║  ██║██║██████╔╗███████╗    ██║     ██║  ██║ ██║  ██║ ██║ ╚████║ ██████╗ ███████╗
║   ╚═╝  ╚═╝╚═╝╚═════╝╚═══════╝    ╚═╝     ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
║                                                                               ║
║   🔪 AIDE-FRANCE v{VERSION} - PLATEFORME DE RENSEIGNEMENT CRIMINEL FRANÇAISE  ║
║                                                                               ║
║   ═══════════════════════════════════════════════════════════════════════     ║
║                                                                               ║
║   📊 Surveillance en temps réel: Trafic de drogue · Violence des gangs        ║
║   🏴 Couvre tous les 101 départements français                                ║
║   🔄 150+ User-Agents rotatifs · Découverte auto-URL · Anti-blocage           ║
║   📈 Graphiques interactifs · Dashboard web · Interface complète              ║
║   🔍 Mécanisme de réessai intelligent · Cache URL · Persistance session       ║
║                                                                               ║
║   ═══════════════════════════════════════════════════════════════════════     ║
║                                                                               ║
║   🛡️  "Un grand pouvoir implique de grandes responsabilités" - Spider-Man     ║
║                                                                               ║
║     - Par Condor2026                                                          ║
║                                                     •SpectrumSecurity•        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")

if __name__ == '__main__':
    # Sélectionner la langue d'abord
    seleccionar_idioma()
    
    # Afficher la bannière
    afficher_banniere_initiale()
    
    # Initialiser gestionnaire et sources
    gestionnaire_global = GestionnaireDonnees()
    sources_global = SOURCES_BASE.copy()
    
    # Afficher statistiques initiales
    stats = gestionnaire_global.statistiques()
    cprint(f"\n{Color.GREEN}📊 Base de données: {stats['total']} incidents stockés{Color.RESET}")
    cprint(f"{Color.YELLOW}⏳ Dernière mise à jour: {gestionnaire_global.datos.get('derniere_mise_a_jour', 'Jamais')}{Color.RESET}")
    cprint(f"{Color.CYAN}📰 Sources configurées: {len(sources_global)} médias français{Color.RESET}")
    
    # Demander mode d'exécution
    print(f"\n{Color.CYAN}┌{'─' * 40}┐{Color.RESET}")
    print(f"{Color.CYAN}│{Color.WHITE}  Comment souhaitez-vous exécuter?{' ' * 16}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}├{'─' * 40}┤{Color.RESET}")
    print(f"{Color.CYAN}│{Color.GREEN}  [1] Mode Terminal (recommandé){' ' * 13}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}│{Color.GREEN}  [2] Mode Web (dashboard graphiques){' ' * 8}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}└{'─' * 40}┘{Color.RESET}")
    
    mode = input(f"\n{Color.CYAN}➤ {Color.YELLOW}Choisissez: {Color.RESET}")
    
    if mode == '2':
        cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
        cprint(f"   📊 Dashboard avec graphiques: Barres, Donut, Ligne et Classement", 'cyan')
        cprint(f"   🔪 Auto-découverte activé pour les URLs tombées", 'cyan')
        cprint(f"   {Color.GRAY}Appuyez sur Ctrl+C pour revenir au menu{Color.RESET}")
        app.run(host='127.0.0.1', port=PUERTO, debug=False)
    else:
        menu()
