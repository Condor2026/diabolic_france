# Changelog

Tous les changements notables de **DIABOLIC FRANCE** sont documentés dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

- **Auteur** : Condor2026 · **SpectrumSecurity**
- **Licence** : GPL-3.0-or-later

---

## [Unreleased]

### Prévu
- Support multilingue étendu (PT, NL) — voir `ROADMAP.md`
- Export PDF des rapports
- Intégration RSS native pour toutes les sources faits divers
- Historisation longue durée avec rotation des fichiers JSON
- Mode serveur `--workers` pour déploiement derrière reverse-proxy

---

## [3.0.0] — 2026-06-XX

> **Refonte majeure.** DIABOLIC FRANCE devient une plateforme de renseignement criminel multi-domaines : crime physique, conflits de rue, cybercriminalité, alertes officielles. Le scraping v1 est conservé mais enrichi d'un classificateur anti-faux-positifs, d'une fusion multi-sources, d'une alarme sonore et d'une carte 2D multi-couches.

### Ajouté

#### Sources & scraping
- **8 sources officielles** : CERT-FR (RSS), ANSSI, Cybermalveillance.gouv.fr, Intérieur, Gendarmerie nationale, Police nationale, Préfecture de police de Paris, info.gouv.fr (Vigipirate).
- **9 médias cyber spécialisés** : ZATAZ (RSS), LeMagIT, Numerama Cyberguerre, Silicon.fr, 01net, Le Monde Informatique, Next.ink (RSS), France Info Cybercriminalité, Le Figaro Cybersécurité.
- **Ajout de sources depuis le panneau web** (`/api/sources/add`), persisté dans `estado_fuentes_crime.json`.
- **Activation/désactivation par source** (`/api/sources/toggle`).
- **Auto-discovery d'URL renforcé** : variantes www/apex/slash final → liens de la home (scoring par mots-clés) → chemins v1 (50+). Cache persistant dans `url_cache_crime.json`.
- **Détection automatique du flux RSS** d'une source si la page principale ne produit rien.
- **Suivi de redirections** : si une source redirige vers un autre host/section, l'URL est mise à jour automatiquement.
- **Budget par source** (90 s) : aucune source ne peut bloquer le scan global.
- **Cache DNS** (10 min) : un domaine mort ne coûte plus 6 essais.
- **Respect optionnel de `robots.txt`** via `--robots` (désactivé par défaut, comme la v1).

#### Classification & anti-faux-positifs
- **Classificateur détaillé** : mots « forts » (suffisent seuls) vs « faibles » (exigent un indice policier/judiciaire), pondération titre ×1.5.
- **25 types classifiés** répartis en 3 catégories : `fisico` (11), `rue` (6), `cyber` (7), + `other`.
- **Score de confiance 0-100** : base 45 (fort) / 30 (faible) + 10 titre + 10 indice policier + 10 géoloc − pénalités.
- **Indice de pertinence 0-100** : `4.5×sévérité + 0.25×confiance + 20×(sources−1)/3 + 10×fraîcheur`.
- **Filtres anti-faux-positifs** : `foreign` (Ukraine, Gaza, USA…), `sport` (Ligue 1, PSG…), `culture` (film, série…), `accident` (route, noyade…), `advice` / `vuln` (CVE, patch, conseils), `nav` (cookies, abonnement).
- **Scrub des usages non criminels** : vols de nuit, bandes dessinées, incendies de forêt, tensions diplomatiques, etc.
- **Sensibilité ajustable** : `amplio` (≈ v1, seuil 20), `equilibrado` (défaut, 45), `estricto` (60).

#### Fusion multi-sources
- **Similarité Jaccard** sur les tokens du titre (≥ 0.8 = fusion ; ≥ 0.5 + même catégorie + ≤ 3 j + même dept = fusion).
- **Confiance +8 par source** supplémentaire (max 100).
- **Sévérité = max** des deux événements.
- **Nettoyage des doublons existants** (menu option 11) : fusion rétroactive.

#### Géolocalisation
- **Ville → département → source** avec jitter déterministe (hash MD5).
- **Désambiguïsation** : Tours, Valence, Nancy, Pau, Saint-Pierre ne sont géolocalisés que précédés d'une préposition (« à Tours », « vers Valence »…).
- **101 départements** métropole + Outre-mer (971, 972, 973, 974, 976).
- **Codes postaux** `(75)`, `(2A)`, `(2B)` reconnus.

#### Alarme & conflits de rue
- **Alarme sonore WebAudio** : sirène / pulse / klaxon, volume réglable, mute 5/30 min.
- **Armement/désarmement** persistant (`localStorage`).
- **Seuil de sévérité** configurable (5-9, défaut 6).
- **Déclencheurs** : terrorisme, conflit de rue ≥ seuil, cluster ≥ 3 en 24 h dans un même département.
- **Notifications navigateur** (opt-in).
- **Historique des alarmes** (`alarma_hist`, max 100).
- **Bandeau d'alerte** en bas du panneau quand la sirène sonne.

