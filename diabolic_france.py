#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Condor2026 / SpectrumSecurity

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🔪 DIABOLIC FRANCE v3.0 - SURVEILLANCE CRIMINELLE · RUE · CYBERCRIMINALITÉ   ║
║  ═══════════════════════════════════════════════════════════════════════════  ║
║  🕷️  Scraping v1 conservé (séquentiel, 150+ UA, 2 essais puis source suivante) ║
║  🔁 Auto-discovery: sous-domaine/www/section changés → URL retrouvée seule    ║
║  🎯 Classifieur anti-faux-positifs + score de confiance + pertinence          ║
║  🔗 Fusion multi-sources (une info = plusieurs sources confirmées)            ║
║  🚨 Conflits de rue + alarme sonore (armer/couper/test) + alertes officielles ║
║  📈 Indicateurs façon crypto (RSI, SMA, Bollinger, indice de menace)          ║
║  🗺️  Carte 2D: Carto sombre · plan réel OSM · satellite · chaleur · clusters  ║
║  🌍 5 langues: FR · ES · EN · IT · DE        🖥️  Panneau holographique        ║
║                                                                               ║
║  🛡️ "L'union fait la force" - Devise française                                ║
║                                                                               ║
║     - By Condor2026                                                           ║
║                                         •SpectrumSecurity•                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Dépendances:   pip install flask requests beautifulsoup4
Optionnelles:  pip install matplotlib networkx      (graphiques statiques PNG)

Usage:  python diabolic_france_v3.py                 (menu interactif)
        python diabolic_france_v3.py --web --lang es (panneau web)
        python diabolic_france_v3.py --scan fd       (scan en ligne de commande)
"""

import os
import sys
import io
import re
import csv
import json
import time
import math
import socket
import html as htmllib
import random
import hashlib
import logging
import argparse
import threading
import unicodedata
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, Response, jsonify
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

try:
    import networkx as nx
    HAS_NX = True
except Exception:
    HAS_NX = False

# ============================================================================
# LOGGING  (fichier complet; console seulement les avertissements → terminal propre)
# ============================================================================

_fh = logging.FileHandler('diabolic_france.log', encoding='utf-8')
_fh.setLevel(logging.INFO)
_ch = logging.StreamHandler()
_ch.setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[_fh, _ch])
logger = logging.getLogger('diabolic')
logging.getLogger('urllib3').setLevel(logging.ERROR)      # plus de bruit "Retrying (Retry(total=..."
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# ============================================================================
# CONSTANTES  (valeurs v1 conservées pour le temps de scraping)
# ============================================================================

VERSION = "3.0"
PUERTO = 5016
ARCHIVO_DATOS = 'diabolic_france.json'          # même base que v1/v2 (migration automatique)
ARCHIVO_CACHE = 'url_cache_crime.json'
ARCHIVO_ESTADO = 'estado_fuentes_crime.json'
ARCHIVO_BACKUP = 'diabolic_france_backup.json'
DIR_ESTATICOS = 'graficos_estaticos'
PAGINAS_BUSQUEDA = 3
TIMEOUT = 25
MAX_INTENTOS = 3              # v1 (vérification des sources)
INTENTOS_ESCANEO = 2          # "deux essais et on passe à la source suivante"
DELAY_MIN = 1.3               # v1 = 0.8 (un poco más lento para no ser bloqueado)
DELAY_MAX = 3.2               # v1 = 2.0
PRESUPUESTO_FUENTE = 90       # secondes max par source (aucune source ne bloque le scan)
MAX_ELEMENTOS = 60            # v1 regardait 30 éléments par page
RESPETAR_ROBOTS = False       # v1 ne lisait pas robots.txt (activable: --robots)
UMBRAL_ALARMA = 6             # sévérité minimale d'un conflit de rue pour déclencher l'alarme
AUTO_REFRESH_MIN = 0          # 0 = pas de scan automatique (--auto 30 pour activer)
SENSIBILIDAD = 'equilibrado'  # amplio (≈ v1) | equilibrado | estricto
SCHEMA = 3
_UMBRAL_CONF = {'amplio': 20, 'equilibrado': 45, 'estricto': 60}

# ============================================================================
# IDIOMAS  (fr | es | en | it | de)
# ============================================================================

LANGS = ('fr', 'es', 'en', 'it', 'de')
LANG_FLAGS = {'fr': '🇫🇷', 'es': '🇪🇸', 'en': '🇬🇧', 'it': '🇮🇹', 'de': '🇩🇪'}
LANG_NAMES = {'fr': 'Français', 'es': 'Español', 'en': 'English', 'it': 'Italiano', 'de': 'Deutsch'}
IDIOMA_ACTUAL = 'fr'

_TXT = {
    # ---- general / CLI
    'app_sub': "Surveillance criminelle & cybercriminalité – France|Vigilancia criminal y cibercrimen – Francia|Crime & cybercrime monitoring – France|Monitoraggio di criminalità e cybercrimine – Francia|Überwachung von Kriminalität & Cybercrime – Frankreich",
    'menu_title': "MENU PRINCIPAL|MENÚ PRINCIPAL|MAIN MENU|MENU PRINCIPALE|HAUPTMENÜ",
    'm_search': "Rechercher crimes et cybercrimes|Buscar crímenes y cibercrimen|Search crimes and cybercrime|Cerca crimini e cybercrimine|Verbrechen & Cybercrime suchen",
    'm_analysis': "Analyse complète|Análisis completo|Full analysis|Analisi completa|Gesamtanalyse",
    'm_patterns': "Modèles et tendances|Patrones y tendencias|Patterns and trends|Modelli e tendenze|Muster und Trends",
    'm_evolution': "Évolution mensuelle|Evolución mensual|Monthly evolution|Evoluzione mensile|Monatliche Entwicklung",
    'm_web': "Serveur web (carte + graphes)|Servidor web (mapa + gráficos)|Web server (map + charts)|Server web (mappa + grafici)|Webserver (Karte + Diagramme)",
    'm_last': "20 derniers événements|Últimos 20 eventos|Last 20 events|Ultimi 20 eventi|Letzte 20 Ereignisse",
    'm_export': "Exporter données (JSON/CSV/HTML/GeoJSON)|Exportar datos (JSON/CSV/HTML/GeoJSON)|Export data (JSON/CSV/HTML/GeoJSON)|Esporta dati (JSON/CSV/HTML/GeoJSON)|Daten exportieren (JSON/CSV/HTML/GeoJSON)",
    'm_verify': "Vérifier sources|Verificar fuentes|Verify sources|Verifica fonti|Quellen prüfen",
    'm_types': "Distribution par type|Distribución por tipo|Distribution by type|Distribuzione per tipo|Verteilung nach Typ",
    'm_adv': "Statistiques avancées|Estadísticas avanzadas|Advanced statistics|Statistiche avanzate|Erweiterte Statistiken",
    'm_clean': "Nettoyer doublons|Limpiar duplicados|Remove duplicates|Pulisci duplicati|Duplikate entfernen",
    'm_quick': "Statistiques rapides|Estadísticas rápidas|Quick stats|Statistiche rapide|Schnellstatistik",
    'm_analytics': "Analytique: alertes, tendances, prévision|Analítica: alertas, tendencias, pronóstico|Analytics: alerts, trends, forecast|Analitica: allarmi, tendenze, previsioni|Analytik: Alarme, Trends, Prognose",
    'm_png': "Générer graphiques statiques PNG|Generar gráficos estáticos PNG|Generate static PNG charts|Genera grafici statici PNG|Statische PNG-Diagramme erzeugen",
    'm_exit': "Quitter|Salir|Exit|Esci|Beenden",
    'bye': "Au revoir!|¡Hasta pronto!|See you soon!|Arrivederci!|Auf Wiedersehen!",
    'invalid': "Option invalide|Opción no válida|Invalid option|Opzione non valida|Ungültige Option",
    'processing': "Traitement...|Procesando...|Processing...|Elaborazione...|Verarbeitung...",
    'press_enter': "Entrée pour continuer...|Enter para continuar...|Press Enter to continue...|Invio per continuare...|Eingabe zum Fortfahren...",
    'no_data': "Pas assez de données|Sin datos suficientes|Not enough data|Dati insufficienti|Nicht genug Daten",
    'new_events': "nouveaux événements|eventos nuevos|new events|nuovi eventi|neue Ereignisse",
    'top_type': "Type le plus fréquent|Tipo más común|Most common type|Tipo più comune|Häufigster Typ",
    'top_day': "Jour le plus actif|Día más activo|Most active day|Giorno più attivo|Aktivster Tag",
    'top_source': "Source la plus active|Fuente más activa|Most active source|Fonte più attiva|Aktivste Quelle",
    'top_dept': "Département critique|Departamento crítico|Critical département|Dipartimento critico|Kritisches Département",
    'trend': "Tendance|Tendencia|Trend|Andamento|Trend",
    'severity': "Sévérité|Severidad|Severity|Severità|Schweregrad",
    # ---- web
    'tab_dash': "Tableau de bord|Panel|Dashboard|Pannello|Dashboard",
    'tab_map': "Carte|Mapa|Map|Mappa|Karte",
    'tab_graphs': "Graphiques|Gráficos|Charts|Grafici|Diagramme",
    'tab_network': "Réseau|Red|Network|Rete|Netzwerk",
    'tab_static': "Statiques|Estáticos|Static|Statici|Statisch",
    'tab_feed': "Flux|Flujo|Feed|Flusso|Feed",
    'k_total': "Total événements|Total eventos|Total events|Totale eventi|Ereignisse gesamt",
    'k_7d': "7 derniers jours|Últimos 7 días|Last 7 days|Ultimi 7 giorni|Letzte 7 Tage",
    'k_30d': "30 derniers jours|Últimos 30 días|Last 30 days|Ultimi 30 giorni|Letzte 30 Tage",
    'k_sources': "Sources actives|Fuentes activas|Active sources|Fonti attive|Aktive Quellen",
    'k_depts': "Départements|Departamentos|Départements|Dipartimenti|Départements",
    'k_types': "Types détectés|Tipos detectados|Types detected|Tipi rilevati|Erkannte Typen",
    'k_sev': "Sévérité moyenne|Severidad media|Average severity|Severità media|Ø Schweregrad",
    'k_cyber': "Part cyber|Cuota cyber|Cyber share|Quota cyber|Cyber-Anteil",
    'f_all': "Tout|Todo|All|Tutto|Alle",
    'cat_all': "Tout|Todo|All|Tutto|Alle",
    'cat_phys': "Crime physique|Crimen físico|Physical crime|Crimine fisico|Physische Kriminalität",
    'cat_cyber': "Cybercrime|Cibercrimen|Cybercrime|Cybercrimine|Cybercrime",
    'all_types': "Tous les types|Todos los tipos|All types|Tutti i tipi|Alle Typen",
    'search_ph': "Rechercher...|Buscar...|Search...|Cerca...|Suchen...",
    'btn_update': "Mettre à jour|Actualizar|Update|Aggiorna|Aktualisieren",
    'updating': "Mise à jour en cours|Actualizando|Updating|Aggiornamento in corso|Aktualisierung läuft",
    'm_heat': "Chaleur|Calor|Heat|Calore|Hitze",
    'm_clusters': "Événements (clusters)|Eventos (clusters)|Events (clusters)|Eventi (cluster)|Ereignisse (Cluster)",
    'm_choro': "Choroplèthe départements|Coroplético departamentos|Département choropleth|Coropletica dipartimenti|Choroplethen Départements",
    'm_hot': "Hotspots|Hotspots|Hotspots|Hotspot|Hotspots",
    'c_dept': "Top départements|Top departamentos|Top départements|Top dipartimenti|Top Départements",
    'c_types': "Types de crime|Tipos de crimen|Crime types|Tipi di crimine|Verbrechenstypen",
    'c_monthly': "Évolution mensuelle (physique vs cyber)|Evolución mensual (físico vs cyber)|Monthly evolution (physical vs cyber)|Evoluzione mensile (fisico vs cyber)|Monatsverlauf (physisch vs. Cyber)",
    'c_radar': "Radar des types|Radar de tipos|Type radar|Radar dei tipi|Typ-Radar",
    'c_sev': "Distribution de la sévérité|Distribución de severidad|Severity distribution|Distribuzione severità|Schweregrad-Verteilung",
    'c_weekday': "Carte thermique jour × type|Mapa térmico día × tipo|Heatmap weekday × type|Mappa termica giorno × tipo|Heatmap Wochentag × Typ",
    'c_forecast': "Prévision hebdomadaire (Holt)|Pronóstico semanal (Holt)|Weekly forecast (Holt)|Previsione settimanale (Holt)|Wochenprognose (Holt)",
    'c_sankey': "Flux Sankey: catégorie → type → département|Flujo Sankey: categoría → tipo → departamento|Sankey flow: category → type → département|Flusso Sankey: categoria → tipo → dipartimento|Sankey-Fluss: Kategorie → Typ → Département",
    'c_anom': "Anomalies quotidiennes (z-score)|Anomalías diarias (z-score)|Daily anomalies (z-score)|Anomalie giornaliere (z-score)|Tägliche Anomalien (z-Score)",
    'c_trend': "Mots en tendance|Palabras en tendencia|Trending words|Parole in tendenza|Trendbegriffe",
    'c_net': "Réseau type ↔ département|Red tipo ↔ departamento|Type ↔ département network|Rete tipo ↔ dipartimento|Netzwerk Typ ↔ Département",
    'alerts': "Alertes|Alertas|Alerts|Allarmi|Alarme",
    'alert_ok': "Aucune anomalie détectée|Ninguna anomalía detectada|No anomalies detected|Nessuna anomalia rilevata|Keine Anomalien erkannt",
    'alert_spike': "Pic d'activité|Pico de actividad|Activity spike|Picco di attività|Aktivitätsspitze",
    'hotspots_t': "Zones chaudes|Zonas calientes|Hot zones|Zone calde|Hotspot-Zonen",
    'prev': "← Précédent|← Anterior|← Previous|← Precedente|← Zurück",
    'next': "Suivant →|Siguiente →|Next →|Successivo →|Weiter →",
    'page': "Page|Página|Page|Pagina|Seite",
    'events': "événements|eventos|events|eventi|Ereignisse",
    'open': "Ouvrir|Abrir|Open|Apri|Öffnen",
    'geo_note': "Points géolocalisés au niveau ville ou département (approximatif)|Puntos geolocalizados a nivel ciudad o departamento (aproximado)|Points geolocated at city or département level (approximate)|Punti geolocalizzati a livello città o dipartimento (approssimativo)|Punkte auf Stadt- oder Départementebene geokodiert (ungefähr)",
    'st_tipos': "Répartition par type|Reparto por tipo|Distribution by type|Distribuzione per tipo|Verteilung nach Typ",
    'st_mensual': "Évolution mensuelle|Evolución mensual|Monthly evolution|Evoluzione mensile|Monatsverlauf",
    'st_heatmap': "Jour × type|Día × tipo|Weekday × type|Giorno × tipo|Wochentag × Typ",
    'st_hexbin': "Densité géographique (hexbin)|Densidad geográfica (hexbin)|Geographic density (hexbin)|Densità geografica (hexbin)|Geografische Dichte (Hexbin)",
    'st_red': "Graphe type ↔ département (networkx)|Grafo tipo ↔ departamento (networkx)|Type ↔ département graph (networkx)|Grafo tipo ↔ dipartimento (networkx)|Graph Typ ↔ Département (networkx)",
    'st_missing': "Installez matplotlib (et networkx) pour ce graphique|Instala matplotlib (y networkx) para este gráfico|Install matplotlib (and networkx) for this chart|Installa matplotlib (e networkx) per questo grafico|Installieren Sie matplotlib (und networkx) für dieses Diagramm",
    'phys': "Physique|Físico|Physical|Fisico|Physisch",
    'cyber': "Cyber|Cyber|Cyber|Cyber|Cyber",
    'forecast_lbl': "Prévision|Pronóstico|Forecast|Previsione|Prognose",
    'history_lbl': "Historique|Histórico|History|Storico|Verlauf",
    'motto': "L'union fait la force|La unión hace la fuerza|Strength through unity|L'unione fa la forza|Einigkeit macht stark",
}
_TXT_V3 = {
    'app_sub': "Surveillance criminelle · rue · cybercriminalité – France|Vigilancia criminal · calle · cibercrimen – Francia|Crime · street · cybercrime monitoring – France|Monitoraggio crimine · strada · cybercrimine – Francia|Überwachung Kriminalität · Straße · Cybercrime – Frankreich",
    'm_search': "Scanner tout (crimes, rue, cyber, alertes)|Escanear todo (crimen, calle, cyber, alertas)|Scan everything (crime, street, cyber, alerts)|Scansiona tutto (crimine, strada, cyber, allerte)|Alles scannen (Verbrechen, Straße, Cyber, Warnungen)",
    'm_scan_sub': "Scan ciblé (type / département / source)|Escaneo dirigido (tipo / departamento / fuente)|Targeted scan (type / département / source)|Scansione mirata (tipo / dipartimento / fonte)|Gezielter Scan (Typ / Département / Quelle)",
    'm_gov': "Alertes officielles (CERT-FR, Intérieur…)|Alertas oficiales (CERT-FR, Interior…)|Official alerts (CERT-FR, Interior…)|Allerte ufficiali (CERT-FR, Interno…)|Offizielle Warnungen (CERT-FR, Inneres…)",
    'm_indic': "Indicateurs (RSI, SMA, indice de menace)|Indicadores (RSI, SMA, índice de amenaza)|Indicators (RSI, SMA, threat index)|Indicatori (RSI, SMA, indice di minaccia)|Indikatoren (RSI, SMA, Bedrohungsindex)",
    'm_alarm_test': "Tester l'alarme|Probar la alarma|Test the alarm|Prova l'allarme|Alarm testen",
    'm_health': "Santé des sources (diagnostic des zéros)|Salud de las fuentes (diagnóstico de ceros)|Source health (why zero?)|Salute delle fonti (diagnosi degli zeri)|Quellenstatus (warum null?)",
    'm_sens': "Sensibilité du filtre|Sensibilidad del filtro|Filter sensitivity|Sensibilità del filtro|Filterempfindlichkeit",
    'led_live': "Live|Live|Live|Live|Live",
    'led_scan': "Scan|Scan|Scan|Scan|Scan",
    'led_gov': "Officiel|Oficial|Official|Ufficiale|Offiziell",
    'alarm': "Alarme|Alarma|Alarm|Allarme|Alarm",
    'alarm_conflict': "CONFLIT DÉTECTÉ|CONFLICTO DETECTADO|CONFLICT DETECTED|CONFLITTO RILEVATO|KONFLIKT ERKANNT",
    'alarm_ack': "Couper la sirène|Detener sirena|Stop siren|Ferma sirena|Sirene stoppen",
    'alarm_test': "Test alarme|Probar alarma|Test alarm|Prova allarme|Alarm testen",
    'alarm_mute5': "Silence 5 min|Silenciar 5 min|Mute 5 min|Muto 5 min|Stumm 5 Min.",
    'alarm_vol': "Volume|Volumen|Volume|Volume|Lautstärke",
    'alarm_thr': "Seuil de sévérité|Umbral de severidad|Severity threshold|Soglia di gravità|Schweregrad-Schwelle",
    'alarm_sound': "Son|Sonido|Sound|Suono|Ton",
    'alarm_notif': "Notification navigateur|Notificación del navegador|Browser notification|Notifica del browser|Browser-Benachrichtigung",
    'alarm_hist': "HISTORIQUE|HISTORIAL|HISTORY|STORICO|VERLAUF",
    'alarm_arm': "Armer|Armar|Arm|Attiva|Scharfschalten",
    'alarm_disarm': "Désarmer|Desarmar|Disarm|Disattiva|Entschärfen",
    'alarm_off': "Éteinte|Apagada|Off|Spenta|Aus",
    'alarm_muted': "En sourdine|Silenciada|Muted|In muto|Stumm",
    'alarm_armed': "Armée|Armada|Armed|Attiva|Scharf",
    'alarm_ringing': "SONNE|SONANDO|RINGING|SUONA|ALARM",
    'alarm_click': "Cliquez Armer ou Test pour activer le son du navigateur|Pulsa Armar o Test para activar el sonido del navegador|Click Arm or Test to enable browser sound|Clicca Attiva o Prova per abilitare l'audio|Auf Scharfschalten oder Test klicken, um den Ton zu aktivieren",
    'gov_alerts': "ALERTES OFFICIELLES|ALERTAS OFICIALES|OFFICIAL ALERTS|ALLERTE UFFICIALI|OFFIZIELLE WARNUNGEN",
    'gov_none': "Aucune alerte officielle chargée — lancez le scan « Officiel »|Ninguna alerta oficial cargada — lanza el escaneo «Oficial»|No official alert loaded — run the “Official” scan|Nessuna allerta ufficiale — avvia la scansione «Ufficiale»|Keine offizielle Warnung geladen — „Offiziell“-Scan starten",
    'vig_set': "niveau à définir|nivel por definir|set level|imposta livello|Stufe setzen",
    'vig_1': "Vigilance|Vigilancia|Vigilance|Vigilanza|Wachsamkeit",
    'vig_2': "Sécurité renforcée – risque attentat|Seguridad reforzada – riesgo atentado|Reinforced security – attack risk|Sicurezza rafforzata – rischio attentato|Verstärkte Sicherheit – Anschlagsrisiko",
    'vig_3': "Urgence attentat|Urgencia atentado|Attack emergency|Emergenza attentato|Anschlagsnotstand",
    'vig_prompt': "Niveau Vigipirate en vigueur (1 Vigilance, 2 Sécurité renforcée, 3 Urgence attentat, 0 inconnu). Vérifiez sur info.gouv.fr|Nivel Vigipirate vigente (1 Vigilancia, 2 Seguridad reforzada, 3 Urgencia atentado, 0 desconocido). Verifica en info.gouv.fr|Current Vigipirate level (1 Vigilance, 2 Reinforced, 3 Attack emergency, 0 unknown). Check info.gouv.fr|Livello Vigipirate attuale (1 Vigilanza, 2 Rafforzata, 3 Emergenza, 0 sconosciuto). Verifica su info.gouv.fr|Aktuelle Vigipirate-Stufe (1 Wachsamkeit, 2 Verstärkt, 3 Notstand, 0 unbekannt). Prüfen auf info.gouv.fr",
    'btn_scan_all': "Scanner tout|Escanear todo|Scan all|Scansiona tutto|Alles scannen",
    'btn_scan_fd': "Faits divers + rue|Sucesos + calle|Crime + street|Cronaca + strada|Kriminalität + Straße",
    'btn_scan_cyber': "Cyber|Cyber|Cyber|Cyber|Cyber",
    'btn_scan_gov': "Officiel|Oficial|Official|Ufficiale|Offiziell",
    'btn_stop': "Stop|Parar|Stop|Ferma|Stopp",
    'btn_verify': "Vérifier sources|Verificar fuentes|Verify sources|Verifica fonti|Quellen prüfen",
    'btn_mute': "Sourdine|Silencio|Mute|Muto|Stumm",
    'btn_full': "Plein écran|Pantalla completa|Fullscreen|Schermo intero|Vollbild",
    'btn_copy': "Copier le lien|Copiar enlace|Copy link|Copia link|Link kopieren",
    'btn_reset': "Réinitialiser|Restablecer|Reset|Reimposta|Zurücksetzen",
    'copied': "Copié ✔|Copiado ✔|Copied ✔|Copiato ✔|Kopiert ✔",
    'tab_scan': "Scan / Sources|Escaneo / Fuentes|Scan / Sources|Scansione / Fonti|Scan / Quellen",
    'cat_all': "Tout|Todo|All|Tutto|Alle",
    'cat_phys': "Crime|Crimen|Crime|Crimine|Kriminalität",
    'cat_rue': "Conflits de rue|Conflictos callejeros|Street conflicts|Conflitti di strada|Straßenkonflikte",
    'cat_cyber': "Cybercrime|Cibercrimen|Cybercrime|Cybercrimine|Cybercrime",
    'conf_any': "Toute fiabilité|Cualquier fiabilidad|Any confidence|Qualsiasi affidabilità|Beliebige Verlässlichkeit",
    'conf_med': "Fiabilité ≥ 45%|Fiabilidad ≥ 45%|Confidence ≥ 45%|Affidabilità ≥ 45%|Verlässlichkeit ≥ 45%",
    'conf_high': "Fiabilité ≥ 60%|Fiabilidad ≥ 60%|Confidence ≥ 60%|Affidabilità ≥ 60%|Verlässlichkeit ≥ 60%",
    'k_conf24': "Conflits 24h|Conflictos 24h|Conflicts 24h|Conflitti 24h|Konflikte 24h",
    'k_multi': "Multi-sources|Multi-fuente|Multi-source|Multi-fonte|Mehrfachquellen",
    'k_sev': "Sévérité moyenne|Severidad media|Average severity|Severità media|Ø Schweregrad",
    'threat_idx': "Indice de menace|Índice de amenaza|Threat index|Indice di minaccia|Bedrohungsindex",
    'th_calm': "CALME|CALMA|CALM|CALMA|RUHIG",
    'th_watch': "VIGILANCE|VIGILANCIA|WATCH|VIGILANZA|WACHSAM",
    'th_tense': "TENDU|TENSO|TENSE|TESO|ANGESPANNT",
    'th_crit': "CRITIQUE|CRÍTICO|CRITICAL|CRITICO|KRITISCH",
    'vol': "Volatilité|Volatilidad|Volatility|Volatilità|Volatilität",
    'signal': "Signal|Señal|Signal|Segnale|Signal",
    'sig_up': "ESCALADE|ESCALADA|ESCALATION|ESCALATION|ESKALATION",
    'sig_dn': "APAISEMENT|DISTENSIÓN|DE-ESCALATION|DISTENSIONE|ENTSPANNUNG",
    'sig_neu': "NEUTRE|NEUTRO|NEUTRAL|NEUTRO|NEUTRAL",
    'c_boll': "Flux quotidien · SMA7/30 · Bollinger|Flujo diario · SMA7/30 · Bollinger|Daily flow · SMA7/30 · Bollinger|Flusso giornaliero · SMA7/30 · Bollinger|Tagesfluss · SMA7/30 · Bollinger",
    'c_street': "Conflits de rue récents|Conflictos callejeros recientes|Recent street conflicts|Conflitti di strada recenti|Aktuelle Straßenkonflikte",
    'c_toprel': "Les plus pertinents|Los más relevantes|Most relevant|I più rilevanti|Relevanteste",
    'c_weekly': "Hebdomadaire par catégorie|Semanal por categoría|Weekly by category|Settimanale per categoria|Wöchentlich nach Kategorie",
    'c_bubble': "Départements: volume × sévérité|Departamentos: volumen × severidad|Départements: volume × severity|Dipartimenti: volume × gravità|Départements: Volumen × Schweregrad",
    'c_monthly': "Évolution mensuelle par catégorie|Evolución mensual por categoría|Monthly evolution by category|Evoluzione mensile per categoria|Monatsverlauf nach Kategorie",
    'm_pulse': "Conflits de rue (pulsation)|Conflictos callejeros (pulso)|Street conflicts (pulse)|Conflitti di strada (pulsazione)|Straßenkonflikte (Puls)",
    'm_timelapse': "Timelapse 30j|Timelapse 30d|Timelapse 30d|Timelapse 30g|Zeitraffer 30T",
    'm_fit': "Voir sur la carte|Ver en el mapa|Show on map|Mostra sulla mappa|Auf Karte zeigen",
    'map_dark': "Carto sombre|Carto oscuro|Carto dark|Carto scuro|Carto dunkel",
    'map_street': "Plan réel (OpenStreetMap)|Plano real (OpenStreetMap)|Real street map (OpenStreetMap)|Mappa reale (OpenStreetMap)|Echter Stadtplan (OpenStreetMap)",
    'map_osmfr': "OSM France|OSM Francia|OSM France|OSM Francia|OSM Frankreich",
    'map_voyager': "Carto Voyager|Carto Voyager|Carto Voyager|Carto Voyager|Carto Voyager",
    'map_light': "Carto clair|Carto claro|Carto light|Carto chiaro|Carto hell",
    'map_sat': "Satellite (Esri)|Satélite (Esri)|Satellite (Esri)|Satellite (Esri)|Satellit (Esri)",
    'sort_by': "Trier par|Ordenar por|Sort by|Ordina per|Sortieren nach",
    'sort_date': "Date|Fecha|Date|Data|Datum",
    'sort_rel': "Pertinence|Relevancia|Relevance|Rilevanza|Relevanz",
    'sort_sev': "Sévérité|Severidad|Severity|Gravità|Schweregrad",
    'relevance': "Pertinence|Relevancia|Relevance|Rilevanza|Relevanz",
    'sources_lbl': "Sources|Fuentes|Sources|Fonti|Quellen",
    'confirmed_by': "Confirmé par|Confirmado por|Confirmed by|Confermato da|Bestätigt von",
    'scan_ctl': "Lancer un scan|Lanzar un escaneo|Launch a scan|Avvia una scansione|Scan starten",
    'scan_pages': "Pages|Páginas|Pages|Pagine|Seiten",
    'scan_sens': "Sensibilité|Sensibilidad|Sensitivity|Sensibilità|Empfindlichkeit",
    'sens_wide': "Large (≈ v1)|Amplia (≈ v1)|Wide (≈ v1)|Ampia (≈ v1)|Breit (≈ v1)",
    'sens_bal': "Équilibrée|Equilibrada|Balanced|Bilanciata|Ausgewogen",
    'sens_strict': "Stricte|Estricta|Strict|Rigida|Streng",
    'scan_dep': "Département|Departamento|Département|Dipartimento|Département",
    'scan_src': "Source|Fuente|Source|Fonte|Quelle",
    'scan_note': "Un scan à la fois. Deux essais par source puis on passe à la suivante; si le domaine ou la section change, l'URL est retrouvée automatiquement.|Un escaneo a la vez. Dos intentos por fuente y se pasa a la siguiente; si cambia el dominio o la sección, la URL se encuentra sola.|One scan at a time. Two tries per source, then on to the next; if the domain or section changes the URL is found automatically.|Una scansione alla volta. Due tentativi per fonte, poi si passa alla successiva; se cambia dominio o sezione l'URL viene ritrovato da solo.|Ein Scan gleichzeitig. Zwei Versuche pro Quelle, dann die nächste; ändert sich Domain oder Rubrik, wird die URL automatisch gefunden.",
    'scan_console': "Terminal en direct|Terminal en vivo|Live terminal|Terminale live|Live-Terminal",
    'scan_sources': "Sources|Fuentes|Sources|Fonti|Quellen",
    'scan_busy': "Un scan est déjà en cours|Ya hay un escaneo en curso|A scan is already running|Una scansione è già in corso|Ein Scan läuft bereits",
    'src_name': "Nom|Nombre|Name|Nome|Name",
    'src_type': "Type|Tipo|Type|Tipo|Typ",
    'src_note': "État|Estado|Status|Stato|Status",
    'src_dep': "Département|Departamento|Département|Dipartimento|Département",
    'add_source': "Ajouter une source|Añadir fuente|Add source|Aggiungi fonte|Quelle hinzufügen",
    'official_links': "Liens officiels|Enlaces oficiales|Official links|Link ufficiali|Offizielle Links",
    'status_ok': "OK|OK|OK|OK|OK",
    'status_empty': "0 résultat|0 resultados|0 results|0 risultati|0 Ergebnisse",
    'status_dns': "Domaine mort|Dominio muerto|Dead domain|Dominio morto|Domain tot",
    'status_blocked': "Bloquée|Bloqueada|Blocked|Bloccata|Blockiert",
    'status_gone': "URL disparue|URL desaparecida|URL gone|URL scomparso|URL verschwunden",
    'status_err': "Erreur|Error|Error|Errore|Fehler",
    'status_idle': "Jamais scannée|Sin escanear|Never scanned|Mai scansionata|Nie gescannt",
    'updating': "Scan en cours|Escaneando|Scanning|Scansione in corso|Scan läuft",
    'm_pulse_': "-|-|-|-|-",
}
_TXT.update(_TXT_V3)

TEXTOS = {l: {} for l in LANGS}
for _k, _v in _TXT.items():
    _p = _v.split('|')
    for _i, _l in enumerate(LANGS):
        TEXTOS[_l][_k] = _p[_i] if _i < len(_p) else _p[0]


def t(clave):
    return TEXTOS.get(IDIOMA_ACTUAL, TEXTOS['fr']).get(clave, TEXTOS['fr'].get(clave, clave))

# ============================================================================
# COLORES / CONSOLA
# ============================================================================

class Color:
    BLACK = '\033[30m'; RED = '\033[91m'; DARK_RED = '\033[31m'
    GREEN = '\033[92m'; DARK_GREEN = '\033[32m'; YELLOW = '\033[93m'
    DARK_YELLOW = '\033[33m'; BLUE = '\033[94m'; DARK_BLUE = '\033[34m'
    MAGENTA = '\033[95m'; DARK_MAGENTA = '\033[35m'; CYAN = '\033[96m'
    DARK_CYAN = '\033[36m'; WHITE = '\033[97m'; GRAY = '\033[90m'; LIGHT_GRAY = '\033[37m'
    BOLD = '\033[1m'; DIM = '\033[2m'; ITALIC = '\033[3m'; UNDERLINE = '\033[4m'
    BLINK = '\033[5m'; REVERSE = '\033[7m'; RESET = '\033[0m'
    BG_RED = '\033[41m'


_COLOR_MAP = {
    'black': Color.BLACK, 'red': Color.RED, 'dark_red': Color.DARK_RED, 'green': Color.GREEN,
    'dark_green': Color.DARK_GREEN, 'yellow': Color.YELLOW, 'dark_yellow': Color.DARK_YELLOW,
    'blue': Color.BLUE, 'dark_blue': Color.DARK_BLUE, 'magenta': Color.MAGENTA,
    'dark_magenta': Color.DARK_MAGENTA, 'cyan': Color.CYAN, 'dark_cyan': Color.DARK_CYAN,
    'white': Color.WHITE, 'gray': Color.GRAY, 'light_gray': Color.LIGHT_GRAY,
}


def cprint(texto, color=None, bold=False, dim=False, italic=False, underline=False,
           blink=False, bg=False, end='\n'):
    s = ''
    if bold: s += Color.BOLD
    if dim: s += Color.DIM
    if italic: s += Color.ITALIC
    if underline: s += Color.UNDERLINE
    if blink: s += Color.BLINK
    col = _COLOR_MAP.get(color, '') if color else ''
    print(f"{Color.BG_RED if bg else ''}{s}{col}{texto}{Color.RESET}", end=end, flush=True)


# ============================================================================
# USER-AGENTS  (la liste complète de la v1, sans modification)
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
# BUS D'INFORMATION  (terminal + panneau web partagent le même flux)
# ============================================================================

LOG = deque(maxlen=800)
_LOG_SEQ = [0]
_LOG_LOCK = threading.Lock()
TERMINAL_OUT = True
STATE = {'version': 0, 'tick': 0, 'alarm_seq': 0, 'alarm': {'seq': 0, 'items': [], 'test': False}}
_NIVEL_COLOR = {'ok': 'green', 'warn': 'yellow', 'err': 'red', 'info': 'cyan', 'dim': 'gray', 'disc': 'magenta', 'alarm': 'red'}


def emit(nivel, msg, end='\n'):
    """Écrit dans le terminal ET dans le flux SSE du panneau."""
    with _LOG_LOCK:
        _LOG_SEQ[0] += 1
        LOG.append({'i': _LOG_SEQ[0], 't': datetime.now().strftime('%H:%M:%S'), 'l': nivel, 'm': msg})
        STATE['tick'] += 1
    if TERMINAL_OUT:
        if nivel == 'alarm':
            cprint(f"\a {msg} ", 'white', bold=True, bg=True, end=end)
        else:
            cprint(msg, _NIVEL_COLOR.get(nivel, 'white'), dim=(nivel == 'dim'), end=end)

# ============================================================================
# HTTP  (logique v1: UA aléatoire, 3 essais, pause entre essais; + échec rapide si DNS mort)
# ============================================================================

_SESSION = None
_ROBOTS = {}
_ROBOTS_LOCK = threading.Lock()
_DNS_CACHE = {}
_HOST_LAST = {}
_HOST_LOCK = threading.Lock()


def _session():
    global _SESSION
    if _SESSION is None:
        s = requests.Session()
        # v1: Retry(total=2, read=2, connect=2, backoff 0.5). On ajoute: pas de Retry-After (une source
        # qui répond "attends 1h" ne doit pas geler le scan) et pas d'exception sur statut.
        retry = Retry(total=2, read=2, connect=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504],
                      respect_retry_after_header=False, raise_on_status=False)
        ad = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        s.mount('http://', ad)
        s.mount('https://', ad)
        _SESSION = s
    return _SESSION


def _usa_proxy():
    return any(os.environ.get(k) for k in ('HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy', 'ALL_PROXY'))


def dns_ok(host):
    """Vérifie une fois (cache 10 min) que le domaine existe → un domaine mort ne coûte plus 6 essais."""
    if not host or _usa_proxy():
        return True
    c = _DNS_CACHE.get(host)
    if c and time.time() - c[1] < 600:
        return c[0]
    try:
        socket.getaddrinfo(host, 443)
        ok = True
    except socket.gaierror:
        ok = False
    except Exception:
        ok = True
    _DNS_CACHE[host] = (ok, time.time())
    return ok


def robots_ok(url):
    if not RESPETAR_ROBOTS:
        return True
    p = urlparse(url)
    base = f'{p.scheme}://{p.netloc}'
    with _ROBOTS_LOCK:
        rp = _ROBOTS.get(base, False)
    if rp is False:
        rp = None
        try:
            r = requests.get(base + '/robots.txt', timeout=10, headers={'User-Agent': get_random_ua()})
            if r.status_code == 200:
                rp = robotparser.RobotFileParser()
                rp.parse(r.text.splitlines())
        except Exception:
            rp = None
        with _ROBOTS_LOCK:
            _ROBOTS[base] = rp
    return True if rp is None else rp.can_fetch('*', url)


def _cortesia(host, minimo=1.1):
    with _HOST_LOCK:
        now = time.time()
        wait = minimo - (now - _HOST_LAST.get(host, 0))
        _HOST_LAST[host] = now + max(0.0, wait)
    if wait > 0:
        time.sleep(wait)


def fetch(url, intentos=MAX_INTENTOS, timeout=TIMEOUT):
    """-> (response|None, kind). kind: ok | dns | gone | blocked | timeout | ssl | conn | http | robots | error"""
    p = urlparse(url or '')
    if p.scheme not in ('http', 'https') or not p.netloc:
        return None, 'error'
    if not dns_ok(p.hostname):
        return None, 'dns'
    if not robots_ok(url):
        return None, 'robots'
    kind = 'error'
    for _ in range(intentos):
        _cortesia(p.netloc)
        try:
            headers = {'User-Agent': get_random_ua(), 'Accept-Language': 'fr-FR,fr;q=0.9',                 # idem v1 + cabeceras de navegador
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Referer': 'https://www.google.fr/', 'Upgrade-Insecure-Requests': '1', 'DNT': '1'}
            r = _session().get(url, timeout=timeout, headers=headers, allow_redirects=True)
            sc = r.status_code
            if sc == 200:
                return r, 'ok'
            if sc in (404, 410):
                return None, 'gone'
            kind = 'blocked' if sc in (401, 403, 406, 429, 451, 503) else 'http'
            time.sleep(get_random_delay() * (2 if sc == 429 else 1))
        except requests.exceptions.SSLError:
            kind = 'ssl'
            time.sleep(get_random_delay())
        except requests.exceptions.ConnectionError as e:
            s = str(e)
            if any(x in s for x in ('NameResolution', 'Name or service not known', 'getaddrinfo', 'nodename nor servname')):
                return None, 'dns'
            kind = 'conn'
            time.sleep(get_random_delay())
        except requests.exceptions.Timeout:
            kind = 'timeout'
            time.sleep(get_random_delay())
        except Exception:
            kind = 'error'
            time.sleep(get_random_delay())
    return None, kind


def http_get(url, timeout=TIMEOUT, intentos=MAX_INTENTOS):
    return fetch(url, intentos, timeout)[0]

# ============================================================================
# NORMALISATION
# ============================================================================

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    s = re.sub(r"[’'`\-_/]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def limpiar(s):
    return re.sub(r'\s+', ' ', (s or '').replace('\xa0', ' ')).strip()


# ============================================================================
# MOTS-CLÉS v1 (mode "amplio" = rappel maximal comme la v1)
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
    'féminicide', 'violence conjugale',
    # v3: rue + cyber
    'émeute', 'rixe', 'violences urbaines', 'guet-apens', 'tirs', 'coups de feu', 'caillass',
    'cyberattaque', 'ransomware', 'rançongiciel', 'phishing', 'hameçonnage', 'piratage', 'fuite de données',
]

# ============================================================================
# TYPES  (physique · rue · cyber)   clé, icône, couleur, catégorie, sévérité, poids, noms(fr|es|en|it|de), fort, faible
#  fort  = mot sans ambiguïté (suffit seul)      faible = mot ambigu (exige un indice policier/judiciaire)
# ============================================================================

_TIPOS = [
    # ------------------------------------------------ crime physique
    ('homicide', '🔪', '#ff2d55', 'fisico', 8, 1.0, 'Homicide / Meurtre|Homicidio|Homicide / Murder|Omicidio|Tötungsdelikt',
     r"meurtres?|homicides?|assassinats?|assassine\w*|feminicides?|egorge\w*|corps sans vie|cadavres?|retrouvee? morte?s?|mort violente|mortellement (?:poignarde|agresse|frappe|blesse|tire|roue de coups)|poignarde\w* a mort|tue\w* (?:par balles?|a coups|de plusieurs coups|de plusieurs balles)|battu\w* a mort|etrangle\w*|decapit\w*",
     r"tue\w*|morts?|decede\w*|deces|meurtrier\w*|victimes?"),
    ('terrorisme', '💣', '#c4b5fd', 'fisico', 9, 1.2, 'Terrorisme / Attentat|Terrorismo|Terrorism / Attack|Terrorismo|Terrorismus',
     r"attentats?|terroristes?|terrorisme|djihad\w*|jihad\w*|radicalise\w*|pnat|parquet national antiterroriste|apologie du terrorisme|attaque terroriste|menace terroriste|daech|etat islamique", None),
    ('viol', '⚠️', '#e11d48', 'fisico', 7, 1.0, 'Viol / Agression sexuelle|Violación|Rape / Sexual assault|Stupro|Vergewaltigung',
     r"viols?|violee?s?|violeurs?|violer|agressions? sexuelles?|attouchements?|violences? sexuelles?|exhibition sexuelle|pedocriminal\w*|pedophil\w*|abus sexuels?|agresseurs? sexuels?", None),
    ('braquage', '🔫', '#f97316', 'fisico', 6, 1.0, 'Braquage / Hold-up|Atraco|Armed robbery|Rapina|Raubüberfall',
     r"braquages?|braqueurs?|braquent|braquerent|hold up|vols? a main armee|prises? d otages?|preneurs? d otages?", None),
    ('gang', '👥', '#be123c', 'fisico', 6, 1.0, 'Gang / Règlement de comptes|Pandilla|Gang / Score settling|Gang|Bande / Abrechnung',
     r"reglements? de comptes|crime organise|mafia\w*|banditisme|narcobanditisme|gangs? rivaux|dz mafia", r"gangs?|bandes?"),
    ('kidnapping', '⛓️', '#db2777', 'fisico', 6, 1.0, 'Enlèvement / Séquestration|Secuestro|Kidnapping|Sequestro|Entführung',
     r"enlevements?|enleve\w*|kidnapp\w*|sequestr\w*|alerte enlevement|disparition inquietante", None),
    ('violence', '👊', '#fb923c', 'fisico', 4, 0.9, 'Violence / Agression|Violencia|Violence / Assault|Violenza|Gewalt',
     r"coups? de couteau|coups? de poing|poignard\w*|passages? a tabac|violences? conjugales?|violences? intrafamiliales?|tabasse\w*|agresse\w*|agressions?|agresseurs?|lynch\w*|coups et blessures|violences? volontaires?|violences? en reunion|mutile\w*|blesse\w* (?:grievement|au couteau|a l arme blanche)",
     r"violences?|blesse\w*|blessures?"),
    ('incendie', '🔥', '#ea580c', 'fisico', 4, 1.0, 'Incendie criminel|Incendio provocado|Arson|Incendio doloso|Brandstiftung',
     r"incendies? criminels?|incendies? volontaires?|pyromanes?|mises? a feu|voitures? brulee?s?|vehicules? brules?|incendies? d origine criminelle|incendiaires?",
     r"incendies?|feux?"),
    ('narcotrafic', '💊', '#d946ef', 'fisico', 4, 0.9, 'Narcotrafic / Drogue|Narcotráfico|Drug trafficking|Narcotraffico|Drogenhandel',
     r"narcotraf\w*|narco\w*|stupefiants?|cocaine|heroine|trafics? de drogues?|trafiquants? de drogues?|points? de deal|saisies? de (?:drogues?|cannabis|cocaine|resine|stupefiants)|go fast|dealers?|plantations? de cannabis",
     r"cannabis|drogues?|deals?|trafics?|stups?|crack|mdma|ecstasy|opioides?"),
    ('cambriolage', '🚪', '#eab308', 'fisico', 3, 0.9, 'Cambriolage / Vol|Robo|Burglary / Theft|Furto|Einbruch / Diebstahl',
     r"cambriol\w*|effractions?|voleurs?|receleurs?|recel|vols? (?:avec violence|a main armee|a l etalage|a la tire|a la roulotte|de voitures?|de vehicules?|de bijoux|en reunion|de cuivre|de materiel|de carburant|de colis|de velos?|de motos?|de scooters?|de telephones?|de portables?|par ruse|aggraves?)|carjacking|car jacking",
     r"vols?|voles?|derobe\w*"),
    ('fraude', '💼', '#a3a3a3', 'fisico', 3, 0.8, 'Escroquerie / Fraude|Estafa / Fraude|Fraud / Scam|Truffa / Frode|Betrug',
     r"escroqueries?|abus de confiance|fraudes? fiscales?|blanchiment|faux et usage de faux|detournements? de fonds|abus de faiblesse|escrocs?|fraudes? (?:aux?|a la) (?:allocations?|assurance|tva|subventions?)|travail dissimule|corruption|trafic d influence|prise illegale d interet|favoritisme",
     r"fraudes?|arnaques?"),
    # ------------------------------------------------ conflits de rue
    ('emeutes', '🚨', '#ff3b30', 'rue', 7, 1.1, 'Émeutes / Violences urbaines|Disturbios / Violencia urbana|Riots / Urban violence|Rivolte / Violenza urbana|Ausschreitungen / Urbane Gewalt',
     r"emeutes?|emeutiers?|violences? urbaines?|guerilla urbaine|nuits? de violences|nuits? d emeutes|couvre feu|pillages?|tirs? de mortiers?|mortiers? d artifice|caillass\w*|jets? de pierres?|jets? de projectiles?|barricades?|saccage\w*|affrontements? (?:avec|entre|a|au|dans|devant|opposant)|echauffouree\w*|heurts? (?:avec|entre)|quartiers? sous tension|scenes? de chaos",
     r"affrontements?|heurts?|incidents?|troubles?|tensions?|degradations?"),
    ('rixe', '🥊', '#ff7a00', 'rue', 5, 1.0, 'Rixe / Bagarre|Riña / Pelea|Brawl / Fight|Rissa / Scontro|Schlägerei / Rauferei',
     r"rixes?|bagarres?|bagarre generale|bandes? rivales?|affrontements? entre (?:bandes|jeunes|groupes|supporters|quartiers)|guets? apens|lynchage|expeditions? punitives?|baston|bataille rangee|ultras? (?:s affrontent|violents?)|supporters? (?:s affrontent|violents?)", None),
    ('fusillade', '💥', '#ff1744', 'rue', 8, 1.2, 'Fusillade / Tirs|Tiroteo / Disparos|Shooting / Gunfire|Sparatoria / Spari|Schießerei / Schüsse',
     r"fusillades?|coups? de feu|tirs? (?:de kalachnikov|a l arme|d arme|de kalach|en pleine rue|nourris|de riposte)|kalachnikov|kalach|(?:blesse|touche|tue|atteint)\w* par balles?|balles? perdues?|tirs? sur (?:un|des|la|le|les)", None),
    ('attaque_forces', '🛡️', '#ff5252', 'rue', 6, 1.1, "Attaque contre forces de l'ordre / secours|Ataque a fuerzas del orden / socorro|Attack on police / rescuers|Attacco a forze dell'ordine / soccorsi|Angriff auf Polizei / Rettungskräfte",
     r"(?:policiers?|gendarmes?|pompiers?|agents?|forces de l ordre|crs|bac|surveillants?|controleurs?|chauffeurs? de bus|soignants?|enseignants?|professeurs?|maires?|elus?) (?:agresses?|attaques?|blesses?|caillasses?|vises?|pris(?:es)? pour cible|molestes?)|attaques? (?:d un|du|contre un|contre le|contre les) (?:commissariat|poste de police|vehicules? de police|policiers|gendarmes|pompiers|caserne)|commissariats? (?:attaques?|vises?|incendies?|pris pour cible|caillasses?)|agressions? (?:de|d) (?:un |une |des )?(?:policiers?|gendarmes?|pompiers?)", None),
    ('manif', '📢', '#ff9100', 'rue', 4, 1.0, 'Manifestation violente / Casseurs|Manifestación violenta / Vandalismo|Violent protest / Rioters|Manifestazione violenta / Vandali|Gewalttätige Demo / Randalierer',
     r"casseurs?|black blocs?|blackblocs?|manifestations? (?:violentes?|degenere\w*|sous tension|sauvages?)|gaz lacrymogenes?|lacrymogenes?|canons? a eau|charges? policieres?|charges? des forces de l ordre|interpellations? (?:en marge|lors d une manifestation|lors de la manifestation)|blocages? violents?|ultragauche|ultradroite",
     r"manifestations?|manifestants?"),
    ('rodeo', '🏍️', '#ffb300', 'rue', 3, 0.9, "Rodéo urbain / Refus d'obtempérer|Rodeo urbano / Desobediencia|Street racing / Failure to comply|Rodeo urbano / Rifiuto di fermarsi|Straßenrennen / Flucht vor Polizei",
     r"rodeos? (?:urbains?|sauvages?)|rodeos?|courses? poursuites?|refus d obtemperer|delits? de fuite|fonce sur (?:les |des )?(?:policiers|gendarmes)|(?:policiers?|gendarmes?) (?:percutes?|renverses?)", None),
    # ------------------------------------------------ cybercriminalité
    ('ransomware', '🔐', '#ff4d6d', 'cyber', 7, 1.2, 'Ransomware / Rançongiciel|Ransomware|Ransomware|Ransomware|Ransomware',
     r"ransomwares?|rancongiciels?|ranconnage|lockbit|blackcat|alphv|akira|demandes? de rancon|chiffre\w* (?:les )?donnees|cyberattaques? par rancon\w*", None),
    ('cyber_fuite', '💧', '#00e5ff', 'cyber', 6, 1.1, 'Fuite de données|Fuga de datos|Data breach|Violazione dati|Datenleck',
     r"fuites? de donnees|fuites? massives?|donnees personnelles (?:derobees|volees|piratees|exposees|dans la nature)|data (?:leak|breach)|violations? de donnees|vols? de donnees|bases? de donnees (?:piratee|exposee|en vente)|mis(?:es)? en vente (?:sur|dans) (?:un )?forum|breachforums|cnil (?:sanctionne|amende|saisie)", None),
    ('ddos', '🌐', '#8b5cff', 'cyber', 4, 1.1, 'DDoS / Déni de service|DDoS|DDoS / Denial of service|DDoS|DDoS',
     r"ddos|deni de service|attaques? par deni|botnets?|noname057", None),
    ('phishing', '🎣', '#2bffb4', 'cyber', 3, 1.0, 'Phishing / Hameçonnage|Phishing|Phishing|Phishing|Phishing',
     r"phishing|hameconnage|smishing|vishing|quishing|faux (?:sms|mails?|courriels?|sites?|conseillers?)|usurpations? d identite|spoofing", None),
    ('cyber_arnaque', '💳', '#14b8a6', 'cyber', 3, 1.0, 'Arnaque en ligne|Estafa online|Online scam|Truffa online|Online-Betrug',
     r"arnaques? en ligne|escroqueries? (?:en ligne|sur internet|numerique)|fraudes? (?:a la carte bancaire|bancaire|en ligne|au cpf)|faux (?:investissements?|placements?)|arnaques? (?:crypto|cpf|a la romance)|brouteurs?|ingenierie sociale|fraudes? au president|faux ordres? de virement|pig butchering", None),
    ('harcelement', '🧷', '#f472b6', 'cyber', 4, 1.0, 'Cyberharcèlement|Ciberacoso|Cyberbullying|Cyberbullismo|Cybermobbing',
     r"cyberharcelement\w*|cyber harcelement|harcelements? (?:en ligne|sur les reseaux)|revenge porn|deepfakes?|sextorsion", None),
    ('piratage', '🕷️', '#3b82f6', 'cyber', 5, 0.6, 'Piratage / Cyberattaque|Hackeo / Ciberataque|Hacking / Cyberattack|Hacking / Attacco informatico|Hacking / Cyberangriff',
     r"piratage\w*|pirates? informatiques?|cyberattaques?|cyber attaques?|intrusions? informatiques?|hackers?|hacke\w*|infostealers?|attaques? informatiques?|compromission|revendiquent? (?:l|une) (?:attaque|cyberattaque)|logiciels? malveillants?|malwares?|trojans?",
     r"cybercriminel\w*|cybercriminalite|cybersecurite|vulnerabilit\w*|failles?"),
]


def _rx(s):
    return re.compile(r'\b(?:' + s + r')\b')


TIPOS_CRIMEN = {}
for _k, _i, _c, _cat, _sev, _w, _n, _s, _wk in _TIPOS:
    _nm = _n.split('|')
    TIPOS_CRIMEN[_k] = {
        'icono': _i, 'color': _c, 'cat': _cat, 'sev': _sev, 'peso': _w,
        'nombre': _nm[0], 'fr': _nm[0], 'es': _nm[1], 'en': _nm[2], 'it': _nm[3], 'de': _nm[4],
        'srx': _rx(_s), 'wrx': _rx(_wk) if _wk else None,
    }
TIPOS_CRIMEN['other'] = {'icono': '❓', 'color': '#6b7280', 'cat': 'fisico', 'sev': 2, 'peso': 0,
                         'nombre': 'Autre', 'fr': 'Autre', 'es': 'Otro', 'en': 'Other', 'it': 'Altro', 'de': 'Sonstiges',
                         'srx': re.compile(r'$^'), 'wrx': None}
CATEGORIAS = ('fisico', 'rue', 'cyber')

# ---- expressions neutralisées avant analyse (usages non criminels des mots ambigus)
_SCRUB = re.compile(r"\b(?:enlevements? (?:des? |du )?(?:dechets|ordures|encombrants|vehicules?|epaves|neige|gravats)|"
                    r"vols? (?:de nuit|libre|retour|aller|direct|long courrier|plane|regulier|commercial|spatial|inaugural|habite|domestique|annules?|retardes?|perturbes?)|"
                    r"bande (?:dessinee|passante|son|annonce|originale|magnetique)|bandes? (?:de|d) (?:frequence|roulement)|"
                    r"violences? (?:du vent|de la mer|des vagues|des elements)|feux? (?:d artifice|de camp|de forets?|de signalisation|rouges?|tricolores?)|"
                    r"incendies? de (?:foret|vegetation|broussailles|garrigue)|incendies? (?:accidentels?|domestiques?)|"
                    r"cannabis therapeutique|legalisation du cannabis|cbd|"
                    r"affrontements? (?:politiques?|verbaux?|d idees)|tensions? (?:diplomatiques?|politiques?|sociales?|budgetaires?|geopolitiques?|commerciales?)|"
                    r"degradations? (?:climatique|de la note)|troubles? (?:du sommeil|de l humeur|psychiques?|musculo\w*|alimentaires?)|"
                    r"incidents? (?:technique|de parcours|diplomatique))\b")
_POLICE = re.compile(r"\b(?:police|policiers?|gendarm\w*|enquetes?|interpelle\w*|garde a vue|suspects?|mis en examen|parquet|procureur|victimes?|blesses?|tribunal|condamn\w*|ecroue\w*|arrete\w*|defere\w*|plaintes?|commissariat|brigade|crs|bac|pompiers|samu|sapeurs|perquisition\w*|temoins?|assises|prison|detention|reclusion|forces de l ordre|prefecture|prefet)\b")
_SPORT = re.compile(r"\b(?:ligue 1|ligue 2|ligue des champions|top 14|football|footballeurs?|rugby|tennis|basket|handball|cyclisme|tour de france|formule 1|grand prix|coupe du monde|mercato|transferts?|buteurs?|gardien de but|entraineur|psg|championnat|classement|journee de championnat)\b")
_SPORT_OK = {'rixe', 'fusillade', 'attaque_forces', 'emeutes', 'homicide', 'violence', 'viol', 'manif'}
_CULTURE = re.compile(r"\b(?:films?|series?|romans?|livres?|albums?|concerts?|festivals?|spectacles?|expositions?|musees?|theatre|cinema|netflix|jeux? video|bandes? dessinees?|documentaires?|podcasts?|emissions?|episodes?|acteurs?|actrices?|realisateurs?|chansons?|chanteurs?|chanteuses?|rappeurs?|rappeuses?|clips?)\b")
_LIFESTYLE = re.compile(r"\b(?:recettes?|horoscope|meteo|bourse|cac 40|astuces?|bon plan|loto|euromillions|jeu concours|vacances|tourisme|voyages?|soldes|promos?|shopping|beaute|cuisine|restaurants?|jardin)\b")
_ACCIDENT = re.compile(r"\b(?:accidents? (?:de la route|de voiture|de moto|de scooter|de velo|de train|d avion|mortels?|domestiques?|de la circulation)|collisions?|carambolages?|noyades?|noye\w*|avalanches?|crash|sorties? de route|chutes? mortelles?|monoxyde)\b")
_NAV = re.compile(r"\b(?:abonnez vous|newsletter|se connecter|mon compte|inscription|cookies|mentions legales|confidentialite|lire aussi|a lire aussi|voir plus|en savoir plus|partager|suivez nous|publicite|sponsorise|connexion|menu)\b")
_FOREIGN = re.compile(r"\b(?:ukrain\w*|gaza|israel\w*|palestin\w*|hamas|hezbollah|russie|russes?|poutine|zelensky|kiev|moscou|etats unis|americain\w*|trump|biden|texas|californie|new york|floride|washington|mexique|mexicain\w*|bresil|bresilien\w*|argentine|colombie|equateur|pakistan|inde|chine|chinois\w*|japon|coree|iran\w*|irak|syrie|liban|yemen|soudan|nigeria|mali|niger|burkina|congo|afghanistan|taliban|royaume uni|britannique\w*|londres|allemagne|allemand\w*|berlin|italie|italien\w*|espagne|espagnol\w*|bruxelles|belgique|belge|suisse|canada|canadien\w*|australie|turquie|ethiopie|haiti|venezuela)\b")
_FRANCE = re.compile(r"\b(?:france|francais\w*|francilien\w*|hexagone|paris|cnil|anssi|cybermalveillance|sncf|ameli|urssaf|france travail|pole emploi|impots|dgfip|ministere|prefecture|mairie|conseil departemental|gendarmerie nationale|police nationale|parquet de|tribunal judiciaire|outre mer)\b")
_INC_STRONG = re.compile(r"\b(?:victimes?|touche\w*|vise\w*|cible\w*|revendiqu\w*|pirate\w* (?:de|du|des|la|le|l)|derobe\w*|vole\w*|paralys\w*|mis(?:es)? en vente|interpelle\w*|arrete\w*|condamn\w*|mis en examen|demantel\w*|exploit\w* activement|attaques? en cours|fuites? de donnees)\b")
_ADVICE = re.compile(r"\b(?:comment (?:se )?(?:proteger|eviter|reconnaitre|detecter|reagir)|nos conseils|conseils?|guide|tutos?|meilleur\w* (?:vpn|antivirus|logiciels?)|bon plan|promo\w*|code promo|soldes?|black friday|comparatif|webinaires?|formations?|salon|ateliers?|sensibilis\w*|journee (?:de|du))\b")
_VULN = re.compile(r"\b(?:vulnerabilit\w*|failles?|cve ?\d*|correctifs?|patch\w*|mises? a jour de securite|zero day)\b")
_MOD_SEV = [
    (re.compile(r"\b(?:mort|morts|decede\w*|tue|tuee|tues|tuees|victimes?)\b"), 1),
    (re.compile(r"\b(?:blesse\w*|hospitalise\w*|grievement)\b"), 1),
    (re.compile(r"\b(?:otages?|armes?|kalachnikov|kalach|arme a feu|mortiers?)\b"), 1),
    (re.compile(r"\b(?:plusieurs|dizaines?|centaines?|millions?|massive?|massif|nuit de violences|voitures? brulee?s?)\b"), 1),
    (re.compile(r"\b(?:hopital|hopitaux|collectivite|mairie|ministere|administration|operateur|infrastructure|commissariat|ecole|college|lycee)\b"), 1),
]
_MENU_TITULOS = re.compile(r"^(?:accueil|menu|rechercher|recherche|abonnement|connexion|contact|a propos|plan du site|faits? divers|justice|societe)$")


def clasificar_detalle(titulo, texto='', sens=None, geo_prec='none'):
    """Classifie un titre (+résumé). Retourne dict(tipo, cat, sev, conf, hits) ou {'reject': motif}."""
    sens = sens or SENSIBILIDAD
    thr = _UMBRAL_CONF.get(sens, 45)
    full = limpiar((titulo or '') + ' ' + (texto or ''))[:900]
    n = _SCRUB.sub(' ', norm(full))
    tn = _SCRUB.sub(' ', norm(titulo or ''))
    if len(tn) <= 45 and (_NAV.search(tn) or _MENU_TITULOS.match(tn)):
        return {'reject': 'nav'}
    cue = bool(_POLICE.search(n))
    best = None
    for k, d in TIPOS_CRIMEN.items():
        if k == 'other':
            continue
        ms = d['srx'].findall(n)
        if ms:
            nt = len(set(ms))
            intitle = bool(d['srx'].search(tn))
            cand = (min(nt, 3) * d['peso'] * (1.5 if intitle else 1.0), d['sev'], k, True, nt, intitle)
        elif d['wrx'] is not None and cue and d['wrx'].search(n):
            intitle = bool(d['wrx'].search(tn))
            cand = (0.4 * min(len(d['wrx'].findall(n)), 3) * d['peso'], d['sev'], k, False, 1, intitle)
        else:
            continue
        if best is None or cand[:2] > best[:2]:
            best = cand
    if best is None:
        if sens == 'amplio' and any(kw in full.lower() for kw in PALABRAS_CLAVE_CRIMEN):
            return {'tipo': 'other', 'cat': 'fisico', 'sev': 2, 'conf': 20, 'hits': 0}
        return {'reject': 'sin_keyword'}
    _, _, k, strong, nt, intitle = best
    d = TIPOS_CRIMEN[k]
    cat = d['cat']
    geo_txt = geo_prec in ('ciudad', 'depto')
    if _FOREIGN.search(n) and not _FRANCE.search(n) and not geo_txt:
        return {'reject': 'foreign'}
    penalty = 0
    if cat == 'cyber':
        inc = _INC_STRONG.search(n)
        if _ADVICE.search(n) and not inc:
            return {'reject': 'advice'}
        if _VULN.search(n) and not inc:
            return {'reject': 'vuln'}
    else:
        if _ACCIDENT.search(n) and not strong:
            return {'reject': 'accident'}
        if _CULTURE.search(n):
            if not cue:
                return {'reject': 'culture'}
            penalty += 10
        if _LIFESTYLE.search(n) and not strong:
            return {'reject': 'lifestyle'}
        if _SPORT.search(n):
            if k not in _SPORT_OK:
                return {'reject': 'sport'}
            penalty += 10
    conf = (45 + 5 * min(nt - 1, 3)) if strong else 30
    conf += (10 if intitle else 0) + (10 if cue else 0) + (10 if geo_txt else 0) - penalty
    conf = max(0, min(100, conf))
    if conf < thr:
        return {'reject': 'low_conf'}
    sev = d['sev']
    for rx, pts in _MOD_SEV:
        if rx.search(n):
            sev += pts
    return {'tipo': k, 'cat': cat, 'sev': max(1, min(10, sev)), 'conf': conf, 'hits': nt}


def clasificar(texto):
    """Compat v1/v2 → (tipo, categoria, severidad) en mode équilibré."""
    r = clasificar_detalle(texto, '', 'equilibrado')
    if 'reject' in r:
        return 'other', 'fisico', 1
    return r['tipo'], r['cat'], r['sev']


def es_conflicto(tipo, cat, sev, conf):
    """Un 'conflit' déclenche l'alarme: rue ≥ seuil, fusillade, terrorisme."""
    if conf < 45:
        return False
    if tipo == 'terrorisme':
        return True
    return cat == 'rue' and sev >= UMBRAL_ALARMA

