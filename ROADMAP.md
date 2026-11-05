# Roadmap — DIABOLIC FRANCE

**Feuille de route officielle du projet**

> **Version actuelle** : 3.0.0 (stable)
> **Mainteneur** : Condor2026 · SpectrumSecurity
> **Licence** : GPL-3.0-or-later
> **Dernière mise à jour** : 2026

---

## Légende

| Symbole | Signification |
|---|---|
| ✅ | Terminé et livré |
| 🚧 | En cours de développement |
| 📋 | Planifié (prochaines versions) |
| 💡 | À l'étude (proposition, non validée) |
| ❌ | Abandonné ou non retenu |

---

## Vision du projet

DIABOLIC FRANCE vise à devenir une **plateforme de référence open source pour la veille criminelle française**, en respectant les principes suivants :

1. **Fiabilité** : classification précise, scores de confiance, fusion multi-sources.
2. **Transparence** : code open source, algorithmes documentés, sources citées.
3. **Éthique** : zéro collecte de données personnelles, respect de la dignité des victimes.
4. **Accessibilité** : multilingue, terminal et web, sans dépendance à un service cloud.
5. **Robustesse** : auto-discovery, résistance aux changements de sites, budget par source.
6. **Sobriété** : fonctionne sur une machine modeste, sans GPU, sans base de données lourde.

---

## ✅ v1.0 — Version initiale (2025)

### Fonctionnalités livrées

- ✅ Scraping séquentiel de 45 sources faits divers.
- ✅ 150+ user-agents en rotation.
- ✅ 3 tentatives par source.
- ✅ Délais aléatoires 0.8-2.0 s.
- ✅ Classification par mots-clés v1 (9 types).
- ✅ Géolocalisation par département (101).
- ✅ Export JSON / CSV / HTML.
- ✅ Menu terminal 12 options.
- ✅ Base `diabolic_france.json`.

---

## ✅ v2.0 — Panneau web (2025)

### Fonctionnalités livrées

- ✅ Panneau web Flask (`/`, `/api/stats`, `/api/crimes`, `/api/geo`).
- ✅ Pagination 12 incidents/page.
- ✅ 3 langues : FR / ES / IT.
- ✅ Auto-discovery d'URL (variantes www/apex).
- ✅ Graphiques Chart.js (départements, types, mensuel, top sources).
- ✅ Export JSON / CSV / HTML depuis le web.
- ✅ 55+ sources.
- ✅ 20+ types classifiés.

---

## ✅ v3.0 — Refonte majeure (2026)

### Fonctionnalités livrées

#### Sources & scraping

