# 🗼🇫🇷 AVISE LEGAL - DIABOLIC FRANCE 🇫🇷🗼

# Disclaimer — DIABOLIC FRANCE

**Avertissement légal, éthique et technique**

> **Version** : 1.0
> **Projet** : DIABOLIC FRANCE v3.0
> **Auteur** : Condor2026 · SpectrumSecurity
> **Licence** : GPL-3.0-or-later
> **Dernière mise à jour** : 2026

---

## ⚠️ Avertissement principal

**DIABOLIC FRANCE** est un projet **open source**, **éducatif** et **de veille OSINT défensive**. Il est fourni **« tel quel »** (*as is*), **sans aucune garantie** d'exactitude, de disponibilité, d'exhaustivité ou d'adéquation à un usage particulier.

**L'utilisation de ce logiciel se fait sous votre entière responsabilité.** Les auteurs, mainteneurs et contributeurs déclinent toute responsabilité quant à :

- L'usage qui en est fait par un tiers.
- Les décisions prises sur la base des données produites.
- Les conséquences directes ou indirectes de son utilisation.
- Toute violation des conditions d'utilisation des sites scrapés.
- Toute atteinte à la vie privée, à la réputation ou à la dignité d'une personne.

---

## 1. Nature du projet

DIABOLIC FRANCE est un **agrégateur d'informations publiques**. Il :

- **Ne collecte aucune donnée personnelle** au sens du RGPD (pas de nom, pas d'adresse, pas de numéro de téléphone, pas d'email, pas de données de santé).
- **Ne stocke que** : titres d'articles publics, dates de publication, liens URL, noms de médias, localisations géographiques approximatives (ville/département) telles que publiées par les sources.
- **N'accède qu'à des pages publiques** accessibles sans authentification.
- **N'aspire pas** de contenu derrière paywall, captcha, ou authentification.
- **Ne contourne aucune mesure technique de protection** (voir section 4).

---

## 2. Exactitude des données

Les données affichées par DIABOLIC FRANCE sont issues :

1. **De sources journalistiques tierces** (Le Monde, Le Figaro, Ouest-France, etc.) — leur exactitude, leur mise à jour et leur véracité relèvent de la responsabilité de ces médias.
2. **De sources officielles** (CERT-FR, ANSSI, Intérieur, Gendarmerie, Police nationale, Préfecture de police de Paris, info.gouv.fr) — leur contenu est reproduit tel que publié.
3. **D'un classificateur automatique** (voir README § « Classification ») qui peut comporter des **erreurs de typage, de sévérité ou de géolocalisation**.

**Conséquences** :

- Un événement classifié `homicide` peut en réalité relever d'une autre catégorie.
- Une géolocalisation au niveau ville/département est **approximative** (jitter déterministe) et **ne doit pas être utilisée pour localiser précisément un lieu**.
- Un score de confiance ou de pertinence est **indicatif** et ne constitue **pas une preuve**.
- Une fusion multi-sources peut regrouper deux affaires distinctes aux titres similaires.
- Une alerte Vigipirate saisie manuellement n'engage que l'utilisateur qui l'a saisie ; **la seule source officielle est info.gouv.fr**.

**DIABOLIC FRANCE n'est pas un service de renseignement, ni un outil de police, ni un système d'alerte d'urgence.**

---

## 3. Absence de conseil professionnel

Les informations produites par DIABOLIC FRANCE :

- **Ne constituent pas un conseil juridique.**
- **Ne constituent pas un conseil en sécurité.**
- **Ne constituent pas un diagnostic criminel.**
- **Ne remplacent pas** une source officielle, une autorité compétente, un avocat, un expert en sécurité ou un professionnel de santé.

En cas d'urgence, **contactez immédiatement les services compétents** :