#### Alertes officielles & Vigipirate
- **Bandeau défilant** en haut du panneau : dernières alertes CYBER (CERT-FR/ANSSI/Cybermalveillance) et SÛRETÉ (Intérieur/Gendarmerie/Police/Préfecture).
- **Niveau Vigipirate** saisi manuellement (1/2/3/0) et persisté.
- **Niveau d'alerte** heuristique (3-10) pour chaque alerte officielle.

#### Indicateurs type crypto
- **RSI(14)** Wilder, **SMA7/SMA30**, **Bollinger (SMA20 ± 2σ)**, **volatilité (σ/μ)**.
- **Momentum** `(SMA7/SMA30 − 1)×100`.
- **Indice de menace 0-100** : `38 + 16×z + 3×(sévérité−4) + 14×part_rue` (borné).
- **Signal** ESCALADE / APAISEMENT / NEUTRE.
- **Tickers** avec sparkline 14 j (indice, total, physique, rue, cyber, top types, RSI, sévérité).
- **Timelapse carte 30 j**.

#### Analytique
- **z-score quotidien** + détection d'anomalies (z ≥ 2 et n ≥ 3).
- **Pronostic Holt** (α=0.5, β=0.3, h=4) sur le flux hebdomadaire.
- **Mots en tendance** (score = (count_7j+1)/(espérance_60j+1)).
- **Hotspots** par cellule 0.4° (score = n × (1 + sévérité/5)).
- **Réseau type ↔ département** (top 45 arêtes).
- **Sankey** catégorie → type → département.
- **Heatmap** jour × type.
- **Bulles départements** volume × sévérité.

#### Interface web
- **Panneau holographique** : cadre conic-gradient animé, grid perspective, scanlines, Orbitron/Rajdhani.
- **7 onglets** : Tableau de bord, Carte, Graphiques, Réseau, Statiques, Flux, Scan/Sources.
- **Ticker type Bourse** en haut.
- **Jauge SVG** pour l'indice de menace.
- **Carte Leaflet** : 6 fonds (Carto dark/light/Voyager, OSM, OSM France, Esri satellite) + heat + clusters + choroplèthe + hotspots + pulsations + timelapse.
- **Flux SSE** (`/stream`) : logs, état du job, alarmes en temps réel.
- **Filtres** : période (24h/7j/30j/90j), catégorie (fisico/rue/cyber), type (25), texte, confiance (≥45%/≥60%), tri (date/pertinence/sévérité).
- **Pagination** : 15 événements/page.
- **Export** : JSON, CSV, HTML, GeoJSON depuis la barre d'outils.
- **Bouton Stop** pour interrompre un scan.
- **Plein écran**, **copier le lien**, **réinitialiser les filtres**.
- **Responsive** mobile/tablette/desktop.

#### CLI & menu terminal
- **20 options** (contre 12 en v1/v2) : scan ciblé, alertes officielles, indicateurs, test alarme, santé des sources, sensibilité, graphiques PNG.
- **`--debug-fuente NOM`** : diagnostic détaillé d'une source (HTTP, candidats, motifs de rejet).
- **`--web`, `--host`, `--port`, `--auto N`, `--robots`, `--sens`, `--scan`, `--pages`, `--lang`**.

#### API REST
- `/api/stats`, `/api/analytics`, `/api/indicators`, `/api/geo`, `/api/network`, `/api/sankey`, `/api/crimes`, `/api/alerts`, `/api/sources`, `/api/status`, `/api/alarm/history`.
- `/api/scan`, `/api/scan/stop`, `/api/verify`, `/api/sources/toggle`, `/api/sources/add`, `/api/vigipirate`, `/api/alarm/test`, `/api/alarm/config`.
- `/graph/{kind}.png` : `tipos`, `mensual`, `heatmap`, `hexbin`, `red`.
- `/exportar/{fmt}` : `json`, `csv`, `html`, `geojson`.
- `/stream` : SSE.

#### Internationalisation
- **5 langues** : FR · ES · EN · IT · DE (contre 3 en v2 : FR/ES/IT).
- **Interface 100 % traduite** : terminal, web, graphiques, exports.

#### Sécurité
- **POST protégés** par header `X-DF: 1` (anti-CSRF pour `localhost`).
- **CSV injection-safe** : cellules `= + - @` préfixées par `'`.
- **Liens `http(s)` uniquement** (pas de `javascript:`/`data:`).
- **`X-Content-Type-Options: nosniff`**, **`Referrer-Policy: no-referrer`**.
- **Pas de `Retry-After` bloquant** : une source qui répond « attends 1 h » ne gèle pas le scan.