- ✅ 62 sources : 45 faits divers + 9 cyber + 8 officielles.
- ✅ Auto-discovery renforcé (variantes → liens home → chemins v1).
- ✅ Cache d'URL (`url_cache_crime.json`).
- ✅ Détection automatique du flux RSS.
- ✅ Suivi de redirections (mise à jour d'URL).
- ✅ Budget 90 s par source.
- ✅ Cache DNS 10 min.
- ✅ `robots.txt` optionnel (`--robots`).
- ✅ Ajout/suppression de sources depuis le panneau.
- ✅ Activation/désactivation par source.
- ✅ Santé des sources (dernier scan, nb articles, raison du rejet).

#### Classification & anti-faux-positifs

- ✅ 25 types classifiés en 3 catégories (fisico / rue / cyber).
- ✅ Mots forts vs mots faibles.
- ✅ Pondération titre ×1.5.
- ✅ Score de confiance 0-100.
- ✅ Indice de pertinence 0-100.
- ✅ Filtres anti-faux-positifs (foreign, sport, culture, accident, advice, vuln, nav).
- ✅ Scrub des usages non criminels.
- ✅ Sensibilité ajustable (`amplio` / `equilibrado` / `estricto`).

#### Fusion multi-sources

- ✅ Similarité Jaccard (≥ 0.8 ou ≥ 0.5 + même catégorie + ≤ 3 j + même dept).
- ✅ Confiance +8 par source (max 100).
- ✅ Sévérité = max.
- ✅ Nettoyage rétroactif des doublons (menu option 11).

#### Géolocalisation

- ✅ Ville → département → source.
- ✅ Jitter déterministe (hash MD5).
- ✅ Désambiguïsation (Tours, Valence, Nancy, Pau, Saint-Pierre).
- ✅ 101 départements métropole + Outre-mer.
- ✅ Reconnaissance des codes postaux `(75)`, `(2A)`, `(2B)`.

#### Alarme & conflits de rue

- ✅ Alarme sonore WebAudio (sirène / pulse / klaxon).
- ✅ Armement/désarmement persistant.
- ✅ Seuil de sévérité configurable (5-9).
- ✅ Déclencheurs : terrorisme, conflit de rue ≥ seuil, cluster ≥ 3 en 24 h dans un dept.
- ✅ Notifications navigateur (opt-in).
- ✅ Historique des alarmes.

#### Alertes officielles & Vigipirate

- ✅ 8 sources officielles (CERT-FR, ANSSI, Cybermalveillance, Intérieur, Gendarmerie, Police, Préfecture de Paris, info.gouv.fr).
- ✅ Bandeau défilant CYBER / SÛRETÉ.
- ✅ Niveau Vigipirate manuel (1/2/3/0).
- ✅ Niveau d'alerte heuristique (3-10) pour chaque alerte.

#### Indicateurs type crypto

- ✅ RSI(14) Wilder.
- ✅ SMA7 / SMA30.
- ✅ Bollinger (SMA20 ± 2σ).
- ✅ Volatilité (σ/μ).
- ✅ Momentum.
- ✅ Indice de menace 0-100.
- ✅ Signal ESCALADE / APAISEMENT / NEUTRE.
- ✅ Tickers avec sparkline 14 j.

#### Analytique

- ✅ z-score quotidien + anomalies.
- ✅ Pronostic Holt (α=0.5, β=0.3, h=4).
- ✅ Mots en tendance.
- ✅ Hotspots (cellule 0.4°).
- ✅ Réseau type ↔ département.
- ✅ Sankey catégorie → type → département.
- ✅ Heatmap jour × type.
- ✅ Bulles départements (volume × sévérité).
- ✅ Timelapse carte 30 j.

#### Interface web

- ✅ Panneau holographique (cadre animé, grid perspective, scanlines).
- ✅ 7 onglets (Tableau de bord, Carte, Graphiques, Réseau, Statiques, Flux, Scan/Sources).
- ✅ Ticker type Bourse.
- ✅ Jauge SVG pour l'indice de menace.
- ✅ Carte Leaflet 6 fonds + heat + clusters + choroplèthe + hotspots + pulsations + timelapse.
- ✅ Flux SSE (`/stream`).
- ✅ Filtres (période, catégorie, type, texte, confiance, tri).
- ✅ Pagination 15 événements/page.
- ✅ Export JSON / CSV / HTML / GeoJSON.
- ✅ Bouton Stop.
- ✅ Plein écran, copier le lien, réinitialiser les filtres.
- ✅ Responsive mobile / tablette / desktop.

#### CLI & menu terminal

- ✅ 20 options (contre 12 en v1).
- ✅ `--debug-fuente NOM` (diagnostic détaillé).
- ✅ `--web`, `--host`, `--port`, `--auto N`, `--robots`, `--sens`, `--scan`, `--pages`, `--lang`.
- ✅ Partage du flux entre terminal et panneau web (bus SSE).

#### API REST

- ✅ `/api/stats`, `/api/analytics`, `/api/indicators`, `/api/geo`, `/api/network`, `/api/sankey`, `/api/crimes`, `/api/alerts`, `/api/sources`, `/api/status`, `/api/alarm/history`.
- ✅ `/api/scan`, `/api/scan/stop`, `/api/verify`, `/api/sources/toggle`, `/api/sources/add`, `/api/vigipirate`, `/api/alarm/test`, `/api/alarm/config`.
- ✅ `/graph/{kind}.png` : 5 types de graphiques PNG.
- ✅ `/exportar/{fmt}` : 4 formats.
- ✅ `/stream` : SSE.
- ✅ Protection CSRF via header `X-DF: 1`.

#### Internationalisation

- ✅ 5 langues : FR · ES · EN · IT · DE.
- ✅ Interface 100 % traduite (terminal, web, graphiques, exports).

#### Sécurité

- ✅ POST protégés par header `X-DF: 1`.
- ✅ CSV injection-safe.
- ✅ Liens `http(s)` uniquement.
- ✅ `X-Content-Type-Options: nosniff`.
- ✅ `Referrer-Policy: no-referrer`.
- ✅ Pas de `Retry-After` bloquant.
- ✅ Pas de secrets dans le code.
- ✅ `.gitignore` strict (données, logs, caches, exports).

#### Graphiques statiques

- ✅ 5 PNG générés côté serveur (matplotlib + networkx).
- ✅ Génération CLI (menu option 14) vers `graficos_estaticos/`.

---

## 🚧 v3.1 — Consolidation (en cours)

**Objectif** : stabiliser, corriger les bugs, améliorer l'expérience utilisateur.

### En cours

- 🚧 **Tests unitaires** : couverture ≥ 60 % sur le classifieur, la fusion, la géolocalisation et l'API.
- 🚧 **Tests d'intégration** : scan complet sur sources de test locales (fixtures HTML).
- 🚧 **CI GitHub Actions** : lint (ruff), type-check (mypy), tests (pytest), build Docker.
- 🚧 **Documentation développeur** : `CONTRIBUTING.md`, `ARCHITECTURE.md`, guide d'ajout de source.
- 🚧 **Amélioration de l'auto-discovery** : gestion des SPA (React, Vue) via détection de `<script>` JSON-LD.
- 🚧 **Correction de bugs** signalés via Issues.

### Prévu

- 📋 **Export PDF** des rapports (via WeasyPrint ou reportlab).
- 📋 **Filtres avancés** : plage de dates personnalisée, zone géographique (bounding box), sources multiples.
- 📋 **Historique** : conservation longue durée (rotation des fichiers JSON, compression gzip).
- 📋 **Amélioration du classifieur** : réduction des faux positifs sur `attaque_forces` (confusion avec sport/faits divers bénins).
- 📋 **Détection de langue** des articles (heuristique, sans dépendance lourde).
- 📋 **Logs structurés** (JSON Lines) pour intégration SIEM.
- 📋 **Métriques Prometheus** (`/metrics`).
- 📋 **Amélioration du panneau web** : chargement différé des graphiques lourds, Web Workers pour le rendu des gros volumes.

---

## 📋 v3.2 — Extensions (planifié)

**Objectif** : ajouter des fonctionnalités sans casser l'existant.

### Sources & scraping

- 📋 **Nouvelles sources** : presse locale (La Manche Libre, Le Télégramme, etc.), médias spécialisés (KrebsOnSecurity, BleepingComputer, The Record).
- 📋 **Intégration Bluesky / Mastodon** : comptes officiels (préfectures, gendarmerie, CERT-FR).
- 📋 **Intégration Telegram** : canaux publics officiels uniquement (jamais de scraping de canaux privés).
- 📋 **Support Sitemap.xml** : découverte de nouvelles sections.
- 📋 **Support JSON-LD** : extraction structurée depuis les balises `application/ld+json`.

### Classification

- 📋 **Détection de doublons sémantiques** : via embeddings légers (pas de LLM génératif, modèle spaCy ou fastText).
- 📋 **Scores de sentiment** : sur les titres uniquement, pour mesurer la couverture médiatique.
- 📋 **Extraction d'entités nommées** : lieux, types d'armes, organisations — **sans** noms de personnes.
- 📋 **Détection de campagnes coordonnées** : clusters de titres quasi-identiques sur plusieurs sources.

### Analytique

- 📋 **Détection de ruptures** : CUSUM, Page-Hinkley sur flux quotidiens.
- 📋 **Modèles saisonniers** : SARIMA sur flux mensuels.
- 📋 **Corrélation** : lien entre pics d'un type et pics d'un autre (ex. cyber + terrorisme).
- 📋 **Carte de chaleur temporelle** : heatmap 3D (jour × heure × type).
- 📋 **Clustering géographique** : DBSCAN sur les points géolocalisés.

### Interface

- 📋 **Export PDF** des rapports.
- 📋 **Mode « kiosk »** : dashboard plein écran auto-rafraîchi pour écran mural.
- 📋 **Thème clair** (accessibilité).
- 📋 **Accessibilité WCAG AA** : contrastes, navigation clavier, lecteurs d'écran.
- 📋 **PWA** : installation comme application de bureau/mobile.
- 📋 **Notifications push** (Web Push API) pour les alertes critiques.

### API

- 📋 **OpenAPI 3.1** : spécification complète du REST.
- 📋 **Pagination cursor** (au lieu de page/per).
- 📋 **Webhooks** : POST sortant sur événement (nouveau conflit, nouvelle alerte).
- 📋 **GraphQL** (optionnel) : pour clients avancés.
- 📋 **Rate-limiting** par IP et par token.
- 📋 **API keys** : tokens révocables pour usage programmatique.

---

## 💡 v4.0 — Vision long terme (à l'étude)

**Objectif** : passage à l'échelle, industrialisation, écosystème.

### Architecture

- 💡 **Backend séparé** : FastAPI + SQLite/PostgreSQL pour découpler le scraping du web.
- 💡 **File de messages** : Redis Queue ou RQ pour les scans asynchrones.
- 💡 **Cache distribué** : Redis pour les résultats fréquents.
- 💡 **Base de données** : SQLite par défaut (déploiement simple), PostgreSQL optionnel (déploiement pro).
- 💡 **Reverse-proxy intégré** : Nginx documenté, Caddy en option.
- 💡 **Multi-tenant** : instances isolées pour plusieurs utilisateurs (si pertinent).
- 💡 **Container officiel** : Dockerfile multi-stage, image Alpine ou distroless.

### Fonctionnalités

- 💡 **Analyse d'images** : détection de lieux sur photos (via reverse image search, sans API payante).
- 💡 **Transcription audio** : pour les vidéos de presse (via Whisper local, optionnel).
- 💡 **Résumés automatiques** : via modèle local (Mistral 7B, Llama 3, ou équivalent), **sans** envoi vers des API tierces.
- 💡 **Traduction automatique** : des titres étrangers vers FR/ES/EN/IT/DE (via Marian NMT local).
- 💡 **Cartes historiques** : évolution des hotspots sur 1 an / 5 ans.
- 💡 **Rapports programmés** : PDF hebdomadaire/mensuel envoyé par email (opt-in).
- 💡 **Mode collaboratif** : annotations, commentaires, tags personnalisés (multi-utilisateurs).

### Écosystème

- 💡 **Plugin navigateur** : récupération d'un article vers DIABOLIC FRANCE.
- 💡 **Application mobile** : Flutter ou React Native (réutilise l'API).
- 💡 **Bibliothèque Python** : `diabolic-france-client` publié sur PyPI.
- 💡 **Datasets publics** : exports anonymisés et agrégés pour la recherche.

### Légal & éthique

- 💡 **Audit externe** : revue par un tiers indépendant (juriste + expert éthique).
- 💡 **Charte OSINT** : publication d'une charte détaillée (au-delà du `LEGAL_ETHICAL_NOTICE.md`).
- 💡 **Comité éthique** : 2-3 experts bénévoles pour valider les évolutions sensibles.
- 💡 **Transparence algorithmique** : publication des règles de classification sous forme lisible.

---

## ❌ Abandonné / non retenu

| Idée | Raison |
|---|---|
| ❌ Scraping de réseaux sociaux (X/Twitter, Facebook, Instagram) | CGU restrictives, données personnelles, API fermées ou payantes, risque juridique |
| ❌ Scraping de forums / Telegram non officiels | Risque de contenu illégal, de doxxing, de diffamation |
| ❌ Intégration LLM génératif pour résumés | Coût, dépendance, risque de hallucination, non-déterminisme |
| ❌ Base de données de personnes | Contraire à la minimisation RGPD et à l'éthique du projet |
| ❌ Système de notation individuelle (score de dangerosité) | Contraire à l'éthique, risque de profilage discriminatoire |
| ❌ Prédiction de crimes individuels | Illusoire, contraire à la présomption d'innocence |
| ❌ Support Windows Server / IIS | Le projet reste simple (Python + Flask + scripts) |
| ❌ Interface 100 % JS (SPA) | Complexité inutile, dépendance CDN, accessibilité, SEO |
| ❌ Comptes utilisateurs / login | Contraire à la simplicité et à la minimisation des données |

---

## Comment contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md) (si présent) et [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

**Axes prioritaires pour les contributions** :

1. 🚧 **Tests** (unitaire, intégration) — voir v3.1.
2. 🚧 **CI/CD** (GitHub Actions, Docker).
3. 🚧 **Documentation** (développeur, architecture, ajout de source).
4. 📋 **Nouvelles sources officielles** (vérifiées, publiques).
5. 📋 **Traductions** supplémentaires (PT, NL).
6. 📋 **Graphiques** supplémentaires (statiques ou interactifs).
7. 📋 **Accessibilité** (WCAG AA).

**Axes non prioritaires** :

- ❌ Fonctionnalités contraires à l'éthique (voir `LEGAL_ETHICAL_NOTICE.md`).
- ❌ Ajout de dépendances lourdes sans justification.
- ❌ Refonte UI sans discussion préalable (ouvrir une issue).
- ❌ Ajout de sources non vérifiées ou payantes.

---

## Suivi

| Version | Statut | Date cible |
|---|---|---|
| v1.0 | ✅ Livrée | 2025 |
| v2.0 | ✅ Livrée | 2025 |
| v3.0 | ✅ Livrée | 2026 |
| v3.1 | 🚧 En cours | À définir |
| v3.2 | 📋 Planifiée | À définir |
| v4.0 | 💡 À l'étude | À définir |

Les versions **v3.1** et **v3.2** seront publiées **quand elles seront prêtes**, sans engagement de date. Le projet est **maintenu bénévolement**.

---

## Historique des modifications du roadmap

| Date | Modification |
|---|---|
| 2026 | Ajout de la section v3.0 (livrée) et v3.1 (en cours) |
| 2025 | Création du roadmap initial (v1.0 / v2.0) |

---

## Documents liés

- [README.md](README.md) — Documentation principale
- [CHANGELOG.md](CHANGELOG.md) — Journal des modifications
- [DISCLAIMER.md](DISCLAIMER.md) — Avertissement
- [LEGAL_ETHICAL_NOTICE.md](LEGAL_ETHICAL_NOTICE.md) — Notice légale et éthique
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Code de conduite
- [LICENSE](LICENSE) — Licence GPL-3.0-or-later

---

> **🔪 DIABOLIC FRANCE** — *Vigilamus pro tuendo*
>
> **Surveiller pour protéger, jamais pour nuire.**
>
> Cette feuille de route est un **document vivant** : elle évolue avec le projet, les retours de la communauté et les contraintes légales/éthiques.