| Urgence | Numéro |
|---|---|
| Police / Gendarmerie | **17** |
| Pompiers | **18** |
| SAMU | **15** |
| Urgence européenne | **112** |
| Urgence sourds/malentendants | **114** |
| Signalement cybercriminalité | [cybermalveillance.gouv.fr](https://www.cybermalveillance.gouv.fr/) |
| Signalement contenus illégaux | [internet-signalement.gouv.fr](https://www.internet-signalement.gouv.fr/) |

---

## 4. Scraping — conformité et limites

DIABOLIC FRANCE effectue du **scraping respectueux** de pages publiques :

| Aspect | Comportement |
|---|---|
| **User-Agents** | 150+ navigateurs réalistes, rotation aléatoire |
| **Tentatives** | 2 essais par source (v3), puis passage à la suivante |
| **Délais** | 0.8-2.0 s entre requêtes (aléatoire) |
| **Timeout** | 25 s par requête |
| **Budget par source** | 90 s maximum (aucune source ne bloque le scan global) |
| **Cache DNS** | 10 min (évite les essais inutiles) |
| **robots.txt** | **Ignoré par défaut** (comme la v1), activable avec `--robots` |
| **Retry-After** | **Non respecté** (une source qui répond « attends 1 h » ne gèle pas le scan) |

> **⚠️ Vous êtes seul responsable** du respect des **conditions d'utilisation** (CGU/ToS) de chaque site scrapé, du **robots.txt** si vous activez `--robots`, du **RGPD** si vous traitez des données à caractère personnel (ce que le projet évite par conception), et des **lois locales** applicables.

Le projet **ne fournit aucune garantie** quant à la légalité du scraping dans votre juridiction. En cas de doute, **consultez un avocat** avant utilisation.

---

## 5. Sources officielles — avertissement spécifique

### 5.1 CERT-FR / ANSSI / Cybermalveillance.gouv.fr

Les alertes reproduites depuis ces sources sont **publiées telles quelles**. Elles peuvent être **obsolètes**, **partielles**, ou **complétées** par des publications plus récentes. **Consultez toujours la source originale** avant toute décision technique ou de sécurité.

### 5.2 Intérieur / Gendarmerie / Police nationale / Préfecture de police de Paris

Les communiqués reproduits sont **publics**. Ils ne constituent **pas une autorisation**, **pas un laissez-passer**, **pas une accréditation**. Toute utilisation à des fins de **prétendu statut officiel** est **strictement interdite** et peut constituer une **usurpation d'identité ou de fonction** (art. 433-17 du Code pénal français).

### 5.3 Vigipirate

Le **niveau Vigipirate** affiché dans DIABOLIC FRANCE est **saisi manuellement** par l'utilisateur. **Il ne s'agit en aucun cas d'une donnée officielle en temps réel.** La **seule source officielle** est :

👉 **[info.gouv.fr — Vigipirate](https://www.info.gouv.fr/actualite/vigipirate)**

Toute décision fondée sur le niveau Vigipirate affiché dans DIABOLIC FRANCE se fait **sous votre seule responsabilité**.

---

## 6. Alarme sonore — avertissement

La fonction **alarme sonore** :

- **Nécessite une interaction utilisateur** préalable (politique navigateur WebAudio).
- **Peut être bruyante** — réglez le volume en conséquence.
- **Peut provoquer un stress** chez certaines personnes (sirène, klaxon, pulse).
- **Ne constitue pas un système d'alerte d'urgence** au sens légal.

**N'utilisez pas** cette fonction dans un contexte où une sirène pourrait être confondue avec un signal d'évacuation réel (établissement scolaire, hôpital, aéroport, etc.).

---

## 7. Limitation de responsabilité

Dans la mesure maximale permise par la loi applicable, **les auteurs, mainteneurs et contributeurs de DIABOLIC FRANCE déclinent toute responsabilité** pour :

- Tout dommage direct, indirect, incident, spécial, consécutif ou punitif.
- Toute perte de données, de revenus, de profits, d'opportunités.
- Toute interruption d'activité.
- Toute atteinte à la réputation.
- Toute décision prise sur la base des informations produites.
- Toute utilisation abusive ou illégale du logiciel par un tiers.
- Toute violation des CGU/ToS d'un site scrapé par un utilisateur.
- Toute violation du RGPD, du Code pénal, du Code de la propriété intellectuelle, ou de toute autre loi applicable.

**Cette limitation s'applique même si les auteurs ont été informés de la possibilité de tels dommages.**

---

## 8. Usage interdit

**Il est strictement interdit** d'utiliser DIABOLIC FRANCE pour :

- ❌ **Surveiller, profiler, cibler ou harceler** des individus, des groupes ethniques, religieux, politiques ou sociaux.
- ❌ **Doxxer** ou révéler l'identité de victimes, témoins, suspects, mineurs ou personnes vulnérables.
- ❌ **Contourner** les mesures de protection des sources (captcha, paywall, authentification, robots.txt si activé).
- ❌ **Usurper** une identité ou une fonction officielle (police, gendarmerie, autorité).
- ❌ **Diffuser** de fausses informations, de la propagande terroriste ou de l'apologie de crimes.
- ❌ **Constituer** un fichier de police, de renseignement ou de surveillance sans autorisation légale.
- ❌ **Violer** le secret de l'enquête, le secret professionnel, ou le secret des correspondances.
- ❌ **Discriminer** des personnes sur quelque base que ce soit.
- ❌ **Enfreindre** les CGU/ToS des sites scrapés, le RGPD, ou toute autre loi applicable.

Toute contribution ou utilisation contraire à ces principes sera **retirée sans délai** et pourra entraîner un **bannissement permanent** du projet, **sans préjudice de poursuites judiciaires**.

Voir [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) et [LEGAL_ETHICAL_NOTICE.md](LEGAL_ETHICAL_NOTICE.md) pour les détails.

---

## 9. Propriété intellectuelle

### 9.1 Code source

DIABOLIC FRANCE est distribué sous licence **GNU General Public License v3.0 or later** (GPL-3.0-or-later). Voir [LICENSE](LICENSE).

### 9.2 Contenu des sources

Les **titres d'articles**, **extraits**, **liens** et **logos** reproduits appartiennent à leurs **auteurs et éditeurs respectifs**. DIABOLIC FRANCE :

- **Cite ses sources** dans chaque événement (`fuentes[]`).
- **Renvoie systématiquement** vers l'URL originale.
- **N'archive pas** le contenu intégral des articles.
- **Ne se substitue pas** à la lecture des sources originales.

Conformément à la **directive européenne 2019/790** sur le droit d'auteur dans le marché unique numérique, l'usage est limité à une **citation courte** (titre + lien), à des fins d'**information et de veille**.

### 9.3 Logo

Le logo `Diabolic_France_Logo.png` est fourni avec le projet. Son usage commercial requiert l'accord écrit préalable de l'auteur.

---

## 10. Données personnelles (RGPD)

### 10.1 Principe

DIABOLIC FRANCE **ne collecte, ne stocke et ne traite aucune donnée à caractère personnel** au sens de l'article 4 du RGPD. Les seules données conservées sont :

- Des **titres d'articles** publics (données éditoriales).
- Des **URLs** de pages publiques.
- Des **noms de médias** (personnes morales).
- Des **localisations administratives** (départements, villes) telles que publiées par les sources.

### 10.2 Cas particulier des personnes nommées

Certains titres d'articles peuvent mentionner des **noms de personnes** (victimes, suspects, condamnés) **déjà publiés par des médias dans le cadre de leur mission d'information**. DIABOLIC FRANCE :

- **Ne reproduit pas** ces noms dans des champs structurés.
- **Ne permet pas** de recherche par nom.
- **N'enrichit pas** ces données avec d'autres sources.
- **Ne constitue pas** un fichier de personnes au sens de la loi Informatique et Libertés.

**Si vous êtes une personne concernée** et que vous estimez que votre nom apparaît à tort dans une fiche, vous pouvez demander la suppression en contactant : 📧 **spectrumsecurity@proton.me**

### 10.3 Cookies et traceurs

Le panneau web DIABOLIC FRANCE **ne dépose aucun cookie de suivi**, **aucun traceur analytique**, **aucun script tiers de publicité**. Les seuls stockages navigateur utilisés sont :

- `localStorage` : préférences (langue, armement alarme, volume, type de son, fond de carte, notification).
- **Aucun cookie** n'est émis par le serveur Flask.

Les cartes Leaflet chargent des tuiles depuis :
- OpenStreetMap / OSM France (© OpenStreetMap contributors, ODbL)
- CARTO (© CARTO, CGU CARTO)
- Esri (© Esri, CGU Esri)

Ces services tiers peuvent recevoir votre adresse IP. Consultez leurs politiques respectives.

---

## 11. Disponibilité et maintenance

- Le projet est fourni **sans engagement de disponibilité**.
- Les sources peuvent **changer d'URL**, **bloquer** le scraping, **modifier** leur structure HTML, **exiger** un JavaScript lourd, ou **fermer**.
- L'auto-discovery peut **échouer**.
- Le mainteneur **n'a aucune obligation** de corriger, maintenir ou supporter le projet.
- Les **issues** et **pull requests** sont traitées **au mieux**, **sans SLA**.

---

## 12. Juridiction

Le projet est **édité depuis la France**. En cas de litige, et à défaut de résolution amiable, les **tribunaux français** sont seuls compétents, sous réserve des règles impératives protégeant les consommateurs.

**Rien dans ce disclaimer ne saurait limiter les droits impératifs** dont vous pourriez bénéficier en vertu de la loi applicable (notamment en matière de protection des consommateurs ou de responsabilité du fait des produits défectueux).

---

## 13. Modifications

Ce disclaimer peut être **modifié à tout moment**, sans préavis. La version en vigueur est **toujours celle publiée** dans le dépôt officiel :

👉 **[github.com/Condor2026/diabolic_france/blob/main/DISCLAIMER.md](https://github.com/Condor2026/diabolic_france/blob/main/DISCLAIMER.md)**

Il est de votre responsabilité de **consulter régulièrement** ce document.

---

## 14. Contact

| Objet | Contact |
|---|---|
| Questions générales | [@Condor2026](https://github.com/Condor2026) |
| Sécurité | spectrumsecurity@proton.me |
| Demande RGPD (suppression) | spectrumsecurity@proton.me |
| Code de conduite | Voir [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |

---

## 15. Documents liés

- [README.md](README.md) — Documentation principale
- [LICENSE](LICENSE) — Licence GPL-3.0-or-later
- [LEGAL_ETHICAL_NOTICE.md](LEGAL_ETHICAL_NOTICE.md) — Notice légale et éthique détaillée
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Code de conduite
- [CHANGELOG.md](CHANGELOG.md) — Journal des modifications
- [ROADMAP.md](ROADMAP.md) — Feuille de route

---

> **🔪 DIABOLIC FRANCE** — *Vigilamus pro tuendo*
>
> **Surveiller pour protéger, jamais pour nuire.**
>
> En utilisant ce logiciel, vous reconnaissez avoir lu, compris et accepté l'intégralité de cet avertissement.