#### Graphiques statiques
- **5 PNG** générés côté serveur (matplotlib) : `tipos`, `mensual`, `heatmap`, `hexbin`, `red` (networkx).
- **Génération CLI** (menu option 14) vers `graficos_estaticos/`.

### Modifié

- **Scraping v1 conservé** : séquentiel, 150+ user-agents, **2 essais** par source (au lieu de 3 en v1) puis on passe à la suivante ; délais aléatoires 0.8-2.0 s ; timeout 25 s ; session persistante.
- **Pagination** : détection automatique de `/page/N/`, `?page=N`, `/pagina/N`, `?p=N` (jusqu'à 8 pages).
- **Extraction** : `article`, `div[class*=article|story|post|news|entry]`, `h1-h4` + garde-fou contre les conteneurs gigantesques (>1500 caractères ou >3 sous-articles).
- **Titres** : bornés à 500 caractères, minimum 20.
- **Format de données** : schéma `SCHEMA = 3` (migration automatique v1/v2 → v3).
- **Champs ajoutés** : `categoria`, `confianza`, `fuentes[]`, `precision`, `conflicto`, `v`.
- **Fichiers de données** : `diabolic_france.json`, `url_cache_crime.json`, `estado_fuentes_crime.json`, `diabolic_france_backup.json`, `diabolic_france.log`.
- **État des sources** : format enrichi (`{nombre: {url, activo, last, fails, rss_auto}}`) tout en acceptant le format plat de la v2.

### Corrigé

- **Bruit urllib3** (`Retrying (Retry(total=...`) supprimé des logs.
- **Logs Werkzeug** filtrés (niveau ERROR).
- **Faux positifs massifs** de la v1 (sport, culture, foreign, accident, conseils cyber) réduits par le classificateur.
- **Doublons** : ne sont plus jetés, mais fusionnés avec enrichissement de confiance.
- **Sources mortes** : plus de 6 essais inutiles par domaine (`dns_ok`).
- **Blocage d'un scan entier** par une source lente : budget de 90 s par source.
- **Redirections trompeuses** vers la home : détection et auto-discovery.

### Déprécié

- Le nom d'origine `AIDE-FRANCE` (projet d'entraide) est **abandonné** ; le projet devient **DIABOLIC FRANCE**.
- Les fichiers `aide_france_*.json` ne sont **plus lus** (migration manuelle possible en renommant vers `diabolic_france.json`).

### Supprimé

- Le mode « deux couches » v2 (CLI/web séparés) : désormais CLI et web **partagent le même bus** (`LOG`, `STATE`, `/stream`).
- L'ancien panneau web v2 et ses graphiques fixes : remplacés par le panneau holographique.

### Sécurité

- Voir section **Ajouté > Sécurité**.

---

## [2.0.0] — 2025-XX-XX

### Ajouté
- Panneau web Flask (`/`, `/api/stats`, `/api/crimes`, `/api/geo`).
- Pagination 12 incidents/page.
- 3 langues (FR/ES/IT).
- Auto-discovery d'URL (variantes www/apex).
- Export JSON/CSV/HTML.
- Graphiques Chart.js (départements, types, mensuel, top sources).

### Modifié
- Passage de 9 à 20+ types classifiés.
- 55+ sources (national, régional, Outre-mer).

### Corrigé
- Doublons de titres.
- Gestion des timeouts.

---

## [1.0.0] — 2025-XX-XX

### Ajouté
- Version initiale CLI.
- Scraping séquentiel, 150+ user-agents, 3 essais/source.
- 9 types de crime (drogue, gangs, meurtre, agression, vol, crime organisé, opération police, arme, terrorisme).
- 45 sources faits divers.
- Classification par mots-clés v1.
- Géolocalisation par département (101).
- Export JSON/CSV/HTML.
- Menu terminal 12 options.

---

## Légende

| Symbole | Signification |
|---|---|
| `Ajouté` | Nouvelles fonctionnalités |
| `Modifié` | Changements dans les fonctionnalités existantes |
| `Déprécié` | Fonctionnalités bientôt supprimées |
| `Supprimé` | Fonctionnalités retirées |
| `Corrigé` | Corrections de bugs |
| `Sécurité` | Correctifs de sécurité |

---

## Liens

- [README.md](README.md) — Documentation principale
- [ROADMAP.md](ROADMAP.md) — Feuille de route
- [DISCLAIMER.md](DISCLAIMER.md) — Avertissement
- [LEGAL_ETHICAL_NOTICE.md](LEGAL_ETHICAL_NOTICE.md) — Notice légale & éthique
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Code de conduite
- [LICENSE](LICENSE) — GPL-3.0-or-later
