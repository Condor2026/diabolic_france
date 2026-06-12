#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Condor2026 / SpectrumSecurity

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🇫🇷 AIDE FRANCE v1.0 - PLATEFORME D'ENTRAIDE SOCIALE                          ║
║  ═══════════════════════════════════════════════════════════════════════════  ║
║  📊 Surveillance: Aide sociale · Logement · Chômage · Précarité · Droits      ║
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
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, Response
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Thread, Lock
from queue import Queue

# ============================================================================
# LANGUAGE SELECTOR WITH BEAUTIFUL INTERFACE (3 IDIOMAS)
# ============================================================================

IDIOMA_ACTUAL = None

VERSION = "1.0"
PUERTO = 5015
ARCHIVO_DATOS = 'aide_france_data.json'
ARCHIVO_CACHE = 'url_cache_france.json'
ARCHIVO_ESTADO = 'estado_fuentes_france.json'
ARCHIVO_BACKUP = 'aide_france_backup.json'
PAGINAS_BUSQUEDA = 3   # Reducido para no saturar, pero con paginación real
TIMEOUT = 25
MAX_INTENTOS = 3
DELAY_MIN = 0.8
DELAY_MAX = 2.0

def mostrar_banner_idioma():
    print(f"""
{Color.CYAN}╔════════════════════════════════════════════════════════════════════╗
║                                                                     ║
║   🇫🇷 AIDE FRANCE v{VERSION} - PLATEFORME D'ENTRAIDE SOCIALE              ║
║                                                                    ║
║   "Surveiller pour aider, pas pour stigmatiser. Données publiques, ║
║    éthique inébranlable, transparence absolue."                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")

def mostrar_menu_idioma():
    print(f"\n{Color.YELLOW}┌{'─' * 58}┐{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.CYAN}  🌍 SELECCIONE IDIOMA / CHOISISSEZ LA LANGUE / SCEGLI LINGUA    {Color.YELLOW} │{Color.RESET}")
    print(f"{Color.YELLOW}├{'─' * 58}┤{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [1] Español                                                    {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [2] Français                                                   {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}│{Color.GREEN}  [3] Italiano                                                   {Color.YELLOW}│{Color.RESET}")
    print(f"{Color.YELLOW}└{'─' * 58}┘{Color.RESET}")

def seleccionar_idioma():
    global IDIOMA_ACTUAL
    mostrar_banner_idioma()
    mostrar_menu_idioma()
    
    while True:
        opc = input(f"\n{Color.CYAN}➤ {Color.YELLOW}Opción / Option / Opzione: {Color.RESET}")
        if opc == '1':
            IDIOMA_ACTUAL = 'es'
            print(f"\n{Color.GREEN}✅ Idioma: Español seleccionado{Color.RESET}")
            break
        elif opc == '2':
            IDIOMA_ACTUAL = 'fr'
            print(f"\n{Color.GREEN}✅ Langue: Français sélectionnée{Color.RESET}")
            break
        elif opc == '3':
            IDIOMA_ACTUAL = 'it'
            print(f"\n{Color.GREEN}✅ Lingua: Italiano selezionato{Color.RESET}")
            break
        else:
            print(f"{Color.RED}❌ Opción inválida / Option invalide / Opzione non valida{Color.RESET}")
    
    time.sleep(0.5)

TEXTOS = {
    'es': {
        'app_name': '🇫🇷 AIDE FRANCE v1.0',
        'welcome_title': 'PLATAFORMA DE AYUDA SOCIAL - FRANCIA',
        'elegir_idioma': '🌍 Seleccione idioma: 1. Español  2. Français  3. Italiano',
        'menu_title': 'MENÚ PRINCIPAL',
        'cmd_buscar': '🔍 Buscar ayudas sociales (auto-detección URLs)',
        'cmd_analisis': '📊 Análisis completo con gráficos',
        'cmd_conexiones': '🔗 Patrones y tendencias de ayuda',
        'cmd_evolucion': '📈 Evolución mensual detallada',
        'cmd_web': '🌐 Iniciar servidor web (dashboard con gráficos)',
        'cmd_ultimos': '📰 Últimos 20 avisos registrados',
        'cmd_exportar': '📥 Exportar datos (JSON/CSV/HTML)',
        'cmd_verificar': '🔍 Verificar/actualizar fuentes (auto-discovery)',
        'cmd_tipos': '📊 Distribución por tipo de ayuda',
        'cmd_estadisticas': '📈 Estadísticas avanzadas',
        'cmd_limpiar': '🧹 Limpiar base de datos duplicados',
        'cmd_salir': '🗑️ Salir de la aplicación',
        'stats_total': 'Total avisos',
        'incidentes': 'avisos',
        'fuentes': 'fuentes activas',
        'departamentos': 'departamentos afectados',
        'servidor_web': 'Servidor web iniciado',
        'presiona_ctrl_c': 'Presiona Ctrl+C para volver al menú',
        'hasta_pronto': '¡Hasta pronto! Gracias por usar AIDE FRANCE',
        'opcion_invalida': 'Opción no válida, intenta de nuevo',
        'actualizando': 'ACTUALIZANDO DATOS DE AYUDA SOCIAL EN FRANCIA',
        'analisis_completo': 'ANÁLISIS COMPLETO DE LA SITUACIÓN SOCIAL EN FRANCIA',
        'conexiones': 'PATRONES Y TENDENCIAS DE AYUDA',
        'evolucion_mensual': 'EVOLUCIÓN MENSUAL DE AVISOS',
        'exportando': 'EXPORTANDO DATOS',
        'verificando': 'VERIFICANDO FUENTES FRANCESAS',
        'limpiando': 'LIMPIANDO BASE DE DATOS',
        'estadisticas_avanzadas': 'ESTADÍSTICAS AVANZADAS',
        'error_conexion': 'Error de conexión con la fuente',
        'sin_datos': 'No hay datos suficientes para mostrar',
        'procesando': 'Procesando...'
    },
    'fr': {
        'app_name': '🇫🇷 AIDE FRANCE v1.0',
        'welcome_title': 'PLATEFORME D\'ENTRAIDE SOCIALE - FRANCE',
        'elegir_idioma': '🌍 Choisissez la langue: 1. Español  2. Français  3. Italiano',
        'menu_title': 'MENU PRINCIPAL',
        'cmd_buscar': '🔍 Rechercher aides sociales (auto-découverte URLs)',
        'cmd_analisis': '📊 Analyse complète avec graphiques',
        'cmd_conexiones': '🔗 Modèles et tendances d\'aide',
        'cmd_evolucion': '📈 Évolution mensuelle détaillée',
        'cmd_web': '🌐 Démarrer serveur web (tableau de bord graphique)',
        'cmd_ultimos': '📰 20 derniers avis enregistrés',
        'cmd_exportar': '📥 Exporter les données (JSON/CSV/HTML)',
        'cmd_verificar': '🔍 Vérifier/mettre à jour les sources (auto-découverte)',
        'cmd_tipos': '📊 Distribution par type d\'aide',
        'cmd_estadisticas': '📈 Statistiques avancées',
        'cmd_limpiar': '🧹 Nettoyer les doublons',
        'cmd_salir': '🗑️ Quitter',
        'stats_total': 'Total avis',
        'incidentes': 'avis',
        'fuentes': 'sources actives',
        'departamentos': 'départements touchés',
        'servidor_web': 'Serveur web démarré',
        'presiona_ctrl_c': 'Appuyez sur Ctrl+C pour revenir au menu',
        'hasta_pronto': 'Au revoir! Merci d\'utiliser AIDE FRANCE',
        'opcion_invalida': 'Option invalide, réessayez',
        'actualizando': 'MISE À JOUR DES DONNÉES D\'AIDE SOCIALE EN FRANCE',
        'analisis_completo': 'ANALYSE COMPLÈTE DE LA SITUATION SOCIALE EN FRANCE',
        'conexiones': 'MODÈLES ET TENDANCES D\'AIDE',
        'evolucion_mensual': 'ÉVOLUTION MENSUELLE DES AVIS',
        'exportando': 'EXPORTATION DES DONNÉES',
        'verificando': 'VÉRIFICATION DES SOURCES FRANÇAISES',
        'limpiando': 'NETTOYAGE DE LA BASE DE DONNÉES',
        'estadisticas_avanzadas': 'STATISTIQUES AVANCÉES',
        'error_conexion': 'Erreur de connexion à la source',
        'sin_datos': 'Pas assez de données à afficher',
        'procesando': 'Traitement en cours...'
    },
    'it': {
        'app_name': '🇫🇷 AIDE FRANCE v1.0',
        'welcome_title': 'PIATTAFORMA DI AIUTO SOCIALE - FRANCIA',
        'elegir_idioma': '🌍 Seleziona lingua: 1. Español  2. Français  3. Italiano',
        'menu_title': 'MENU PRINCIPALE',
        'cmd_buscar': '🔍 Cerca aiuti sociali (auto-scoperta URL)',
        'cmd_analisis': '📊 Analisi completa con grafici',
        'cmd_conexiones': '🔗 Modelli e tendenze di aiuto',
        'cmd_evolucion': '📈 Evoluzione mensile dettagliata',
        'cmd_web': '🌐 Avvia server web (dashboard con grafici)',
        'cmd_ultimos': '📰 Ultimi 20 avvisi registrati',
        'cmd_exportar': '📥 Esporta dati (JSON/CSV/HTML)',
        'cmd_verificar': '🔍 Verifica/aggiorna fonti (auto-scoperta)',
        'cmd_tipos': '📊 Distribuzione per tipo di aiuto',
        'cmd_estadisticas': '📈 Statistiche avanzate',
        'cmd_limpiar': '🧹 Pulisci duplicati',
        'cmd_salir': '🗑️ Esci',
        'stats_total': 'Totale avvisi',
        'incidentes': 'avvisi',
        'fuentes': 'fonti attive',
        'departamentos': 'dipartimenti colpiti',
        'servidor_web': 'Server web avviato',
        'presiona_ctrl_c': 'Premi Ctrl+C per tornare al menu',
        'hasta_pronto': 'Arrivederci! Grazie per aver usato AIDE FRANCE',
        'opcion_invalida': 'Opzione non valida, riprova',
        'actualizando': 'AGGIORNAMENTO DATI DI AIUTO SOCIALE IN FRANCIA',
        'analisis_completo': 'ANALISI COMPLETA DELLA SITUAZIONE SOCIALE IN FRANCIA',
        'conexiones': 'MODELLI E TENDENZE DI AIUTO',
        'evolucion_mensual': 'EVOLUZIONE MENSILE DEGLI AVVISI',
        'exportando': 'ESPORTAZIONE DATI',
        'verificando': 'VERIFICA FONTI FRANCESI',
        'limpiando': 'PULIZIA DATABASE',
        'estadisticas_avanzadas': 'STATISTICHE AVANZATE',
        'error_conexion': 'Errore di connessione con la fonte',
        'sin_datos': 'Dati insufficienti da mostrare',
        'procesando': 'Elaborazione...'
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
# 150+ USER-AGENTS MODERNOS (COMPLETOS - MISMO QUE ANTES)
# ============================================================================

USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    # Chrome 125 - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.60 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.42 Safari/537.36
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
    return random.choice(USER_AGENTS)

def get_random_delay():
    return random.uniform(DELAY_MIN, DELAY_MAX)

# ============================================================================
# SISTEMA DE AUTO-DESCOBRIMIENTO DE URLs
# ============================================================================

class URLAutoDiscoverer:
    def __init__(self):
        self.cache_file = ARCHIVO_CACHE
        self.cache = self.load_cache()
        self.common_paths = [
            'social', 'aide-sociale', 'solidarite', 'urgence-sociale', 'precarite',
            'logement', 'emploi', 'chomage', 'droits', 'aides', 'assistance',
            'handicap', 'famille', 'sante', 'alimentation', 'hebergement-urgence',
            'page', 'pagina', 'pagination', 'archive', 'category'
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
    
    def discover_url(self, fuente):
        nombre = fuente['nombre']
        base_url = fuente['base']
        original_url = fuente['url']
        
        if nombre in self.cache and self.cache[nombre].get('url'):
            cached_url = self.cache[nombre]['url']
            cprint(f"   📦 Cache trouvée: {cached_url}", 'gray', dim=True)
            try:
                headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
                r = requests.get(cached_url, timeout=10, headers=headers)
                if r.status_code == 200:
                    return cached_url
            except:
                pass
        
        cprint(f"   🔍 Recherche URL alternative...", 'cyan', dim=True)
        
        for path in self.common_paths:
            urls_to_try = [
                f"{base_url}/{path}" if not base_url.endswith('/') else f"{base_url}{path}",
                f"{base_url}/{path}/",
                f"{base_url}/{path}.html",
                f"{base_url}/category/{path}",
                f"{base_url}/tag/{path}",
                f"{base_url}/topic/{path}",
                f"{base_url}/actualites/{path}",
            ]
            
            for test_url in urls_to_try[:4]:
                try:
                    headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9'}
                    r = requests.get(test_url, timeout=15, headers=headers)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, 'html.parser')
                        page_text = soup.get_text().lower()
                        aide_keywords = ['aide', 'social', 'urgence', 'logement', 'emploi', 'solidarite']
                        if any(kw in page_text for kw in aide_keywords):
                            cprint(f"   ✅ URL trouvée: {test_url}", 'green')
                            self.cache[nombre] = {'url': test_url, 'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                            self.save_cache()
                            return test_url
                except:
                    continue
            time.sleep(0.2)
        
        cprint(f"   ❌ URL alternative non trouvée", 'red')
        return original_url

# ============================================================================
# FUENTES DE AYUDA SOCIAL EN FRANCIA (30+ fuentes activas Abril 2026)
# ============================================================================

FUENTES_BASE = [
    # === GRANDS MÉDIAS NATIONAUX ===
    {'nombre': 'Le Monde - Social', 'url': 'https://www.lemonde.fr/societe/', 'base': 'https://www.lemonde.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': 'Le Figaro - Social', 'url': 'https://www.lefigaro.fr/actualite-france', 'base': 'https://www.lefigaro.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': 'Libération - Société', 'url': 'https://www.liberation.fr/societe/', 'base': 'https://www.liberation.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': '20 Minutes - Société', 'url': 'https://www.20minutes.fr/societe', 'base': 'https://www.20minutes.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': 'France Info - Social', 'url': 'https://www.francetvinfo.fr/societe/', 'base': 'https://www.francetvinfo.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': 'Le Parisien - Société', 'url': 'https://www.leparisien.fr/societe/', 'base': 'https://www.leparisien.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': 'Les Echos - Social', 'url': 'https://www.lesechos.fr/social', 'base': 'https://www.lesechos.fr', 'departement': 'Paris', 'categorie': 'national'},
    {'nombre': 'La Croix - Solidarité', 'url': 'https://www.la-croix.com/Solidarite', 'base': 'https://www.la-croix.com', 'departement': 'Paris', 'categorie': 'national'},
    
    # === AIDE SOCIALE SPÉCIALISÉE ===
    {'nombre': 'Secours Populaire', 'url': 'https://www.secourspopulaire.fr/actualites', 'base': 'https://www.secourspopulaire.fr', 'departement': 'Paris', 'categorie': 'asso'},
    {'nombre': 'Restos du Cœur', 'url': 'https://www.restosducoeur.org/actualites/', 'base': 'https://www.restosducoeur.org', 'departement': 'Paris', 'categorie': 'asso'},
    {'nombre': 'Croix-Rouge française', 'url': 'https://www.croix-rouge.fr/Actualites', 'base': 'https://www.croix-rouge.fr', 'departement': 'Paris', 'categorie': 'asso'},
    {'nombre': 'Fondation Abbé Pierre', 'url': 'https://www.fondation-abbe-pierre.fr/actualites', 'base': 'https://www.fondation-abbe-pierre.fr', 'departement': 'Paris', 'categorie': 'asso'},
    
    # === RÉGIONS (muestra por departamentos clave) ===
    {'nombre': 'France 3 Régions', 'url': 'https://france3-regions.francetvinfo.fr/societe', 'base': 'https://france3-regions.francetvinfo.fr', 'departement': 'National', 'categorie': 'regional'},
    {'nombre': 'Actu.fr - Social', 'url': 'https://actu.fr/societe', 'base': 'https://actu.fr', 'departement': 'National', 'categorie': 'local'},
    {'nombre': 'La Provence - Social', 'url': 'https://www.laprovence.com/actu/societe', 'base': 'https://www.laprovence.com', 'departement': 'Bouches-du-Rhône', 'categorie': 'local'},
    {'nombre': 'Le Progrès - Lyon', 'url': 'https://www.leprogres.fr/societe', 'base': 'https://www.leprogres.fr', 'departement': 'Rhône', 'categorie': 'local'},
    {'nombre': 'Sud Ouest - Social', 'url': 'https://www.sudouest.fr/societe', 'base': 'https://www.sudouest.fr', 'departement': 'Gironde', 'categorie': 'local'},
    {'nombre': 'Ouest-France - Solidarité', 'url': 'https://www.ouest-france.fr/solidarite', 'base': 'https://www.ouest-france.fr', 'departement': 'Ille-et-Vilaine', 'categorie': 'local'},
    {'nombre': 'La Dépêche - Social', 'url': 'https://www.ladepeche.fr/societe', 'base': 'https://www.ladepeche.fr', 'departement': 'Haute-Garonne', 'categorie': 'local'},
    {'nombre': 'Le Télégramme - Social', 'url': 'https://www.letelegramme.fr/societe', 'base': 'https://www.letelegramme.fr', 'departement': 'Finistère', 'categorie': 'local'},
    {'nombre': 'DNA - Alsace', 'url': 'https://www.dna.fr/societe', 'base': 'https://www.dna.fr', 'departement': 'Bas-Rhin', 'categorie': 'local'},
    {'nombre': 'Nice-Matin - Social', 'url': 'https://www.nicematin.com/societe', 'base': 'https://www.nicematin.com', 'departement': 'Alpes-Maritimes', 'categorie': 'local'},
]

# Departamentos franceses principales
DEPARTEMENTS_FRANCE = [
    'Paris', 'Bouches-du-Rhône', 'Rhône', 'Gironde', 'Haute-Garonne', 'Ille-et-Vilaine',
    'Finistère', 'Bas-Rhin', 'Alpes-Maritimes', 'Nord', 'Pas-de-Calais', 'Hauts-de-Seine',
    'Seine-Saint-Denis', 'Val-de-Marne', 'Loire-Atlantique', 'Isère', 'Var', 'Morbihan',
    'Calvados', 'Haute-Savoie', 'France', 'Outre-mer'
]

# ============================================================================
# PALABRAS CLAVE PARA DETECCIÓN DE AYUDA SOCIAL / SITUACIONES DIFÍCILES
# ============================================================================

PALABRAS_CLAVE_AIDE = [
    # Aide sociale
    'aide sociale', 'aide d\'urgence', 'solidarité', 'assistance', 'allocations',
    'RSA', 'AAH', 'APL', 'prime d\'activité', 'CAF', 'MDPH', 'CCAS',
    
    # Logement
    'logement', 'mal-logement', 'sans-abri', 'hébergement d\'urgence', 'marché locatif',
    'habitat indigne', 'expulsion locative', 'bidonville', 'squat', 'logement social',
    'HLM', 'DALO', 'droit au logement', 'ménage précaire',
    
    # Emploi / Chômage
    'chômage', 'précarité', 'emploi précaire', 'contrat courte durée', 'intérim',
    'pôle emploi', 'indemnisation', 'insertion professionnelle', 'formation',
    
    # Précarité / Pauvreté
    'pauvreté', 'précarité énergétique', 'faim', 'colis alimentaire', 'épicerie solidaire',
    'restos du cœur', 'secours populaire', 'banque alimentaire',
    
    # Santé
    'désert médical', 'accès aux soins', 'CMU', 'mutuelle', 'Aide Médicale d\'État',
    'pass sanitaire', 'psychiatrie', 'santé mentale', 'consultation gratuite',
    
    # Droits / Administratif
    'difficultés administratives', 'accès aux droits', 'numérique', 'illectronisme',
    'aide juridique', 'défenseur des droits',
    
    # Urgences sociales
    'urgence sociale', 'maraude', '115', 'Samu social', 'veille hivernale',
    'plan grand froid', 'canicule', 'alerte enlèvement',
    
    # Publics spécifiques
    'personnes âgées', 'isolées', 'handicap', 'jeunes', 'étudiants précaires',
    'familles monoparentales', 'migrants', 'réfugiés'
]

# ============================================================================
# TIPOS DE AYUDA CON ICONOS Y COLORES
# ============================================================================

TIPOS_AYUDA = {
    'logement': {'icono': '🏠', 'color': '#0088cc', 'nombre': 'Logement/Habitat', 'es': 'Vivienda', 'fr': 'Logement', 'it': 'Alloggio'},
    'emploi': {'icono': '💼', 'color': '#00aa66', 'nombre': 'Emploi/Chômage', 'es': 'Empleo/Paro', 'fr': 'Emploi/Chômage', 'it': 'Lavoro/Disoccupazione'},
    'alimentation': {'icono': '🍲', 'color': '#ffaa00', 'nombre': 'Aide alimentaire', 'es': 'Ayuda alimentaria', 'fr': 'Aide alimentaire', 'it': 'Aiuto alimentare'},
    'sante': {'icono': '🏥', 'color': '#cc4444', 'nombre': 'Santé/Accès soins', 'es': 'Sanidad', 'fr': 'Santé', 'it': 'Salute'},
    'precarite': {'icono': '⚠️', 'color': '#ff6600', 'nombre': 'Précarité/Pauvreté', 'es': 'Precariedad/Pobreza', 'fr': 'Précarité/Pauvreté', 'it': 'Precarietà/Povertà'},
    'droits': {'icono': '⚖️', 'color': '#9933cc', 'nombre': 'Droits/Aides sociales', 'es': 'Derechos/Ayudas sociales', 'fr': 'Droits/Aides sociales', 'it': 'Diritti/Aiuti sociali'},
    'urgence': {'icono': '🚨', 'color': '#cc0000', 'nombre': 'Urgence sociale', 'es': 'Emergencia social', 'fr': 'Urgence sociale', 'it': 'Emergenza sociale'},
    'solidarite': {'icono': '🤝', 'color': '#33aa88', 'nombre': 'Solidarité/Bénévoles', 'es': 'Solidaridad/Voluntarios', 'fr': 'Solidarité/Bénévoles', 'it': 'Solidarietà/Volontari'},
    'other': {'icono': '❓', 'color': '#888888', 'nombre': 'Autre aide', 'es': 'Otra ayuda', 'fr': 'Autre aide', 'it': 'Altro aiuto'}
}

# ============================================================================
# CLASE GESTOR DE DATOS (con paginación interna)
# ============================================================================

class GestorDatos:
    def __init__(self):
        self.archivo = ARCHIVO_DATOS
        self.datos = self.cargar()
        self.lock = Lock()
    
    def cargar(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'avisos': [], 'ultima_actualizacion': None, 'estadisticas_historicas': {}}
        return {'avisos': [], 'ultima_actualizacion': None, 'estadisticas_historicas': {}}
    
    def guardar(self):
        with self.lock:
            self.datos['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if os.path.exists(self.archivo):
                try:
                    with open(ARCHIVO_BACKUP, 'w', encoding='utf-8') as f:
                        json.dump(self.datos, f, indent=2, ensure_ascii=False)
                except:
                    pass
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
    
    def agregar_avisos(self, nuevos):
        if not nuevos:
            return 0
        with self.lock:
            ids_existentes = {av['id'] for av in self.datos['avisos']}
            contador = 0
            for n in nuevos:
                if n['id'] not in ids_existentes:
                    self.datos['avisos'].append(n)
                    ids_existentes.add(n['id'])
                    contador += 1
            if contador > 0:
                self._actualizar_historicas(nuevos)
                self.guardar()
            return contador
    
    def _actualizar_historicas(self, nuevos):
        historicas = self.datos.get('estadisticas_historicas', {})
        for av in nuevos:
            fecha = av.get('fecha', '')
            if fecha and len(fecha) >= 7:
                mes = fecha[:7]
                tipo = av.get('tipo', 'other')
                dep = av.get('departement', 'France')
                if mes not in historicas:
                    historicas[mes] = {'total': 0, 'tipos': {}, 'departements': {}}
                historicas[mes]['total'] += 1
                historicas[mes]['tipos'][tipo] = historicas[mes]['tipos'].get(tipo, 0) + 1
                historicas[mes]['departements'][dep] = historicas[mes]['departements'].get(dep, 0) + 1
        self.datos['estadisticas_historicas'] = historicas
    
    def detectar_tipo(self, texto):
        tl = texto.lower()
        if any(p in tl for p in ['logement', 'habitat', 'mal-logement', 'sans-abri', 'expulsion', 'hlm', 'apl']):
            return 'logement'
        if any(p in tl for p in ['emploi', 'chômage', 'travail', 'pole emploi', 'formation', 'intérim']):
            return 'emploi'
        if any(p in tl for p in ['alimentaire', 'restos du cœur', 'banque alimentaire', 'épicerie', 'colis']):
            return 'alimentation'
        if any(p in tl for p in ['santé', 'soins', 'médecin', 'hôpital', 'désert médical', 'mutuelle']):
            return 'sante'
        if any(p in tl for p in ['précarité', 'pauvreté', 'misère', 'exclusion', 'faim']):
            return 'precarite'
        if any(p in tl for p in ['droits', 'aide sociale', 'allocations', 'rsa', 'caf', 'aah', 'prime activité']):
            return 'droits'
        if any(p in tl for p in ['urgence', '115', 'samu social', 'grand froid', 'canicule', 'maraude']):
            return 'urgence'
        if any(p in tl for p in ['solidarité', 'bénévole', 'entraide', 'association']):
            return 'solidarite'
        return 'other'
    
    def estadisticas(self, avisos=None):
        if avisos is None:
            avisos = self.datos['avisos']
        stats = {
            'total': len(avisos),
            'departements': defaultdict(int),
            'tipos': defaultdict(int),
            'fuentes': defaultdict(int),
            'ultimos_7dias': 0,
            'ultimos_30dias': 0,
            'ultimos_90dias': 0,
            'tendencia': defaultdict(int),
            'top_keywords': defaultdict(int)
        }
        hoy = datetime.now()
        hace_7d = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
        hace_30d = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        hace_90d = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')
        
        for av in avisos:
            if av.get('departement'):
                stats['departements'][av['departement']] += 1
            if av.get('tipo'):
                stats['tipos'][av['tipo']] += 1
            if av.get('fuente'):
                stats['fuentes'][av['fuente']] += 1
            fecha_str = av.get('fecha', '')
            if fecha_str:
                if fecha_str >= hace_7d:
                    stats['ultimos_7dias'] += 1
                if fecha_str >= hace_30d:
                    stats['ultimos_30dias'] += 1
                if fecha_str >= hace_90d:
                    stats['ultimos_90dias'] += 1
                if len(fecha_str) >= 7:
                    mes = fecha_str[:7]
                    stats['tendencia'][mes] += 1
            titulo = av.get('titulo', '').lower()
            for kw in PALABRAS_CLAVE_AIDE[:40]:
                if kw in titulo:
                    stats['top_keywords'][kw] += 1
        return stats
    
    def evolucion_mensual(self):
        meses = {}
        for av in self.datos['avisos']:
            if av.get('fecha') and len(av['fecha']) >= 7:
                mes = av['fecha'][:7]
                meses[mes] = meses.get(mes, 0) + 1
        return dict(sorted(meses.items()))
    
    def limpiar_duplicados(self):
        with self.lock:
            ids_vistos = set()
            limpios = []
            dup = 0
            for av in self.datos['avisos']:
                if av['id'] not in ids_vistos:
                    ids_vistos.add(av['id'])
                    limpios.append(av)
                else:
                    dup += 1
            self.datos['avisos'] = limpios
            if dup > 0:
                self.guardar()
            return dup
    
    def exportar_json(self):
        return json.dumps(self.datos, indent=2, ensure_ascii=False)
    
    def exportar_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Titre', 'Date', 'Département', 'Type aide', 'Source'])
        for av in self.datos['avisos']:
            writer.writerow([av['id'], av['titulo'].replace('\n',' '), av['fecha'], av.get('departement',''), av.get('tipo',''), av['fuente']])
        return output.getvalue()
    
    def exportar_html(self):
        stats = self.estadisticas()
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AIDE FRANCE - Rapport Social</title>
<style>body{{background:#0a0a0a;color:#e0e0e0;font-family:sans-serif;padding:20px}}h1{{color:#ff4444}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}}.stat-card{{background:#1a1a1a;padding:15px;border-radius:8px;text-align:center;border-left:4px solid #ff4444}}.stat-number{{font-size:2em;color:#ff4444}}table{{width:100%;border-collapse:collapse;margin:20px0}}th,td{{border:1px solid #333;padding:8px;text-align:left}}th{{background:#333}}</style>
</head><body><h1>🇫🇷 AIDE FRANCE - Rapport Social</h1><p>Généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<div class="stats"><div class="stat-card"><div>Total avis</div><div class="stat-number">{stats['total']}</div></div>
<div class="stat-card"><div>7 derniers jours</div><div class="stat-number">{stats['ultimos_7dias']}</div></div>
<div class="stat-card"><div>30 derniers jours</div><div class="stat-number">{stats['ultimos_30dias']}</div></div>
<div class="stat-card"><div>Sources</div><div class="stat-number">{len(stats['fuentes'])}</div></div></div>
<h2>Top départements</h2><table>"""
        for dep, count in sorted(stats['departements'].items(), key=lambda x:x[1], reverse=True)[:10]:
            html += f"<tr><td>{dep}</td><td>{count}</td></tr>"
        html += "</table><h2>Types d'aide</h2><table>"
        for tip, count in sorted(stats['tipos'].items(), key=lambda x:x[1], reverse=True):
            icono = TIPOS_AYUDA.get(tip, {}).get('icono', '❓')
            html += f"<tr><td>{icono} {tip}</td><td>{count}</td></tr>"
        html += f"""</table><h2>Derniers avis (20)</h2><table><tr><th>Date</th><th>Département</th><th>Type</th><th>Titre</th><th>Source</th></tr>"""
        for av in self.datos['avisos'][-20:][::-1]:
            html += f"<tr><td>{av['fecha']}</td><td>{av.get('departement','?')}</td><td>{av.get('tipo','?')}</td><td>{av['titulo'][:100]}...</td><td>{av['fuente']}</td></tr>"
        html += "</table></body></html>"
        return html

# ============================================================================
# CLASE VERIFICADOR DE FUENTES (adaptado a Francia)
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
                barra = '█' * int(i*50/total) + '░' * (50 - int(i*50/total))
                sys.stdout.write(f"\r   🔪 Progreso: [{barra}] {i}/{total} ({pct:.1f}%)")
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
            time.sleep(0.2)
        print()
        cprint(f"\n{'='*80}", 'green', bold=True)
        cprint(f"📊 RÉSULTATS:", 'green', bold=True)
        cprint(f"   Sources actives: {activas} de {total}", 'white')
        cprint(f"   Auto-discovery appliqué: {auto} URLs trouvées", 'cyan')
        cprint(f"{'='*80}", 'green', bold=True)
        self.guardar_estado()
        return verificadas

# ============================================================================
# CLASE EXTRACTOR DE NOTICIAS (con paginación real)
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
        avisos = []
        url_base = fuente['url']
        for pagina in range(1, paginas+1):
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
                    elementos.extend(soup.find_all(['h1','h2','h3','h4']))
                    encontrados = 0
                    gestor_temp = GestorDatos()
                    for elem in elementos[:30]:
                        texto = elem.get_text().strip()
                        if len(texto) < 40:
                            continue
                        tl = texto.lower()
                        if any(kw in tl for kw in PALABRAS_CLAVE_AIDE):
                            fecha_elem = soup.find('time')
                            fecha = datetime.now().strftime('%Y-%m-%d')
                            if fecha_elem and fecha_elem.get('datetime'):
                                fecha = fecha_elem.get('datetime')[:10]
                            dep = fuente['departement']
                            for d in DEPARTEMENTS_FRANCE:
                                if d.lower() in tl:
                                    dep = d
                                    break
                            tipo = gestor_temp.detectar_tipo(texto)
                            avisos.append({
                                'id': hashlib.md5(texto.encode()).hexdigest()[:16],
                                'titulo': texto[:500],
                                'fecha': fecha,
                                'departement': dep,
                                'tipo': tipo,
                                'fuente': fuente['nombre']
                            })
                            encontrados += 1
                    cprint(f"✓ {encontrados} trouvés", 'green')
                    if encontrados == 0 and pagina > 2:
                        break
                else:
                    cprint(f"✗ Pas de réponse", 'red')
                    break
            except Exception as e:
                cprint(f"✗ Erreur: {str(e)[:30]}", 'red')
            time.sleep(get_random_delay())
        return avisos
    
    def extraer_todas(self, paginas=PAGINAS_BUSQUEDA):
        cprint(f"\n{'='*80}", 'red', bold=True)
        cprint(f"🇫🇷 AIDE FRANCE - ANALYSE SOCIALE", 'red', bold=True, bg=True)
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
            avisos_f = self.extraer_de_fuente(fuente, paginas)
            todas.extend(avisos_f)
            cprint(f"   📊 Total source: {len(avisos_f)} avis", 'cyan')
        print()
        unicos = {}
        for av in todas:
            if av['id'] not in unicos:
                unicos[av['id']] = av
        resultado = list(unicos.values())
        cprint(f"\n{'='*80}", 'green', bold=True)
        cprint(f"🇫🇷 RÉSULTAT FINAL:", 'green', bold=True)
        cprint(f"   Avis trouvés: {len(resultado)}", 'white')
        cprint(f"   Sources actives: {total_act}", 'white')
        cprint(f"   Auto-discovery appliqué", 'cyan')
        cprint(f"{'='*80}", 'green', bold=True)
        return resultado

# ============================================================================
# INTERFAZ WEB CON PAGINACIÓN Y 3 IDIOMAS
# ============================================================================

app = Flask(__name__)
gestor_global = None
fuentes_global = None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇫🇷 AIDE FRANCE - Aide Sociale</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:linear-gradient(135deg,#0a0a0a,#1a0a2a);color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:20px}
        .container{max-width:1400px;margin:0 auto}
        .header{background:linear-gradient(135deg,#1a0a2a,#2a0a2a);padding:30px;border-radius:20px;text-align:center;margin-bottom:30px;border:1px solid #ff6666;box-shadow:0 0 30px rgba(255,102,102,0.3)}
        h1{font-size:3em;color:#ff6666}
        .stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:30px 0}
        .stat-card{background:#111;padding:25px;border-radius:15px;text-align:center;border-left:5px solid #ff6666}
        .stat-number{font-size:3em;color:#ff6666;font-weight:bold}
        .btn{background:#222;color:#ff6666;border:2px solid #ff6666;padding:12px 30px;border-radius:40px;margin:10px;cursor:pointer;transition:0.3s}
        .btn:hover{background:#ff6666;color:#000;transform:scale(1.05)}
        .filtros{display:flex;gap:15px;justify-content:center;margin:30px 0;flex-wrap:wrap}
        .filtro-btn{background:#1a1a1a;color:#ccc;border:2px solid #333;padding:10px 25px;border-radius:30px;text-decoration:none}
        .filtro-btn.active,.filtro-btn:hover{background:#ff6666;color:#000;border-color:#ff6666}
        .charts-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));gap:30px;margin:30px 0}
        .chart-container{background:#111;border-radius:15px;padding:20px}
        .pagination{display:flex;justify-content:center;gap:15px;margin:30px 0;align-items:center}
        .page-link{background:#222;color:#ff6666;padding:8px 16px;border-radius:8px;text-decoration:none;border:1px solid #ff6666}
        .page-link.active{background:#ff6666;color:#000}
        .incidente-card{background:#0a0a0a;margin:15px 0;padding:20px;border-radius:12px;border-left:6px solid #ff6666}
        .footer{text-align:center;margin-top:50px;padding:20px;background:#111;border-radius:15px}
        @media(max-width:768px){.charts-row{grid-template-columns:1fr}}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🇫🇷 AIDE FRANCE</h1>
        <p>{{ texts.subtitle if texts.subtitle else "Plateforme d'entraide sociale" }}</p>
        <div class="version-badge">v{{ version }} · {{ lang|upper }}</div>
    </div>
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-number">{{ stats.total }}</div><div class="stat-label">📊 {{ texts.stats_total or "Total avis" }}</div></div>
        <div class="stat-card"><div class="stat-number">{{ stats.ultimos_7dias }}</div><div class="stat-label">⚡ 7 {{ texts.days or "jours" }}</div></div>
        <div class="stat-card"><div class="stat-number">{{ stats.ultimos_30dias }}</div><div class="stat-label">🔥 30 {{ texts.days or "jours" }}</div></div>
        <div class="stat-card"><div class="stat-number">{{ periodicos_activos }}</div><div class="stat-label">📰 {{ texts.fuentes or "Sources" }}</div></div>
    </div>
    <div style="text-align:center">
        <form action="/actualizar" method="post" style="display:inline"><button class="btn">🔄 {{ texts.actualizar or "Actualiser" }}</button></form>
        <a href="/exportar/json" class="btn">📥 JSON</a>
        <a href="/exportar/csv" class="btn">📥 CSV</a>
        <a href="/exportar/html" class="btn">📄 HTML</a>
        <div style="display:inline-block; margin-left:20px">
            <a href="?lang=es" class="btn">🇪🇸 ES</a>
            <a href="?lang=fr" class="btn">🇫🇷 FR</a>
            <a href="?lang=it" class="btn">🇮🇹 IT</a>
        </div>
    </div>
    <div class="filtros">
        <a href="/?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='todo' %}active{% endif %}">📅 {{ texts.todo or "Tout" }}</a>
        <a href="/filtro/7d?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='7d' %}active{% endif %}">⚡ 7d</a>
        <a href="/filtro/30d?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='30d' %}active{% endif %}">🔥 30d</a>
        <a href="/filtro/90d?page=1&lang={{ lang }}" class="filtro-btn {% if filtro=='90d' %}active{% endif %}">📊 90d</a>
    </div>
    <div class="charts-row">
        <div class="chart-container"><canvas id="depChart"></canvas></div>
        <div class="chart-container"><canvas id="typeChart"></canvas></div>
    </div>
    <div class="charts-row">
        <div class="chart-container"><canvas id="trendChart"></canvas></div>
        <div class="chart-container"><canvas id="sourcesChart"></canvas></div>
    </div>
    
    <!-- PAGINACIÓN REAL -->
    <div class="pagination">
        {% if page > 1 %}<a href="?page={{ page-1 }}&lang={{ lang }}{% if filtro != 'todo' %}&filtro={{ filtro }}{% endif %}" class="page-link">← {{ texts.prev or "Précédent" }}</a>{% endif %}
        <span>{{ texts.page or "Page" }} {{ page }} / {{ total_pages }} ({{ total_items }} {{ texts.items or "éléments" }})</span>
        {% if page < total_pages %}<a href="?page={{ page+1 }}&lang={{ lang }}{% if filtro != 'todo' %}&filtro={{ filtro }}{% endif %}" class="page-link">{{ texts.next or "Suivant" }} →</a>{% endif %}
    </div>
    
    <div class="chart-container">
        <h3>📰 {{ texts.last_news or "Derniers avis" }}</h3>
        {% for av in avisos_paginados %}
        <div class="incidente-card">
            <div class="incidente-titulo">{{ av.titulo[:150] }}...</div>
            <div class="incidente-meta">📍 {{ av.departement or '?' }} | 📅 {{ av.fecha }} | 📰 {{ av.fuente }} | 🔪 {{ av.tipo }}</div>
        </div>
        {% endfor %}
    </div>
    <div class="footer"><p>🇫🇷 AIDE FRANCE v{{ version }} · {{ periodicos_activos }} sources actives · Données publiques à but solidaire</p></div>
</div>
<script>
    new Chart(document.getElementById('depChart'),{type:'bar',data:{labels:{{ condados_labels|tojson }}, datasets:[{label:'Avis',data:{{ condados_data|tojson }},backgroundColor:'#ff6666'}]},options:{responsive:true}});
    new Chart(document.getElementById('typeChart'),{type:'doughnut',data:{labels:{{ tipos_labels|tojson }}, datasets:[{data:{{ tipos_data|tojson }},backgroundColor:['#cc4444','#00aa66','#ffaa00','#0088cc','#ff6600','#9933cc','#cc0000','#33aa88','#888888']}]}});
    new Chart(document.getElementById('trendChart'),{type:'line',data:{labels:{{ tendencia_labels|tojson }}, datasets:[{label:'Évolution',data:{{ tendencia_data|tojson }},borderColor:'#ff6666',fill:true}]}});
    new Chart(document.getElementById('sourcesChart'),{type:'bar',data:{labels:{{ fuentes_labels|tojson }}, datasets:[{label:'Articles',data:{{ fuentes_data|tojson }},backgroundColor:'#ff8888'}]},options:{indexAxis:'y'}});
</script>
</body>
</html>
'''

# Textos web multilingüe
WEB_TEXTS = {
    'es': {'subtitle': 'Información actual para situaciones difíciles (ayuda social, empleo, vivienda, derechos)', 'stats_total': 'Total avisos', 'fuentes': 'fuentes activas', 'actualizar': 'Actualizar', 'todo': 'Todo', 'days': 'días', 'prev': '← Anterior', 'next': 'Siguiente →', 'page': 'Página', 'items': 'avisos', 'last_news': 'Últimos avisos con paginación'},
    'fr': {'subtitle': "Informations actuelles pour situations difficiles (aide sociale, emploi, logement, droits)", 'stats_total': 'Total avis', 'fuentes': 'sources actives', 'actualizar': 'Mettre à jour', 'todo': 'Tout', 'days': 'jours', 'prev': '← Précédent', 'next': 'Suivant →', 'page': 'Page', 'items': 'avis', 'last_news': 'Derniers avis avec pagination'},
    'it': {'subtitle': 'Informazioni attuali per situazioni difficili (aiuto sociale, lavoro, alloggio, diritti)', 'stats_total': 'Totale avvisi', 'fuentes': 'fonti attive', 'actualizar': 'Aggiorna', 'todo': 'Tutto', 'days': 'giorni', 'prev': '← Precedente', 'next': 'Successivo →', 'page': 'Pagina', 'items': 'avvisi', 'last_news': 'Ultimi avvisi con paginazione'}
}

@app.route('/')
def home():
    lang = request.args.get('lang', IDIOMA_ACTUAL or 'fr')
    page = int(request.args.get('page', 1))
    filtro = request.args.get('filtro', 'todo')
    per_page = 12
    
    avisos = gestor_global.datos['avisos']
    if filtro == '7d':
        hace = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        avisos = [a for a in avisos if a.get('fecha', '') >= hace]
    elif filtro == '30d':
        hace = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        avisos = [a for a in avisos if a.get('fecha', '') >= hace]
    elif filtro == '90d':
        hace = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        avisos = [a for a in avisos if a.get('fecha', '') >= hace]
    
    total_items = len(avisos)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = avisos[start:end] if avisos else []
    
    stats = gestor_global.estadisticas(avisos)
    condados_labels = list(stats['departements'].keys())[:8]
    condados_data = list(stats['departements'].values())[:8]
    tipos_labels = [f"{TIPOS_AYUDA.get(t,{}).get('icono','❓')} {t}" for t in stats['tipos'].keys()]
    tipos_data = list(stats['tipos'].values())
    tendencia_items = list(stats['tendencia'].items())[-8:]
    tendencia_labels = [i[0] for i in tendencia_items]
    tendencia_data = [i[1] for i in tendencia_items]
    fuentes_top = dict(sorted(stats['fuentes'].items(), key=lambda x:x[1], reverse=True)[:5])
    fuentes_labels = list(fuentes_top.keys())
    fuentes_data = list(fuentes_top.values())
    periodicos_activos = len([f for f in fuentes_global if f.get('activo', True)])
    
    return render_template_string(HTML_TEMPLATE, version=VERSION, lang=lang, texts=WEB_TEXTS.get(lang, WEB_TEXTS['fr']),
                                  stats=stats, periodicos_activos=periodicos_activos, filtro=filtro,
                                  condados_labels=condados_labels, condados_data=condados_data,
                                  tipos_labels=tipos_labels, tipos_data=tipos_data,
                                  tendencia_labels=tendencia_labels, tendencia_data=tendencia_data,
                                  fuentes_labels=fuentes_labels, fuentes_data=fuentes_data,
                                  avisos_paginados=paginated, page=page, total_pages=total_pages, total_items=total_items)

@app.route('/filtro/<periodo>')
def filtro_route(periodo):
    lang = request.args.get('lang', IDIOMA_ACTUAL or 'fr')
    page = int(request.args.get('page', 1))
    return home()  # redirect implícito, manteniendo filtro

@app.route('/actualizar', methods=['POST'])
def actualizar():
    global gestor_global, fuentes_global
    cprint(f"\n{'='*80}", 'red', bold=True)
    cprint(f"🇫🇷 {t('actualizando')}", 'red', bold=True, bg=True)
    cprint(f"{'='*80}", 'red', bold=True)
    verificador = VerificadorFuentes()
    fuentes_global = verificador.verificar_todas(fuentes_global)
    extractor = ExtractorNoticias(fuentes_global)
    nuevos = extractor.extraer_todas(paginas=PAGINAS_BUSQUEDA)
    agregados = gestor_global.agregar_avisos(nuevos)
    cprint(f"\n✅ {agregados} {t('incidentes')} nouveaux enregistrés", 'green', bold=True)
    return home()

@app.route('/exportar/json')
def exportar_json():
    return Response(gestor_global.exportar_json(), mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=aide_france.json'})

@app.route('/exportar/csv')
def exportar_csv():
    return Response(gestor_global.exportar_csv(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=aide_france.csv'})

@app.route('/exportar/html')
def exportar_html():
    return Response(gestor_global.exportar_html(), mimetype='text/html', headers={'Content-Disposition': 'attachment; filename=aide_france.html'})

# ============================================================================
# MENÚ PRINCIPAL DE TERMINAL (adaptado 3 idiomas)
# ============================================================================

def mostrar_menu_principal():
    stats = gestor_global.estadisticas()
    activas = len([f for f in fuentes_global if f.get('activo', True)])
    print(f"""
{Color.RED}╔{'═' * 70}╗{Color.RESET}
{Color.RED}║{Color.BOLD}{Color.WHITE}  🇫🇷 {t('app_name')}{' ' * 45}{Color.RED}║{Color.RESET}
{Color.RED}╠{'═' * 70}╣{Color.RESET}
{Color.RED}║{Color.CYAN}  📊 {t('stats_total')}: {stats['total']} {t('incidentes')}{' ' * 37}{Color.RED}║{Color.RESET}
{Color.RED}║{Color.YELLOW}  📰 {t('fuentes')}: {activas} de {len(fuentes_global)}{' ' * 38}{Color.RED}║{Color.RESET}
{Color.RED}║{Color.GREEN}  🏴 {t('departamentos')}: {len(stats['departements'])}{' ' * 39}{Color.RED}║{Color.RESET}
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
    global gestor_global, fuentes_global
    while True:
        mostrar_menu_principal()
        opc = input(f"{Color.CYAN}➤ {Color.YELLOW}Opción: {Color.RESET}")
        if opc == '1':
            cprint(f"\n🔍 {t('procesando')}", 'cyan', bold=True)
            verificador = VerificadorFuentes()
            fuentes_global = verificador.verificar_todas(fuentes_global)
            extractor = ExtractorNoticias(fuentes_global)
            nuevos = extractor.extraer_todas(paginas=PAGINAS_BUSQUEDA)
            agregados = gestor_global.agregar_avisos(nuevos)
            cprint(f"\n✅ {agregados} {t('incidentes')} nuevos", 'green', bold=True)
            input(f"\n{Color.GRAY}Enter...{Color.RESET}")
        elif opc == '2':
            stats = gestor_global.estadisticas()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📊 {t('analisis_completo')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            cprint(f"\n📈 {t('stats_total')}: {stats['total']}", 'white')
            cprint(f"   7d: {stats['ultimos_7dias']} | 30d: {stats['ultimos_30dias']} | 90d: {stats['ultimos_90dias']}", 'white')
            cprint(f"\n📍 TOP départements:", 'yellow')
            for dep, cnt in sorted(stats['departements'].items(), key=lambda x:x[1], reverse=True)[:8]:
                cprint(f"   {dep}: {cnt}", 'cyan')
            input(f"\n{Color.GRAY}Enter...{Color.RESET}")
        elif opc == '5':
            cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
            cprint(f"   📊 Dashboard avec pagination réelle", 'cyan')
            cprint(f"   🌍 3 langues: ES/FR/IT", 'cyan')
            cprint(f"   🔪 {t('presiona_ctrl_c')}", 'gray')
            app.run(host='127.0.0.1', port=PUERTO, debug=False)
        elif opc == '6':
            cprint(f"\n📰 {t('cmd_ultimos')}", 'red', bold=True, bg=True)
            for i, av in enumerate(gestor_global.datos['avisos'][-20:][::-1], 1):
                cprint(f"\n{i:2d}. {av['titulo'][:100]}...", 'white')
                cprint(f"      📅 {av['fecha']} | 📍 {av.get('departement','?')} | 📰 {av['fuente']} | 🔪 {av.get('tipo','?')}", 'gray')
            if gestor_global.estadisticas()['total'] == 0:
                cprint(f"   {Color.GRAY}Aucune donnée. Lancez une recherche d'abord.{Color.RESET}")
            input(f"\n{Color.GRAY}Enter...{Color.RESET}")
        elif opc == '12':
            cprint(f"\n👋 {t('hasta_pronto')}", 'red', bold=True)
            break
        else:
            cprint(f"\n❌ {t('opcion_invalida')}", 'red')
            time.sleep(1)

def mostrar_banner_inicial():
    print(f"""
{Color.RED}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   █████╗ ██╗██████╗ ███████╗    ███████╗██████╗  █████╗ ███╗   ██╗ ██████╗███████╗
║  ██╔══██╗██║██╔══██╗██╔════╝    ██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝
║  ███████║██║██║  ██║█████╗      █████╗  ██████╔╝███████║██╔██╗ ██║██║     █████╗  
║  ██╔══██║██║██║  ██║██╔══╝      ██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║     ██╔══╝  
║  ██║  ██║██║██████╔╝███████╗    ██║     ██║  ██║██║  ██║██║ ╚████║╚██████╗███████╗
║  ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
║                                                                               ║
║   🇫🇷 AIDE FRANCE v{VERSION} - PLATEFORME D'ENTRAIDE SOCIALE                   ║
║   ══════════════════════════════════════════════════════════════════════════  ║
║   📊 Surveillance: Aide sociale · Logement · Chômage · Précarité · Droits     ║
║   🔄 150+ User-Agents · Auto-discovery · Anti-blocage · Pagination réelle     ║
║   📈 Graphiques interactifs · Dashboard web · 3 langues (ES/FR/IT)            ║
║                                                                               ║
║   🛡️  "L'union fait la force" - Devise française                              ║
║                                                                               ║
║                                         - By Condor2026                       ║
║                                         •SpectrumSecurity•                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")

def menu():
    global gestor_global, fuentes_global
    
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Color.CYAN}➤ {Color.YELLOW}Opción: {Color.RESET}")
        
        if opcion == '1':
            cprint(f"\n🔍 {t('procesando')}", 'cyan', bold=True)
            verificador = VerificadorFuentes()
            fuentes_global = verificador.verificar_todas(fuentes_global)
            extractor = ExtractorNoticias(fuentes_global)
            nuevos = extractor.extraer_todas(paginas=PAGINAS_BUSQUEDA)
            agregados = gestor_global.agregar_avisos(nuevos)
            cprint(f"\n✅ {agregados} {t('incidentes')} nouveaux enregistrés", 'green', bold=True)
            input(f"\n{Color.GRAY}Presiona Enter para continuar...{Color.RESET}")
        
        elif opcion == '2':
            stats = gestor_global.estadisticas()
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📊 {t('analisis_completo')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            cprint(f"\n📈 {t('stats_total')}: {stats['total']}", 'white')
            cprint(f"   7d: {stats['ultimos_7dias']} | 30d: {stats['ultimos_30dias']} | 90d: {stats['ultimos_90dias']}", 'white')
            cprint(f"\n📍 TOP départements:", 'yellow')
            for dep, cnt in sorted(stats['departements'].items(), key=lambda x: x[1], reverse=True)[:8]:
                cprint(f"   {dep}: {cnt}", 'cyan')
            input(f"\n{Color.GRAY}Presiona Enter para continuar...{Color.RESET}")
        
        elif opcion == '5':
            cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
            cprint(f"   📊 Pagination réelle + 3 langues", 'cyan')
            cprint(f"   {Color.GRAY}Ctrl+C pour revenir au menu{Color.RESET}")
            app.run(host='127.0.0.1', port=PUERTO, debug=False)
        
        elif opcion == '6':
            cprint(f"\n{'='*70}", 'red', bold=True)
            cprint(f"📰 {t('cmd_ultimos')}", 'red', bold=True, bg=True)
            cprint(f"{'='*70}", 'red', bold=True)
            for i, av in enumerate(gestor_global.datos['avisos'][-20:][::-1], 1):
                cprint(f"\n{i:2d}. {av['titulo'][:100]}...", 'white')
                cprint(f"      📅 {av['fecha']} | 📍 {av.get('departement','?')} | 📰 {av['fuente']} | 🔪 {av.get('tipo','?')}", 'gray')
            if gestor_global.estadisticas()['total'] == 0:
                cprint(f"   {Color.GRAY}Aucune donnée. Lancez une recherche d'abord.{Color.RESET}")
            input(f"\n{Color.GRAY}Presiona Enter para continuar...{Color.RESET}")
        
        elif opcion == '8':
            cprint(f"\n🔍 {t('verificando')}", 'cyan', bold=True)
            verificador = VerificadorFuentes()
            fuentes_global = verificador.verificar_todas(fuentes_global)
            input(f"\n{Color.GRAY}Presiona Enter para continuar...{Color.RESET}")
        
        elif opcion == '12':
            cprint(f"\n👋 {t('hasta_pronto')}", 'red', bold=True)
            break
        
        else:
            cprint(f"\n❌ {t('opcion_invalida')}", 'red')
            time.sleep(1)


def mostrar_menu_principal():
    stats = gestor_global.estadisticas()
    activas = len([f for f in fuentes_global if f.get('activo', True)])
    print(f"""
{Color.RED}╔{'═' * 70}╗{Color.RESET}
{Color.RED}║{Color.BOLD}{Color.WHITE}  🇫🇷 {t('app_name')}{' ' * 46}{Color.RED}║{Color.RESET}
{Color.RED}╠{'═' * 70}╣{Color.RESET}
{Color.RED}║{Color.CYAN}  📊 {t('stats_total')}: {stats['total']} {t('incidentes')}{' ' * 37}{Color.RED}║{Color.RESET}
{Color.RED}║{Color.YELLOW}  📰 {t('fuentes')}: {activas} de {len(fuentes_global)}{' ' * 39}{Color.RED}║{Color.RESET}
{Color.RED}║{Color.GREEN}  🏴 {t('departamentos')}: {len(stats['departements'])}{' ' * 40}{Color.RED}║{Color.RESET}
{Color.RED}╚{'═' * 70}╝{Color.RESET}

{Color.YELLOW}┌{'─' * 52}┐{Color.RESET}
{Color.YELLOW}│{Color.CYAN}  📋 {t('menu_title')}{' ' * 38}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}├{'─' * 52}┤{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [1]  🔍 {t('cmd_buscar')}{' ' * 31}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [2]  📊 {t('cmd_analisis')}{' ' * 30}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [3]  🔗 {t('cmd_conexiones')}{' ' * 29}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [4]  📈 {t('cmd_evolucion')}{' ' * 30}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [5]  🌐 {t('cmd_web')}{' ' * 34}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [6]  📰 {t('cmd_ultimos')}{' ' * 32}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [7]  📥 {t('cmd_exportar')}{' ' * 32}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [8]  🔍 {t('cmd_verificar')}{' ' * 31}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [9]  📊 {t('cmd_tipos')}{' ' * 33}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [10] 📈 {t('cmd_estadisticas')}{' ' * 28}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.GREEN}  [11] 🧹 {t('cmd_limpiar')}{' ' * 33}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}│{Color.RED}  [12] 🗑️ {t('cmd_salir')}{' ' * 35}{Color.YELLOW}│{Color.RESET}
{Color.YELLOW}└{'─' * 52}┘{Color.RESET}
""")


if __name__ == '__main__':
    seleccionar_idioma()
    mostrar_banner_inicial()
    gestor_global = GestorDatos()
    fuentes_global = FUENTES_BASE.copy()
    stats = gestor_global.estadisticas()
    cprint(f"\n{Color.GREEN}📊 Base de données: {stats['total']} avis stockés{Color.RESET}")
    cprint(f"{Color.YELLOW}⏳ Dernière mise à jour: {gestor_global.datos.get('ultima_actualizacion', 'Jamais')}{Color.RESET}")
    cprint(f"{Color.CYAN}📰 Sources configurées: {len(fuentes_global)} médias français{Color.RESET}")
    
    print(f"\n{Color.CYAN}┌{'─' * 40}┐{Color.RESET}")
    print(f"{Color.CYAN}│{Color.WHITE}  Mode d'exécution:{' ' * 25}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}├{'─' * 40}┤{Color.RESET}")
    print(f"{Color.CYAN}│{Color.GREEN}  [1] Terminal (recommandé){' ' * 17}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}│{Color.GREEN}  [2] Web (dashboard graphique){' ' * 12}{Color.CYAN}│{Color.RESET}")
    print(f"{Color.CYAN}└{'─' * 40}┘{Color.RESET}")
    
    modo = input(f"\n{Color.CYAN}➤ {Color.YELLOW}Choisissez: {Color.RESET}")
    
    if modo == '2':
        cprint(f"\n🌐 {t('servidor_web')}: http://localhost:{PUERTO}", 'green', bold=True)
        cprint(f"   📊 Dashboard avec pagination réelle", 'cyan')
        cprint(f"   {Color.GRAY}Presiona Ctrl+C para volver al menú{Color.RESET}")
        app.run(host='127.0.0.1', port=PUERTO, debug=False)
    else:
        menu()