# ============================================================================
# GEOGRAFÍA: departamentos + ciudades principales
# ============================================================================

_DEPS_RAW = """01|Ain|46.20|5.35
02|Aisne|49.45|3.60
03|Allier|46.40|3.20
04|Alpes-de-Haute-Provence|44.10|6.20
05|Hautes-Alpes|44.66|6.35
06|Alpes-Maritimes|43.95|7.20
07|Ardèche|44.75|4.40
08|Ardennes|49.60|4.65
09|Ariège|42.95|1.45
10|Aube|48.30|4.10
11|Aude|43.10|2.40
12|Aveyron|44.30|2.65
13|Bouches-du-Rhône|43.55|5.10
14|Calvados|49.10|-0.35
15|Cantal|45.05|2.65
16|Charente|45.70|0.20
17|Charente-Maritime|45.85|-0.80
18|Cher|47.05|2.50
19|Corrèze|45.35|1.85
2A|Corse-du-Sud|41.85|8.95
2B|Haute-Corse|42.45|9.20
21|Côte-d'Or|47.45|4.80
22|Côtes-d'Armor|48.45|-2.75
23|Creuse|46.10|2.05
24|Dordogne|45.15|0.75
25|Doubs|47.15|6.35
26|Drôme|44.70|5.15
27|Eure|49.10|1.05
28|Eure-et-Loir|48.35|1.40
29|Finistère|48.30|-4.05
30|Gard|44.00|4.20
31|Haute-Garonne|43.35|1.20
32|Gers|43.70|0.45
33|Gironde|44.80|-0.55
34|Hérault|43.60|3.40
35|Ille-et-Vilaine|48.15|-1.65
36|Indre|46.80|1.60
37|Indre-et-Loire|47.25|0.70
38|Isère|45.25|5.60
39|Jura|46.75|5.75
40|Landes|43.95|-0.80
41|Loir-et-Cher|47.60|1.35
42|Loire|45.75|4.25
43|Haute-Loire|45.10|3.75
44|Loire-Atlantique|47.35|-1.70
45|Loiret|47.90|2.30
46|Lot|44.60|1.65
47|Lot-et-Garonne|44.35|0.45
48|Lozère|44.50|3.50
49|Maine-et-Loire|47.40|-0.35
50|Manche|49.00|-1.30
51|Marne|48.95|4.20
52|Haute-Marne|48.10|5.20
53|Mayenne|48.15|-0.65
54|Meurthe-et-Moselle|48.75|6.15
55|Meuse|49.00|5.35
56|Morbihan|47.85|-2.80
57|Moselle|49.00|6.65
58|Nièvre|47.10|3.50
59|Nord|50.45|3.20
60|Oise|49.40|2.40
61|Orne|48.60|0.05
62|Pas-de-Calais|50.50|2.30
63|Puy-de-Dôme|45.75|3.15
64|Pyrénées-Atlantiques|43.25|-0.75
65|Hautes-Pyrénées|43.00|0.15
66|Pyrénées-Orientales|42.60|2.55
67|Bas-Rhin|48.65|7.55
68|Haut-Rhin|47.85|7.25
69|Rhône|45.85|4.65
70|Haute-Saône|47.65|6.10
71|Saône-et-Loire|46.65|4.55
72|Sarthe|48.00|0.20
73|Savoie|45.50|6.40
74|Haute-Savoie|46.00|6.35
75|Paris|48.86|2.35
76|Seine-Maritime|49.65|1.00
77|Seine-et-Marne|48.65|2.95
78|Yvelines|48.80|1.85
79|Deux-Sèvres|46.50|-0.35
80|Somme|49.95|2.30
81|Tarn|43.80|2.15
82|Tarn-et-Garonne|44.05|1.30
83|Var|43.45|6.25
84|Vaucluse|44.00|5.15
85|Vendée|46.65|-1.30
86|Vienne|46.55|0.45
87|Haute-Vienne|45.90|1.25
88|Vosges|48.20|6.35
89|Yonne|47.85|3.55
90|Territoire de Belfort|47.62|6.90
91|Essonne|48.50|2.20
92|Hauts-de-Seine|48.84|2.24
93|Seine-Saint-Denis|48.91|2.48
94|Val-de-Marne|48.78|2.47
95|Val-d'Oise|49.07|2.15
971|Guadeloupe|16.25|-61.55
972|Martinique|14.65|-61.00
973|Guyane|4.00|-53.00
974|La Réunion|-21.10|55.50
976|Mayotte|-12.80|45.15"""

DEPS = {}
for _ln in _DEPS_RAW.splitlines():
    _c, _n, _la, _lo = _ln.split('|')
    DEPS[_c] = (_n, float(_la), float(_lo))
DEP_BY_NAME = {norm(v[0]): k for k, v in DEPS.items()}
DEP_BY_NAME['reunion'] = '974'
DEP_BY_NAME['corse'] = '2A'
# nombres cortos/ambiguos: sólo se usan si vienen de la fuente, no al buscar en el texto
_AMBIGUOS = {'nord', 'var', 'somme', 'oise', 'eure', 'lot', 'marne', 'manche', 'jura', 'cher', 'gard', 'aude',
             'gers', 'tarn', 'indre', 'landes', 'loire', 'ain', 'orne', 'corse', 'meuse', 'doubs', 'isere'}
_DEP_TXT = [n for n in DEP_BY_NAME if n not in _AMBIGUOS and len(n) >= 5]
_DEP_RX = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, _DEP_TXT), key=len, reverse=True)) + r')\b')
_CODE_RX = re.compile(r'\((\d{2,3}|2a|2b)\)')

_CITIES_RAW = """Paris|48.8566|2.3522|75
Marseille|43.2965|5.3698|13
Lyon|45.7640|4.8357|69
Toulouse|43.6047|1.4442|31
Nice|43.7102|7.2620|06
Nantes|47.2184|-1.5536|44
Montpellier|43.6119|3.8772|34
Strasbourg|48.5734|7.7521|67
Bordeaux|44.8378|-0.5792|33
Lille|50.6292|3.0573|59
Rennes|48.1173|-1.6778|35
Reims|49.2583|4.0317|51
Grenoble|45.1885|5.7245|38
Dijon|47.3220|5.0415|21
Angers|47.4784|-0.5632|49
Nîmes|43.8367|4.3601|30
Toulon|43.1242|5.9280|83
Le Havre|49.4944|0.1079|76
Saint-Étienne|45.4397|4.3872|42
Clermont-Ferrand|45.7772|3.0870|63
Amiens|49.8941|2.2958|80
Limoges|45.8336|1.2611|87
Metz|49.1193|6.1757|57
Perpignan|42.6887|2.8948|66
Besançon|47.2378|6.0241|25
Orléans|47.9029|1.9093|45
Rouen|49.4432|1.0993|76
Caen|49.1829|-0.3707|14
Nancy|48.6921|6.1844|54
Avignon|43.9493|4.8055|84
Tours|47.3941|0.6848|37
Calais|50.9513|1.8587|62
Roubaix|50.6942|3.1746|59
Tourcoing|50.7239|3.1612|59
Villeurbanne|45.7667|4.8795|69
Cannes|43.5528|7.0174|06
Antibes|43.5808|7.1239|06
Ajaccio|41.9192|8.7386|2A
Bastia|42.7028|9.4500|2B
Pointe-à-Pitre|16.2411|-61.5330|971
Fort-de-France|14.6161|-61.0588|972
Cayenne|4.9224|-52.3135|973
Saint-Denis de La Réunion|-20.8789|55.4481|974
Mamoudzou|-12.7806|45.2278|976
Mulhouse|47.7508|7.3359|68
Poitiers|46.5802|0.3404|86
La Rochelle|46.1603|-1.1511|17
Brest|48.3904|-4.4861|29
Lorient|47.7482|-3.3702|56
Pau|43.2951|-0.3708|64
Bayonne|43.4929|-1.4748|64
Créteil|48.7904|2.4556|94
Nanterre|48.8924|2.2071|92
Bobigny|48.9094|2.4396|93
Évry|48.6297|2.4417|91
Saint-Ouen|48.9117|2.3339|93
Aubervilliers|48.9146|2.3830|93
Sevran|48.9392|2.5282|93
Argenteuil|48.9472|2.2467|95
Versailles|48.8049|2.1204|78
Valence|44.9334|4.8924|26
Béziers|43.3442|3.2158|34
Troyes|48.2973|4.0744|10
Chambéry|45.5646|5.9178|73
Annecy|45.8992|6.1294|74
Colmar|48.0794|7.3585|68
Dunkerque|51.0343|2.3768|59
Le Mans|48.0061|0.1996|72
Saint-Nazaire|47.2733|-2.2138|44
Vitrolles|43.4600|5.2486|13
Aix-en-Provence|43.5297|5.4474|13
Saint-Pierre|-21.3393|55.4781|974"""

CITIES = {}
for _ln in _CITIES_RAW.splitlines():
    _n, _la, _lo, _c = _ln.split('|')
    CITIES[norm(_n)] = (_n, float(_la), float(_lo), _c)
_CITY_RX = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, CITIES), key=len, reverse=True)) + r')\b')

# medios cuyo ámbito es nacional → sin geolocalización por defecto
_FUENTES_REGIONALES_PARIS = {'Le Parisien - Faits divers'}


def dep_code_fuente(fuente):
    d = fuente.get('departement', '')
    if d in ('National', 'Outre-mer', '', None):
        return None
    if d == 'Paris' and fuente.get('nombre') not in _FUENTES_REGIONALES_PARIS:
        return None
    return DEP_BY_NAME.get(norm(d))


def _jitter(seed, amp):
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    return (((h & 0xffff) / 65535) - .5) * 2 * amp, ((((h >> 16) & 0xffff) / 65535) - .5) * 2 * amp



_CITY_AMB = {'tours', 'valence', 'nancy', 'pau', 'saint pierre'}
_CITY_RX_SAFE = re.compile(r'\b(' + '|'.join(sorted((re.escape(c) for c in CITIES if c not in _CITY_AMB), key=len, reverse=True)) + r')\b')
_CITY_AMB_RX = re.compile(r'\b(?:a|au|aux|dans|pres de|vers|sur|en banlieue de|region de|agglomeration de|metropole de|ville de) ('
                          + '|'.join(re.escape(c) for c in sorted(_CITY_AMB, key=len, reverse=True)) + r')\b')


def geolocalizar(texto, code_fuente=None, seed=''):
    """Devuelve dict(lat, lon, departement, dep_code, precision). Villes ambiguës (Tours, Valence, Nancy…) seulement après une préposition."""
    n = norm(texto)
    m = _CITY_RX_SAFE.search(n) or _CITY_AMB_RX.search(n)
    if m:
        nombre, la, lo, code = CITIES[m.group(1)]
        dx, dy = _jitter(seed or n, 0.025)
        return {'lat': round(la + dx, 5), 'lon': round(lo + dy, 5), 'departement': DEPS[code][0],
                'dep_code': code, 'precision': 'ciudad'}
    code, prec = None, None
    mc = _CODE_RX.search(n)
    if mc and mc.group(1).upper() in DEPS:
        code, prec = mc.group(1).upper(), 'depto'
    if not code:
        md = _DEP_RX.search(n)
        if md:
            code, prec = DEP_BY_NAME[md.group(1)], 'depto'
    if not code and code_fuente:
        code, prec = code_fuente, 'fuente'
    if code:
        la, lo = DEPS[code][1], DEPS[code][2]
        dx, dy = _jitter(seed or n, 0.22)
        return {'lat': round(la + dx, 5), 'lon': round(lo + dy, 5), 'departement': DEPS[code][0],
                'dep_code': code, 'precision': prec}
    return {'lat': None, 'lon': None, 'departement': 'National', 'dep_code': None, 'precision': 'none'}


# ============================================================================
# FUENTES  (v1: 45 médias faits-divers · + cyber · + alertes officielles)
# ============================================================================

_FUENTES_RAW = [
    ('Le Monde - Faits divers', 'https://www.lemonde.fr/faits-divers/', 'Paris'),
    ('Le Figaro - Faits divers', 'https://www.lefigaro.fr/faits-divers', 'Paris'),
    ('Libération - Faits divers', 'https://www.liberation.fr/faits-divers/', 'Paris'),
    ('20 Minutes - Faits divers', 'https://www.20minutes.fr/faits-divers', 'Paris'),
    ('France Info - Faits divers', 'https://www.francetvinfo.fr/faits-divers/', 'Paris'),
    ('Le Parisien - Faits divers', 'https://www.leparisien.fr/faits-divers/', 'Paris'),
    ('Le Point - Faits divers', 'https://www.lepoint.fr/faits-divers/', 'Paris'),
    ("L'Express - Faits divers", 'https://www.lexpress.fr/actualite/faits-divers/', 'Paris'),
    ('France 3 Régions - Faits divers', 'https://france3-regions.francetvinfo.fr/faits-divers', 'National'),
    ('Actu.fr - Faits divers', 'https://actu.fr/faits-divers', 'National'),
    ('La Provence - Faits divers', 'https://www.laprovence.com/actu/faits-divers', 'Bouches-du-Rhône'),
    ('Le Progrès - Faits divers', 'https://www.leprogres.fr/faits-divers', 'Rhône'),
    ('Sud Ouest - Faits divers', 'https://www.sudouest.fr/faits-divers', 'Gironde'),
    ('Ouest-France - Faits divers', 'https://www.ouest-france.fr/faits-divers', 'Ille-et-Vilaine'),
    ('La Dépêche - Faits divers', 'https://www.ladepeche.fr/faits-divers', 'Haute-Garonne'),
    ('Nice-Matin - Faits divers', 'https://www.nicematin.com/faits-divers', 'Alpes-Maritimes'),
    ('Midi Libre - Faits divers', 'https://www.midilibre.fr/faits-divers', 'Hérault'),
    ('La Voix du Nord - Faits divers', 'https://www.lavoixdunord.fr/faits-divers', 'Nord'),
    ('France Info Outre-mer - Faits divers', 'https://la1ere.francetvinfo.fr/faits-divers/', 'Outre-mer'),
    ('Actu17', 'https://actu17.fr/', 'Paris'),
    ('Citoyens.com', 'https://www.citoyens.com/faits-divers/', 'Paris'),
    ('Paris Normandie', 'https://www.paris-normandie.fr/faits-divers', 'Seine-Maritime'),
    ('Marsactu', 'https://marsactu.fr/categorie/justice/', 'Bouches-du-Rhône'),
    ('Made in Marseille', 'https://madeinmarseille.net/actualites/faits-divers-marseille/', 'Bouches-du-Rhône'),
    ('Var-Matin', 'https://www.varmatin.com/faits-divers', 'Var'),
    ('Lyon Capitale', 'https://lyoncapitale.fr/categorie/justice/', 'Rhône'),
    ('Nord Éclair', 'https://www.nordeclair.fr/faits-divers', 'Nord'),
    ('Observateur du Douaisis', 'https://www.observateurdouaisis.fr/faits-divers/', 'Nord'),
    ('Bordeaux Gazette', 'https://bordeaux-gazette.com/justice/', 'Gironde'),
    ('Charente Libre', 'https://www.charentelibre.fr/faits-divers', 'Charente'),
    ('Presse Océan', 'https://www.presseocean.fr/faits-divers', 'Loire-Atlantique'),
    ("Courrier de l'Ouest", 'https://www.courrierdelouest.fr/faits-divers', 'Maine-et-Loire'),
    ("L'Alsace", 'https://www.lalsace.fr/faits-divers', 'Haut-Rhin'),
    ('Républicain Lorrain', 'https://www.republicain-lorrain.fr/faits-divers', 'Moselle'),
    ("L'Est Républicain", 'https://www.estrepublicain.fr/faits-divers', 'Meurthe-et-Moselle'),
    ('La Montagne', 'https://www.lamontagne.fr/faits-divers', 'Puy-de-Dôme'),
    ('La République du Centre', 'https://www.larep.fr/faits-divers', 'Loiret'),
    ('Le Bien Public', 'https://www.bienpublic.com/faits-divers', "Côte-d'Or"),
    ('Le Populaire du Centre', 'https://www.lepopulaire.fr/faits-divers', 'Haute-Vienne'),
    ('Corse-Matin', 'https://www.corsematin.com/faits-divers', 'Corse-du-Sud'),
    ('RTL', 'https://www.rtl.fr/actu/justice-faits-divers', 'Paris'),
    ('Europe 1', 'https://www.europe1.fr/societe/faits-divers', 'Paris'),
    ('Martinique France Info', 'https://la1ere.francetvinfo.fr/martinique/faits-divers/', 'Martinique'),
    ('Guadeloupe France Info', 'https://la1ere.francetvinfo.fr/guadeloupe/faits-divers/', 'Guadeloupe'),
    ('Réunion France Info', 'https://la1ere.francetvinfo.fr/reunion/faits-divers/', 'Réunion'),
]

# presse cyber: (nombre, url, departement, rss|None)
_FUENTES_CYBER_RAW = [
    ('ZATAZ', 'https://www.zataz.com/', 'National', 'https://www.zataz.com/feed/'),
    ('LeMagIT - Sécurité', 'https://www.lemagit.fr/Securite', 'National', 'https://www.lemagit.fr/rss/ContentSyndication.xml'),
    ('Numerama - Cyberguerre', 'https://www.numerama.com/cyberguerre/', 'National', 'https://www.numerama.com/cyberguerre/feed/'),
    ('Silicon.fr - Cybersécurité', 'https://www.silicon.fr/categorie/cybersecurite', 'National', 'https://www.silicon.fr/categorie/cybersecurite/feed'),
    ('01net - Cybersécurité', 'https://www.01net.com/actualites/cybersecurite/', 'National', 'https://www.01net.com/feed/'),
    ('Le Monde Informatique - Sécurité', 'https://www.lemondeinformatique.fr/securite.html', 'National', None),
    ('Next - Sécurité', 'https://next.ink/category/securite/', 'National', 'https://next.ink/feed/'),
    ('France Info - Cybercriminalité', 'https://www.francetvinfo.fr/internet/securite-sur-internet/', 'National', 'https://www.francetvinfo.fr/internet/securite-sur-internet.rss'),
    ('Le Figaro - Cybersécurité', 'https://www.lefigaro.fr/secteur/high-tech/cybersecurite', 'National', None),
    ('Data Security Breach', 'https://www.datasecuritybreach.fr/', 'National', 'https://www.datasecuritybreach.fr/feed/'),
    ('UnderNews', 'https://www.undernews.fr/', 'National', 'https://www.undernews.fr/feed'),
    ('Global Security Mag', 'https://www.globalsecuritymag.fr/', 'National', 'https://www.globalsecuritymag.fr/spip.php?page=backend'),
    ('Clubic - Cybersécurité', 'https://www.clubic.com/actualite-cybersecurite.html', 'National', None),
    ('Usine Digitale - Cybersécurité', 'https://www.usine-digitale.fr/cybersecurite/', 'National', None),
]
# alertes officielles: (nombre, url, departement, ctx, rss|None, filtre|None)
#  ctx 'cyber' → CERT-FR/ANSSI/Cybermalveillance · ctx 'crime' → Intérieur/Police/Gendarmerie/Vigipirate
_FUENTES_GOV_RAW = [
    ('CERT-FR (ANSSI)', 'https://www.cert.ssi.gouv.fr/', 'National', 'cyber', 'https://www.cert.ssi.gouv.fr/feed/', None),
    ('CERT-FR - Alertes (temps réel)', 'https://www.cert.ssi.gouv.fr/alerte/', 'National', 'cyber', 'https://www.cert.ssi.gouv.fr/alerte/feed/', None),
    ('CERT-FR - Avis de sécurité', 'https://www.cert.ssi.gouv.fr/avis/', 'National', 'cyber', 'https://www.cert.ssi.gouv.fr/avis/feed/', None),
    ('CERT-FR - Menaces et incidents (CTI)', 'https://www.cert.ssi.gouv.fr/cti/', 'National', 'cyber', 'https://www.cert.ssi.gouv.fr/cti/feed/', None),
    ('ANSSI - Actualités', 'https://cyber.gouv.fr/actualites', 'National', 'cyber', None, None),
    ('Cybermalveillance.gouv.fr', 'https://www.cybermalveillance.gouv.fr/tous-nos-contenus/actualites', 'National', 'cyber', None, None),
    ('Intérieur - Communiqués', 'https://www.interieur.gouv.fr/Actualites/Communiques-de-presse', 'National', 'crime', None, None),
    ('Gendarmerie nationale - Actualités', 'https://www.gendarmerie.interieur.gouv.fr/actualites', 'National', 'crime', None, None),
    ('Police nationale - Actualités', 'https://www.police-nationale.interieur.gouv.fr/actualites', 'National', 'crime', None, None),
    ('Préfecture de police de Paris', 'https://www.prefecturedepolice.interieur.gouv.fr/actualites', 'Paris', 'crime', None, None),
    ('SGDSN - Vigipirate / Sécurité nationale', 'https://www.sgdsn.gouv.fr/', 'National', 'crime',
     None, r"vigipirate|attentat|terror|securite|menace|crise|alerte|cyber"),
    ('Ministère de la Justice - Actualités', 'https://www.justice.gouv.fr/actualites', 'National', 'crime',
     None, r"terror|criminal|crime|trafic|stupefiant|police|gendarm|securite|cyber|violence|mafia|banditisme"),
    ('Gouvernement.fr - Actualités', 'https://www.gouvernement.fr/actualites', 'National', 'crime',
     None, r"vigipirate|attentat|terror|securite|police|gendarm|alerte|crise|menace|cyber|delinquance|trafic"),
    ('Service-Public - Actualités', 'https://www.service-public.fr/particuliers/actualites', 'National', 'crime',
     None, r"vigipirate|attentat|alerte|cyber|arnaque|escroquerie|phishing|securite|delinquance"),
    ('Gouvernement - Sécurité (info.gouv.fr)', 'https://www.info.gouv.fr/actualite', 'National', 'crime',
     None, r"vigipirate|attentat|terror|securite|police|gendarm|alerte|crise|menace|cyber"),
]
_FUENTES_EXTRA_RAW = [
    ('BFM TV - Police & Justice', 'https://www.bfmtv.com/police-justice/', 'National'),
    ('CNews - Faits divers', 'https://www.cnews.fr/faits-divers', 'National'),
    ('TF1 Info - Faits divers', 'https://www.tf1info.fr/faits-divers/', 'National'),
    ('Le Télégramme - Faits divers', 'https://www.letelegramme.fr/faits-divers/', 'Finistère'),
    ('Le Dauphiné Libéré - Faits divers', 'https://www.ledauphine.com/faits-divers', 'Isère'),
    ('La Nouvelle République - Faits divers', 'https://www.lanouvellerepublique.fr/faits-divers', 'Indre-et-Loire'),
    ("L'Union - Faits divers", 'https://www.lunion.fr/faits-divers', 'Marne'),
    ('Courrier Picard - Faits divers', 'https://www.courrier-picard.fr/faits-divers', 'Somme'),
    ('DNA - Faits divers', 'https://www.dna.fr/faits-divers', 'Bas-Rhin'),
    ("L'Indépendant - Faits divers", 'https://www.lindependant.fr/faits-divers/', 'Pyrénées-Orientales'),
    ('Clicanoo - Faits divers', 'https://www.clicanoo.re/faits-divers', 'Réunion'),
    ('Zinfos974', 'https://www.zinfos974.com/', 'Réunion'),
]
# RSS conocidos (se leen primero: suelen pasar aunque la web bloquee). Si alguno ya no existe, solo cuesta una petición.
_RSS_CONOCIDOS = {
    'Le Monde - Faits divers': 'https://www.lemonde.fr/faits-divers/rss_full.xml',
    'Le Figaro - Faits divers': 'https://www.lefigaro.fr/rss/figaro_faits-divers.xml',
    'France Info - Faits divers': 'https://www.francetvinfo.fr/faits-divers.rss',
    'Le Parisien - Faits divers': 'https://www.leparisien.fr/faits-divers/rss.xml',
    '20 Minutes - Faits divers': 'https://www.20minutes.fr/feeds/rss-faits-divers.xml',
    'Actu17': 'https://actu17.fr/feed/',
    'Marsactu': 'https://marsactu.fr/feed/',
    'Made in Marseille': 'https://madeinmarseille.net/feed/',
    'Sud Ouest - Faits divers': 'https://www.sudouest.fr/faits-divers/rss.xml',
    'BFM TV - Police & Justice': 'https://www.bfmtv.com/rss/police-justice/',
}
_FUENTES_REGIONALES_PARIS = {'Le Parisien - Faits divers', 'Paris Normandie'}


def _mk_fuentes():
    out = []

    def base(u):
        p = urlparse(u)
        return f'{p.scheme}://{p.netloc}'
    for n, u, d in list(_FUENTES_RAW) + _FUENTES_EXTRA_RAW:
        out.append({'nombre': n, 'url': u, 'base': base(u), 'departement': d, 'activo': True, 'tipo': 'faits_divers', 'ctx': 'crime',
                    'rss': _RSS_CONOCIDOS.get(n)})
    for n, u, d, rss in _FUENTES_CYBER_RAW:
        out.append({'nombre': n, 'url': u, 'base': base(u), 'departement': d, 'activo': True, 'tipo': 'cyber', 'ctx': 'cyber', 'rss': rss})
    for n, u, d, ctx, rss, flt in _FUENTES_GOV_RAW:
        out.append({'nombre': n, 'url': u, 'base': base(u), 'departement': d, 'activo': True, 'tipo': 'gov', 'ctx': ctx, 'rss': rss, 'filtro': flt})
    return out


FUENTES_BASE = _mk_fuentes()


def dep_code_fuente(fuente):
    d = fuente.get('departement', '')
    if d in ('National', 'Outre-mer', '', None):
        return None
    if d == 'Paris' and fuente.get('nombre') not in _FUENTES_REGIONALES_PARIS and fuente.get('tipo') != 'gov':
        return None
    return DEP_BY_NAME.get(norm(d))

# ============================================================================
# GESTOR DE DATOS  (fusion multi-sources, pertinence, alertes officielles)
# ============================================================================

_RLOCK = threading.RLock()


def _fecha_ok(s):
    return bool(s) and re.match(r'^\d{4}-\d{2}-\d{2}', s) is not None


def _parse_fecha(c):
    try:
        return datetime.strptime((c.get('fecha') or '')[:10], '%Y-%m-%d')
    except Exception:
        return None


def _tokens(s):
    return set(re.findall(r'[a-z]{4,}', norm(s)))


def _csv_safe(v):
    v = '' if v is None else str(v).replace('\n', ' ')
    return "'" + v if v[:1] in ('=', '+', '-', '@') else v


def relevancia(c, hoy=None):
    """0-100: sévérité + confiance + nombre de sources qui confirment + fraîcheur."""
    hoy = hoy or datetime.now()
    nf = len(c.get('fuentes') or []) or 1
    dt = _parse_fecha(c)
    dias = max(0, (hoy - dt).days) if dt else 30
    rec = max(0.0, 1 - dias / 14.0)
    r = 4.5 * c.get('severidad', 1) + 0.25 * c.get('confianza', 50) + 20 * min(1.0, (nf - 1) / 3.0) + 10 * rec
    return int(max(0, min(100, round(r))))


def ser(c, hoy=None):
    """Représentation JSON d'un événement pour l'API."""
    return {'id': c.get('id'), 'titulo': c.get('titulo', ''), 'fecha': c.get('fecha', ''), 'departement': c.get('departement', ''),
            'tipo': c.get('tipo', 'other'), 'categoria': c.get('categoria', 'fisico'), 'fuente': c.get('fuente', ''),
            'severidad': c.get('severidad', 1), 'confianza': c.get('confianza', 50), 'relevancia': relevancia(c, hoy),
            'url': c.get('url', ''), 'fuentes': [[f.get('n', ''), f.get('u', '')] for f in (c.get('fuentes') or [])],
            'conflicto': bool(c.get('conflicto'))}


class GestorDatos:
    def __init__(self, archivo=None):
        self.archivo = archivo or ARCHIVO_DATOS
        self.datos = self.cargar()

    # ---- persistencia
    def cargar(self):
        data = {'crimes': [], 'alertas': [], 'ultima_actualizacion': None, 'estadisticas_historicas': {},
                'alarma_ids': [], 'alarma_hist': [], 'config': {}, 'schema': SCHEMA}
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
            except Exception as e:
                logger.error(f'Error cargando {self.archivo}: {e}')
        for k, v in (('crimes', []), ('alertas', []), ('alarma_ids', []), ('alarma_hist', []), ('config', {})):
            data.setdefault(k, v)
        self._migrar(data)
        return data

    def _migrar(self, data):
        """v1/v2 → v3: catégorie (physique/rue/cyber), géo, confiance, liste de sources."""
        n = 0
        for c in data['crimes']:
            if c.get('v') == SCHEMA:
                continue
            c.setdefault('url', '')
            c.setdefault('fuente', '')
            r = clasificar_detalle(c.get('titulo', ''), '', 'equilibrado')
            if 'reject' not in r:
                c['tipo'], c['categoria'], c['severidad'], c['confianza'] = r['tipo'], r['cat'], r['sev'], max(50, r['conf'])
            else:
                tp = c.get('tipo') if c.get('tipo') in TIPOS_CRIMEN else 'other'
                c['tipo'] = tp
                c['categoria'] = TIPOS_CRIMEN[tp]['cat']
                c['severidad'] = c.get('severidad') or TIPOS_CRIMEN[tp]['sev']
                c['confianza'] = 40
            if not c.get('dep_code') and c.get('lat') is None:
                c.update(geolocalizar(c.get('titulo', ''), None, c.get('id', '')))
            c.setdefault('precision', 'none')
            c['fuentes'] = c.get('fuentes') or ([{'n': c['fuente'], 'u': c.get('url', ''), 'f': c.get('fecha', '')}] if c.get('fuente') else [])
            c['conflicto'] = es_conflicto(c['tipo'], c['categoria'], c['severidad'], c['confianza'])
            c['v'] = SCHEMA
            n += 1
        data['schema'] = SCHEMA
        if n:
            logger.info(f'Migrados {n} registros al esquema v{SCHEMA}')

    def guardar(self):
        with _RLOCK:
            self.datos['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tmp = self.archivo + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=1, ensure_ascii=False)
            if os.path.exists(self.archivo):
                try:
                    os.replace(self.archivo, ARCHIVO_BACKUP)
                except Exception:
                    pass
            os.replace(tmp, self.archivo)

    # ---- altas con fusión multi-fuente
    @staticmethod
    def _similar(c, recientes):
        tk = _tokens(c['titulo'])
        if not tk:
            return None
        dc = _parse_fecha(c)
        for tk2, e in reversed(recientes):
            if not tk2:
                continue
            j = len(tk & tk2) / len(tk | tk2)
            if j >= 0.8:
                return e
            if j >= 0.5 and e.get('categoria') == c.get('categoria'):
                de = _parse_fecha(e)
                if dc and de and abs((dc - de).days) > 3:
                    continue
                if e.get('dep_code') == c.get('dep_code') or not e.get('dep_code') or not c.get('dep_code'):
                    return e
        return None

    @staticmethod
    def _fusionar(e, c):
        names = {f.get('n') for f in e.get('fuentes', [])}
        changed = False
        for f in c.get('fuentes', []):
            if f.get('n') not in names:
                e.setdefault('fuentes', []).append(f)
                names.add(f.get('n'))
                changed = True
        if changed:
            e['confianza'] = min(100, e.get('confianza', 50) + 8)
            if not e.get('url') and c.get('url'):
                e['url'] = c['url']
            if c.get('severidad', 0) > e.get('severidad', 0):
                e['severidad'] = c['severidad']
            e['conflicto'] = es_conflicto(e['tipo'], e['categoria'], e['severidad'], e['confianza'])
        return changed

    def agregar_crimes(self, nuevos):
        """-> {'added': [events], 'merged': [events]}  (un doublon n'est plus jeté: il devient une source de plus)."""
        res = {'added': [], 'merged': []}
        if not nuevos:
            return res
        with _RLOCK:
            crimes = self.datos['crimes']
            por_id = {c['id']: c for c in crimes}
            recientes = [(_tokens(c['titulo']), c) for c in crimes[-1500:]]
            for c in nuevos:
                e = por_id.get(c['id']) or self._similar(c, recientes)
                if e is not None:
                    if self._fusionar(e, c) and e not in res['merged'] and e not in res['added']:
                        res['merged'].append(e)
                    continue
                crimes.append(c)
                por_id[c['id']] = c
                recientes.append((_tokens(c['titulo']), c))
                res['added'].append(c)
            if res['added']:
                self._actualizar_historicas(res['added'])
            if res['added'] or res['merged']:
                self.guardar()
        return res

    def _actualizar_historicas(self, nuevos):
        h = self.datos.setdefault('estadisticas_historicas', {})
        for c in nuevos:
            f = c.get('fecha', '')
            if len(f) >= 7:
                m = h.setdefault(f[:7], {'total': 0, 'tipos': {}, 'departements': {}})
                m['total'] += 1
                m['tipos'][c.get('tipo', 'other')] = m['tipos'].get(c.get('tipo', 'other'), 0) + 1
                d = c.get('departement', 'National')
                m['departements'][d] = m['departements'].get(d, 0) + 1

    # ---- alertas oficiales
    def agregar_alertas(self, nuevas):
        with _RLOCK:
            al = self.datos['alertas']
            ids = {a['id'] for a in al}
            fresh = []
            for a in nuevas:
                if a['id'] not in ids:
                    al.append(a)
                    ids.add(a['id'])
                    fresh.append(a)
            if fresh:
                al.sort(key=lambda a: (a.get('fecha', ''), a.get('nivel', 0)))
                del al[:-500]
                self.guardar()
            return fresh

    def alertas(self, ctx='all'):
        with _RLOCK:
            al = list(self.datos.get('alertas', []))
        if ctx in ('crime', 'cyber'):
            al = [a for a in al if a.get('ctx') == ctx]
        return sorted(al, key=lambda a: (a.get('fecha', ''), a.get('nivel', 0)), reverse=True)

    # ---- alarma / config
    def alarma_ya_vista(self, _id):
        return _id in set(self.datos.get('alarma_ids', []))

    def registrar_alarma(self, items, test=False):
        with _RLOCK:
            if not test:
                ids = self.datos.setdefault('alarma_ids', [])
                ids.extend(i['id'] for i in items)
                del ids[:-2000]
            h = self.datos.setdefault('alarma_hist', [])
            for i in items:
                h.insert(0, {'ts': datetime.now().strftime('%Y-%m-%d %H:%M'), 'titulo': ('[TEST] ' if test else '') + i.get('titulo', ''), 'id': i.get('id')})
            del h[100:]
            self.guardar()

    def cfg(self, k, d=None):
        return self.datos.get('config', {}).get(k, d)

    def set_cfg(self, k, v):
        with _RLOCK:
            self.datos.setdefault('config', {})[k] = v
            self.guardar()

    def copia(self):
        with _RLOCK:
            return list(self.datos.get('crimes', []))

    # ---- compat v1
    def detectar_tipo_crimen(self, texto):
        return clasificar(texto)[0]

    def calcular_severidad(self, texto):
        return clasificar(texto)[2]

    # ---- estadísticas
    def estadisticas(self, crimes=None):
        crimes = self.copia() if crimes is None else crimes
        hoy = datetime.now()
        s = {'total': len(crimes), 'departements': defaultdict(int), 'tipos': defaultdict(int), 'fuentes': defaultdict(int),
             'categorias': defaultdict(int), 'ultimos_7dias': 0, 'prev_7dias': 0, 'ultimos_30dias': 0, 'prev_30dias': 0, 'ultimos_90dias': 0,
             'tendencia': defaultdict(int), 'mensual': defaultdict(lambda: {'fisico': 0, 'rue': 0, 'cyber': 0}),
             'sev_hist': [0] * 10, 'weekday_type': defaultdict(lambda: [0] * 7), 'severidad_promedio': 0.0,
             'conflictos_24h': 0, 'multi_fuente': 0}
        d = lambda n: (hoy - timedelta(days=n)).strftime('%Y-%m-%d')
        h1, h7, h14, h30, h60, h90 = d(1), d(7), d(14), d(30), d(60), d(90)
        lunes = (hoy - timedelta(days=hoy.weekday())).date()
        sem = [(lunes - timedelta(weeks=i)) for i in range(11, -1, -1)]
        semk = {w: {'fisico': 0, 'rue': 0, 'cyber': 0} for w in sem}
        dep_sev = defaultdict(lambda: [0, 0.0])
        ssum, scnt = 0.0, 0
        for c in crimes:
            dep = c.get('departement')
            if dep and dep not in ('National', 'Outre-mer'):
                s['departements'][dep] += 1
                dep_sev[dep][0] += 1
                dep_sev[dep][1] += c.get('severidad', 1)
            if c.get('tipo'):
                s['tipos'][c['tipo']] += 1
            if c.get('fuente'):
                s['fuentes'][c['fuente']] += 1
            cat = c.get('categoria', 'fisico')
            cat = cat if cat in CATEGORIAS else 'fisico'
            s['categorias'][cat] += 1
            if len(c.get('fuentes') or []) > 1:
                s['multi_fuente'] += 1
            sv = c.get('severidad')
            if sv:
                ssum += sv
                scnt += 1
                s['sev_hist'][max(1, min(10, int(sv))) - 1] += 1
            f = c.get('fecha', '')
            if f:
                if f >= h7: s['ultimos_7dias'] += 1
                elif f >= h14: s['prev_7dias'] += 1
                if f >= h30: s['ultimos_30dias'] += 1
                elif f >= h60: s['prev_30dias'] += 1
                if f >= h90: s['ultimos_90dias'] += 1
                if f >= h1 and c.get('conflicto'): s['conflictos_24h'] += 1
                if len(f) >= 7:
                    s['tendencia'][f[:7]] += 1
                    s['mensual'][f[:7]][cat] += 1
                dt = _parse_fecha(c)
                if dt:
                    s['weekday_type'][c.get('tipo', 'other')][dt.weekday()] += 1
                    w = dt.date() - timedelta(days=dt.weekday())
                    if w in semk:
                        semk[w][cat] += 1
        if scnt:
            s['severidad_promedio'] = ssum / scnt
        s['semanal'] = {'labels': [w.strftime('%d/%m') for w in sem], **{k: [semk[w][k] for w in sem] for k in CATEGORIAS}}
        s['dept_bubble'] = [{'d': k, 'n': v[0], 'sev': round(v[1] / v[0], 1)} for k, v in sorted(dep_sev.items(), key=lambda x: -x[1][0])[:15]]
        return s

    def evolucion_mensual(self):
        m = {}
        for c in self.copia():
            f = c.get('fecha', '')
            if len(f) >= 7:
                m[f[:7]] = m.get(f[:7], 0) + 1
        return dict(sorted(m.items()))

    def limpiar_duplicados(self):
        """Fusionne les quasi-doublons existants (les sources s'additionnent)."""
        with _RLOCK:
            antes = len(self.datos['crimes'])
            out, recientes = [], []
            for c in self.datos['crimes']:
                e = self._similar(c, recientes[-1200:]) if c.get('titulo') else None
                if e is not None:
                    self._fusionar(e, c)
                    continue
                out.append(c)
                recientes.append((_tokens(c['titulo']), c))
            self.datos['crimes'] = out
            if len(out) != antes:
                self.guardar()
            return antes - len(out)

    def estadisticas_rapidas(self):
        crimes = self.copia()
        st = self.estadisticas(crimes)
        if not st['total']:
            return {}
        tm = max(st['tipos'].items(), key=lambda x: x[1]) if st['tipos'] else ('other', 0)
        dias = Counter(c['fecha'][:10] for c in crimes if c.get('fecha'))
        dm = dias.most_common(1)[0] if dias else ('-', 0)
        fm = max(st['fuentes'].items(), key=lambda x: x[1]) if st['fuentes'] else ('-', 0)
        dc = max(st['departements'].items(), key=lambda x: x[1]) if st['departements'] else ('-', 0)
        tend = 0.0
        ms = sorted(st['tendencia'])
        if len(ms) >= 2 and st['tendencia'][ms[-2]] > 0:
            tend = (st['tendencia'][ms[-1]] - st['tendencia'][ms[-2]]) / st['tendencia'][ms[-2]] * 100
        return {'tipo_mas_comun': tm[0], 'tipo_mas_comun_count': tm[1], 'tipo_mas_comun_porcentaje': tm[1] / st['total'] * 100,
                'dia_mas_activo': dm[0], 'dia_mas_activo_count': dm[1], 'fuente_mas_activa': fm[0], 'fuente_mas_activa_count': fm[1],
                'departamento_critico': dc[0], 'departamento_critico_count': dc[1], 'tendencia': tend}

    # ---- exportaciones
    def exportar_json(self):
        return json.dumps(self.datos, indent=2, ensure_ascii=False)

    def exportar_csv(self, crimes=None):
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(['ID', 'Titre', 'Date', 'Département', 'Code', 'Type', 'Catégorie', 'Source', 'Sévérité', 'Confiance', 'Pertinence', 'Nb sources', 'Sources', 'Lat', 'Lon', 'URL'])
        for c in (self.copia() if crimes is None else crimes):
            fs = c.get('fuentes') or []
            w.writerow([c['id'], _csv_safe(c.get('titulo')), c.get('fecha', ''), _csv_safe(c.get('departement')), c.get('dep_code') or '',
                        c.get('tipo', ''), c.get('categoria', ''), _csv_safe(c.get('fuente')), c.get('severidad', 0), c.get('confianza', ''),
                        relevancia(c), len(fs), _csv_safe(' | '.join(f.get('n', '') for f in fs)), c.get('lat') or '', c.get('lon') or '', c.get('url', '')])
        return out.getvalue()

    def exportar_geojson(self, crimes=None):
        feats = []
        for c in (self.copia() if crimes is None else crimes):
            if c.get('lat') is None:
                continue
            p = {k: c.get(k) for k in ('id', 'titulo', 'fecha', 'departement', 'tipo', 'categoria', 'fuente', 'severidad', 'confianza', 'url', 'precision')}
            p['relevancia'] = relevancia(c)
            p['fuentes'] = [{'n': f.get('n'), 'u': f.get('u')} for f in (c.get('fuentes') or [])]
            feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [c['lon'], c['lat']]}, 'properties': p})
        return json.dumps({'type': 'FeatureCollection', 'features': feats}, ensure_ascii=False)

    def exportar_html(self):
        st = self.estadisticas()
        e = htmllib.escape
        h = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>DIABOLIC FRANCE - Rapport</title>
<style>body{{background:#03050c;color:#e6f4ff;font-family:'Segoe UI',sans-serif;padding:20px}}h1{{color:#00e5ff;text-align:center}}h2{{color:#ff2bd6;margin-top:30px}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px}}.c{{background:#0a1630;padding:14px;border-radius:10px;text-align:center;border-left:4px solid #00e5ff}}.n{{font-size:2em;color:#00e5ff;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin:14px 0}}th,td{{border:1px solid #16304f;padding:7px;text-align:left}}th{{background:#0a1630;color:#ff2bd6}}a{{color:#00e5ff}}</style></head><body>
<h1>🔪 DIABOLIC FRANCE v{VERSION}</h1><p style="text-align:center">{datetime.now():%Y-%m-%d %H:%M:%S}</p>
<div class="g"><div class="c">Total<div class="n">{st['total']}</div></div><div class="c">7 j<div class="n">{st['ultimos_7dias']}</div></div>
<div class="c">Rue<div class="n">{st['categorias'].get('rue', 0)}</div></div><div class="c">Cyber<div class="n">{st['categorias'].get('cyber', 0)}</div></div></div>
<h2>Départements</h2><table><tr><th>Département</th><th>#</th></tr>"""
        for d, n in sorted(st['departements'].items(), key=lambda x: -x[1])[:15]:
            h += f"<tr><td>{e(d)}</td><td>{n}</td></tr>"
        h += "</table><h2>Types</h2><table><tr><th>Type</th><th>#</th></tr>"
        for k, n in sorted(st['tipos'].items(), key=lambda x: -x[1]):
            dd = TIPOS_CRIMEN.get(k, TIPOS_CRIMEN['other'])
            h += f"<tr><td>{dd['icono']} {e(dd['fr'])}</td><td>{n}</td></tr>"
        h += "</table><h2>Derniers (25) par pertinence</h2><table><tr><th>Date</th><th>Dép.</th><th>Type</th><th>Titre</th><th>Pert.</th><th>Sources</th></tr>"
        for c in sorted(self.copia(), key=lambda x: (x.get('fecha', ''), relevancia(x)), reverse=True)[:25]:
            srcs = ', '.join((f'<a href="{e(f["u"])}">{e(f["n"])}</a>' if re.match(r'^https?://', f.get('u') or '') else e(f.get('n', ''))) for f in (c.get('fuentes') or []))
            h += f"<tr><td>{e(c.get('fecha',''))}</td><td>{e(c.get('departement','?'))}</td><td>{e(c.get('tipo','?'))}</td><td>{e(c['titulo'][:140])}</td><td>{relevancia(c)}</td><td>{srcs}</td></tr>"
        return h + "</table></body></html>"

# ============================================================================
# ANALÍTICA  (z-score, tendencias, Holt, hotspots, grafos, INDICADORES estilo crypto)
# ============================================================================

STOP = set("""dans pour avec sans sous sur cette ainsi alors apres avant aussi autre autres entre depuis encore comme
contre selon vers etre avoir fait faits faire sont etait ete elle elles ils leur leurs nous vous plus tres tout tous toute
toutes dont ceux celui celle quand mais donc lors chez peut peuvent deux trois quatre cinq premier premiere ans jours jour
semaine mois annee hier aujourd demain apres police gendarmerie gendarmes policiers enquete journal article lire video
photos direct france francais francaise suite rappel nouvelle nouveau nouvelles""".split())


def _hav(la1, lo1, la2, lo2):
    return math.hypot(la1 - la2, (lo1 - lo2) * math.cos(math.radians((la1 + la2) / 2)))


def _sma(a, w):
    out = []
    for i in range(len(a)):
        seg = a[max(0, i - w + 1): i + 1]
        out.append(sum(seg) / len(seg))
    return out


def _std(a):
    if not a:
        return 0.0
    m = sum(a) / len(a)
    return math.sqrt(sum((x - m) ** 2 for x in a) / len(a))


def _rsi(a, n=14):
    """RSI de Wilder sur la série des comptes quotidiens (0-100; >70 escalade, <30 apaisement)."""
    out = [50.0] * len(a)
    if len(a) <= n:
        return out
    gains = [max(0, a[i] - a[i - 1]) for i in range(1, len(a))]
    loss = [max(0, a[i - 1] - a[i]) for i in range(1, len(a))]
    ag, al = sum(gains[:n]) / n, sum(loss[:n]) / n
    for i in range(n, len(a)):
        if i > n:
            ag = (ag * (n - 1) + gains[i - 1]) / n
            al = (al * (n - 1) + loss[i - 1]) / n
        out[i] = 100.0 if al == 0 and ag > 0 else (50.0 if al == 0 else 100 - 100 / (1 + ag / al))
    return out


def _threat(counts, sev7, rue_share):
    base = counts[:-7] or counts
    mu, sd = (sum(base) / len(base), _std(base)) if base else (0, 0)
    last7 = sum(counts[-7:]) / 7.0
    z = (last7 - mu) / sd if sd > 0 else 0.0
    idx = 38 + 16 * max(-2.0, min(3.0, z)) + 3.0 * (sev7 - 4) + 14 * rue_share
    return max(0.0, min(100.0, idx))


class Analitica:
    @staticmethod
    def serie_diaria(crimes, dias=60):
        hoy = datetime.now().date()
        base = {(hoy - timedelta(days=i)).strftime('%Y-%m-%d'): 0 for i in range(dias - 1, -1, -1)}
        for c in crimes:
            f = (c.get('fecha') or '')[:10]
            if f in base:
                base[f] += 1
        vals = list(base.values())
        mu = sum(vals) / len(vals) if vals else 0
        sd = _std(vals)
        return [{'date': d, 'count': n, 'z': round((n - mu) / sd, 2) if sd > 0 else 0.0} for d, n in base.items()]

    @staticmethod
    def holt(series, alpha=.5, beta=.3, h=4):
        if len(series) < 4:
            return []
        lv, b = series[0], series[1] - series[0]
        for y in series[1:]:
            lp = lv
            lv = alpha * y + (1 - alpha) * (lv + b)
            b = beta * (lv - lp) + (1 - beta) * b
        return [max(0.0, round(lv + (i + 1) * b, 1)) for i in range(h)]

    @staticmethod
    def pronostico(crimes, semanas=16, h=4):
        hoy = datetime.now().date()
        lunes_act = hoy - timedelta(days=hoy.weekday())
        wk = [lunes_act - timedelta(weeks=i) for i in range(semanas, 0, -1)]
        cnt = Counter()
        for c in crimes:
            dt = _parse_fecha(c)
            if dt:
                d = dt.date()
                cnt[d - timedelta(days=d.weekday())] += 1
        hist = [cnt.get(w, 0) for w in wk]
        pred = Analitica.holt(hist, h=h)
        fut = [(lunes_act + timedelta(weeks=i)).strftime('%Y-%m-%d') for i in range(h)]
        return {'hist_labels': [w.strftime('%Y-%m-%d') for w in wk], 'hist': hist, 'pred_labels': fut, 'pred': pred}

    @staticmethod
    def tendencias(crimes, n=28):
        hoy = datetime.now()
        h7 = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
        h60 = (hoy - timedelta(days=60)).strftime('%Y-%m-%d')
        a, b = Counter(), Counter()
        for c in crimes:
            f = c.get('fecha', '')
            toks = [w for w in re.findall(r'[a-z]{4,}', norm(c['titulo'])) if w not in STOP]
            if f >= h7:
                a.update(set(toks))
            elif f >= h60:
                b.update(set(toks))
        out = []
        for w, ca in a.items():
            if ca < 3:
                continue
            esperado = b.get(w, 0) * 7 / 53
            out.append({'word': w, 'count': ca, 'score': round((ca + 1) / (esperado + 1), 2)})
        out.sort(key=lambda x: (-x['score'], -x['count']))
        return out[:n]

    @staticmethod
    def hotspots(crimes, celda=0.4, top=8):
        g = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
        for c in crimes:
            if c.get('lat') is None or c.get('lon') is None:
                continue
            k = (round(c['lat'] / celda), round(c['lon'] / celda))
            v = g[k]
            v[0] += 1; v[1] += c['lat']; v[2] += c['lon']; v[3] += c.get('severidad', 1)
        res = []
        for k, (n, sl, so, ss) in g.items():
            la, lo = sl / n, so / n
            code = min(DEPS, key=lambda d: _hav(la, lo, DEPS[d][1], DEPS[d][2]))
            res.append({'lat': round(la, 4), 'lon': round(lo, 4), 'count': n, 'sev': round(ss / n, 1),
                        'score': round(n * (1 + ss / n / 5), 1), 'label': DEPS[code][0]})
        res.sort(key=lambda x: -x['score'])
        return res[:top]

    @staticmethod
    def red(crimes, max_edges=45):
        cnt = Counter((c['tipo'], c['departement']) for c in crimes if c.get('dep_code') and c.get('tipo') != 'other')
        edges = cnt.most_common(max_edges)
        nodes, tv, dv = {}, Counter(), Counter()
        for (tp, dp), n in edges:
            tv[tp] += n; dv[dp] += n
        for tp, n in tv.items():
            nodes['t:' + tp] = {'id': 't:' + tp, 'key': tp, 'group': 'tipo', 'label': tp, 'value': n}
        for dp, n in dv.items():
            nodes['d:' + dp] = {'id': 'd:' + dp, 'key': dp, 'group': 'dep', 'label': dp, 'value': n}
        return {'nodes': list(nodes.values()), 'edges': [{'from': 't:' + tp, 'to': 'd:' + dp, 'value': n} for (tp, dp), n in edges]}

    @staticmethod
    def sankey(crimes, top_deps=8):
        deps = Counter(c['departement'] for c in crimes if c.get('dep_code'))
        top = {d for d, _ in deps.most_common(top_deps)}
        a, b = Counter(), Counter()
        for c in crimes:
            if c.get('tipo') == 'other':
                continue
            a[('cat:' + c.get('categoria', 'fisico'), 'tipo:' + c['tipo'])] += 1
            if c.get('departement') in top:
                b[('tipo:' + c['tipo'], 'dep:' + c['departement'])] += 1
        return {'flows': [[x, y, n] for (x, y), n in list(a.items()) + list(b.items())]}

    @staticmethod
    def indicadores(crimes, dias=90):
        """Indicateurs façon marché crypto appliqués au flux criminel: SMA, Bollinger, RSI, indice de menace, tickers."""
        hoy = datetime.now().date()
        ds = [(hoy - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(dias - 1, -1, -1)]
        pos = {d: i for i, d in enumerate(ds)}
        counts = [0] * dias
        bycat = {k: [0] * dias for k in CATEGORIAS}
        bytipo = defaultdict(lambda: [0] * dias)
        sev = [[] for _ in range(dias)]
        for c in crimes:
            i = pos.get((c.get('fecha') or '')[:10])
            if i is None:
                continue
            counts[i] += 1
            cat = c.get('categoria') if c.get('categoria') in CATEGORIAS else 'fisico'
            bycat[cat][i] += 1
            bytipo[c.get('tipo', 'other')][i] += 1
            sev[i].append(c.get('severidad', 1))
        sma7, sma30 = _sma(counts, 7), _sma(counts, 30)
        bb_up, bb_dn = [], []
        for i in range(dias):
            seg = counts[max(0, i - 19): i + 1]
            m, sd = sum(seg) / len(seg), _std(seg)
            bb_up.append(round(m + 2 * sd, 2)); bb_dn.append(round(max(0.0, m - 2 * sd), 2))
        rsi = _rsi(counts)
        mom = (sma7[-1] / sma30[-1] - 1) * 100 if sma30[-1] > 0 else 0.0
        signal = 'up' if (rsi[-1] > 65 or mom > 15) else 'dn' if (rsi[-1] < 35 or mom < -15) else 'fl'
        l14 = counts[-14:]
        vol = (_std(l14) / (sum(l14) / 14)) if sum(l14) > 0 else 0.0
        flat = lambda L: [x for s in L[-7:] for x in s]
        sv7 = flat(sev)
        sev7 = sum(sv7) / len(sv7) if sv7 else 4.0
        sv_prev = [x for s in sev[-14:-7] for x in s]
        sevp = sum(sv_prev) / len(sv_prev) if sv_prev else sev7
        n7 = sum(counts[-7:])
        share = (sum(bycat['rue'][-7:]) / n7) if n7 else 0.0
        idx = _threat(counts, sev7, share)
        n7p = sum(counts[-14:-7])
        sev_p = [x for s in sev[:-7] for x in s]
        idx_prev = _threat(counts[:-7], sevp, (sum(bycat['rue'][-14:-7]) / n7p) if n7p else 0.0) if dias > 21 else idx
        dl = lambda a, b: ((a - b) / b * 100) if b > 0 else (100.0 if a > 0 else 0.0)
        T = []
        T.append({'key': 'idx', 'kind': 'idx', 'label': 'threat_idx', 'value': round(idx, 1), 'delta': round(dl(idx, idx_prev), 1), 'series': [round(_threat(counts[:len(counts) - k], sev7, share), 1) for k in range(13, -1, -1)]})
        T.append({'key': 'all', 'kind': 'all', 'label': 'f_all', 'value': n7, 'delta': round(dl(n7, n7p), 1), 'series': counts[-14:]})
        for k in CATEGORIAS:
            a, b = sum(bycat[k][-7:]), sum(bycat[k][-14:-7])
            T.append({'key': k, 'kind': 'cat', 'value': a, 'delta': round(dl(a, b), 1), 'series': bycat[k][-14:]})
        top = sorted(((sum(v[-30:]), k) for k, v in bytipo.items() if k != 'other'), reverse=True)[:6]
        for _, k in top:
            a, b = sum(bytipo[k][-7:]), sum(bytipo[k][-14:-7])
            T.append({'key': k, 'kind': 'tipo', 'value': a, 'delta': round(dl(a, b), 1), 'series': bytipo[k][-14:]})
        T.append({'key': 'rsi', 'kind': 'rsi', 'label': 'RSI', 'value': round(rsi[-1], 1), 'delta': round(dl(rsi[-1], rsi[-8]), 1), 'series': [round(x, 1) for x in rsi[-14:]]})
        T.append({'key': 'sev', 'kind': 'sev', 'label': 'k_sev', 'value': round(sev7, 1), 'delta': round(dl(sev7, sevp), 1), 'series': [round(sum(s) / len(s), 1) if s else 0 for s in sev[-14:]]})
        return {'tickers': T, 'rsi': round(rsi[-1], 1), 'momentum': round(mom, 1), 'signal': signal, 'volatility': round(vol, 2),
                'threat': {'idx': round(idx, 1), 'level': 0 if idx < 25 else 1 if idx < 50 else 2 if idx < 75 else 3},
                'series': {'dates': ds, 'counts': counts, 'sma7': [round(x, 2) for x in sma7], 'sma30': [round(x, 2) for x in sma30],
                           'up': bb_up, 'dn': bb_dn, 'rsi': [round(x, 1) for x in rsi]}}

    @staticmethod
    def analytics(crimes):
        diaria = Analitica.serie_diaria(crimes)
        return {'daily': diaria, 'anomalies': [d for d in diaria if d['z'] >= 2 and d['count'] >= 3],
                'forecast': Analitica.pronostico(crimes), 'trending': Analitica.tendencias(crimes), 'hotspots': Analitica.hotspots(crimes)}

# ============================================================================
# GRÁFICOS ESTÁTICOS (matplotlib / networkx)
# ============================================================================

def render_estatico(kind, crimes, lang='fr'):
    """Devuelve bytes PNG, o None si falta matplotlib (o networkx para 'red')."""
    if not HAS_MPL or (kind == 'red' and not HAS_NX):
        return None
    lang = lang if lang in LANGS else 'fr'
    bg, fg, grid = '#0b0f1a', '#d7dbe5', '#222a3d'
    plt.rcParams.update({'text.color': fg, 'axes.labelcolor': fg, 'xtick.color': fg, 'ytick.color': fg,
                         'axes.edgecolor': grid, 'axes.facecolor': bg, 'figure.facecolor': bg, 'font.size': 9})
    fig, ax = plt.subplots(figsize=(9, 5.2))
    tn = lambda k: TIPOS_CRIMEN.get(k, TIPOS_CRIMEN['other'])[lang]
    try:
        if kind == 'tipos':
            cnt = Counter(c['tipo'] for c in crimes if c.get('tipo') != 'other').most_common()[::-1]
            if not cnt: raise ValueError('empty')
            ax.barh([tn(k) for k, _ in cnt], [n for _, n in cnt], color=[TIPOS_CRIMEN[k]['color'] for k, _ in cnt])
            ax.set_title(TEXTOS[lang]['st_tipos'])
            ax.grid(axis='x', color=grid)
        elif kind == 'mensual':
            m = defaultdict(lambda: [0, 0])
            for c in crimes:
                f = c.get('fecha', '')[:7]
                if len(f) == 7:
                    m[f][1 if c.get('categoria') == 'cyber' else 0] += 1
            if not m: raise ValueError('empty')
            ks = sorted(m)[-18:]
            ax.bar(ks, [m[k][0] for k in ks], color='#ed2939', label=TEXTOS[lang]['phys'])
            ax.bar(ks, [m[k][1] for k in ks], bottom=[m[k][0] for k in ks], color='#2f5bff', label=TEXTOS[lang]['cyber'])
            ax.legend(facecolor=bg, edgecolor=grid)
            ax.set_title(TEXTOS[lang]['st_mensual'])
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            ax.grid(axis='y', color=grid)
        elif kind == 'heatmap':
            cnt = Counter(c['tipo'] for c in crimes if c.get('tipo') != 'other')
            tipos = [k for k, _ in cnt.most_common(12)]
            if not tipos: raise ValueError('empty')
            mat = [[0] * 7 for _ in tipos]
            for c in crimes:
                if c.get('tipo') in tipos:
                    dt = _parse_fecha(c)
                    if dt: mat[tipos.index(c['tipo'])][dt.weekday()] += 1
            im = ax.imshow(mat, cmap='inferno', aspect='auto')
            ax.set_yticks(range(len(tipos))); ax.set_yticklabels([tn(k) for k in tipos])
            ax.set_xticks(range(7)); ax.set_xticklabels(['L', 'M', 'X', 'J', 'V', 'S', 'D'] if lang == 'es'
                                                        else ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'])
            for i in range(len(tipos)):
                for j in range(7):
                    ax.text(j, i, mat[i][j], ha='center', va='center', color='white', fontsize=7)
            fig.colorbar(im, ax=ax)
            ax.set_title(TEXTOS[lang]['st_heatmap'])
        elif kind == 'hexbin':
            pts = [(c['lon'], c['lat']) for c in crimes if c.get('lat') is not None and -6 < c['lon'] < 10 and 41 < c['lat'] < 52]
            if not pts: raise ValueError('empty')
            hb = ax.hexbin([p[0] for p in pts], [p[1] for p in pts], gridsize=34, cmap='inferno', mincnt=1,
                           extent=(-5.5, 9.8, 41, 51.5))
            ax.set_aspect(1 / math.cos(math.radians(46)))
            ax.set_xlim(-5.5, 9.8); ax.set_ylim(41, 51.5)
            fig.colorbar(hb, ax=ax)
            for code in ('75', '13', '69', '31', '06', '33', '59', '67', '44', '35'):
                n, la, lo = DEPS[code]
                ax.annotate(n, (lo, la), color='#9aa3b2', fontsize=7)
            ax.set_title(TEXTOS[lang]['st_hexbin'])
        elif kind == 'red':
            red = Analitica.red(crimes, 40)
            if not red['edges']: raise ValueError('empty')
            G = nx.Graph()
            for n in red['nodes']:
                G.add_node(n['id'], **n)
            for e in red['edges']:
                G.add_edge(e['from'], e['to'], weight=e['value'])
            pos = nx.spring_layout(G, seed=7, k=0.9)
            cols = [TIPOS_CRIMEN[G.nodes[n]['key']]['color'] if n.startswith('t:') else '#475569' for n in G]
            sizes = [180 + 55 * G.nodes[n]['value'] for n in G]
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=.35, edge_color='#64748b',
                                   width=[0.5 + .4 * G[u][v]['weight'] for u, v in G.edges()])
            nx.draw_networkx_nodes(G, pos, ax=ax, node_color=cols, node_size=sizes, linewidths=0)
            nx.draw_networkx_labels(G, pos, ax=ax, font_color='#e5e7eb', font_size=7,
                                    labels={n: tn(G.nodes[n]['key']) if n.startswith('t:') else G.nodes[n]['label'] for n in G})
            ax.axis('off')
            ax.set_title(TEXTOS[lang]['st_red'])
        else:
            plt.close(fig)
            return None
    except ValueError:
        ax.text(.5, .5, TEXTOS[lang]['no_data'], ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=130, facecolor=bg)
    plt.close(fig)
    return buf.getvalue()


# ============================================================================
# ESTADO DE LAS FUENTES (salud, URL descubierta, fuentes añadidas desde el panel)
# ============================================================================

_ESTADO_LOCK = threading.RLock()
ESTADO = {'fuentes': {}, 'custom': []}


def cargar_estado():
    """Lee el estado; acepta el formato plano de la v2 ({nombre: {url, activo}})."""
    global ESTADO
    try:
        with open(ARCHIVO_ESTADO, 'r', encoding='utf-8') as f:
            d = json.load(f)
    except Exception:
        d = {}
    if 'fuentes' not in d:
        d = {'fuentes': {k: v for k, v in d.items() if isinstance(v, dict)}, 'custom': []}
    d.setdefault('custom', [])
    ESTADO = d
    return ESTADO


def guardar_estado():
    with _ESTADO_LOCK:
        try:
            tmp = ARCHIVO_ESTADO + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(ESTADO, f, indent=1, ensure_ascii=False)
            os.replace(tmp, ARCHIVO_ESTADO)
        except Exception as e:
            logger.warning(f'estado: {e}')


def aplicar_estado(fuentes):
    cargar_estado()
    nombres = {f['nombre'] for f in fuentes}
    for c in ESTADO.get('custom', []):
        if c.get('nombre') not in nombres:
            fuentes.append(c)
    for f in fuentes:
        e = ESTADO['fuentes'].get(f['nombre'])
        if e:
            f['url'] = e.get('url') or f['url']
            f['activo'] = e.get('activo', True)
            if e.get('rss_auto') and not f.get('rss'):
                f['rss_auto'] = e['rss_auto']
            p = urlparse(f['url'])
            f['base'] = f'{p.scheme}://{p.netloc}'
    return fuentes


def registrar_salud(f, info=None):
    with _ESTADO_LOCK:
        e = ESTADO['fuentes'].setdefault(f['nombre'], {})
        e['url'] = f['url']
        e['activo'] = f.get('activo', True)
        if f.get('rss_auto'):
            e['rss_auto'] = f['rss_auto']
        if info is not None:
            ok = info.get('kind') == 'ok'
            e['last'] = {'n': info.get('n', 0), 'cand': info.get('cand', 0), 'kind': info.get('kind', ''), 'dur': info.get('dur', 0),
                         'note': info.get('note', ''), 'ts': datetime.now().isoformat(timespec='seconds')}
            e['fails'] = 0 if ok else e.get('fails', 0) + 1
    guardar_estado()

# ============================================================================
# AUTO-DISCOVERY DE URLs   (la herramienta se repara sola cuando una fuente cambia de cabecera/subdominio/sección)
# ============================================================================

_SEC_CRIME = {'faits divers': 12, 'fait divers': 10, 'faits-divers': 12, 'justice': 6, 'police': 5, 'gendarmerie': 5,
              'criminalite': 6, 'insecurite': 5, 'delinquance': 5, 'enquete': 3, 'securite': 3}
_SEC_CYBER = {'cybersecurite': 12, 'cybercriminalite': 12, 'cyberattaque': 10, 'securite': 8, 'piratage': 8, 'hacking': 6,
              'cyber': 6, 'ransomware': 8, 'menaces': 4, 'alerte': 6}
_SEC_GOV = {'actualites': 8, 'actualite': 8, 'communiques': 8, 'presse': 4, 'alertes': 7, 'alerte': 6, 'actus': 6, 'securite': 3}
_PATHS_V1 = ['faits-divers', 'faits_divers', 'actualite', 'actualites', 'justice', 'police', 'gendarmerie', 'criminalite',
             'delinquance', 'arrestation', 'interpellation', 'enquete', 'crime', 'crimes', 'violence']
_PATHS_CYBER = ['cybersecurite', 'securite', 'cybercriminalite', 'actualites', 'actualite', 'cyber']
_PATHS_GOV = ['actualites', 'actualite', 'communiques-de-presse', 'alertes', 'presse', 'actus']


def _reg(host):
    return '.'.join((host or '').split(':')[0].split('.')[-2:])


def _fecha_desde_url(u):
    m = re.search(r'/(20\d\d)[/-](0[1-9]|1[0-2])[/-](0[1-9]|[12]\d|3[01])(?:/|-|$)', u or '')
    return f'{m.group(1)}-{m.group(2)}-{m.group(3)}' if m else None


class URLAutoDiscoverer:
    def __init__(self):
        self.cache_file = ARCHIVO_CACHE
        self.cache = self.load_cache()
        self.common_paths = _PATHS_V1

    def load_cache(self):
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @staticmethod
    def pagina_valida(html):
        """¿Parece un listado de noticias? (estructura) o contiene palabras clave v1 del dominio."""
        if len(re.findall(r'<article|<h[23][ >]', html or '', re.I)) >= 4:
            return True
        low = (html or '').lower()
        return any(k in low for k in ('meurtre', 'violence', 'crime', 'braquage', 'cyberattaque', 'ransomware', 'piratage'))

    def probar_url(self, url, intentos=1):
        r, _ = fetch(url, intentos=intentos, timeout=15)
        return r.text if (r is not None and self.pagina_valida(r.text)) else None

    @staticmethod
    def variantes(url):
        p = urlparse(url)
        hosts = [p.netloc, p.netloc[4:] if p.netloc.startswith('www.') else 'www.' + p.netloc]
        path = p.path or '/'
        paths = [path, path.rstrip('/') if path != '/' else path, (path + '/') if not path.endswith('/') else path]
        out = []
        for h in hosts:
            for pa in paths:
                u = f'{p.scheme}://{h}{pa}' + (('?' + p.query) if p.query else '')
                if u != url and u not in out:
                    out.append(u)
        return out

    @staticmethod
    def feeds_de(html, base):
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            return []
        out = []
        for l in soup.find_all('link', href=True):
            t = (l.get('type') or '').lower()
            if 'rss' in t or 'atom' in t:
                out.append(urljoin(base, l['href']))
        return list(dict.fromkeys(out))[:4]

    def candidatos_home(self, base_url, html, ctx):
        words = _SEC_CYBER if ctx == 'cyber' else _SEC_GOV if ctx == 'gov' else _SEC_CRIME
        host = _reg(urlparse(base_url).netloc)
        found = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            return []
        for a in soup.find_all('a', href=True)[:900]:
            href = urljoin(base_url, a['href']).split('#')[0]
            pu = urlparse(href)
            if pu.scheme not in ('http', 'https') or _reg(pu.netloc) != host:
                continue
            path = norm(pu.path)
            segs = [s for s in pu.path.split('/') if s]
            txt = norm(a.get_text(' '))[:60]
            sc = sum(w for k, w in words.items() if k in path) + sum(w * 0.6 for k, w in words.items() if k in txt)
            if len(segs) > 3:
                sc -= 4
            if re.search(r'\d{5,}|[-_]\d{3,}\.html?$', pu.path):
                sc -= 6
            if pu.query:
                sc -= 2
            if sc >= 5:
                found[href] = max(found.get(href, 0), sc)
        return sorted(((s, u) for u, s in found.items()), reverse=True)[:6]

    def _guardar(self, nombre, url, how):
        self.cache[nombre] = {'url': url, 'found_date': datetime.now().isoformat(timespec='seconds'), 'how': how}
        self.save_cache()
        return url

    def discover_url(self, fuente, razon='', deadline=None):
        """-> (nueva_url | None, como).  Orden: caché → www/apex/slash → enlaces de la portada → rutas v1."""
        nombre, orig = fuente['nombre'], fuente['url']
        ctx = 'gov' if fuente.get('tipo') == 'gov' else fuente.get('ctx', 'crime')
        vencido = lambda: deadline is not None and time.time() > deadline
        cu = self.cache.get(nombre, {}).get('url')
        if cu and cu != orig and self.probar_url(cu):
            return cu, 'cache'
        for v in self.variantes(orig):
            if vencido():
                return None, 'tiempo'
            if self.probar_url(v):
                return self._guardar(nombre, v, 'variante'), 'variante'
        bases = [fuente['base']] + [b for b in self.variantes(fuente['base'] + '/')]
        for b in dict.fromkeys(bases):
            if vencido():
                return None, 'tiempo'
            r, k = fetch(b, 1, 15)
            if r is None:
                continue
            feeds = self.feeds_de(r.text, r.url)
            if feeds and not fuente.get('rss'):
                fuente['rss_auto'] = feeds[0]
            for sc, u in self.candidatos_home(r.url, r.text, ctx):
                if vencido():
                    return None, 'tiempo'
                if self.probar_url(u):
                    return self._guardar(nombre, u, 'nav'), 'nav'
            break
        paths = _PATHS_GOV if ctx == 'gov' else _PATHS_CYBER if ctx == 'cyber' else self.common_paths
        base = fuente['base'].rstrip('/')
        for path in paths[:8]:
            for test in (f'{base}/{path}', f'{base}/{path}/', f'{base}/rubrique/{path}'):
                if vencido():
                    return None, 'tiempo'
                if self.probar_url(test):
                    return self._guardar(nombre, test, 'ruta'), 'ruta'
        return None, 'sin_resultado'


class VerificadorFuentes:
    """Menú 8 / botón 'Verificar': comprueba cada fuente (3 intentos como v1) y repara URLs con auto-discovery."""
    def __init__(self):
        self.discoverer = URLAutoDiscoverer()

    def verificar_fuente(self, fuente, aplicar_discovery=True):
        r, kind = fetch(fuente['url'], MAX_INTENTOS)
        if r is not None:
            fuente['activo'] = True
            return fuente, True, kind
        if aplicar_discovery:
            nueva, how = self.discoverer.discover_url(fuente, kind, time.time() + PRESUPUESTO_FUENTE)
            if nueva:
                fuente['url'] = nueva
                p = urlparse(nueva)
                fuente['base'] = f'{p.scheme}://{p.netloc}'
                fuente['activo'] = True
                return fuente, True, 'disc:' + how
        fuente['activo'] = False
        return fuente, False, kind

    def verificar_todas(self, fuentes, mostrar_progreso=True, progreso=None, stop=None):
        emit('info', f"\n{'═' * 78}\n🔍 {t('m_verify').upper()}\n{'═' * 78}")
        activas, auto, total = 0, 0, len(fuentes)
        res = []
        for i, f in enumerate(fuentes, 1):
            if stop is not None and stop.is_set():
                emit('warn', '■ stop')
                break
            orig = f['url']
            fv, ok, how = self.verificar_fuente(f, True)
            if ok:
                activas += 1
                if fv['url'] != orig:
                    auto += 1
                    emit('disc', f"[{i:2d}/{total}] ↻ {fv['nombre']}  {orig}  →  {fv['url']}")
                else:
                    emit('ok', f"[{i:2d}/{total}] ✔ {fv['nombre']}")
            else:
                emit('err', f"[{i:2d}/{total}] ✖ {fv['nombre']}  ({how})")
            registrar_salud(fv)
            res.append(fv)
            if progreso:
                progreso(i / total, fv['nombre'], i)
        emit('info', f"📊 {activas}/{total} OK · ↻ {auto} auto-discovery")
        return res

# ============================================================================
# EXTRACTOR  (cosecha v1 + RSS + clasificación anti-falsos-positivos)
# ============================================================================

def _xml_texto(s):
    s = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return limpiar(htmllib.unescape(s))


def parse_rss(texto):
    out = []
    for blk in re.findall(r'<item[ >].*?</item>|<entry[ >].*?</entry>', texto, re.S | re.I)[:60]:
        def g(tag):
            m = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', blk, re.S | re.I)
            return _xml_texto(m.group(1)) if m else ''
        link = g('link')
        if not link:
            m = re.search(r'<link[^>]+href="([^"]+)"', blk, re.I)
            link = m.group(1) if m else ''
        fecha = None
        raw = g('pubDate') or g('updated') or g('published')
        try:
            fecha = parsedate_to_datetime(raw).strftime('%Y-%m-%d')
        except Exception:
            if _fecha_ok(raw):
                fecha = raw[:10]
        out.append({'titulo': g('title'), 'texto': g('description') or g('summary'), 'url': link, 'fecha': fecha})
    return out


def _url_segura(u):
    return u if u and urlparse(u).scheme in ('http', 'https') else ''


def _nivel_gov(it, fuente):
    u, tt = (it.get('url') or '').lower(), norm(it.get('titulo', ''))
    n = 3
    if '-ale-' in u or '/alerte/' in u or tt.startswith('alerte'):
        n = 8
    elif '-avi-' in u or '/avis/' in u:
        n = 4
    elif '/cti/' in u or '-cti-' in u:
        n = 5
    if re.search(r'critique|urgence attentat|ransomware|rancongiciel|exploit\w* activement|attentat|menace terroriste', tt):
        n += 2
    return min(10, n)


class ExtractorNoticias:
    def __init__(self, fuentes, sens=None):
        self.fuentes = fuentes
        self.sens = sens or SENSIBILIDAD
        self.disc = URLAutoDiscoverer()

    # ---- cosecha: lógica v1 (article + div.class + h1-h4), con protección contra contenedores gigantes
    def cosechar(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        elementos = []
        elementos.extend(soup.find_all('article'))
        elementos.extend(soup.find_all('div', class_=re.compile(r'article|story|post|news|entry', re.I)))
        elementos.extend(soup.find_all(['h1', 'h2', 'h3', 'h4']))
        items, vistos = [], set()
        for elem in elementos:
            if len(items) >= MAX_ELEMENTOS:
                break
            texto = limpiar(elem.get_text(' '))
            if len(texto) < 40:                                   # v1
                continue
            if elem.name in ('div', 'article') and (len(texto) > 1500 or len(elem.find_all(['article', 'h2', 'h3'])) > 3):
                continue                                          # contenedor de página entera, no una noticia
            is_h = elem.name in ('h1', 'h2', 'h3', 'h4')
            head = elem if is_h else elem.find(['h1', 'h2', 'h3', 'h4'])
            titulo = limpiar(head.get_text(' ')) if head is not None else ''
            if len(titulo) < 20:
                titulo = texto[:220]
            key = norm(titulo)[:120]
            if key in vistos:
                continue
            vistos.add(key)
            a = elem if elem.name == 'a' else None
            if a is None and head is not None:
                a = head.find('a', href=True) or head.find_parent('a')
            if a is None:
                a = elem.find('a', href=True) or elem.find_parent('a')
            href = urljoin(url, a['href']) if a is not None and a.get('href') else ''
            tm = elem.find('time')
            if tm is None:
                par = elem.find_parent('article')
                tm = par.find('time') if par is not None else None
            fecha = tm.get('datetime', '')[:10] if tm is not None and tm.get('datetime') else None
            if not _fecha_ok(fecha):
                fecha = _fecha_desde_url(href)
            items.append({'titulo': titulo[:500], 'texto': texto[:900], 'url': href, 'fecha': fecha})
        return items

    def _evento(self, fuente, it, rej):
        titulo = limpiar(it['titulo'])
        if not (20 <= len(titulo) <= 400):
            rej['nav'] += 1
            return None
        _id = hashlib.md5(norm(titulo)[:200].encode()).hexdigest()[:16]
        teaser = it.get('texto', '')[:350]
        geo = geolocalizar(titulo + ' ' + teaser, dep_code_fuente(fuente), _id)
        r = clasificar_detalle(titulo, teaser, self.sens, geo['precision'])
        if 'reject' in r:
            rej[r['reject']] += 1
            return None
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha = it.get('fecha') if _fecha_ok(it.get('fecha')) else hoy
        fecha = min(fecha[:10], hoy)
        url = _url_segura(it.get('url'))
        return {'id': _id, 'titulo': titulo[:500], 'fecha': fecha, 'tipo': r['tipo'], 'categoria': r['cat'], 'fuente': fuente['nombre'],
                'severidad': r['sev'], 'confianza': r['conf'], 'url': url,
                'fuentes': [{'n': fuente['nombre'], 'u': url, 'f': fecha}],
                'conflicto': es_conflicto(r['tipo'], r['cat'], r['sev'], r['conf']), 'v': SCHEMA, **geo}

    def _alerta(self, fuente, it, rej):
        titulo = limpiar(it['titulo'])
        if len(titulo) < 25 or len(titulo) > 400 or (_NAV.search(norm(titulo)) and len(titulo) <= 45):
            rej['nav'] += 1
            return None
        if fuente.get('filtro') and not re.search(fuente['filtro'], norm(titulo + ' ' + it.get('texto', '')[:300])):
            rej['sin_keyword'] += 1
            return None
        url = _url_segura(it.get('url'))
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha = it.get('fecha') if _fecha_ok(it.get('fecha')) else hoy
        return {'id': hashlib.md5(('gov' + norm(titulo)[:200]).encode()).hexdigest()[:16], 'titulo': titulo[:300], 'fecha': min(fecha[:10], hoy),
                'url': url, 'fuente': fuente['nombre'], 'ctx': fuente.get('ctx', 'crime'), 'nivel': _nivel_gov(it, fuente)}

    def extraer_de_fuente(self, fuente, paginas=PAGINAS_BUSQUEDA, stop=None):
        """-> (eventos, alertas, info). Dos intentos y se sigue; si cambia de dominio/sección se auto-descubre la URL nueva."""
        t0 = time.time()
        deadline = t0 + PRESUPUESTO_FUENTE
        info = {'nombre': fuente['nombre'], 'kind': '', 'n': 0, 'cand': 0, 'rej': Counter(), 'url_nueva': None, 'note': '', 'dur': 0}
        es_gov = fuente.get('tipo') == 'gov'
        eventos, alertas, vistos_ids = [], [], set()

        def procesar(items):
            n0 = len(eventos) + len(alertas)
            for it in items:
                if es_gov:
                    a = self._alerta(fuente, it, info['rej'])
                    if a and a['id'] not in vistos_ids:
                        vistos_ids.add(a['id']); alertas.append(a)
                else:
                    e = self._evento(fuente, it, info['rej'])
                    if e and e['id'] not in vistos_ids:
                        vistos_ids.add(e['id']); eventos.append(e)
            return len(eventos) + len(alertas) - n0

        def rss(url):
            r, _ = fetch(url, 1)
            its = parse_rss(r.text) if r is not None else []
            info['cand'] += len(its)
            return procesar(its)

        def adoptar(url, nota):
            fuente['url'] = url
            p = urlparse(url)
            fuente['base'] = f'{p.scheme}://{p.netloc}'
            info['url_nueva'] = url
            emit('disc', f"      ↻ {fuente['nombre']}: URL actualizada ({nota}) → {url}")

        try:
            if fuente.get('rss') or fuente.get('rss_auto'):
                rss(fuente.get('rss') or fuente.get('rss_auto'))
            r, kind = fetch(fuente['url'], INTENTOS_ESCANEO)
            if r is not None:                                      # ¿redirigida a otro host/sección?
                pf, po = urlparse(r.url), urlparse(fuente['url'])
                if pf.netloc != po.netloc or pf.path.rstrip('/') != po.path.rstrip('/'):
                    if pf.path.strip('/') == '' and po.path.strip('/') != '':
                        r, kind = None, 'gone'                       # nos mandó a la portada: la sección cambió
                    elif _reg(pf.netloc) == _reg(po.netloc):
                        adoptar(r.url, 'redirección')
            if r is None and kind == 'blocked' and not (stop is not None and stop.is_set()):
                info['kind'] = kind                                # bloqueo = problema del host, no de la URL: solo RSS, sin probar variantes
                if not (eventos or alertas):
                    pu = urlparse(fuente['url']); b0 = f'{pu.scheme}://{pu.netloc}'; u0 = fuente['url'].rstrip('/')
                    probados = {fuente.get('rss'), fuente.get('rss_auto')}
                    for fd in (fuente.get('rss_auto'), b0 + '/feed/', b0 + '/rss.xml', b0 + '/rss', u0 + '/rss', u0 + '/feed/', u0 + '.rss'):
                        if not fd or (fd in probados and fd != fuente.get('rss_auto')) or time.time() > deadline or (stop is not None and stop.is_set()):
                            continue
                        probados.add(fd)
                        n_ant = info['cand']
                        rss(fd)
                        if info['cand'] > n_ant:
                            fuente['rss_auto'] = fd
                            break
                        time.sleep(get_random_delay())
            elif r is None and not (stop is not None and stop.is_set()):
                info['kind'] = kind
                nueva, how = self.disc.discover_url(fuente, kind, deadline)
                if nueva:
                    adoptar(nueva, how)
                    r, kind = fetch(nueva, 1)
            info['kind'] = kind
            if r is None:
                info['note'] = {'dns': 'dominio muerto', 'blocked': 'bloqueada', 'gone': 'URL desaparecida', 'timeout': 'timeout'}.get(kind, kind)
            else:
                hashes = set()
                base_url = fuente['url']
                for pagina in range(1, paginas + 1):
                    if stop is not None and stop.is_set() or time.time() > deadline:
                        break
                    if pagina > 1:
                        r = None
                        for pat in (base_url.rstrip('/') + f'/page/{pagina}/', base_url.rstrip('/') + f'?page={pagina}',
                                    base_url.rstrip('/') + f'/pagina/{pagina}', base_url.rstrip('/') + f'?p={pagina}'):
                            r, _ = fetch(pat, 1)
                            if r is not None:
                                break
                        if r is None:
                            break
                    h = hashlib.md5(r.text.encode('utf-8', 'ignore')).hexdigest()
                    if h in hashes:                                  # misma página repetida
                        break
                    hashes.add(h)
                    its = self.cosechar(r.text, r.url)
                    info['cand'] += len(its)
                    ok_pag = procesar(its)
                    if pagina == 1 and len(its) < 3 and not (fuente.get('rss') or fuente.get('rss_auto')):
                        for fd in self.disc.feeds_de(r.text, r.url)[:1]:      # página sin contenido: usa su RSS
                            ok_pag += rss(fd)
                            fuente['rss_auto'] = fd
                            info['note'] = 'vía RSS'
                    if ok_pag == 0 and pagina > 2:                 # v1
                        break
                    time.sleep(get_random_delay())                  # v1
        except Exception as e:
            logger.warning(f"{fuente['nombre']}: {e}")
            info['kind'] = info['kind'] or 'error'
            info['note'] = str(e)[:60]
        info['n'] = len(eventos) + len(alertas)
        if info['n'] > 0 and info['kind'] != 'ok':                   # la web falló pero el RSS entregó
            info['kind'], info['note'] = 'ok', 'vía RSS (web bloqueada)'
        if info['n'] == 0 and info['kind'] == 'ok':
            info['note'] = info['note'] or ('sin contenido (JS/bloqueo)' if info['cand'] == 0 else 'filtrado: ' + ', '.join(f'{k} {v}' for k, v in info['rej'].most_common(3)))
        info['dur'] = round(time.time() - t0, 1)
        return eventos, alertas, info

# ============================================================================
# ALARMA  (conflictos de calle detectados → SSE → sirena en el panel + campana en la terminal)
# ============================================================================

gestor_global = None
fuentes_global = None
JOB = {'running': False, 'progress': 0.0, 'msg': '', 'added': 0, 'merged': 0, 'total': 0, 'done': 0, 'scope': '', 'mode': '',
       'started': None, 'finished': None}
STOP_EVENT = threading.Event()
_JOB_LOCK = threading.Lock()


def detectar_conflictos(nuevos):
    """Conflictos nuevos: rue ≥ umbral, terrorismo, y clusters (≥3 eventos de calle en 24h en un mismo departamento)."""
    out = [c for c in nuevos if c.get('conflicto') and not gestor_global.alarma_ya_vista(c['id'])]
    hoy = datetime.now()
    ayer = (hoy - timedelta(days=1)).strftime('%Y-%m-%d')
    rec = [c for c in gestor_global.copia()[-1000:] if c.get('categoria') == 'rue' and c.get('fecha', '') >= ayer and c.get('dep_code')]
    por_dep = Counter(c['dep_code'] for c in rec)
    dep_nuevos = {c.get('dep_code') for c in nuevos if c.get('categoria') == 'rue'}
    for dep, n in por_dep.items():
        cid = f"cluster:{dep}:{hoy:%Y-%m-%d}"
        if n >= 3 and dep in dep_nuevos and not gestor_global.alarma_ya_vista(cid):
            nm, la, lo = DEPS[dep]
            out.append({'id': cid, 'titulo': f'{n} conflits de rue en 24h — {nm}', 'departement': nm, 'tipo': 'emeutes',
                        'severidad': 7, 'lat': la, 'lon': lo})
    return out


def lanzar_alarma(items, test=False):
    ser_items = [{'id': c.get('id'), 'titulo': c.get('titulo', ''), 'dep': c.get('departement', ''), 'tipo': c.get('tipo', ''),
                  'sev': c.get('severidad', 0), 'lat': c.get('lat'), 'lon': c.get('lon')} for c in items][:6]
    gestor_global.registrar_alarma(ser_items, test)
    STATE['alarm_seq'] += 1
    STATE['alarm'] = {'seq': STATE['alarm_seq'], 'items': ser_items, 'test': test, 'ts': datetime.now().isoformat(timespec='seconds')}
    top = ser_items[0] if ser_items else {}
    emit('alarm', f"🚨 {'TEST ' if test else ''}ALARME — {len(items)} conflit(s): {top.get('titulo', '')[:110]} ({top.get('dep', '')})")


def alarma_test():
    lanzar_alarma([{'id': 'test', 'titulo': 'Test alarme — conflit de rue simulé', 'departement': 'Paris', 'tipo': 'emeutes',
                    'severidad': 7, 'lat': 48.8566, 'lon': 2.3522}], test=True)

# ============================================================================
# ESCÁNER  (secuencial como v1; progreso y log compartidos por terminal y panel)
# ============================================================================

def init_globals(archivo=None):
    global gestor_global, fuentes_global
    gestor_global = GestorDatos(archivo)
    fuentes_global = aplicar_estado(_mk_fuentes())
    v = gestor_global.cfg('umbral')
    if v:
        _set_umbral(int(v))


def _set_umbral(v):
    global UMBRAL_ALARMA
    UMBRAL_ALARMA = max(3, min(10, int(v)))


def seleccionar_fuentes(scope):
    act = [f for f in fuentes_global if f.get('activo', True)]
    if scope == 'fd':
        return [f for f in act if f.get('tipo') == 'faits_divers']
    if scope == 'cyber':
        return [f for f in act if f.get('tipo') == 'cyber']
    if scope == 'gov':
        return [f for f in act if f.get('tipo') == 'gov']
    if scope.startswith('dep:'):
        d = scope[4:]
        return [f for f in act if f.get('departement') == d]
    if scope.startswith('src:'):
        return [f for f in fuentes_global if f['nombre'] == scope[4:]]
    return act


def _resumen_rej(rej):
    return ', '.join(f'{k} {v}' for k, v in rej.most_common(3))


def ejecutar_actualizacion(scope='all', paginas=None, sens=None, interactivo=False):
    with _JOB_LOCK:
        if JOB['running']:
            return False
        JOB.update(running=True, progress=0.0, msg='', added=0, merged=0, total=0, done=0, scope=scope, mode='scan',
                   started=datetime.now().isoformat(timespec='seconds'))
        STOP_EVENT.clear()
        STATE['tick'] += 1
    paginas = max(1, min(8, int(paginas or PAGINAS_BUSQUEDA)))
    sens = sens if sens in _UMBRAL_CONF else SENSIBILIDAD
    t0 = time.time()
    infos, tot_add, tot_merge, tot_alert, tot_conf = [], 0, 0, 0, 0
    try:
        fuentes = seleccionar_fuentes(scope)
        total = len(fuentes)
        JOB['total'] = total
        emit('info', f"\n{'═' * 78}\n🔪 DIABOLIC FRANCE — scan [{scope}] · {total} sources · {paginas} p · sens={sens}\n{'═' * 78}")
        ext = ExtractorNoticias(fuentes, sens)
        for i, f in enumerate(fuentes, 1):
            if STOP_EVENT.is_set():
                emit('warn', '■ Scan interrompu')
                break
            JOB.update(msg=f['nombre'], done=i - 1, progress=(i - 1) / max(1, total))
            STATE['tick'] += 1
            ev, al, info = ext.extraer_de_fuente(f, paginas, STOP_EVENT)
            res = gestor_global.agregar_crimes(ev)
            nuevas_al = gestor_global.agregar_alertas(al)
            conflictos = detectar_conflictos(res['added'])
            registrar_salud(f, info)
            infos.append(info)
            tot_add += len(res['added']); tot_merge += len(res['merged']); tot_alert += len(nuevas_al)
            JOB.update(added=tot_add, merged=tot_merge, done=i, progress=i / max(1, total))
            dec = f"+{len(res['added'])}" if not al else f"+{len(nuevas_al)} alertes"
            extra = f" · 🔗{len(res['merged'])} confirmés" if res['merged'] else ''
            if info['n'] > 0:
                emit('ok', f"[{i:2d}/{total}] ✔ {f['nombre'][:38]:38} {dec:>10}  ({info['n']} ev · {info['cand']} cand){extra}  {info['dur']}s")
            elif info['kind'] == 'ok':
                emit('warn', f"[{i:2d}/{total}] ◌ {f['nombre'][:38]:38} {'0':>10}  ({info['cand']} cand) {info['note']}  {info['dur']}s")
            else:
                emit('err', f"[{i:2d}/{total}] ✖ {f['nombre'][:38]:38} {info['note'] or info['kind']}  {info['dur']}s")
            if res['added'] or res['merged'] or nuevas_al:
                STATE['version'] += 1
            if conflictos:
                tot_conf += len(conflictos)
                lanzar_alarma(conflictos)
        rej = Counter()
        for x in infos:
            rej.update(x['rej'])
        ceros = [x['nombre'] for x in infos if x['n'] == 0]
        emit('info', f"{'─' * 78}\n🔪 {tot_add} {t('new_events')} · 🔗 {tot_merge} confirmés par d'autres sources · 🏛 {tot_alert} alertes · 🚨 {tot_conf} conflits\n"
                     f"⛔ filtrés (faux positifs évités): {_resumen_rej(rej) or '-'}\n📰 sans résultat: {len(ceros)}/{len(infos)}   ⏱ {round(time.time() - t0)}s")
    except Exception as e:
        logger.exception(e)
        emit('err', f'scan: {e}')
    finally:
        JOB.update(running=False, progress=1.0, finished=datetime.now().isoformat(timespec='seconds'), msg='')
        STATE['version'] += 1
        STATE['tick'] += 1
    return {'added': tot_add, 'merged': tot_merge, 'alerts': tot_alert, 'infos': infos}


def ejecutar_verificacion():
    with _JOB_LOCK:
        if JOB['running']:
            return False
        JOB.update(running=True, progress=0.0, msg='', added=0, merged=0, total=len(fuentes_global), done=0, scope='verify', mode='verify',
                   started=datetime.now().isoformat(timespec='seconds'))
        STOP_EVENT.clear()
        STATE['tick'] += 1

    def cb(p, nombre, i):
        JOB.update(progress=round(p, 3), msg=nombre, done=i)
        STATE['tick'] += 1
    try:
        VerificadorFuentes().verificar_todas(fuentes_global, progreso=cb, stop=STOP_EVENT)
    except Exception as e:
        logger.exception(e)
        emit('err', f'verify: {e}')
    finally:
        JOB.update(running=False, progress=1.0, finished=datetime.now().isoformat(timespec='seconds'), msg='')
        STATE['version'] += 1
        STATE['tick'] += 1
    return True


def iniciar_scheduler(minutos=None):
    minutos = AUTO_REFRESH_MIN if minutos is None else minutos
    if minutos <= 0:
        return

    def loop():
        while True:
            time.sleep(minutos * 60)
            ejecutar_actualizacion('all')
    threading.Thread(target=loop, daemon=True, name='scheduler').start()


# ============================================================================
# FILTROS + API
# ============================================================================

def filtrar(crimes, periodo='all', cat='all', tipo='', q='', conf=0):
    if periodo in ('24h', '7d', '30d', '90d'):
        dias = 1 if periodo == '24h' else int(periodo[:-1])
        lim = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
        crimes = [c for c in crimes if c.get('fecha', '') >= lim]
    if cat in CATEGORIAS:
        crimes = [c for c in crimes if c.get('categoria') == cat]
    if tipo:
        crimes = [c for c in crimes if c.get('tipo') == tipo]
    if conf:
        crimes = [c for c in crimes if c.get('confianza', 0) >= conf]
    if q:
        qn = norm(q)
        crimes = [c for c in crimes if qn in norm(f"{c.get('titulo', '')} {c.get('departement', '')} {c.get('tipo', '')} {c.get('fuente', '')}")]
    return crimes


def _int(v, d=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return d


def _args_filtro():
    a = request.args
    return filtrar(gestor_global.copia(), a.get('periodo', 'all'), a.get('cat', 'all'), a.get('tipo', ''), a.get('q', '')[:80], _int(a.get('conf')))


app = Flask(__name__)


@app.after_request
def _headers(r):
    r.headers['X-Content-Type-Options'] = 'nosniff'
    r.headers['Referrer-Policy'] = 'no-referrer'
    return r


def _post_ok():
    """Les POST exigent un en-tête perso (X-DF): une page web tierce ne peut pas déclencher scans/alarmes sur localhost."""
    return request.headers.get('X-DF') == '1'


def _json_body():
    return request.get_json(silent=True) or {}


@app.route('/api/stats')
def api_stats():
    cr = _args_filtro()
    hoy = datetime.now()
    st = gestor_global.estadisticas(cr)
    ms = sorted(st['mensual'])[-18:]
    wt = {k: v for k, v in sorted(st['weekday_type'].items(), key=lambda x: -sum(x[1]))[:12] if k != 'other'}
    street = sorted((c for c in cr if c.get('categoria') == 'rue'), key=lambda c: (c.get('fecha', ''), relevancia(c, hoy)), reverse=True)[:5]
    return jsonify({
        'total': st['total'], 'ultimos_7dias': st['ultimos_7dias'], 'prev_7dias': st['prev_7dias'], 'ultimos_30dias': st['ultimos_30dias'],
        'prev_30dias': st['prev_30dias'], 'ultimos_90dias': st['ultimos_90dias'], 'severidad_promedio': round(st['severidad_promedio'], 2),
        'departements': dict(sorted(st['departements'].items(), key=lambda x: -x[1])[:15]), 'n_departements': len(st['departements']),
        'tipos': dict(st['tipos']), 'fuentes': dict(sorted(st['fuentes'].items(), key=lambda x: -x[1])[:10]),
        'n_fuentes': len([f for f in fuentes_global if f.get('activo', True)]), 'categorias': dict(st['categorias']),
        'mensual': {m: st['mensual'][m] for m in ms}, 'semanal': st['semanal'], 'dept_bubble': st['dept_bubble'],
        'sev_hist': st['sev_hist'], 'weekday_type': wt, 'conflictos_24h': st['conflictos_24h'], 'multi_fuente': st['multi_fuente'],
        'street': [ser(c, hoy) for c in street], 'ultima_actualizacion': gestor_global.datos.get('ultima_actualizacion')})


@app.route('/api/analytics')
def api_analytics():
    return jsonify(Analitica.analytics(_args_filtro()))


@app.route('/api/indicators')
def api_indicators():
    return jsonify(Analitica.indicadores(_args_filtro()))


@app.route('/api/geo')
def api_geo():
    hoy = datetime.now()
    cr = [c for c in _args_filtro() if c.get('lat') is not None]
    cr = sorted(cr, key=lambda c: c.get('fecha', ''), reverse=True)[:4000]
    pts = [[c['lat'], c['lon'], c.get('severidad', 1), c['id'], c['tipo'], c['titulo'][:200], c.get('fecha', ''), c.get('departement', ''),
            c.get('url', ''), c.get('precision', ''), c.get('categoria', 'fisico'), relevancia(c, hoy), len(c.get('fuentes') or []) or 1,
            [[f.get('n', ''), f.get('u', '')] for f in (c.get('fuentes') or [])][:6]] for c in cr]
    dep = Counter(c['dep_code'] for c in cr if c.get('dep_code'))
    return jsonify({'points': pts, 'dept_counts': dep, 'hotspots': Analitica.hotspots(cr)})


@app.route('/api/network')
def api_network():
    return jsonify(Analitica.red(_args_filtro()))


@app.route('/api/sankey')
def api_sankey():
    return jsonify(Analitica.sankey(_args_filtro()))


@app.route('/api/crimes')
def api_crimes():
    hoy = datetime.now()
    cr = _args_filtro()
    sort = request.args.get('sort', 'date')
    if sort == 'rel':
        cr = sorted(cr, key=lambda c: (relevancia(c, hoy), c.get('fecha', '')), reverse=True)
    elif sort == 'sev':
        cr = sorted(cr, key=lambda c: (c.get('severidad', 0), c.get('fecha', '')), reverse=True)
    else:
        cr = sorted(cr, key=lambda c: (c.get('fecha', ''), relevancia(c, hoy)), reverse=True)
    per = max(1, min(50, _int(request.args.get('per'), 15)))
    page = max(1, _int(request.args.get('page'), 1))
    pages = max(1, math.ceil(len(cr) / per))
    page = min(page, pages)
    return jsonify({'items': [ser(c, hoy) for c in cr[(page - 1) * per: page * per]], 'page': page, 'total_pages': pages, 'total': len(cr)})


@app.route('/api/alerts')
def api_alerts():
    cat = request.args.get('cat', 'all')
    ctx = 'cyber' if cat == 'cyber' else 'crime' if cat in ('fisico', 'rue') else 'all'
    items = gestor_global.alertas(ctx)[:40]
    return jsonify({'items': items, 'ctx': ctx, 'vigipirate': gestor_global.cfg('vigipirate', {'nivel': 0})})


@app.route('/api/sources')
def api_sources():
    out = []
    for f in fuentes_global:
        e = ESTADO['fuentes'].get(f['nombre'], {})
        out.append({'nombre': f['nombre'], 'url': f['url'], 'tipo': f.get('tipo'), 'ctx': f.get('ctx'), 'departement': f.get('departement'),
                    'activo': f.get('activo', True), 'rss': f.get('rss') or f.get('rss_auto') or '', 'last': e.get('last'), 'fails': e.get('fails', 0)})
    return jsonify({'sources': out})


@app.route('/api/status')
def api_status():
    return jsonify({'job': JOB, 'version': STATE['version']})


@app.route('/stream')
def stream():
    def gen():
        last_tick, last_log = -1, max(0, _LOG_SEQ[0] - 40)
        while True:
            if STATE['tick'] != last_tick:
                last_tick = STATE['tick']
                with _LOG_LOCK:
                    nuevos = [e for e in LOG if e['i'] > last_log]
                if nuevos:
                    last_log = nuevos[-1]['i']
                payload = {'version': STATE['version'], 'job': dict(JOB), 'log': nuevos, 'alarm': STATE['alarm']}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            else:
                yield ': ka\n\n'
            time.sleep(1.0)
    return Response(gen(), mimetype='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


_SCOPE_RX = re.compile(r'^(?:all|fd|cyber|gov|dep:.{1,60}|src:.{1,100})$')


@app.route('/api/scan', methods=['POST'])
def api_scan():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    b = _json_body()
    scope = str(b.get('scope', 'all'))
    if not _SCOPE_RX.match(scope):
        return jsonify({'started': False, 'error': 'scope'}), 400
    if JOB['running']:
        return jsonify({'started': False, 'running': True})
    threading.Thread(target=ejecutar_actualizacion, args=(scope, _int(b.get('paginas'), PAGINAS_BUSQUEDA), b.get('sens')), daemon=True).start()
    return jsonify({'started': True})


@app.route('/actualizar', methods=['POST'])         # compat v2
def actualizar():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    if JOB['running']:
        return jsonify({'started': False, 'running': True})
    threading.Thread(target=ejecutar_actualizacion, args=('all',), daemon=True).start()
    return jsonify({'started': True})


@app.route('/api/scan/stop', methods=['POST'])
def api_scan_stop():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    STOP_EVENT.set()
    emit('warn', '■ Stop demandé…')
    return jsonify({'ok': True})


@app.route('/api/verify', methods=['POST'])
def api_verify():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    if JOB['running']:
        return jsonify({'started': False, 'running': True})
    threading.Thread(target=ejecutar_verificacion, daemon=True).start()
    return jsonify({'started': True})


@app.route('/api/sources/toggle', methods=['POST'])
def api_src_toggle():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    n = _json_body().get('nombre')
    for f in fuentes_global:
        if f['nombre'] == n:
            f['activo'] = not f.get('activo', True)
            registrar_salud(f)
            return jsonify({'ok': True, 'activo': f['activo']})
    return jsonify({'ok': False}), 404


@app.route('/api/sources/add', methods=['POST'])
def api_src_add():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    b = _json_body()
    nombre, url = limpiar(str(b.get('nombre', '')))[:80], str(b.get('url', '')).strip()[:300]
    p = urlparse(url)
    if len(nombre) < 2 or p.scheme not in ('http', 'https') or not p.netloc:
        return jsonify({'ok': False, 'error': 'nom/URL invalide'}), 400
    if any(f['nombre'] == nombre for f in fuentes_global):
        return jsonify({'ok': False, 'error': 'déjà existante'}), 400
    tipo = {'faits_divers': ('faits_divers', 'crime'), 'cyber': ('cyber', 'cyber'), 'gov_crime': ('gov', 'crime'), 'gov_cyber': ('gov', 'cyber')}.get(b.get('tipo'), ('faits_divers', 'crime'))
    dep = limpiar(str(b.get('departement') or 'National'))[:40]
    f = {'nombre': nombre, 'url': url, 'base': f'{p.scheme}://{p.netloc}', 'departement': dep, 'activo': True, 'tipo': tipo[0], 'ctx': tipo[1]}
    fuentes_global.append(f)
    with _ESTADO_LOCK:
        ESTADO.setdefault('custom', []).append(dict(f))
    registrar_salud(f)
    emit('info', f'＋ Source ajoutée: {nombre}')
    return jsonify({'ok': True})


@app.route('/api/vigipirate', methods=['POST'])
def api_vig():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    n = max(0, min(3, _int(_json_body().get('nivel'))))
    gestor_global.set_cfg('vigipirate', {'nivel': n, 'ts': datetime.now().strftime('%Y-%m-%d %H:%M')})
    return jsonify({'ok': True})


@app.route('/api/alarm/test', methods=['POST'])
def api_alarm_test():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    alarma_test()
    return jsonify({'ok': True})


@app.route('/api/alarm/config', methods=['POST'])
def api_alarm_cfg():
    if not _post_ok():
        return jsonify({'error': 'forbidden'}), 403
    _set_umbral(_int(_json_body().get('umbral'), UMBRAL_ALARMA))
    gestor_global.set_cfg('umbral', UMBRAL_ALARMA)
    emit('info', f'🔔 Seuil alarme = {UMBRAL_ALARMA}')
    return jsonify({'ok': True, 'umbral': UMBRAL_ALARMA})


@app.route('/api/alarm/history')
def api_alarm_hist():
    return jsonify({'items': gestor_global.datos.get('alarma_hist', [])[:30]})


@app.route('/graph/<kind>.png')
def graph_png(kind):
    if kind not in ('tipos', 'mensual', 'heatmap', 'hexbin', 'red'):
        return Response('not found', status=404)
    png = render_estatico(kind, _args_filtro(), request.args.get('lang', 'fr'))
    if not png:
        return Response('missing dependency', status=501)
    return Response(png, mimetype='image/png', headers={'Cache-Control': 'no-store'})


@app.route('/exportar/<fmt>')
def exportar(fmt):
    g = gestor_global
    m = {'json': (g.exportar_json, 'application/json'), 'csv': (g.exportar_csv, 'text/csv'),
         'html': (g.exportar_html, 'text/html'), 'geojson': (g.exportar_geojson, 'application/geo+json')}
    if fmt not in m:
        return Response('not found', status=404)
    return Response(m[fmt][0](), mimetype=m[fmt][1], headers={'Content-Disposition': f'attachment; filename=diabolic_france.{fmt}'})


@app.route('/')
def home():
    i18n = json.dumps(TEXTOS, ensure_ascii=False)
    tipos = json.dumps({k: {'i': v['icono'], 'c': v['color'], 'cat': v['cat'], 'n': {l: v[l] for l in LANGS}} for k, v in TIPOS_CRIMEN.items()}, ensure_ascii=False)
    cfg = json.dumps({'umbral': UMBRAL_ALARMA, 'auto': AUTO_REFRESH_MIN, 'sens': SENSIBILIDAD})
    h = HTML_TEMPLATE.replace('__I18N__', i18n).replace('__TYPES__', tipos).replace('__CFG__', cfg) \
        .replace('__LANG__', IDIOMA_ACTUAL or 'fr')
    return Response(h, mimetype='text/html')

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="__LANG__">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>DIABOLIC FRANCE</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.12.1/dist/chartjs-chart-sankey.min.js"></script>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
@property --a{syntax:'<angle>';initial-value:0deg;inherits:false}
:root{--bg:#03050c;--cy:#00e5ff;--mg:#ff2bd6;--vi:#8b5cff;--gn:#2bffb4;--rd:#ff2d55;--am:#ffb800;--bl:#2f6bff;--tx:#e6f4ff;--mut:#7f93b5;--bd:#16304f;--glass:rgba(8,18,38,.72)}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:'Rajdhani','Segoe UI',system-ui,sans-serif;font-size:16px;color:var(--tx);min-height:100vh;
 background:radial-gradient(1100px 600px at 8% -10%,rgba(0,229,255,.13),transparent 60%),radial-gradient(900px 600px at 100% 0,rgba(255,43,214,.11),transparent 60%),radial-gradient(700px 500px at 50% 120%,rgba(139,92,255,.16),transparent 60%),var(--bg);overflow-x:hidden}
body:before{content:'';position:fixed;left:-20%;right:-20%;bottom:-8vh;height:52vh;pointer-events:none;z-index:0;
 background:linear-gradient(to bottom,transparent,rgba(0,229,255,.10)),repeating-linear-gradient(90deg,rgba(0,229,255,.16) 0 1px,transparent 1px 64px),repeating-linear-gradient(0deg,rgba(0,229,255,.16) 0 1px,transparent 1px 64px);
 transform:perspective(520px) rotateX(62deg);transform-origin:50% 100%;-webkit-mask:linear-gradient(to top,#000 10%,transparent 85%);mask:linear-gradient(to top,#000 10%,transparent 85%)}
body:after{content:'';position:fixed;inset:0;pointer-events:none;z-index:300;background:repeating-linear-gradient(0deg,rgba(255,255,255,.028) 0 1px,transparent 1px 3px);mix-blend-mode:overlay}
.wrap{position:relative;z-index:1;max-width:1560px;margin:0 auto;padding:14px 16px 40px}
/* ===== HOLO FRAME ===== */
.holo{position:relative;background:linear-gradient(160deg,rgba(10,24,48,.80),rgba(5,11,24,.74));border-radius:14px;backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);box-shadow:0 0 24px rgba(0,229,255,.06),inset 0 0 30px rgba(0,229,255,.03)}
.holo:before{content:'';position:absolute;inset:0;border-radius:inherit;padding:1px;pointer-events:none;
 background:conic-gradient(from var(--a),var(--cy),var(--vi),var(--mg),var(--vi),var(--cy));
 -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);animation:spin 9s linear infinite;opacity:.75}
.holo:after{content:'';position:absolute;inset:-1px;border-radius:inherit;pointer-events:none;
 background:linear-gradient(var(--cy),var(--cy)) top left/16px 2px no-repeat,linear-gradient(var(--cy),var(--cy)) top left/2px 16px no-repeat,
 linear-gradient(var(--mg),var(--mg)) top right/16px 2px no-repeat,linear-gradient(var(--mg),var(--mg)) top right/2px 16px no-repeat,
 linear-gradient(var(--mg),var(--mg)) bottom left/16px 2px no-repeat,linear-gradient(var(--mg),var(--mg)) bottom left/2px 16px no-repeat,
 linear-gradient(var(--cy),var(--cy)) bottom right/16px 2px no-repeat,linear-gradient(var(--cy),var(--cy)) bottom right/2px 16px no-repeat;filter:drop-shadow(0 0 5px var(--cy))}
@keyframes spin{to{--a:360deg}}
@keyframes sheen{to{background-position:300% 0}}
@keyframes flick{0%,100%{opacity:1}91%{opacity:1}92%{opacity:.7}93%{opacity:1}95%{opacity:.85}96%{opacity:1}}
@keyframes pulse{0%{transform:scale(.6);opacity:.9}100%{transform:scale(2.6);opacity:0}}
@keyframes blink{50%{opacity:.25}}
@keyframes tape{to{transform:translateX(-50%)}}
@keyframes hue{to{filter:hue-rotate(360deg)}}
.hl{background:linear-gradient(90deg,var(--cy),#fff,var(--mg),var(--cy));background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:sheen 7s linear infinite}
/* ===== HEADER ===== */
.hud{z-index:500;display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding:14px 20px;margin-bottom:10px}
.brand{display:flex;align-items:center;gap:14px}
.logo{font-family:Orbitron,monospace;font-weight:900;font-size:1.9em;letter-spacing:6px;animation:flick 5s infinite;white-space:nowrap}
.logo small{font-size:.35em;letter-spacing:3px;display:block;color:var(--mut);font-weight:500;margin-top:2px;-webkit-text-fill-color:var(--mut)}
.flag{display:flex;height:34px;width:8px;border-radius:3px;overflow:hidden;flex-direction:column;box-shadow:0 0 12px rgba(0,229,255,.6)}
.flag i{flex:1}.flag i:nth-child(1){background:var(--bl)}.flag i:nth-child(2){background:#fff}.flag i:nth-child(3){background:var(--rd)}
.leds{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.led{display:flex;align-items:center;gap:6px;font-size:.78em;letter-spacing:1.4px;text-transform:uppercase;color:var(--mut)}
.led i{width:9px;height:9px;border-radius:50%;background:#394a66;box-shadow:0 0 0 0 transparent}
.led.on i{background:var(--gn);box-shadow:0 0 10px var(--gn)}
.led.warn i{background:var(--am);box-shadow:0 0 10px var(--am)}
.led.bad i{background:var(--rd);box-shadow:0 0 12px var(--rd);animation:blink .7s infinite}
.led.run i{background:var(--cy);box-shadow:0 0 12px var(--cy);animation:blink .9s infinite}
select,input[type=text],input[type=url],input[type=number]{background:rgba(3,10,22,.85);color:var(--tx);border:1px solid var(--bd);border-radius:10px;padding:8px 12px;font:inherit;font-size:.92em}
select:focus,input:focus{outline:none;border-color:var(--cy);box-shadow:0 0 12px rgba(0,229,255,.3)}
.btn{position:relative;background:linear-gradient(180deg,rgba(0,229,255,.16),rgba(0,229,255,.04));color:var(--tx);border:1px solid rgba(0,229,255,.5);border-radius:10px;padding:7px 14px;font:inherit;font-weight:600;font-size:.88em;letter-spacing:.8px;cursor:pointer;transition:.18s;white-space:nowrap;text-decoration:none;display:inline-flex;gap:6px;align-items:center}
.btn:hover{box-shadow:0 0 16px rgba(0,229,255,.5);transform:translateY(-1px);background:rgba(0,229,255,.22)}
.btn:disabled{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}
.btn.red{border-color:rgba(255,45,85,.6);background:linear-gradient(180deg,rgba(255,45,85,.25),rgba(255,45,85,.05))}.btn.red:hover{box-shadow:0 0 16px rgba(255,45,85,.6)}
.btn.mg{border-color:rgba(255,43,214,.55);background:linear-gradient(180deg,rgba(255,43,214,.2),rgba(255,43,214,.04))}.btn.mg:hover{box-shadow:0 0 16px rgba(255,43,214,.55)}
.btn.sm{padding:4px 9px;font-size:.78em}
.job{width:100%;display:none;gap:12px;align-items:center;font-size:.82em;color:var(--mut)}.job.on{display:flex}
.bar{flex:1;height:5px;background:#0b1a30;border-radius:5px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--cy),var(--mg));box-shadow:0 0 12px var(--cy);transition:width .4s}
/* ===== TICKER TAPE ===== */
.tapebox{overflow:hidden;white-space:nowrap;padding:7px 0;margin-bottom:10px;border-radius:10px}
.tape-in{display:inline-flex;gap:30px;animation:tape 70s linear infinite;padding-left:20px}
.tapebox:hover .tape-in{animation-play-state:paused}
.tk{display:inline-flex;align-items:center;gap:7px;font-size:.92em}
.tk b{color:var(--cy);letter-spacing:1.2px;font-weight:700}.tk i{font-style:normal;font-family:Orbitron,monospace;font-size:.85em}
.tk em{font-style:normal;font-weight:700}.tk em.up{color:var(--rd)}.tk em.dn{color:var(--gn)}.tk em.fl{color:var(--mut)}
.arw{display:inline-block;width:11px;height:12px;background:linear-gradient(120deg,var(--cy),#fff,var(--mg),var(--cy));background-size:300% 300%;animation:sheen 3s linear infinite;filter:drop-shadow(0 0 4px currentColor)}
.arw.up{clip-path:polygon(50% 0,100% 100%,50% 72%,0 100%);filter:drop-shadow(0 0 5px var(--rd)) hue-rotate(-40deg)}
.arw.dn{clip-path:polygon(50% 100%,100% 0,50% 28%,0 0);filter:drop-shadow(0 0 5px var(--gn)) hue-rotate(60deg)}
.arw.fl{clip-path:polygon(0 40%,70% 40%,70% 15%,100% 50%,70% 85%,70% 60%,0 60%);opacity:.7}
.spk{vertical-align:middle}
/* ===== GOV BAR ===== */
.gov{display:flex;gap:14px;align-items:center;padding:8px 14px;margin-bottom:10px;font-size:.9em;overflow:hidden}
.gov .tag{font-family:Orbitron,monospace;font-size:.7em;letter-spacing:2px;padding:3px 10px;border-radius:6px;background:linear-gradient(90deg,var(--bl),var(--rd));color:#fff;white-space:nowrap}
.gov .items{flex:1;display:flex;gap:22px;overflow-x:auto;scrollbar-width:none;white-space:nowrap}
.gov .items::-webkit-scrollbar{display:none}
.gov a{color:var(--tx);text-decoration:none}.gov a:hover{color:var(--cy)}
.gov .it{display:inline-flex;gap:7px;align-items:center}
.gov .it u{text-decoration:none;font-size:.7em;letter-spacing:1px;padding:1px 7px;border-radius:5px;border:1px solid}
.gov .it u.cyber{color:var(--cy);border-color:var(--cy)}.gov .it u.crime{color:var(--am);border-color:var(--am)}
.gov .it.hi a{color:#ff8da1}
.vig{padding:3px 10px;border-radius:7px;border:1px solid;font-size:.78em;letter-spacing:1px;white-space:nowrap;cursor:pointer;background:transparent;color:inherit;font-family:inherit}
.vig.l1{color:var(--gn)}.vig.l2{color:var(--am)}.vig.l3{color:var(--rd);animation:blink 1.4s infinite}.vig.l0{color:var(--mut)}
/* ===== TOOLBAR / TABS / FILTERS ===== */
.tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;align-items:center}
.tools .sep{width:1px;height:22px;background:var(--bd);margin:0 4px}
.tabs{position:sticky;top:0;z-index:60;display:flex;gap:4px;overflow-x:auto;padding:6px;margin-bottom:10px;border-radius:12px;background:rgba(3,8,18,.86);backdrop-filter:blur(10px);border:1px solid var(--bd)}
.tab-btn{background:transparent;border:0;color:var(--mut);padding:9px 18px;border-radius:9px;font:inherit;font-weight:700;letter-spacing:1px;font-size:.92em;cursor:pointer;white-space:nowrap;text-transform:uppercase}
.tab-btn.on{color:#fff;background:rgba(0,229,255,.12);box-shadow:inset 0 -2px 0 var(--cy),0 0 18px rgba(0,229,255,.2)}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}
.grp{display:flex;gap:5px;padding-right:12px;margin-right:4px;border-right:1px solid var(--bd)}
.chip{background:rgba(5,14,30,.8);color:var(--mut);border:1px solid var(--bd);border-radius:18px;padding:4px 13px;font-size:.82em;cursor:pointer;font-weight:600;letter-spacing:.6px;transition:.15s}
.chip:hover{color:var(--tx);border-color:var(--cy)}
.chip.on{background:rgba(0,229,255,.18);border-color:var(--cy);color:#fff;box-shadow:0 0 12px rgba(0,229,255,.35)}
.chip[data-v=fisico].on{background:rgba(255,45,85,.2);border-color:var(--rd);box-shadow:0 0 12px rgba(255,45,85,.4)}
.chip[data-v=rue].on{background:rgba(255,184,0,.2);border-color:var(--am);box-shadow:0 0 12px rgba(255,184,0,.4)}
.tab{display:none}.tab.on{display:block}
/* ===== GRID / CARDS ===== */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:12px;margin-bottom:14px}
.kpi{padding:12px 15px}.kpi small{color:var(--mut);font-size:.72em;text-transform:uppercase;letter-spacing:1.2px;display:block}
.kpi b{font-family:Orbitron,monospace;font-size:1.65em;display:inline-block;margin-top:3px}
.kpi .d{font-size:.78em;margin-left:6px;font-weight:700}.d.up{color:var(--rd)}.d.dn{color:var(--gn)}.d.fl{color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(390px,1fr));gap:14px;margin-bottom:14px}
.card{padding:16px 16px 14px}.card h3{font-family:Orbitron,monospace;font-size:.7em;letter-spacing:2px;color:var(--cy);text-transform:uppercase;margin-bottom:10px;font-weight:500}
.card .cv{position:relative;height:250px}.card.wide{grid-column:1/-1}
.row2{display:grid;grid-template-columns:minmax(300px,1fr) 2fr;gap:14px;margin-bottom:14px}
@media(max-width:900px){.row2{grid-template-columns:1fr}.grid{grid-template-columns:1fr}.logo{font-size:1.3em;letter-spacing:3px}}
.gauge{display:flex;flex-direction:column;align-items:center}
.gauge svg{width:100%;max-width:310px}.gauge .gl{font-family:Orbitron,monospace;letter-spacing:3px;font-size:.95em;margin-top:-8px}
.ind{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;width:100%}
.ind div{background:rgba(0,229,255,.05);border:1px solid var(--bd);border-radius:10px;padding:7px 9px;text-align:center}
.ind small{display:block;color:var(--mut);font-size:.68em;letter-spacing:1.2px;text-transform:uppercase}.ind b{font-family:Orbitron,monospace;font-size:1.05em}
.sig{padding:2px 12px;border-radius:8px;font-family:Orbitron,monospace;font-size:.8em;letter-spacing:1.5px;border:1px solid}
.sig.up{color:var(--rd);border-color:var(--rd);box-shadow:0 0 12px rgba(255,45,85,.4)}.sig.dn{color:var(--gn);border-color:var(--gn);box-shadow:0 0 12px rgba(43,255,180,.35)}.sig.fl{color:var(--mut);border-color:var(--bd)}
/* ===== LISTS ===== */
.item{position:relative;background:rgba(2,8,20,.7);border:1px solid var(--bd);border-left:3px solid var(--rd);border-radius:11px;padding:10px 14px;margin-bottom:8px;transition:.18s;display:flex;gap:12px;align-items:center}
.item:hover{transform:translateX(4px);background:rgba(0,229,255,.06);box-shadow:0 0 18px rgba(0,229,255,.12)}
.item .tt{flex:1;min-width:0}.item a.t{color:var(--tx);text-decoration:none;font-weight:700;font-size:1.02em;line-height:1.25}.item a.t:hover{color:var(--cy)}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;font-size:.76em;color:var(--mut);align-items:center}
.badge{border:1px solid var(--bd);border-radius:14px;padding:1px 9px;background:rgba(3,10,22,.8)}
.srcs a{color:var(--cy);text-decoration:none;border:1px solid rgba(0,229,255,.35);border-radius:12px;padding:1px 8px;font-size:.95em}.srcs a:hover{background:rgba(0,229,255,.15)}
.ring{width:46px;height:46px;flex:none}
.ring text{font-family:Orbitron,monospace;font-size:13px;fill:var(--tx)}
.alert{display:flex;justify-content:space-between;gap:10px;padding:7px 10px;border-radius:9px;background:rgba(255,45,85,.08);border:1px solid rgba(255,45,85,.35);margin-bottom:6px;font-size:.88em}
.alert.ok{background:rgba(43,255,180,.07);border-color:rgba(43,255,180,.3);color:var(--gn)}
.hli{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--bd);font-size:.9em}
.cloud{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;min-height:190px;align-content:flex-start}.cloud span{font-weight:700;cursor:default}
.hm{border-collapse:collapse;width:100%;font-size:.78em}.hm td,.hm th{padding:4px 6px;text-align:center}.hm th{color:var(--mut);font-weight:600}.hm td.l{text-align:left;white-space:nowrap}
.pager{display:flex;justify-content:center;align-items:center;gap:14px;margin:14px 0;color:var(--mut);font-size:.9em}
.empty{color:var(--mut);text-align:center;padding:26px}
/* ===== MAP ===== */
#map{isolation:isolate;height:70vh;border-radius:12px;border:1px solid var(--bd);background:#050a14}
.maptools{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;align-items:center}.note{color:var(--mut);font-size:.78em;margin-left:auto}
.leaflet-container{font-family:inherit}.leaflet-control-layers,.leaflet-popup-content-wrapper,.leaflet-popup-tip{background:rgba(6,14,30,.94)!important;color:var(--tx)!important;border:1px solid var(--cy);box-shadow:0 0 18px rgba(0,229,255,.3)!important}
.leaflet-popup-content{margin:10px 12px;font-size:.95em;line-height:1.35}.leaflet-popup-content a{color:var(--cy)}
.leaflet-marker-icon.pulse{position:absolute}.pulse i{position:absolute;inset:0;border-radius:50%;background:var(--am);box-shadow:0 0 14px var(--am)}.pulse:before{content:'';position:absolute;inset:0;border-radius:50%;border:2px solid var(--am);animation:pulse 1.6s infinite}
.pulse.hi i{background:var(--rd);box-shadow:0 0 16px var(--rd)}.pulse.hi:before{border-color:var(--rd)}
.relbar{height:4px;background:#0b1a30;border-radius:4px;overflow:hidden;margin:5px 0}.relbar i{display:block;height:100%;background:linear-gradient(90deg,var(--cy),var(--mg))}
#tlLbl{color:var(--cy);font-family:Orbitron,monospace;font-size:.85em}
#net{height:66vh;border:1px solid var(--bd);border-radius:12px;background:rgba(2,6,14,.8)}
.statics{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:14px}.statics img{width:100%;border-radius:8px;display:block;background:#0b0f1a;min-height:150px}
/* ===== SCAN CENTER ===== */
.scan-grid{display:grid;grid-template-columns:minmax(330px,1fr) 1.6fr;gap:14px}@media(max-width:1000px){.scan-grid{grid-template-columns:1fr}}
.ctl{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;align-items:center}.ctl label{color:var(--mut);font-size:.8em;letter-spacing:1px;text-transform:uppercase}
#console{height:300px;overflow:auto;background:rgba(0,4,10,.9);border:1px solid var(--bd);border-radius:10px;padding:10px;font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace}
#console div{white-space:pre-wrap;word-break:break-word}.l-ok{color:var(--gn)}.l-warn{color:var(--am)}.l-err{color:var(--rd)}.l-info{color:var(--cy)}.l-dim{color:#566a8a}.l-alarm{color:#fff;background:var(--rd);padding:0 6px}.l-disc{color:var(--mg)}
.srctbl{width:100%;border-collapse:collapse;font-size:.86em}.srctbl th{color:var(--mut);text-align:left;font-weight:600;font-size:.78em;letter-spacing:1px;text-transform:uppercase;padding:5px 6px;position:sticky;top:0;background:#071022}
.srctbl td{padding:5px 6px;border-top:1px solid var(--bd);vertical-align:middle}.srctbl a{color:var(--cy);text-decoration:none}
.srcwrap{max-height:540px;overflow:auto;border-radius:10px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#394a66;margin-right:6px}.dot.ok{background:var(--gn);box-shadow:0 0 8px var(--gn)}.dot.warn{background:var(--am);box-shadow:0 0 8px var(--am)}.dot.bad{background:var(--rd);box-shadow:0 0 8px var(--rd)}
.addsrc{display:grid;grid-template-columns:1fr 1.4fr;gap:6px;margin-top:10px}.addsrc input,.addsrc select{width:100%}
/* ===== ALARM ===== */
.alarmbtn{position:relative}.alarmbtn .led{margin-left:2px}
#alarmPanel{position:absolute;right:0;top:44px;z-index:600;width:310px;padding:14px;display:none;background:#070d1c;box-shadow:0 12px 50px rgba(0,0,0,.85),0 0 28px rgba(0,229,255,.25)}#alarmPanel.on{display:block}
#alarmPanel .r{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:9px;font-size:.9em}
#alarmPanel input[type=range]{width:130px;accent-color:var(--cy)}
.ahist{max-height:130px;overflow:auto;font-size:.78em;color:var(--mut);margin-top:6px}.ahist div{border-top:1px solid var(--bd);padding:3px 0}
#alarmOv{position:fixed;left:0;right:0;bottom:0;z-index:400;display:none;padding:14px 22px;background:linear-gradient(90deg,rgba(255,45,85,.96),rgba(255,43,214,.9));color:#fff;align-items:center;gap:16px;box-shadow:0 -6px 60px rgba(255,45,85,.9);animation:blink 1s infinite}
#alarmOv.on{display:flex}#alarmOv b{font-family:Orbitron,monospace;letter-spacing:3px}#alarmOv span{flex:1}
body.alarming .hud:before{animation-duration:1.2s}
footer{text-align:center;color:#4d6285;font-size:.78em;padding:26px;letter-spacing:1px}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}

/* ampliar gráficos */
.card h3.zm{cursor:zoom-in}.card h3.zm:after{content:'⤢';float:right;font-size:1.5em;line-height:.8;opacity:.8;margin-left:8px}.card h3.zm:hover:after{color:var(--mg);opacity:1}
.card .cv canvas,.card .statics img,.card img{cursor:zoom-in}
.card .cv{min-height:250px}
#zoomOv{position:fixed;inset:0;z-index:2000;background:rgba(2,6,14,.9);display:flex;padding:2.5vh 2.5vw}
#zoomOv .zbox{flex:1;display:flex;flex-direction:column;padding:14px 18px;background:#070d1c;min-width:0;min-height:0}
#zoomOv .zh{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-family:Orbitron,monospace;letter-spacing:2px;color:var(--cy)}
#zoomOv .zb{flex:1;min-height:0;overflow:auto}#zoomOv .zb .cv{height:100%!important}#zoomOv .zb #net{height:100%!important}
#zoomOv .zb img{display:block;width:auto;max-width:100%;max-height:100%;margin:0 auto;cursor:default}
body.zooming{overflow:hidden}
</style>
</head>
<body>
<div id="alarmOv"><b>⚠ <span style="display:inline" data-i18n="alarm_conflict"></span></b><span id="alarmTxt"></span><button class="btn sm" id="alarmGo" data-i18n="m_fit"></button><button class="btn sm" id="alarmAck" data-i18n="alarm_ack"></button></div>
<div class="wrap">

<header class="holo hud">
  <div class="brand"><div class="flag"><i></i><i></i><i></i></div>
    <div class="logo"><span class="hl">DIABOLIC FRANCE</span><small data-i18n="app_sub"></small></div></div>
  <div class="leds">
    <span class="led" id="ledLive"><i></i><span data-i18n="led_live"></span></span>
    <span class="led" id="ledScan"><i></i><span data-i18n="led_scan"></span></span>
    <span class="led" id="ledGov"><i></i><span data-i18n="led_gov"></span></span>
    <span style="position:relative"><button class="btn alarmbtn" id="alarmBtn"><span class="led" id="ledAlarm"><i></i></span><span data-i18n="alarm"></span></button>
      <div id="alarmPanel" class="holo">
        <div class="r"><b class="hl" data-i18n="alarm"></b><span id="alarmState" class="badge"></span></div>
        <div class="r"><button class="btn sm" id="aArm"></button><button class="btn sm red" id="aTest" data-i18n="alarm_test"></button></div>
        <div class="r"><button class="btn sm" id="aMute" data-i18n="alarm_mute5"></button><button class="btn sm mg" id="aStop" data-i18n="alarm_ack"></button></div>
        <div class="r"><span data-i18n="alarm_vol"></span><input type="range" id="aVol" min="0" max="100" value="60"></div>
        <div class="r"><span data-i18n="alarm_thr"></span><select id="aThr"><option>5</option><option>6</option><option>7</option><option>8</option><option>9</option></select></div>
        <div class="r"><span data-i18n="alarm_sound"></span><select id="aSnd"><option value="siren">Sirène</option><option value="pulse">Pulse</option><option value="klaxon">Klaxon</option></select></div>
        <div class="r"><span data-i18n="alarm_notif"></span><input type="checkbox" id="aNot"></div>
        <small style="color:var(--mut)" id="aHint"></small>
        <b style="font-size:.78em;color:var(--cy);letter-spacing:1px" data-i18n="alarm_hist"></b><div class="ahist" id="aHist"></div>
      </div></span>
    <select id="lang"><option value="fr">🇫🇷 Français</option><option value="es">🇪🇸 Español</option><option value="en">🇬🇧 English</option><option value="it">🇮🇹 Italiano</option><option value="de">🇩🇪 Deutsch</option></select>
  </div>
  <div class="job" id="job"><span id="jobTxt"></span><div class="bar"><i id="jobBar"></i></div><span id="jobPct"></span></div>
</header>

<div class="holo tapebox" id="tape"></div>

<div class="holo gov" id="gov"><span class="tag" data-i18n="gov_alerts"></span><div class="items" id="govItems"></div><button class="vig l0" id="vig"></button></div>

<div class="tools">
  <button class="btn red" data-scan="all">▶ <span data-i18n="btn_scan_all"></span></button>
  <button class="btn" data-scan="fd">🔪 <span data-i18n="btn_scan_fd"></span></button>
  <button class="btn" data-scan="cyber">🛡 <span data-i18n="btn_scan_cyber"></span></button>
  <button class="btn" data-scan="gov">🏛 <span data-i18n="btn_scan_gov"></span></button>
  <button class="btn mg" id="btnStop">■ <span data-i18n="btn_stop"></span></button>
  <button class="btn" id="btnVerify">🔍 <span data-i18n="btn_verify"></span></button>
  <span class="sep"></span>
  <button class="btn" id="btnMute">🔔 <span data-i18n="btn_mute"></span></button>
  <button class="btn" id="btnFull">⛶ <span data-i18n="btn_full"></span></button>
  <button class="btn" id="btnCopy">🔗 <span data-i18n="btn_copy"></span></button>
  <button class="btn" id="btnReset">↺ <span data-i18n="btn_reset"></span></button>
  <a class="btn" href="/exportar/geojson">GeoJSON</a><a class="btn" href="/exportar/csv">CSV</a><a class="btn" href="/exportar/json">JSON</a><a class="btn" href="/exportar/html">HTML</a>
</div>

<nav class="tabs" id="tabs">
  <button class="tab-btn on" data-tab="dash" data-i18n="tab_dash"></button>
  <button class="tab-btn" data-tab="map" data-i18n="tab_map"></button>
  <button class="tab-btn" data-tab="graphs" data-i18n="tab_graphs"></button>
  <button class="tab-btn" data-tab="network" data-i18n="tab_network"></button>
  <button class="tab-btn" data-tab="static" data-i18n="tab_static"></button>
  <button class="tab-btn" data-tab="feed" data-i18n="tab_feed"></button>
  <button class="tab-btn" data-tab="scan" data-i18n="tab_scan"></button>
</nav>
<div class="filters">
  <div class="grp" id="fPer"><span class="chip on" data-v="all" data-i18n="f_all"></span><span class="chip" data-v="24h">24h</span><span class="chip" data-v="7d">7d</span><span class="chip" data-v="30d">30d</span><span class="chip" data-v="90d">90d</span></div>
  <div class="grp" id="fCat"><span class="chip on" data-v="all" data-i18n="cat_all"></span><span class="chip" data-v="fisico" data-i18n="cat_phys"></span><span class="chip" data-v="rue" data-i18n="cat_rue"></span><span class="chip" data-v="cyber" data-i18n="cat_cyber"></span></div>
  <select id="fTipo"></select>
  <input type="text" id="fQ" data-i18n-ph="search_ph">
  <select id="fConf"><option value="0" data-i18n="conf_any"></option><option value="45" data-i18n="conf_med"></option><option value="60" data-i18n="conf_high"></option></select>
</div>

<section class="tab on" id="tab-dash">
  <div class="kpis" id="kpis"></div>
  <div class="row2">
    <div class="holo card gauge"><h3 data-i18n="threat_idx"></h3><div id="gauge" style="width:100%"></div><div class="ind" id="ind"></div></div>
    <div class="holo card"><h3 data-i18n="c_boll"></h3><div class="cv" style="height:330px"><canvas id="chBoll"></canvas></div></div>
  </div>
  <div class="grid">
    <div class="holo card"><h3 data-i18n="c_street"></h3><div id="streetList"></div></div>
    <div class="holo card"><h3 data-i18n="c_toprel"></h3><div id="topRel"></div></div>
    <div class="holo card"><h3 data-i18n="c_dept"></h3><div class="cv"><canvas id="chDept"></canvas></div></div>
    <div class="holo card"><h3 data-i18n="c_types"></h3><div class="cv"><canvas id="chTypes"></canvas></div></div>
    <div class="holo card wide"><h3 data-i18n="c_monthly"></h3><div class="cv"><canvas id="chMonthly"></canvas></div></div>
    <div class="holo card"><h3 data-i18n="c_radar"></h3><div class="cv"><canvas id="chRadar"></canvas></div></div>
    <div class="holo card"><h3 data-i18n="c_sev"></h3><div class="cv"><canvas id="chSev"></canvas></div></div>
    <div class="holo card"><h3 data-i18n="c_forecast"></h3><div class="cv"><canvas id="chFore"></canvas></div></div>
    <div class="holo card"><h3 data-i18n="c_anom"></h3><div class="cv"><canvas id="chAnom"></canvas></div></div>
    <div class="holo card wide"><h3 data-i18n="c_weekday"></h3><div id="hm"></div></div>
    <div class="holo card"><h3 data-i18n="c_trend"></h3><div class="cloud" id="cloud"></div></div>
    <div class="holo card"><h3>⚠ <span data-i18n="alerts"></span></h3><div id="alerts"></div><h3 style="margin-top:14px" data-i18n="hotspots_t"></h3><div id="hotl"></div></div>
  </div>
</section>

<section class="tab" id="tab-map">
  <div class="maptools">
    <button class="btn sm" data-fly="46.6,2.4,6">🇫🇷</button><button class="btn sm" data-fly="16.25,-61.55,9">971</button><button class="btn sm" data-fly="14.65,-61.0,10">972</button>
    <button class="btn sm" data-fly="4.0,-53.0,7">973</button><button class="btn sm" data-fly="-21.1,55.5,9">974</button><button class="btn sm" data-fly="-12.8,45.15,10">976</button>
    <button class="btn sm mg" id="tlBtn">▶ <span data-i18n="m_timelapse"></span></button><span id="tlLbl"></span>
    <button class="btn sm" id="fitBtn">◎ <span data-i18n="m_fit"></span></button>
    <span class="note" id="mapNote"></span>
  </div>
  <div class="holo" style="padding:8px"><div id="map"></div></div>
</section>

<section class="tab" id="tab-graphs"><div class="grid">
  <div class="holo card wide"><h3 data-i18n="c_sankey"></h3><div class="cv" style="height:520px"><canvas id="chSankey"></canvas></div></div>
  <div class="holo card"><h3 data-i18n="c_weekly"></h3><div class="cv"><canvas id="chWeekly"></canvas></div></div>
  <div class="holo card"><h3 data-i18n="c_bubble"></h3><div class="cv"><canvas id="chBubble"></canvas></div></div>
</div></section>
<section class="tab" id="tab-network"><div class="holo card wide"><h3 data-i18n="c_net"></h3><div id="net"></div></div></section>
<section class="tab" id="tab-static"><div class="statics" id="statics"></div></section>
<section class="tab" id="tab-feed"><div class="holo card"><div class="ctl"><label data-i18n="sort_by"></label><select id="fSort"><option value="date" data-i18n="sort_date"></option><option value="rel" data-i18n="sort_rel"></option><option value="sev" data-i18n="sort_sev"></option></select></div><div id="feed"></div><div class="pager" id="pager"></div></div></section>

<section class="tab" id="tab-scan"><div class="scan-grid">
  <div>
    <div class="holo card" style="margin-bottom:14px"><h3 data-i18n="scan_ctl"></h3>
      <div class="ctl"><label data-i18n="scan_pages"></label><select id="sPages"><option>1</option><option>2</option><option selected>3</option><option>4</option><option>5</option></select>
        <label data-i18n="scan_sens"></label><select id="sSens"><option value="amplio" data-i18n="sens_wide"></option><option value="equilibrado" data-i18n="sens_bal" selected></option><option value="estricto" data-i18n="sens_strict"></option></select></div>
      <div class="ctl"><button class="btn red" data-scan="all">▶ <span data-i18n="btn_scan_all"></span></button><button class="btn" data-scan="fd">🔪 <span data-i18n="btn_scan_fd"></span></button><button class="btn" data-scan="cyber">🛡 <span data-i18n="btn_scan_cyber"></span></button><button class="btn" data-scan="gov">🏛 <span data-i18n="btn_scan_gov"></span></button></div>
      <div class="ctl"><label data-i18n="scan_dep"></label><select id="sDep"></select><button class="btn sm" id="sDepGo">▶</button></div>
      <div class="ctl"><label data-i18n="scan_src"></label><select id="sSrc"></select><button class="btn sm" id="sSrcGo">▶</button></div>
      <div class="ctl"><button class="btn mg" id="btnStop2">■ <span data-i18n="btn_stop"></span></button><button class="btn" id="btnVerify2">🔍 <span data-i18n="btn_verify"></span></button></div>
      <small style="color:var(--mut)" data-i18n="scan_note"></small>
    </div>
    <div class="holo card"><h3 data-i18n="scan_console"></h3><div id="console"></div></div>
  </div>
  <div class="holo card"><h3><span data-i18n="scan_sources"></span> · <span id="srcCount"></span></h3>
    <div class="srcwrap"><table class="srctbl"><thead><tr><th></th><th data-i18n="src_name"></th><th data-i18n="src_type"></th><th>#</th><th data-i18n="src_note"></th><th></th></tr></thead><tbody id="srcBody"></tbody></table></div>
    <div class="addsrc"><input type="text" id="nName" data-i18n-ph="src_name"><input type="url" id="nUrl" placeholder="https://..."><input type="text" id="nDep" data-i18n-ph="src_dep">
      <select id="nTipo"><option value="faits_divers">faits divers</option><option value="cyber">cyber</option><option value="gov_crime">gov · crime</option><option value="gov_cyber">gov · cyber</option></select></div>
    <div class="ctl" style="margin-top:8px"><button class="btn" id="btnAdd">＋ <span data-i18n="add_source"></span></button></div>
    <h3 style="margin-top:14px" data-i18n="official_links"></h3><div class="ctl" id="offLinks"></div>
  </div>
</div></section>

<footer>🛡 <span data-i18n="motto"></span> · By Condor2026 · •SpectrumSecurity• · <span id="upd"></span></footer>
</div>

<script>
const I18N=__I18N__, TYPES=__TYPES__, CFG=__CFG__, LOC={fr:'fr-FR',es:'es-ES',en:'en-GB',it:'it-IT',de:'de-DE'};
let LANG=new URLSearchParams(location.search).get('lang')||(()=>{try{return localStorage.getItem('df_lang')}catch(e){return null}})()||'__LANG__';
if(!I18N[LANG])LANG='fr';
const S={periodo:'all',cat:'all',tipo:'',q:'',conf:0,sort:'date',page:1,tab:'dash'}, STALE={};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const lsGet=(k,d)=>{try{const v=localStorage.getItem(k);return v===null?d:v}catch(e){return d}}, lsSet=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}};
const T=k=>(I18N[LANG]&&I18N[LANG][k])||I18N.fr[k]||k;
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=u=>/^https?:\/\//i.test(u||'')?u:'';
const tname=t=>TYPES[t]?(TYPES[t].n[LANG]||TYPES[t].n.fr):t, ticon=t=>TYPES[t]?TYPES[t].i:'❓', tcol=t=>TYPES[t]?TYPES[t].c:'#6b7280';
const CATC={fisico:'#ff2d55',rue:'#ffb800',cyber:'#00e5ff'}, catName=c=>T(c==='fisico'?'cat_phys':c==='rue'?'cat_rue':'cat_cyber');
const nf=n=>new Intl.NumberFormat(LOC[LANG]).format(n);
const qs=()=>new URLSearchParams({periodo:S.periodo,cat:S.cat,tipo:S.tipo,q:S.q,conf:S.conf,lang:LANG}).toString();
async function api(p,extra=''){const r=await fetch(p+'?'+qs()+extra);if(!r.ok)throw new Error(p+' '+r.status);return r.json();}
async function post(p,body){const r=await fetch(p,{method:'POST',headers:{'Content-Type':'application/json','X-DF':'1'},body:JSON.stringify(body||{})});return r.json().catch(()=>({}));}
const CH={};
function mk(id,cfg){const el=document.getElementById(id);if(!el)return;if(CH[id])CH[id].destroy();CH[id]=new Chart(el,cfg);}
Chart.defaults.color='#8aa0c4';Chart.defaults.borderColor='rgba(40,80,130,.35)';Chart.defaults.font.family="Rajdhani,'Segoe UI',sans-serif";Chart.defaults.maintainAspectRatio=false;Chart.defaults.font.size=13;
const CY='#00e5ff',MG='#ff2bd6',RD='#ff2d55',AM='#ffb800',GN='#2bffb4';
const arrow=d=>`<span class="arw ${d>1?'up':d<-1?'dn':'fl'}"></span>`, dcls=d=>d>1?'up':d<-1?'dn':'fl', sgn=d=>(d>0?'+':'')+d.toFixed(1)+'%';
function spark(a,w=48,h=15,col='#00e5ff'){if(!a||a.length<2)return'';const mx=Math.max(...a,1),mn=Math.min(...a),r=(mx-mn)||1;
  const pts=a.map((v,i)=>(i/(a.length-1)*w).toFixed(1)+','+(h-1-(v-mn)/r*(h-2)).toFixed(1)).join(' ');
  return `<svg class="spk" width="${w}" height="${h}"><polyline points="${pts}" fill="none" stroke="${col}" stroke-width="1.4" style="filter:drop-shadow(0 0 3px ${col})"/></svg>`;}
function ring(v,col){v=Math.max(0,Math.min(100,Math.round(v)));const c=2*Math.PI*18,o=c*(1-v/100);
  return `<svg class="ring" viewBox="0 0 46 46"><circle cx="23" cy="23" r="18" fill="none" stroke="#0e2240" stroke-width="4"/><circle cx="23" cy="23" r="18" fill="none" stroke="${col}" stroke-width="4" stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${o.toFixed(1)}" transform="rotate(-90 23 23)" style="filter:drop-shadow(0 0 4px ${col})"/><text x="23" y="27" text-anchor="middle">${v}</text></svg>`;}
function srcChips(f){return (f||[]).slice(0,6).map(s=>{const u=safeUrl(s[1]);return u?`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(s[0])}</a>`:`<span class="badge">${esc(s[0])}</span>`}).join(' ');}
function evItem(c){const u=safeUrl(c.url);const col=CATC[c.categoria]||'#888';
  return `<div class="item" style="border-left-color:${col}">${ring(c.relevancia,col)}<div class="tt"><a class="t" ${u?`href="${esc(u)}" target="_blank" rel="noopener noreferrer"`:''}>${esc(c.titulo)}</a>
  <div class="meta"><span class="badge" style="border-color:${tcol(c.tipo)};color:${tcol(c.tipo)}">${ticon(c.tipo)} ${esc(tname(c.tipo))}</span><span class="badge" style="color:${col}">${esc(catName(c.categoria))}</span>
  <span class="badge">📍 ${esc(c.departement||'?')}</span><span class="badge">📅 ${esc(c.fecha)}</span><span class="badge">💀 ${c.severidad}/10</span><span class="badge">✔ ${c.confianza}%</span>
  <span class="srcs">${esc(T('sources_lbl'))}: ${srcChips(c.fuentes)}</span></div></div></div>`;}

function applyI18n(){
  $$('[data-i18n]').forEach(e=>e.textContent=T(e.dataset.i18n));
  $$('[data-i18n-ph]').forEach(e=>e.placeholder=T(e.dataset.i18nPh));
  document.documentElement.lang=LANG;$('#lang').value=LANG;
  const sel=$('#fTipo'),cur=S.tipo;sel.innerHTML='<option value="">'+esc(T('all_types'))+'</option>';
  Object.keys(TYPES).filter(k=>k!=='other').forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent=ticon(k)+' '+tname(k);sel.appendChild(o);});sel.value=cur;
  updAlarmUI();updVig();
}

/* ===================== TICKER (crypto style) ===================== */
async function renderTicker(){
  const d=await api('/api/indicators');
  const lab=k=>k.kind==='cat'?catName(k.key):k.kind==='tipo'?ticon(k.key)+' '+tname(k.key):T(k.label||k.key);
  const col=k=>k.kind==='cat'?CATC[k.key]:k.kind==='tipo'?tcol(k.key):CY;
  const one=d.tickers.map(k=>`<span class="tk"><b style="color:${col(k)}">${esc(lab(k))}</b><i>${k.kind==='rsi'||k.kind==='idx'?k.value.toFixed(0):nf(k.value)}</i>${arrow(k.delta)}<em class="${dcls(k.delta)}">${sgn(k.delta)}</em>${spark(k.series,48,15,col(k))}</span>`).join('');
  $('#tape').innerHTML=`<div class="tape-in">${one}${one}</div>`;
}
/* ===================== GOV ALERTS ===================== */
let VIG=null;
async function renderGov(){
  const d=await api('/api/alerts');VIG=d.vigipirate;
  $('#govItems').innerHTML=d.items.length?d.items.slice(0,24).map(a=>{const u=safeUrl(a.url);return `<span class="it ${a.nivel>=7?'hi':''}"><u class="${a.ctx}">${a.ctx==='cyber'?'CYBER':'SÛRETÉ'}</u>${u?`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(a.titulo)}</a>`:esc(a.titulo)}<small style="color:var(--mut)">${esc(a.fecha)} · ${esc(a.fuente)}</small></span>`}).join(''):`<span style="color:var(--mut)">${esc(T('gov_none'))}</span>`;
  $('#ledGov').className='led '+(d.items.length?'on':'warn');updVig();
}
function updVig(){const b=$('#vig');if(!b)return;const n=VIG&&VIG.nivel?VIG.nivel:0;b.className='vig l'+n;b.textContent='VIGIPIRATE · '+(n?T('vig_'+n):T('vig_set'));}
$('#vig').onclick=async()=>{const n=prompt(T('vig_prompt'),(VIG&&VIG.nivel)||'');if(n===null)return;const v=parseInt(n);await post('/api/vigipirate',{nivel:(v>=1&&v<=3)?v:0});renderGov();};

/* ===================== DASHBOARD ===================== */
const GAUGE_LBL=['th_calm','th_watch','th_tense','th_crit'];
function gaugeSVG(v){const a=Math.PI*(1-v/100),cx=150,cy=140,r=110,x=cx+r*Math.cos(a)*0.9,y=cy-r*Math.sin(a)*0.9;
  return `<svg viewBox="0 0 300 175"><defs><linearGradient id="gg" x1="0" x2="1"><stop offset="0" stop-color="#2bffb4"/><stop offset=".45" stop-color="#ffb800"/><stop offset=".75" stop-color="#ff2bd6"/><stop offset="1" stop-color="#ff2d55"/></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <path d="M40 140 A110 110 0 0 1 260 140" fill="none" stroke="#0e2240" stroke-width="16" stroke-linecap="round"/>
  <path d="M40 140 A110 110 0 0 1 260 140" fill="none" stroke="url(#gg)" stroke-width="16" stroke-linecap="round" pathLength="100" stroke-dasharray="${v} 100" filter="url(#glow)"/>
  <line x1="150" y1="140" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#fff" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/><circle cx="150" cy="140" r="7" fill="#fff"/>
  <text x="150" y="112" text-anchor="middle" font-family="Orbitron" font-size="34" fill="#fff" filter="url(#glow)">${Math.round(v)}</text></svg>`;}
async function renderDash(){
  const [st,an,ind,geoRel]=await Promise.all([api('/api/stats'),api('/api/analytics'),api('/api/indicators'),api('/api/crimes','&sort=rel&per=6')]);
  const dl=(a,b)=>b>0?(a-b)/b*100:(a>0?100:0), cy=st.total?Math.round((st.categorias.cyber||0)/st.total*100):0;
  const K=[['📊',nf(st.total),'k_total',null],['⚡',nf(st.ultimos_7dias),'k_7d',dl(st.ultimos_7dias,st.prev_7dias)],['🔥',nf(st.ultimos_30dias),'k_30d',dl(st.ultimos_30dias,st.prev_30dias)],
   ['🚨',nf(st.categorias.rue||0),'cat_rue',null],['🛡',nf(st.categorias.cyber||0)+' · '+cy+'%','k_cyber',null],['⚔',nf(st.conflictos_24h),'k_conf24',null],['🔗',nf(st.multi_fuente),'k_multi',null],
   ['📰',st.n_fuentes,'k_sources',null],['📍',st.n_departements,'k_depts',null],['💀',st.severidad_promedio.toFixed(1)+'/10','k_sev',null]];
  $('#kpis').innerHTML=K.map(k=>`<div class="holo kpi"><small>${k[0]} ${esc(T(k[2]))}</small><b>${esc(k[1])}</b>${k[3]!==null?`<span class="d ${dcls(k[3])}">${arrow(k[3])} ${sgn(k[3])}</span>`:''}</div>`).join('');
  $('#upd').textContent=st.ultima_actualizacion||'';
  const th=ind.threat;$('#gauge').innerHTML=gaugeSVG(th.idx)+`<div class="gl hl" style="text-align:center">${esc(T(GAUGE_LBL[th.level]))}</div>`;
  const sg=ind.signal==='up'?['sig_up','up']:ind.signal==='dn'?['sig_dn','dn']:['sig_neu','fl'];
  $('#ind').innerHTML=`<div><small>RSI·14</small><b style="color:${ind.rsi>70?RD:ind.rsi<30?GN:CY}">${ind.rsi.toFixed(0)}</b></div><div><small>SMA7/30</small><b>${arrow(ind.momentum)}${sgn(ind.momentum)}</b></div><div><small>${esc(T('vol'))}</small><b>${ind.volatility.toFixed(2)}</b></div>
   <div style="grid-column:1/-1"><small>${esc(T('signal'))}</small><span class="sig ${sg[1]}">${esc(T(sg[0]))}</span></div>`;
  const s=ind.series;
  mk('chBoll',{type:'line',data:{labels:s.dates.map(d=>d.slice(5)),datasets:[
    {label:'BB+',data:s.up,borderColor:'rgba(139,92,255,.6)',borderWidth:1,pointRadius:0,fill:false,tension:.3},
    {label:'BB−',data:s.dn,borderColor:'rgba(139,92,255,.6)',borderWidth:1,pointRadius:0,fill:'-1',backgroundColor:'rgba(139,92,255,.12)',tension:.3},
    {label:'SMA30',data:s.sma30,borderColor:AM,borderWidth:1.6,pointRadius:0,tension:.3},{label:'SMA7',data:s.sma7,borderColor:MG,borderWidth:1.8,pointRadius:0,tension:.3},
    {label:T('k_total'),type:'bar',data:s.counts,backgroundColor:s.counts.map((_,i)=>s.rsi[i]>70?'rgba(255,45,85,.7)':'rgba(0,229,255,.35)'),borderRadius:2}]},
    options:{interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{boxWidth:10,font:{size:10}}}},scales:{x:{ticks:{maxTicksLimit:12}}}}});
  $('#streetList').innerHTML=st.street.length?st.street.map(evItem).join(''):`<div class="empty">${esc(T('no_data'))}</div>`;
  $('#topRel').innerHTML=geoRel.items.length?geoRel.items.map(evItem).join(''):`<div class="empty">${esc(T('no_data'))}</div>`;
  const dep=Object.entries(st.departements).slice(0,10);
  mk('chDept',{type:'bar',data:{labels:dep.map(d=>d[0]),datasets:[{data:dep.map(d=>d[1]),borderRadius:5,backgroundColor:dep.map((_,i)=>i%2?'rgba(0,229,255,.75)':'rgba(255,43,214,.75)')}]},options:{indexAxis:'y',plugins:{legend:{display:false}}}});
  const tp=Object.entries(st.tipos).sort((a,b)=>b[1]-a[1]);
  mk('chTypes',{type:'doughnut',data:{labels:tp.map(x=>ticon(x[0])+' '+tname(x[0])),datasets:[{data:tp.map(x=>x[1]),backgroundColor:tp.map(x=>tcol(x[0])),borderColor:'#050a14',borderWidth:3}]},options:{cutout:'58%',plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:10}}}}}});
  const ms=Object.keys(st.mensual),ln=(k,c)=>({label:catName(k),data:ms.map(m=>st.mensual[m][k]),borderColor:c,backgroundColor:c+'30',fill:true,tension:.35,pointRadius:2});
  mk('chMonthly',{type:'line',data:{labels:ms,datasets:[ln('fisico',RD),ln('rue',AM),ln('cyber',CY)]},options:{interaction:{mode:'index',intersect:false}}});
  const top8=tp.slice(0,8),mx=Math.max(1,...top8.map(x=>x[1]));
  mk('chRadar',{type:'radar',data:{labels:top8.map(x=>tname(x[0])),datasets:[{data:top8.map(x=>Math.round(x[1]/mx*100)),borderColor:CY,backgroundColor:'rgba(0,229,255,.2)',pointBackgroundColor:MG}]},options:{plugins:{legend:{display:false}},scales:{r:{ticks:{display:false},grid:{color:'rgba(40,80,130,.4)'},angleLines:{color:'rgba(40,80,130,.4)'},pointLabels:{font:{size:10}}}}}});
  mk('chSev',{type:'polarArea',data:{labels:[1,2,3,4,5,6,7,8,9,10],datasets:[{data:st.sev_hist,backgroundColor:st.sev_hist.map((_,i)=>`hsla(${190+i*18},90%,58%,.7)`)}]},options:{plugins:{legend:{display:false}},scales:{r:{ticks:{display:false},grid:{color:'rgba(40,80,130,.4)'}}}}});
  const f=an.forecast,L=f.hist_labels.concat(f.pred_labels),pad=f.hist.map(()=>null);
  mk('chFore',{type:'line',data:{labels:L,datasets:[{label:T('history_lbl'),data:f.hist.concat(f.pred.map(()=>null)),borderColor:CY,tension:.3,pointRadius:2},
    {label:T('forecast_lbl'),data:f.pred.length?pad.slice(0,-1).concat([f.hist[f.hist.length-1]]).concat(f.pred):[],borderColor:MG,borderDash:[6,5],tension:.3,pointRadius:3}]}});
  mk('chAnom',{type:'bar',data:{labels:an.daily.map(d=>d.date.slice(5)),datasets:[{data:an.daily.map(d=>d.count),backgroundColor:an.daily.map(d=>d.z>=2?RD:'rgba(0,229,255,.45)'),borderRadius:3}]},options:{plugins:{legend:{display:false}},scales:{x:{ticks:{maxTicksLimit:10}}}}});
  renderHeat(st.weekday_type);
  const tr=an.trending,mxs=Math.max(1,...tr.map(x=>x.score));
  $('#cloud').innerHTML=tr.length?tr.map(x=>`<span title="x${x.score} · ${x.count}" style="font-size:${(.85+x.score/mxs*1.5).toFixed(2)}em;color:hsl(${(300-x.score/mxs*120)|0},90%,66%)">${esc(x.word)}</span>`).join(''):`<div class="empty">${esc(T('no_data'))}</div>`;
  $('#alerts').innerHTML=an.anomalies.length?an.anomalies.slice(-6).reverse().map(a=>`<div class="alert"><span>⚡ ${esc(T('alert_spike'))} · ${esc(a.date)}</span><b>${a.count} (z=${a.z})</b></div>`).join(''):`<div class="alert ok">✔ ${esc(T('alert_ok'))}</div>`;
  $('#hotl').innerHTML=an.hotspots.slice(0,5).map((h,i)=>`<div class="hli"><span>${i+1}. ${esc(h.label)}</span><b>${h.count} · ${h.sev}/10</b></div>`).join('')||`<div class="empty">${esc(T('no_data'))}</div>`;
}
function renderHeat(wt){const ks=Object.keys(wt);if(!ks.length){$('#hm').innerHTML=`<div class="empty">${esc(T('no_data'))}</div>`;return;}
  const mx=Math.max(1,...ks.flatMap(k=>wt[k])),d0=new Date(2024,0,1);
  const days=[...Array(7)].map((_,i)=>new Date(d0.getTime()+i*864e5).toLocaleDateString(LOC[LANG],{weekday:'short'}));
  $('#hm').innerHTML='<table class="hm"><tr><th></th>'+days.map(d=>`<th>${esc(d)}</th>`).join('')+'</tr>'+ks.map(k=>`<tr><td class="l">${ticon(k)} ${esc(tname(k))}</td>`+wt[k].map(v=>`<td style="background:rgba(255,43,214,${(v/mx*.8+.04).toFixed(2)});color:${v/mx>.5?'#fff':'#a9bad6'}">${v}</td>`).join('')+'</tr>').join('')+'</table>';}

/* ===================== MAP ===================== */
let MAP,LAYERS={},LCTRL,GEOJ=null,PTS=[],HEAT=null,TL=null,BASES=null;
function popup(p){const u=safeUrl(p[8]),col=CATC[p[10]]||'#888';
  return `<b>${ticon(p[4])} ${esc(tname(p[4]))}</b> <span style="color:${col}">· ${esc(catName(p[10]))}</span><br>${u?`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(p[5])}</a>`:esc(p[5])}<br>
  <small>${esc(p[7])} · ${esc(p[6])} · ${esc(T('severity'))} ${p[2]}/10</small><div class="relbar" title="${esc(T('relevance'))}"><i style="width:${p[11]}%"></i></div>
  <small>${esc(T('relevance'))} ${p[11]}% · ${esc(T('confirmed_by'))} ${p[12]}</small><div class="srcs" style="margin-top:4px">${srcChips(p[13])}</div>`;}
function initMap(){
  MAP=L.map('map',{preferCanvas:true}).setView([46.6,2.4],6);
  const mkT=(u,o)=>L.tileLayer(u,Object.assign({maxZoom:19,attribution:'© OpenStreetMap contributors'},o||{}));
  BASES={'map_dark':mkT('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{subdomains:'abcd',attribution:'© OpenStreetMap · © CARTO'}),
   'map_street':mkT('https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
   'map_osmfr':mkT('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',{subdomains:'abc',attribution:'© OpenStreetMap France'}),
   'map_voyager':mkT('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',{subdomains:'abcd',attribution:'© OpenStreetMap · © CARTO'}),
   'map_light':mkT('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{subdomains:'abcd',attribution:'© OpenStreetMap · © CARTO'}),
   'map_sat':mkT('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{attribution:'Tiles © Esri'})};
  const sel=lsGet('df_base','map_dark');(BASES[sel]||BASES.map_dark).addTo(MAP);
  MAP.on('baselayerchange',e=>{for(const k in BASES)if(BASES[k]===e.layer)lsSet('df_base',k);});
  $$('[data-fly]').forEach(b=>b.onclick=()=>{const [a,o,z]=b.dataset.fly.split(',').map(Number);MAP.flyTo([a,o],z);});
}
async function renderMap(){
  if(!MAP)initMap();
  const g=await api('/api/geo');PTS=g.points;
  Object.values(LAYERS).forEach(l=>MAP.removeLayer(l));if(LCTRL)MAP.removeControl(LCTRL);LAYERS={};
  HEAT=L.heatLayer(PTS.map(p=>[p[0],p[1],Math.max(.15,p[2]/10)]),{radius:22,blur:20,minOpacity:.3,gradient:{.2:'#2f6bff',.45:'#00e5ff',.65:'#ffb800',.85:'#ff2d55',1:'#fff'}});
  LAYERS[T('m_heat')]=HEAT;
  const cl=L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:45,chunkedLoading:true});
  PTS.forEach(p=>cl.addLayer(L.circleMarker([p[0],p[1]],{radius:5+p[2]*.45,color:'#03050c',weight:1,fillColor:tcol(p[4]),fillOpacity:.9}).bindPopup(popup(p))));
  LAYERS[T('m_clusters')]=cl;
  const rue=PTS.filter(p=>p[10]==='rue').slice(0,160);
  LAYERS[T('m_pulse')]=L.layerGroup(rue.map(p=>L.marker([p[0],p[1]],{icon:L.divIcon({className:'pulse'+(p[2]>=(CFG.umbral||6)?' hi':''),html:'<i></i>',iconSize:[18,18]})}).bindPopup(popup(p))));
  LAYERS[T('m_hot')]=L.layerGroup(g.hotspots.map(h=>L.circle([h.lat,h.lon],{radius:15000+h.count*3500,color:RD,weight:1.5,fillColor:RD,fillOpacity:.12,dashArray:'4 4'}).bindTooltip(`🔥 ${esc(h.label)} · ${h.count} · ${h.sev}/10`)));
  if(GEOJ===null){try{GEOJ=await (await fetch('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson')).json();}catch(e){GEOJ=false;}}
  if(GEOJ){const mx=Math.max(1,...Object.values(g.dept_counts));
    LAYERS[T('m_choro')]=L.geoJSON(GEOJ,{style:f=>{const v=(g.dept_counts[f.properties.code]||0)/mx;return{color:'#16304f',weight:1,fillColor:v?`hsl(${(260+v*100)|0},90%,${40+v*15|0}%)`:'#050a14',fillOpacity:v?.5:.12};},onEachFeature:(f,l)=>l.bindTooltip(`${esc(f.properties.nom)}: ${g.dept_counts[f.properties.code]||0}`,{sticky:true})});}
  const bl={};for(const k in BASES)bl[T(k)]=BASES[k];
  LCTRL=L.control.layers(bl,LAYERS,{collapsed:false}).addTo(MAP);
  [T('m_heat'),T('m_clusters'),T('m_pulse'),T('m_hot')].forEach(k=>LAYERS[k]&&LAYERS[k].addTo(MAP));
  $('#mapNote').textContent=T('geo_note')+' · '+nf(PTS.length)+' '+T('events');
  setTimeout(()=>MAP.invalidateSize(),60);
}
function fitMap(){if(!MAP||!PTS.length)return;MAP.fitBounds(L.latLngBounds(PTS.map(p=>[p[0],p[1]])).pad(.1));}
function flyTo(lat,lon,z){if(MAP)MAP.flyTo([lat,lon],z||11);}
$('#fitBtn').onclick=fitMap;
$('#tlBtn').onclick=()=>{if(TL){clearInterval(TL);TL=null;$('#tlLbl').textContent='';if(HEAT)HEAT.setLatLngs(PTS.map(p=>[p[0],p[1],Math.max(.15,p[2]/10)]));return;}
  if(!HEAT||!PTS.length)return;const days=[...new Set(PTS.map(p=>p[6]))].sort().slice(-30);let i=0;
  TL=setInterval(()=>{const d=days[i];HEAT.setLatLngs(PTS.filter(p=>p[6]<=d).map(p=>[p[0],p[1],Math.max(.15,p[2]/10)]));$('#tlLbl').textContent=d;if(++i>=days.length){clearInterval(TL);TL=null;}},450);};

/* ===================== GRAPHS / NETWORK / STATIC / FEED ===================== */
const nodeLabel=k=>{const[p,v]=k.split(/:(.*)/);return p==='cat'?'◆ '+catName(v):p==='tipo'?ticon(v)+' '+tname(v):'📍 '+v;};
const nodeColor=k=>{const[p,v]=k.split(/:(.*)/);return p==='cat'?CATC[v]:p==='tipo'?tcol(v):'#64748b';};
async function renderGraphs(){
  const [d,st]=await Promise.all([api('/api/sankey'),api('/api/stats')]),labels={};
  d.flows.forEach(f=>{labels[f[0]]=nodeLabel(f[0]);labels[f[1]]=nodeLabel(f[1]);});
  mk('chSankey',{type:'sankey',data:{datasets:[{data:d.flows.map(f=>({from:f[0],to:f[1],flow:f[2]})),labels,colorFrom:c=>nodeColor(c.dataset.data[c.dataIndex].from),colorTo:c=>nodeColor(c.dataset.data[c.dataIndex].to),colorMode:'gradient',size:'max',color:'#e6f4ff',font:{size:11}}]},options:{plugins:{legend:{display:false}}}});
  const w=st.semanal;
  mk('chWeekly',{type:'bar',data:{labels:w.labels,datasets:['fisico','rue','cyber'].map(k=>({label:catName(k),data:w[k],backgroundColor:CATC[k]+'cc',borderRadius:3}))},options:{scales:{x:{stacked:true},y:{stacked:true}}}});
  mk('chBubble',{type:'bubble',data:{datasets:[{label:T('c_dept'),data:st.dept_bubble.map(b=>({x:b.n,y:b.sev,r:5+Math.min(18,b.n/2),d:b.d})),backgroundColor:'rgba(255,43,214,.45)',borderColor:MG}]},
    options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`${c.raw.d}: ${c.raw.x} · ${c.raw.y}/10`}}},scales:{x:{title:{display:true,text:'#'}},y:{title:{display:true,text:T('severity')},min:0,max:10}}}});
}
let NET;
async function renderNet(){const d=await api('/api/network');
  const nodes=d.nodes.map(n=>({id:n.id,value:n.value,label:n.group==='tipo'?ticon(n.key)+' '+tname(n.key):n.label,shape:n.group==='tipo'?'dot':'box',color:n.group==='tipo'?{background:tcol(n.key),border:'#03050c'}:{background:'#0b1a30',border:'#00e5ff'},font:{color:'#e6f4ff',size:13}}));
  NET=new vis.Network($('#net'),{nodes:new vis.DataSet(nodes),edges:new vis.DataSet(d.edges.map(e=>({...e,color:{color:'#2f6bff',opacity:.5}})))},{physics:{solver:'forceAtlas2Based',stabilization:{iterations:160}},interaction:{hover:true},edges:{smooth:{type:'continuous'}}});}
function imgFail(el){const d=document.createElement('div');d.className='empty';d.textContent='⚠ '+T('st_missing');el.replaceWith(d);}
function renderStatic(){const k=[['tipos','st_tipos'],['mensual','st_mensual'],['heatmap','st_heatmap'],['hexbin','st_hexbin'],['red','st_red']],ts=Date.now();
  $('#statics').innerHTML=k.map(x=>`<div class="holo card"><h3>${esc(T(x[1]))}</h3><img alt="" loading="lazy" src="/graph/${x[0]}.png?${qs()}&t=${ts}" onerror="imgFail(this)"></div>`).join('');}
async function renderFeed(){const d=await api('/api/crimes','&page='+S.page+'&sort='+S.sort);
  $('#feed').innerHTML=d.items.length?d.items.map(evItem).join(''):`<div class="empty">${esc(T('no_data'))}</div>`;
  $('#pager').innerHTML=`<button class="btn sm" ${d.page<=1?'disabled':''} id="pp">${esc(T('prev'))}</button><span>${esc(T('page'))} ${d.page} / ${d.total_pages} · ${nf(d.total)} ${esc(T('events'))}</span><button class="btn sm" ${d.page>=d.total_pages?'disabled':''} id="pn">${esc(T('next'))}</button>`;
  $('#pp').onclick=()=>{S.page--;renderFeed();};$('#pn').onclick=()=>{S.page++;renderFeed();};}

/* ===================== SCAN CENTER ===================== */
const OFF=[['CERT-FR','https://www.cert.ssi.gouv.fr/'],['Cybermalveillance','https://www.cybermalveillance.gouv.fr/'],['Pharos','https://www.internet-signalement.gouv.fr/'],['Intérieur','https://www.interieur.gouv.fr/'],['Gouvernement','https://www.gouvernement.fr/'],['Service-Public','https://www.service-public.fr/'],['17 · 18 · 112 · 114','tel:112']];
let SRC=[];
function lastDot(l){if(!l||!l.kind)return['','status_idle'];if(l.kind==='ok'&&l.n>0)return['ok','status_ok'];if(l.kind==='ok')return['warn','status_empty'];if(l.kind==='dns')return['bad','status_dns'];if(l.kind==='blocked')return['warn','status_blocked'];if(l.kind==='gone')return['warn','status_gone'];return['bad','status_err'];}
async function renderScan(){
  const r=await (await fetch('/api/sources')).json();SRC=r.sources;
  $('#srcCount').textContent=SRC.filter(s=>s.activo).length+'/'+SRC.length;
  $('#srcBody').innerHTML=SRC.map((s,i)=>{const l=s.last||{},[dc,tk]=lastDot(l),u=safeUrl(s.url);
    return `<tr><td><span class="dot ${dc}"></span></td><td>${u?`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(s.nombre)}</a>`:esc(s.nombre)}<br><small style="color:var(--mut)">${esc(s.departement)}</small></td><td>${esc(s.tipo)}</td><td>${l.n!=null?l.n:'–'}<br><small style="color:var(--mut)">${l.dur!=null?l.dur+'s':''}</small></td>
    <td><small>${esc(T(tk))}${l.note?' · '+esc(l.note):''}${s.fails>1?' · ✖'+s.fails:''}</small></td><td style="white-space:nowrap"><button class="btn sm" data-sc="${i}">▶</button> <button class="btn sm ${s.activo?'':'red'}" data-tg="${i}">${s.activo?'ON':'OFF'}</button></td></tr>`}).join('');
  $$('[data-sc]').forEach(b=>b.onclick=()=>startScan('src:'+SRC[b.dataset.sc].nombre));
  $$('[data-tg]').forEach(b=>b.onclick=async()=>{await post('/api/sources/toggle',{nombre:SRC[b.dataset.tg].nombre});renderScan();});
  const dp=[...new Set(SRC.map(s=>s.departement))].sort();
  const keep=$('#sDep').value;$('#sDep').innerHTML=dp.map(d=>`<option>${esc(d)}</option>`).join('');if(keep)$('#sDep').value=keep;
  const ks=$('#sSrc').value;$('#sSrc').innerHTML=SRC.map(s=>`<option>${esc(s.nombre)}</option>`).join('');if(ks)$('#sSrc').value=ks;
  $('#offLinks').innerHTML=OFF.map(o=>`<a class="btn sm" href="${o[1]}" target="_blank" rel="noopener noreferrer">${esc(o[0])}</a>`).join('');
}
async function startScan(scope){const r=await post('/api/scan',{scope,paginas:+$('#sPages').value,sens:$('#sSens').value});if(r.started===false)logLine({l:'warn',t:'',m:T('scan_busy')});}
$$('[data-scan]').forEach(b=>b.onclick=()=>startScan(b.dataset.scan));
$('#sDepGo').onclick=()=>startScan('dep:'+$('#sDep').value);$('#sSrcGo').onclick=()=>startScan('src:'+$('#sSrc').value);
['#btnStop','#btnStop2'].forEach(s=>$(s).onclick=()=>post('/api/scan/stop'));
['#btnVerify','#btnVerify2'].forEach(s=>$(s).onclick=()=>post('/api/verify'));
$('#btnAdd').onclick=async()=>{const r=await post('/api/sources/add',{nombre:$('#nName').value,url:$('#nUrl').value,departement:$('#nDep').value||'National',tipo:$('#nTipo').value});if(r.ok){$('#nName').value='';$('#nUrl').value='';renderScan();}else alert(r.error||'error');};
function logLine(e){const c=$('#console');if(!c)return;const d=document.createElement('div');d.className='l-'+(e.l||'info');d.textContent=(e.t?e.t+'  ':'')+e.m;c.appendChild(d);while(c.childNodes.length>400)c.removeChild(c.firstChild);c.scrollTop=c.scrollHeight;}

/* ===================== ALARM ===================== */
const AL={armed:lsGet('df_armed','0')==='1',vol:+lsGet('df_vol','60'),snd:lsGet('df_snd','siren'),muteUntil:0,ctx:null,node:null,playing:false,last:null,seq:null,notif:lsGet('df_notif','0')==='1'};
function ensureCtx(){if(!AL.ctx){try{AL.ctx=new (window.AudioContext||window.webkitAudioContext)();}catch(e){}}if(AL.ctx&&AL.ctx.state==='suspended')AL.ctx.resume();return AL.ctx;}
function stopSiren(){if(AL.node){try{AL.node.stop();}catch(e){}AL.node=null;}AL.playing=false;$('#alarmOv').classList.remove('on');document.body.classList.remove('alarming');updAlarmUI();}
function playSiren(){const c=ensureCtx();if(!c||AL.playing)return;AL.playing=true;
  const o=c.createOscillator(),g=c.createGain(),lfo=c.createOscillator(),lg=c.createGain();
  const m={siren:['sawtooth',900,.55,350],pulse:['square',880,5,0],klaxon:['square',420,2.2,0]}[AL.snd]||['sawtooth',900,.55,350];
  o.type=m[0];o.frequency.value=m[1];lfo.frequency.value=m[2];lg.gain.value=m[3];
  if(AL.snd==='siren'){lfo.connect(lg);lg.connect(o.frequency);}
  else{lfo.type='square';const lg2=c.createGain();lg2.gain.value=.5;lfo.connect(lg2);lg2.connect(g.gain);}
  g.gain.value=Math.max(0,AL.vol/100)*.25;o.connect(g);g.connect(c.destination);o.start();lfo.start();
  const stop=o.stop.bind(o);o.stop=()=>{try{stop();lfo.stop();}catch(e){}};AL.node=o;setTimeout(()=>{if(AL.node===o)stopSiren();},9000);if(navigator.vibrate)navigator.vibrate([300,150,300,150,300]);}
function trigger(al){AL.last=al;const it=(al.items||[])[0]||{};
  const txt=(al.test?'[TEST] ':'')+(it.titulo||T('alarm_conflict'))+(it.dep?' · '+it.dep:'')+(al.items&&al.items.length>1?' (+'+(al.items.length-1)+')':'');
  $('#alarmTxt').textContent=txt;$('#alarmOv').classList.add('on');document.body.classList.add('alarming');
  const ah=$('#aHist');const dv=document.createElement('div');dv.textContent=new Date().toLocaleTimeString(LOC[LANG])+' · '+txt;ah.prepend(dv);
  if(AL.notif&&window.Notification&&Notification.permission==='granted'){try{new Notification('DIABOLIC FRANCE',{body:txt});}catch(e){}}
  if((AL.armed||al.test)&&Date.now()>AL.muteUntil)playSiren();updAlarmUI();}
function updAlarmUI(){const led=$('#ledAlarm'),st=$('#alarmState'),muted=Date.now()<AL.muteUntil;
  led.className='led '+(AL.playing?'bad':!AL.armed?'':muted?'warn':'on');
  if(st)st.textContent=T(AL.playing?'alarm_ringing':!AL.armed?'alarm_off':muted?'alarm_muted':'alarm_armed');
  const a=$('#aArm');if(a)a.textContent=AL.armed?T('alarm_disarm'):T('alarm_arm');
  const h=$('#aHint');if(h)h.textContent=(AL.ctx&&AL.ctx.state==='running')?'':T('alarm_click');
  const bm=$('#btnMute');if(bm)bm.style.opacity=muted?.5:1;}
$('#alarmBtn').onclick=e=>{e.stopPropagation();$('#alarmPanel').classList.toggle('on');};
document.addEventListener('click',e=>{if(!e.target.closest('#alarmPanel')&&!e.target.closest('#alarmBtn'))$('#alarmPanel').classList.remove('on');});
$('#aArm').onclick=()=>{AL.armed=!AL.armed;lsSet('df_armed',AL.armed?'1':'0');ensureCtx();updAlarmUI();};
$('#aTest').onclick=async()=>{ensureCtx();AL.muteUntil=0;await post('/api/alarm/test');};
$('#aMute').onclick=()=>{AL.muteUntil=Date.now()+5*60000;stopSiren();setTimeout(updAlarmUI,5*60000+100);};
$('#btnMute').onclick=()=>{AL.muteUntil=Date.now()<AL.muteUntil?0:Date.now()+30*60000;stopSiren();};
$('#aStop').onclick=stopSiren;$('#alarmAck').onclick=stopSiren;
$('#alarmGo').onclick=()=>{const it=(AL.last&&AL.last.items||[])[0];stopSiren();show('map');if(it&&it.lat!=null)setTimeout(()=>flyTo(it.lat,it.lon,11),400);};
$('#aVol').value=AL.vol;$('#aVol').oninput=e=>{AL.vol=+e.target.value;lsSet('df_vol',AL.vol);};
$('#aSnd').value=AL.snd;$('#aSnd').onchange=e=>{AL.snd=e.target.value;lsSet('df_snd',AL.snd);};
$('#aThr').value=String(CFG.umbral||6);$('#aThr').onchange=e=>post('/api/alarm/config',{umbral:+e.target.value});
$('#aNot').checked=AL.notif;$('#aNot').onchange=e=>{AL.notif=e.target.checked;lsSet('df_notif',AL.notif?'1':'0');if(AL.notif&&window.Notification&&Notification.permission==='default')Notification.requestPermission();};

/* ===================== ORQUESTACIÓN ===================== */
const R={dash:renderDash,map:renderMap,graphs:renderGraphs,network:renderNet,static:renderStatic,feed:renderFeed,scan:renderScan};
async function show(tab){S.tab=tab;$$('.tab-btn').forEach(b=>b.classList.toggle('on',b.dataset.tab===tab));$$('.tab').forEach(s=>s.classList.toggle('on',s.id==='tab-'+tab));
  if(STALE[tab]!==false){STALE[tab]=false;try{await R[tab]();}catch(e){console.error(e);}}
  if(tab==='map'&&MAP)MAP.invalidateSize();if(tab==='network'&&NET)NET.fit();}
function invalidate(){Object.keys(R).forEach(k=>STALE[k]=true);show(S.tab);renderTicker().catch(console.error);renderGov().catch(console.error);}
$$('.tab-btn').forEach(b=>b.onclick=()=>show(b.dataset.tab));
const chipGroup=(sel,key)=>$$(sel+' .chip').forEach(c=>c.onclick=()=>{S[key]=c.dataset.v;S.page=1;$$(sel+' .chip').forEach(x=>x.classList.toggle('on',x===c));invalidate();});
chipGroup('#fPer','periodo');chipGroup('#fCat','cat');
$('#fTipo').onchange=e=>{S.tipo=e.target.value;S.page=1;invalidate();};
$('#fConf').onchange=e=>{S.conf=+e.target.value;S.page=1;invalidate();};
$('#fSort').onchange=e=>{S.sort=e.target.value;S.page=1;STALE.feed=true;if(S.tab==='feed')show('feed');};
let qt;$('#fQ').oninput=e=>{clearTimeout(qt);qt=setTimeout(()=>{S.q=e.target.value;S.page=1;invalidate();},350);};
$('#lang').onchange=e=>{LANG=e.target.value;lsSet('df_lang',LANG);applyI18n();invalidate();};
$('#btnReset').onclick=()=>{Object.assign(S,{periodo:'all',cat:'all',tipo:'',q:'',conf:0,page:1});$('#fQ').value='';$('#fConf').value='0';$$('#fPer .chip,#fCat .chip').forEach(c=>c.classList.toggle('on',c.dataset.v==='all'));applyI18n();invalidate();};
$('#btnFull').onclick=()=>{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();};
$('#btnCopy').onclick=async()=>{try{await navigator.clipboard.writeText(location.origin+'/?lang='+LANG);const b=$('#btnCopy span');const o=b.textContent;b.textContent=T('copied');setTimeout(()=>b.textContent=o,1200);}catch(e){}};
let lastV=null,jobWas=false;
function jobUI(j){const on=j&&j.running;$('#job').classList.toggle('on',!!on);$('#ledScan').className='led '+(on?'run':'');
  $$('[data-scan],#sDepGo,#sSrcGo').forEach(b=>b.disabled=!!on);
  if(on){const p=Math.round((j.progress||0)*100);$('#jobBar').style.width=p+'%';$('#jobPct').textContent=p+'%';$('#jobTxt').textContent=T('updating')+' · '+(j.msg||'')+' · '+(j.done||0)+'/'+(j.total||0);}
  if(jobWas&&!on){STALE.scan=true;if(S.tab==='scan')show('scan');}jobWas=!!on;}
function connect(){let es;try{es=new EventSource('/stream');}catch(e){return;}
  es.onopen=()=>$('#ledLive').className='led on';
  es.onerror=()=>{$('#ledLive').className='led bad';};
  es.onmessage=ev=>{const d=JSON.parse(ev.data);$('#ledLive').className='led on';jobUI(d.job);(d.log||[]).forEach(logLine);
    if(d.alarm&&AL.seq!==null&&d.alarm.seq!==AL.seq)trigger(d.alarm);if(d.alarm)AL.seq=d.alarm.seq;
    if(lastV!==null&&d.version!==lastV)invalidate();lastV=d.version;};}

/* ── ampliar gráficos: botón ⤢ en el título, doble clic en el gráfico, Esc para cerrar ── */
let ZM=null;
function zoomClose(){if(!ZM)return;const{ov,body,ph}=ZM;ph.parentNode.insertBefore(body,ph);ph.remove();ov.remove();document.body.classList.remove('zooming');ZM=null;zoomResize();}
function zoomResize(){setTimeout(()=>{try{window.dispatchEvent(new Event('resize'));if(window.Chart)document.querySelectorAll('canvas').forEach(c=>{const ch=Chart.getChart(c);if(ch)ch.resize();});if(typeof NET!=='undefined'&&NET&&NET.fit)NET.fit();}catch(e){}},80);}
function zoomOpen(card){
  if(ZM)return;const body=card.querySelector('.cv,#net,img');if(!body)return;
  const ph=document.createComment('zm');body.parentNode.insertBefore(ph,body);
  const ov=document.createElement('div');ov.id='zoomOv';
  ov.innerHTML='<div class="holo zbox"><div class="zh"><span></span><button class="btn sm mg">✕</button></div><div class="zb"></div></div>';
  const h=card.querySelector('h3');ov.querySelector('.zh span').textContent=h?h.textContent:'';
  ov.querySelector('.zb').appendChild(body);document.body.appendChild(ov);document.body.classList.add('zooming');
  ov.querySelector('button').onclick=zoomClose;ov.addEventListener('mousedown',e=>{if(e.target===ov)zoomClose();});
  ZM={ov,body,ph};zoomResize();
}
document.addEventListener('keydown',e=>{if(e.key==='Escape')zoomClose();});
const zoomable=c=>c&&c.querySelector&&c.querySelector('.cv,#net,img');
document.addEventListener('click',e=>{if(ZM)return;const h=e.target.closest('.card > h3');if(h&&zoomable(h.parentElement))zoomOpen(h.parentElement);});
document.addEventListener('dblclick',e=>{if(ZM)return;const c=e.target.closest('.card');if(c&&zoomable(c)&&!e.target.closest('input,select,button,textarea'))zoomOpen(c);});
new MutationObserver(()=>document.querySelectorAll('.card > h3:not(.zm)').forEach(h=>{if(zoomable(h.parentElement))h.classList.add('zm');})).observe(document.body,{childList:true,subtree:true});
document.querySelectorAll('.card > h3').forEach(h=>{if(zoomable(h.parentElement))h.classList.add('zm');});
applyI18n();show('dash');renderTicker().catch(console.error);renderGov().catch(console.error);connect();
fetch('/api/alarm/history').then(r=>r.json()).then(h=>{const ah=$('#aHist');(h.items||[]).slice(0,12).forEach(x=>{const d=document.createElement('div');d.textContent=x.ts+' · '+x.titulo;ah.appendChild(d);});}).catch(()=>{});
</script></body></html>
"""



# ============================================================================
# CLI  (terminal alimentada por el mismo bus que el panel web)
# ============================================================================

def mostrar_banner_inicial():
    print(f"""{Color.CYAN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║    ██████╗ ██╗ █████╗ ██████╗  ██████╗ ██╗     ██╗ ██████╗                    ║
║    ██╔══██╗██║██╔══██╗██╔══██╗██╔═══██╗██║     ██║██╔════╝                    ║
║    ██║  ██║██║███████║██████╔╝██║   ██║██║     ██║██║                         ║
║    ██║  ██║██║██╔══██║██╔══██╗██║   ██║██║     ██║██║                         ║
║    ██████╔╝██║██║  ██║██████╔╝╚██████╔╝███████╗██║╚██████╗                    ║
║    ╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝╚═╝ ╚═════╝                    ║
║{Color.MAGENTA}   🔪 DIABOLIC FRANCE v{VERSION} · CRIME · RUE · CYBER · ALARME · ALERTES OFFICIELLES   {Color.CYAN}║
║{Color.RESET}{Color.BLUE}   ██████{Color.WHITE}██████{Color.RED}██████{Color.CYAN}   "L'union fait la force"          - By Condor2026          ║
║                                                      •SpectrumSecurity•       ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Color.RESET}""")


def _pausa():
    input(f"\n{Color.GRAY}{t('press_enter')}{Color.RESET}")


def _barra(v, mx, n=30):
    return '█' * min(int(v / mx * n), n) if mx else ''


def tipo_nombre(k):
    return TIPOS_CRIMEN.get(k, TIPOS_CRIMEN['other']).get(IDIOMA_ACTUAL, k)


def _titulo(txt):
    cprint(f"\n{'═' * 70}", 'cyan', bold=True)
    cprint(f"  {txt}", 'magenta', bold=True)
    cprint(f"{'═' * 70}", 'cyan', bold=True)


def mostrar_stats_rapidas():
    r = gestor_global.estadisticas_rapidas()
    st = gestor_global.estadisticas()
    if not r:
        cprint(f"\n⚠️ {t('no_data')}", 'yellow')
        return
    _titulo(f"⚡ {t('m_quick')}")
    print(f"  🔪 {t('top_type')}: {tipo_nombre(r['tipo_mas_comun'])} ({r['tipo_mas_comun_count']} - {r['tipo_mas_comun_porcentaje']:.1f}%)")
    print(f"  📅 {t('top_day')}: {r['dia_mas_activo']} ({r['dia_mas_activo_count']})")
    print(f"  📰 {t('top_source')}: {r['fuente_mas_activa']} ({r['fuente_mas_activa_count']})")
    print(f"  🏴 {t('top_dept')}: {r['departamento_critico']} ({r['departamento_critico_count']})")
    ic = '▲' if r['tendencia'] > 0 else '▼' if r['tendencia'] < 0 else '■'
    print(f"  📈 {t('trend')}: {ic} {abs(r['tendencia']):.1f}%")
    c = st['categorias']
    print(f"  💀 {t('severity')}: {st['severidad_promedio']:.1f}/10 · 🔪 {c.get('fisico', 0)} · 🚨 {c.get('rue', 0)} · 🛡️ {c.get('cyber', 0)} · 🔗 {st['multi_fuente']}")


_MENU = [('m_search', '🔍'), ('m_analysis', '📊'), ('m_patterns', '🔗'), ('m_evolution', '📈'), ('m_web', '🌐'), ('m_last', '📰'),
         ('m_export', '📥'), ('m_verify', '🛠️'), ('m_types', '📊'), ('m_adv', '📈'), ('m_clean', '🧹'), ('m_quick', '⚡'),
         ('m_analytics', '🧠'), ('m_png', '🖼️'), ('m_scan_sub', '🎯'), ('m_gov', '🏛️'), ('m_indic', '📉'), ('m_alarm_test', '🚨'),
         ('m_health', '🩺'), ('m_sens', '🎚️')]


def mostrar_menu_principal():
    st = gestor_global.estadisticas()
    act = len([f for f in fuentes_global if f.get('activo', True)])
    c = st['categorias']
    print(f"\n{Color.CYAN}{'═' * 66}{Color.RESET}\n{Color.BOLD}  🔪 DIABOLIC FRANCE v{VERSION}{Color.RESET}   {Color.GRAY}sens={SENSIBILIDAD} · seuil alarme={UMBRAL_ALARMA}{Color.RESET}\n{Color.CYAN}{'═' * 66}{Color.RESET}")
    print(f"  📊 {t('k_total')}: {st['total']}   🔪 {c.get('fisico', 0)}  🚨 {c.get('rue', 0)}  🛡️ {c.get('cyber', 0)}   🏛️ {len(gestor_global.alertas())}")
    print(f"  📰 {t('k_sources')}: {act}/{len(fuentes_global)}   🏴 {t('k_depts')}: {len(st['departements'])}")
    print(f"{Color.YELLOW}{'─' * 66}{Color.RESET}\n{Color.CYAN}  📋 {t('menu_title')}{Color.RESET}")
    half = (len(_MENU) + 1) // 2
    for i in range(half):
        l = f"{Color.GREEN} {i + 1:2d}. {_MENU[i][1]} {t(_MENU[i][0])[:30]:30}{Color.RESET}"
        j = i + half
        r = f"{Color.GREEN}{j + 1:2d}. {_MENU[j][1]} {t(_MENU[j][0])[:30]}{Color.RESET}" if j < len(_MENU) else ''
        print(l + '  ' + r)
    print(f"{Color.RED}  0. 🗑️ {t('m_exit')}{Color.RESET}\n{Color.YELLOW}{'═' * 66}{Color.RESET}")


def servir_web(host='127.0.0.1'):
    iniciar_scheduler()
    if not gestor_global.copia() and not gestor_global.alertas():
        threading.Thread(target=ejecutar_actualizacion, args=('all',), daemon=True).start()
    emit('ok', f"\n🌐 http://localhost:{PUERTO}   (Ctrl+C)   — les scans lancés depuis le panneau s'affichent ici aussi")
    app.run(host=host, port=PUERTO, debug=False, threaded=True)


def _menu_scan():
    _titulo(f"🎯 {t('m_scan_sub')}")
    opts = [('fd', t('btn_scan_fd')), ('cyber', t('btn_scan_cyber')), ('gov', t('btn_scan_gov')), ('dep', t('scan_dep')), ('src', t('scan_src'))]
    for i, (_, n) in enumerate(opts, 1):
        print(f"  {Color.GREEN}{i}. {n}{Color.RESET}")
    o = input(f"{Color.CYAN}➤ {Color.RESET}").strip()
    if o in ('1', '2', '3'):
        ejecutar_actualizacion(opts[int(o) - 1][0])
    elif o == '4':
        deps = sorted({f['departement'] for f in fuentes_global})
        for i, d in enumerate(deps, 1):
            print(f"  {i:2d}. {d}")
        k = input('➤ ').strip()
        if k.isdigit() and 1 <= int(k) <= len(deps):
            ejecutar_actualizacion('dep:' + deps[int(k) - 1])
    elif o == '5':
        for i, f in enumerate(fuentes_global, 1):
            print(f"  {i:2d}. {f['nombre']}")
        k = input('➤ ').strip()
        if k.isdigit() and 1 <= int(k) <= len(fuentes_global):
            ejecutar_actualizacion('src:' + fuentes_global[int(k) - 1]['nombre'])


def _mostrar_alertas():
    _titulo(f"🏛️ {t('gov_alerts')}")
    vg = gestor_global.cfg('vigipirate', {'nivel': 0})
    print(f"  VIGIPIRATE: {t('vig_' + str(vg['nivel'])) if vg.get('nivel') else t('vig_set')}")
    for a in gestor_global.alertas()[:25]:
        col = 'red' if a['nivel'] >= 7 else 'yellow' if a['nivel'] >= 5 else 'cyan'
        cprint(f"  [{a['ctx'].upper():5}] {a['fecha']}  {a['titulo'][:90]}", col)
        cprint(f"          {a['fuente']}  {a['url']}", 'gray')
    if not gestor_global.alertas():
        cprint(f"  {t('gov_none')}", 'gray')


def _mostrar_indicadores():
    ind = Analitica.indicadores(gestor_global.copia())
    _titulo(f"📉 {t('m_indic')}")
    th = ind['threat']
    bar = '█' * int(th['idx'] / 5) + '░' * (20 - int(th['idx'] / 5))
    col = ['green', 'yellow', 'magenta', 'red'][th['level']]
    cprint(f"  {t('threat_idx')}: [{bar}] {th['idx']:.0f}/100  {t(['th_calm', 'th_watch', 'th_tense', 'th_crit'][th['level']])}", col, bold=True)
    print(f"  RSI(14)={ind['rsi']:.0f}   SMA7/30={ind['momentum']:+.1f}%   {t('vol')}={ind['volatility']:.2f}   {t('signal')}: {t({'up': 'sig_up', 'dn': 'sig_dn', 'fl': 'sig_neu'}[ind['signal']])}")
    print()
    for k in ind['tickers']:
        nm = t('cat_' + {'fisico': 'phys', 'rue': 'rue', 'cyber': 'cyber'}[k['key']]) if k['kind'] == 'cat' else tipo_nombre(k['key']) if k['kind'] == 'tipo' else k['key'].upper()
        arrow = '▲' if k['delta'] > 1 else '▼' if k['delta'] < -1 else '■'
        cprint(f"  {nm:30} {k['value']:>7}  {arrow} {k['delta']:+6.1f}%  {''.join('▁▂▃▄▅▆▇█'[min(7, int(v / max(1, max(k['series'])) * 7))] for v in k['series'])}",
               'red' if k['delta'] > 1 else 'green' if k['delta'] < -1 else 'gray')


def _mostrar_salud():
    _titulo(f"🩺 {t('m_health')}")
    for f in fuentes_global:
        e = ESTADO['fuentes'].get(f['nombre'], {})
        l = e.get('last') or {}
        k = l.get('kind', '-')
        col = 'green' if k == 'ok' and l.get('n') else 'yellow' if k in ('ok', 'blocked', 'gone', '') else 'red'
        cprint(f"  {'●' if f.get('activo', True) else '○'} {f['nombre'][:38]:38} {k:8} n={l.get('n', '-'):>3} cand={l.get('cand', '-'):>3} {l.get('note', '')[:40]}", col)


def debug_fuente(nombre):
    """Diagnóstico: muestra, para UNA fuente, cada candidato cosechado y por qué se acepta o se rechaza."""
    f = next((x for x in fuentes_global if nombre.lower() in x['nombre'].lower()), None)
    if not f:
        cprint('source inconnue', 'red')
        return
    ext = ExtractorNoticias([f])
    r, kind = fetch(f['url'], INTENTOS_ESCANEO)
    cprint(f"{f['nombre']} → {f['url']}  [{kind}]  {'HTTP ok, ' + str(len(r.text)) + ' o' if r else ''}", 'cyan', bold=True)
    if not r:
        nueva, how = ext.disc.discover_url(f, kind)
        cprint(f"auto-discovery: {nueva} ({how})", 'magenta')
        return
    its = ext.cosechar(r.text, r.url)
    cprint(f"{len(its)} candidats cosechados", 'white')
    for it in its[:40]:
        rej = Counter()
        geo = geolocalizar(it['titulo'] + ' ' + it['texto'][:250], dep_code_fuente(f), 'dbg')
        d = clasificar_detalle(it['titulo'], it['texto'][:350], SENSIBILIDAD, geo['precision'])
        if 'reject' in d:
            cprint(f"  ✖ {d['reject']:11} {it['titulo'][:95]}", 'gray')
        else:
            cprint(f"  ✔ {d['tipo']:11} conf={d['conf']:3} sev={d['sev']} {it['titulo'][:80]}", 'green')


def menu():
    global SENSIBILIDAD
    while True:
        mostrar_menu_principal()
        opc = input(f"{Color.CYAN}➤ {Color.YELLOW}Option: {Color.RESET}").strip()
        if opc == '1':
            ejecutar_actualizacion('all')
            _pausa()
        elif opc == '2':
            st = gestor_global.estadisticas()
            _titulo(f"📊 {t('m_analysis').upper()}")
            print(f"  {t('k_total')}: {st['total']} | 7d: {st['ultimos_7dias']} | 30d: {st['ultimos_30dias']} | 90d: {st['ultimos_90dias']}")
            print(f"  💀 {st['severidad_promedio']:.1f}/10   🔪 {st['categorias'].get('fisico', 0)}  🚨 {st['categorias'].get('rue', 0)}  🛡️ {st['categorias'].get('cyber', 0)}")
            top = sorted(st['departements'].items(), key=lambda x: -x[1])[:10]
            for d, n in top:
                cprint(f"   {d:26}{n:5} {_barra(n, top[0][1])}", 'cyan')
            _pausa()
        elif opc == '3':
            st = gestor_global.estadisticas()
            _titulo(f"🔗 {t('m_patterns').upper()}")
            top = sorted(st['fuentes'].items(), key=lambda x: -x[1])[:10]
            for f, n in top:
                cprint(f"   {f:32}{n:5} {_barra(n, top[0][1])}", 'cyan')
            _pausa()
        elif opc == '4':
            ev = gestor_global.evolucion_mensual()
            _titulo(f"📈 {t('m_evolution').upper()}")
            if ev:
                mx = max(ev.values())
                for m, n in list(ev.items())[-12:]:
                    cprint(f"   {m}  {n:4} {_barra(n, mx)}", 'cyan')
            else:
                cprint(f"   {t('no_data')}", 'gray')
            _pausa()
        elif opc == '5':
            servir_web()
        elif opc == '6':
            _titulo(f"📰 {t('m_last').upper()}")
            hoy = datetime.now()
            for i, c in enumerate(sorted(gestor_global.copia(), key=lambda x: x.get('fecha', ''), reverse=True)[:20], 1):
                d = TIPOS_CRIMEN.get(c.get('tipo'), TIPOS_CRIMEN['other'])
                cprint(f"\n{i:2d}. {d['icono']} {c['titulo'][:100]}", 'white')
                fs = ', '.join(f.get('n', '') for f in (c.get('fuentes') or [])[:4])
                cprint(f"      📅 {c['fecha']} | 📍 {c.get('departement', '?')} | 💀 {c.get('severidad', 0)}/10 | ✔ {c.get('confianza', 0)}% | ⭐ {relevancia(c, hoy)} | 📰 {fs}", 'gray')
            _pausa()
        elif opc == '7':
            fmt = input(f"{Color.YELLOW}1=JSON 2=CSV 3=HTML 4=GeoJSON ➤ {Color.RESET}").strip()
            m = {'1': ('json', gestor_global.exportar_json), '2': ('csv', gestor_global.exportar_csv),
                 '3': ('html', gestor_global.exportar_html), '4': ('geojson', gestor_global.exportar_geojson)}
            if fmt in m:
                fn = f'diabolic_export.{m[fmt][0]}'
                with open(fn, 'w', encoding='utf-8') as f:
                    f.write(m[fmt][1]())
                cprint(f"✅ {fn}", 'green')
            else:
                cprint(f"❌ {t('invalid')}", 'red')
            _pausa()
        elif opc == '8':
            VerificadorFuentes().verificar_todas(fuentes_global)
            _pausa()
        elif opc == '9':
            st = gestor_global.estadisticas()
            _titulo(f"📊 {t('m_types').upper()}")
            top = sorted(st['tipos'].items(), key=lambda x: -x[1])
            for k, n in top:
                cprint(f"   {TIPOS_CRIMEN.get(k, TIPOS_CRIMEN['other'])['icono']} {tipo_nombre(k):34}{n:5} {_barra(n, top[0][1])}", 'cyan')
            _pausa()
        elif opc == '10':
            st = gestor_global.estadisticas()
            _titulo(f"📈 {t('m_adv').upper()}")
            print(f"  {t('k_total')}: {st['total']} · 7d {st['ultimos_7dias']} · 30d {st['ultimos_30dias']} · 90d {st['ultimos_90dias']}")
            print(f"  🔪 {len(st['tipos'])} types · 📍 {len(st['departements'])} dép. · 📰 {len(st['fuentes'])} sources · 💀 {st['severidad_promedio']:.1f}/10 · 🔗 {st['multi_fuente']} confirmés")
            _pausa()
        elif opc == '11':
            cprint(f"✅ {gestor_global.limpiar_duplicados()} doublons fusionnés", 'green')
            _pausa()
        elif opc == '12':
            mostrar_stats_rapidas()
            _pausa()
        elif opc == '13':
            an = Analitica.analytics(gestor_global.copia())
            _titulo(f"🧠 {t('m_analytics').upper()}")
            cprint(f"\n⚠️ {t('alerts')}:", 'yellow')
            for a in an['anomalies'][-8:]:
                cprint(f"   ⚡ {a['date']}  n={a['count']}  z={a['z']}", 'red')
            if not an['anomalies']:
                cprint(f"   ✔ {t('alert_ok')}", 'green')
            cprint(f"\n🔥 {t('c_trend')}:", 'yellow')
            cprint('   ' + (', '.join(f"{x['word']}(x{x['score']})" for x in an['trending'][:15]) or '-'), 'cyan')
            cprint(f"\n🗺️ {t('hotspots_t')}:", 'yellow')
            for h in an['hotspots'][:8]:
                cprint(f"   {h['label']:24} n={h['count']:4} sev={h['sev']}", 'cyan')
            f = an['forecast']
            cprint(f"\n🔮 {t('c_forecast')}: " + (' → '.join(f"{d[5:]}:{v}" for d, v in zip(f['pred_labels'], f['pred'])) or '-'), 'magenta')
            _pausa()
        elif opc == '14':
            if not HAS_MPL:
                cprint('⚠️ pip install matplotlib networkx', 'yellow')
                _pausa()
                continue
            os.makedirs(DIR_ESTATICOS, exist_ok=True)
            cr = gestor_global.copia()
            for k in ('tipos', 'mensual', 'heatmap', 'hexbin', 'red'):
                png = render_estatico(k, cr, IDIOMA_ACTUAL)
                if png:
                    p = os.path.join(DIR_ESTATICOS, f'{k}.png')
                    with open(p, 'wb') as fh:
                        fh.write(png)
                    cprint(f"✅ {p}", 'green')
                else:
                    cprint(f"⚠️ {k}: {t('st_missing')}", 'yellow')
            _pausa()
        elif opc == '15':
            _menu_scan()
            _pausa()
        elif opc == '16':
            _mostrar_alertas()
            _pausa()
        elif opc == '17':
            _mostrar_indicadores()
            _pausa()
        elif opc == '18':
            alarma_test()
            _pausa()
        elif opc == '19':
            _mostrar_salud()
            _pausa()
        elif opc == '20':
            o = input(f"{Color.YELLOW}1=amplio (≈v1) 2=equilibrado 3=estricto ➤ {Color.RESET}").strip()
            if o in ('1', '2', '3'):
                SENSIBILIDAD = ('amplio', 'equilibrado', 'estricto')[int(o) - 1]
                cprint(f"✅ sens={SENSIBILIDAD}", 'green')
            _pausa()
        elif opc in ('0', 'q', 'Q'):
            cprint(f"\n👋 {t('bye')}", 'red', bold=True)
            break
        else:
            cprint(f"\n❌ {t('invalid')}", 'red')
            time.sleep(1)


def seleccionar_idioma():
    global IDIOMA_ACTUAL
    print(f"\n{Color.YELLOW}🌍 LANGUE / IDIOMA / LANGUAGE / LINGUA / SPRACHE{Color.RESET}")
    for i, l in enumerate(LANGS, 1):
        print(f"  {Color.GREEN}[{i}] {LANG_FLAGS[l]} {LANG_NAMES[l]}{Color.RESET}")
    while True:
        o = input(f"\n{Color.CYAN}➤ {Color.RESET}").strip()
        if o.isdigit() and 1 <= int(o) <= len(LANGS):
            IDIOMA_ACTUAL = LANGS[int(o) - 1]
            break


def main():
    global IDIOMA_ACTUAL, PUERTO, AUTO_REFRESH_MIN, RESPETAR_ROBOTS, SENSIBILIDAD
    ap = argparse.ArgumentParser(description='DIABOLIC FRANCE v3')
    ap.add_argument('--web', action='store_true', help='panneau web direct')
    ap.add_argument('--lang', choices=LANGS)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int)
    ap.add_argument('--auto', type=int, default=0, help='scan automatique toutes les N minutes (web)')
    ap.add_argument('--robots', action='store_true', help='respecter robots.txt (désactivé par défaut, comme la v1)')
    ap.add_argument('--sens', choices=('amplio', 'equilibrado', 'estricto'), default='equilibrado')
    ap.add_argument('--scan', choices=('all', 'fd', 'cyber', 'gov'), help='lance un scan puis quitte')
    ap.add_argument('--pages', type=int, default=PAGINAS_BUSQUEDA)
    ap.add_argument('--debug-fuente', metavar='NOM', help='diagnostic détaillé d\'une source (pourquoi 0 résultat)')
    a = ap.parse_args()
    if a.port:
        PUERTO = a.port
    AUTO_REFRESH_MIN, RESPETAR_ROBOTS, SENSIBILIDAD = a.auto, a.robots, a.sens
    if a.lang:
        IDIOMA_ACTUAL = a.lang
    elif not (a.web or a.scan or a.debug_fuente):
        seleccionar_idioma()
    init_globals()
    if a.debug_fuente:
        debug_fuente(a.debug_fuente)
        return
    if a.scan:
        ejecutar_actualizacion(a.scan, a.pages)
        return
    if a.web:
        servir_web(a.host)
        return
    mostrar_banner_inicial()
    st = gestor_global.estadisticas()
    cprint(f"📊 {st['total']} · ⏳ {gestor_global.datos.get('ultima_actualizacion') or '-'} · 📰 {len(fuentes_global)} · 🧬 UA: {len(USER_AGENTS)}", 'green')
    menu()


if __name__ == '__main__':
    main()
