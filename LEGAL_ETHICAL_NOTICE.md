# 📄🇫🇷⚖️ 
# Legal & Ethical Notice — DIABOLIC FRANCE

**Notice légale et éthique détaillée**

> **Version** : 1.0
> **Projet** : DIABOLIC FRANCE v3.0
> **Auteur** : Condor2026 · SpectrumSecurity
> **Licence** : GPL-3.0-or-later
> **Dernière mise à jour** : 2026

---

## Préambule

Ce document complète [DISCLAIMER.md](DISCLAIMER.md). Il expose :

1. Le **cadre légal** dans lequel s'inscrit DIABOLIC FRANCE (France + Union européenne).
2. Les **principes éthiques OSINT** que le projet s'engage à respecter.
3. Les **règles de contribution** conformes à ces principes.
4. Les **procédures** en cas de manquement.

**En utilisant ou en contribuant à DIABOLIC FRANCE, vous acceptez l'intégralité de ce document.**

---

## 1. Cadre légal

### 1.1 Nature du projet

DIABOLIC FRANCE est un **agrégateur d'informations publiques** à des fins de **veille journalistique et de recherche OSINT défensive**. Il ne constitue **ni** un service de renseignement, **ni** un outil de police, **ni** un système de surveillance.

### 1.2 Lois françaises applicables

| Texte | Pertinence pour le projet |
|---|---|
| **Loi n° 78-17 du 6 janvier 1978** (Informatique et Libertés) | Encadre le traitement des données personnelles. Le projet **ne traite pas** de données personnelles (voir § 3). |
| **Règlement (UE) 2016/679** (RGPD) | Voir § 3. |
| **Loi n° 2004-575 du 21 juin 2004** (LCEN) | Responsabilité des hébergeurs et éditeurs de contenus en ligne. |
| **Code pénal, art. 226-1 à 226-10** | Atteinte à la vie privée, à la représentation de la personne, à la dignité. |
| **Code pénal, art. 226-16 à 226-24** | Traitement illégal de données personnelles. |
| **Code pénal, art. 322-1 à 322-17** | Destructions, dégradations, détériorations. |
| **Code pénal, art. 433-17** | Usurpation de fonction (police, gendarmerie, autorité). |
| **Code pénal, art. 421-1 à 421-8** | Actes de terrorisme (apologie, provocation). |
| **Code de la propriété intellectuelle** | Droit d'auteur, droit voisin, citation courte. |
| **Directive (UE) 2019/790** | Droit d'auteur dans le marché unique numérique (citation courte, liens). |
| **Loi n° 2018-493 du 20 juin 2018** | Protection des données personnelles (adaptation RGPD). |
| **Loi n° 2024-120 du 19 février 2024** | Sécurisation et régulation de l'espace numérique (SREN). |

### 1.3 Lois européennes applicables

| Texte | Pertinence |
|---|---|
| **RGPD (UE) 2016/679** | Voir § 3. |
| **Directive (UE) 2019/790** | Droit d'auteur et droits voisins. |
| **Directive (UE) 2016/1148** (NIS 1) / **2022/2555** (NIS 2) | Sécurité des réseaux et systèmes d'information. |
| **Règlement (UE) 2024/1689** (AI Act) | Classification des systèmes d'IA. DIABOLIC FRANCE n'est **pas** un système d'IA à haut risque au sens de l'Annexe III. |
| **Digital Services Act (UE) 2022/2065** | Responsabilité des plateformes (non applicable directement : le projet n'est pas une plateforme). |

### 1.4 Conformité déclarée

Le projet **déclare** :

- ✅ Ne pas traiter de **données à caractère personnel** au sens de l'article 4 du RGPD (voir § 3).
- ✅ Ne pas constituer un **fichier de police** ou de **renseignement** au sens des articles 230-1 et suivants du Code de procédure pénale.
- ✅ Ne pas réaliser de **profilage** ni de **surveillance individualisée**.
- ✅ Ne pas contourner de **mesure technique de protection** au sens de l'article 323-1 du Code pénal (accès frauduleux à un système de traitement automatisé de données).
- ✅ Ne pas diffuser de **contenu illégal** (apologie du terrorisme, pédocriminalité, incitation à la haine).
- ✅ Ne pas se livrer à du **spam** ou à des **pratiques commerciales trompeuses**.

---

## 2. Principes éthiques OSINT

Le projet adhère aux principes éthiques reconnus de l'**OSINT défensif** et de la **recherche ouverte** :

### 2.1 Principe de légalité

Toute donnée collectée doit provenir d'une **source publique** et l'accès doit être **légal dans la juridiction de l'utilisateur**.

### 2.2 Principe de nécessité et de proportionnalité

Seules les données **strictement nécessaires** à la finalité (veille criminelle) sont collectées. Aucune collecte « au cas où ».

### 2.3 Principe de minimisation

- **Pas de noms** dans les champs structurés.
- **Pas d'adresses** précises.
- **Pas de données** de santé, d'orientation sexuelle, d'opinions politiques ou religieuses.
- **Pas de données** concernant des mineurs (au-delà de ce que publient les sources journalistiques).

### 2.4 Principe de dignité des victimes

Les victimes ne sont **jamais** tournées en dérision, **jamais** réduites à un fait divers, **jamais** instrumentalisées. Le projet **rappelle systématiquement** de consulter la source originale et respecte le **secret de l'enquête**.

### 2.5 Principe de non-nuisance

Le projet **ne doit pas pouvoir être détourné** pour porter préjudice à une personne ou à un groupe. Toute contribution facilitant un usage malveillant est **refusée** et **retirée**.

### 2.6 Principe de transparence

Le code est **open source**, les sources sont **citées**, les algorithmes de classification sont **documentés**, les limites sont **publiques** (voir README § Limitations).

### 2.7 Principe de réversibilité

Toute personne peut demander la **suppression** de données la concernant (voir § 4).

### 2.8 Principe de respect des CGU

L'utilisateur est **seul responsable** du respect des conditions d'utilisation des sites scrapés. Le projet fournit des **garde-fous** (délais, budget, cache DNS, `--robots` optionnel) mais **ne peut garantir** la conformité dans toutes les juridictions.

### 2.9 Principe de proportionnalité technique

Le scraping est **limité** :

| Mesure | Valeur |
|---|---|
| Essais par source | 2 |
| Délai entre requêtes | 0.8-2.0 s |
| Budget par source | 90 s |
| Pages par source | 3 (par défaut, max 8) |
| Timeout | 25 s |
| User-Agents | 150+ (rotation) |
| Cache DNS | 10 min |
| `robots.txt` | Optionnel (`--robots`) |

### 2.10 Principe de non-substitution

DIABOLIC FRANCE **ne remplace pas** :

- Les **services d'urgence** (17/18/15/112).
- Les **autorités compétentes** (police, gendarmerie, justice).
- Les **sources officielles** (info.gouv.fr, CERT-FR, ANSSI).
- Les **médias d'origine** (le projet renvoie systématiquement vers l'URL source).

---

## 3. Données personnelles — position du projet

### 3.1 Ce que le projet NE collecte PAS

- ❌ Noms de famille, prénoms (au-delà de ce que publie le titre de l'article).
- ❌ Adresses postales.
- ❌ Numéros de téléphone.
- ❌ Adresses email.
- ❌ Dates de naissance.
- ❌ Numéros de sécurité sociale.
- ❌ Données bancaires.
- ❌ Données de santé.
- ❌ Données biométriques.
- ❌ Données génétiques.
- ❌ Opinions politiques, religieuses, philosophiques.
- ❌ Orientation sexuelle.
- ❌ Appartenance syndicale.
- ❌ Casier judiciaire.
- ❌ Données de géolocalisation précises (< ville).
- ❌ Adresses IP des visiteurs du panneau web (pas de logs d'accès conservés par le serveur Flask).
- ❌ Cookies de suivi, traceurs analytiques, publicités.

### 3.2 Ce que le projet stocke

| Donnée | Nature | Base légale |
|---|---|---|
| Titres d'articles | Donnée éditoriale publique | Intérêt légitime (veille journalistique) |
| Dates de publication | Donnée éditoriale publique | Intérêt légitime |
| URLs | Donnée technique publique | Intérêt légitime |
| Noms de médias | Personne morale | Intérêt légitime |
| Département/ville | Donnée administrative publique | Intérêt légitime |
| Type de crime (classifié) | Métadonnée dérivée | Intérêt légitime |
| Score de confiance | Métadonnée dérivée | Intérêt légitime |

**Aucune de ces données ne constitue une donnée à caractère personnel** au sens de l'article 4 du RGPD, sauf si le **titre de l'article** contient lui-même un nom — ce qui relève de la **responsabilité du média d'origine**, pas du projet.

### 3.3 Base légale (RGPD art. 6)

Le traitement éventuel repose sur :

- **L'intérêt légitime** (art. 6.1.f) : veille journalistique, information du public.
- **La mission d'intérêt public** (art. 6.1.e) : information sur la criminalité.

### 3.4 Durée de conservation

- Les données sont conservées **tant que le fichier `diabolic_france.json` existe**.
- L'utilisateur peut **supprimer** ce fichier à tout moment.
- Le projet **ne pratique pas** de rétention automatique au-delà de ce que l'utilisateur stocke.

### 3.5 Droits des personnes (RGPD art. 15-22)

Toute personne estimant que des données la concernant apparaissent à tort peut exercer ses droits :

- **Droit d'accès** (art. 15)
- **Droit de rectification** (art. 16)
- **Droit à l'effacement** (art. 17)
- **Droit à la limitation** (art. 18)
- **Droit d'opposition** (art. 21)

**Contact** : 📧 **spectrumsecurity@proton.me**

**Délai de réponse** : 30 jours (conforme à l'art. 12.3 du RGPD).

### 3.6 Autorité de contrôle

En cas de désaccord persistant, vous pouvez saisir la **CNIL** :

👉 [www.cnil.fr/fr/plaintes](https://www.cnil.fr/fr/plaintes)

---

## 4. Procédure de demande de suppression

Toute personne peut demander la suppression d'une fiche la concernant :

1. **Envoyer un email** à spectrumsecurity@proton.me avec :
   - L'**URL exacte** de la fiche (ou l'identifiant `id` de l'événement).
   - Une **preuve d'identité** (pièce d'identité, ou justification légitime).
   - Le **motif** de la demande.
2. **Accusé de réception** sous 72 h ouvrées.
3. **Vérification** de la demande par le mainteneur.
4. **Suppression** de la fiche dans les 30 jours (conforme RGPD).
5. **Notification** de la suppression.

**Cas d'urgence** (danger immédiat pour la personne) : la suppression est traitée **sous 24 h**.

---

## 5. Règles de contribution

Toute contribution (code, source, documentation, issue, pull request) doit respecter :

### 5.1 Règles techniques

- **Code lisible**, commenté, testé.
- **Pas de dépendances** non maintenues ou non open source.
- **Pas de secrets** (clés API, tokens, mots de passe) dans le code.
- **Pas de `eval`, `exec`, `pickle.loads`** sur des données non fiables.
- **Pas de requêtes HTTP sans timeout**.
- **Pas de scraping** de sites privés, authentifiés, ou derrière paywall contourné.
- **Pas d'ajout** de sources sans vérifier leur **légalité** et leur **éthique**.

### 5.2 Règles éthiques

- **Pas de code** facilitant la surveillance d'individus, le doxxing, le harcèlement, la discrimination.
- **Pas de code** contournant les protections techniques des sources (captcha, paywall, robots.txt si activé).
- **Pas de code** collectant des données personnelles au-delà de ce que publient les sources.
- **Pas de contenu** violent, gore, pornographique, illégal, ou apologie de crimes.
- **Pas de sources** d'extrême droite, complotistes, ou non professionnelles reconnues.
- **Pas de sources** nécessitant une authentification frauduleuse.

### 5.3 Règles de documentation

- **Toute nouvelle fonctionnalité** doit être documentée (README, CHANGELOG).
- **Toute nouvelle source** doit être justifiée (nom, URL, focus, cadre légal).
- **Tout nouveau type de crime** doit être documenté avec ses mots-clés.
- **Tout nouveau champ** dans le schéma JSON doit être documenté.

### 5.4 Règles de sécurité

- **Aucune vulnérabilité** connue ne doit être introduite.
- **Toute dépendance** doit être à jour.
- **Tout code** doit passer un scan statique (ruff, mypy).
- **Aucun secret** ne doit être commité (voir `.gitignore`).
- **Toute faille** découverte doit être signalée à spectrumsecurity@proton.me (voir § 7).

### 5.5 Sanctions

Toute contribution contraire à ces règles sera **refusée** et pourra entraîner :

1. **Avertissement** écrit.
2. **Bannissement temporaire** (1 à 30 jours).
3. **Bannissement permanent** du dépôt et de tous les espaces associés.
4. **Signalement** aux autorités compétentes en cas d'infraction pénale.

Voir [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) pour le détail du processus.

---

## 6. Signalement de contenu problématique

Si vous constatez qu'une fiche, une source, ou une contribution contient un contenu **illégal**, **choquant**, **diffamatoire**, ou **contraire à l'éthique du projet** :

📧 **spectrumsecurity@proton.me**

Merci d'inclure :

- L'**URL** ou l'**identifiant** concerné.
- La **nature** du problème (illégal, éthique, erreur factuelle, etc.).
- La **date** de constatation.
- Tout **élément** susceptible d'aider à la vérification.

**Engagement** : traitement sous 72 h ouvrées.

---

## 7. Signalement de vulnérabilité de sécurité

DIABOLIC FRANCE prend la sécurité au sérieux.

**Pour signaler une vulnérabilité** (XSS, injection, SSRF, path traversal, RCE, dépendance compromise, etc.) :

📧 **spectrumsecurity@proton.me**

**Ne pas** ouvrir d'issue publique pour une vulnérabilité de sécurité.

**Engagement** :

- **Accusé de réception** sous 72 h ouvrées.
- **Analyse** sous 7 jours ouvrés.
- **Correctif** sous 30 jours (selon gravité).
- **Publication coordonnée** après correctif (délai raisonnable).
- **Crédit** au rapporteur (sauf si anonymat demandé).

**Portée** :

- Code source du projet.
- Panneau web (localhost par défaut, mais également en `--host 0.0.0.0`).
- API REST.
- Dépendances.

**Hors portée** :

- Services tiers (Leaflet, Chart.js, vis-network).
- Sites scrapés.
- Infrastructure de l'hébergeur.

---

## 8. Sources autorisées et interdites

### 8.1 Sources autorisées

- Médias **professionnels** reconnus (presse nationale, régionale, locale).
- Sources **officielles** (CERT-FR, ANSSI, Cybermalveillance, Intérieur, Gendarmerie, Police, Préfecture, info.gouv.fr).
- Blogs **spécialisés reconnus** (ZATAZ, LeMagIT, Numerama, Next.ink, etc.).
- Flux **RSS** publics.

### 8.2 Sources interdites

- ❌ Sites nécessitant une **authentification** (paywall, login).
- ❌ Sites **illégaux** (vente de drogues, armes, données volées).
- ❌ Sites **extrémistes** (propagande terroriste, incitation à la haine).
- ❌ Sites **complotistes** non professionnels.
- ❌ Sites **personnels** (blogs individuels non vérifiés).
- ❌ Sites **pornographiques**.
- ❌ Sites **de doxxing** ou de **vengeance**.
- ❌ Sites **de fuite de données** (breach forums).
- ❌ Sites **de scraping massif** d'autres outils.

### 8.3 Vérification d'une nouvelle source

Toute nouvelle source proposée doit :

1. Être **publique** et accessible sans authentification.
2. Être **reconnue** dans sa catégorie.
3. Avoir une **URL stable** (ou auto-discovery fonctionnel).
4. Respecter les **CGU** (ou être ajoutée en connaissance de cause).
5. Ne pas **contourner** de protection technique.
6. Ne pas **collecter** de données personnelles au-delà de ce que publie l'article.

---

## 9. Utilisation de l'IA et de l'automatisation

DIABOLIC FRANCE utilise :

- **Un classifieur par expressions régulières** (pas d'IA générative, pas de LLM).
- **Des indicateurs statistiques** (RSI, SMA, Bollinger, z-score, Holt).
- **Aucun modèle d'apprentissage automatique** entraîné sur des données personnelles.

**Conformité AI Act (UE) 2024/1689** :

- Le projet **n'est pas** un système d'IA à haut risque (Annexe III).
- Le projet **n'est pas** un système de notation sociale.
- Le projet **n'est pas** un système de police prédictive individualisée.
- Le projet **n'est pas** un système de reconnaissance biométrique.

---

## 10. Contribution et fork

### 10.1 Fork

Vous êtes **libre** de forker le projet (GPL-3.0-or-later). En cas de fork :

- **Conservez** la licence GPL-3.0-or-later.
- **Conservez** les mentions de copyright.
- **Conservez** ce notice légale et éthique.
- **N'utilisez pas** le nom « DIABOLIC FRANCE » sans autorisation écrite (marque non déposée, mais usage de fait).
- **N'utilisez pas** le logo sans autorisation écrite.

### 10.2 Contribution au projet principal

En soumettant une contribution (pull request, patch, code, documentation) :

- Vous **cédez** vos droits sur la contribution au projet (licence GPL-3.0-or-later).
- Vous **certifiez** que votre contribution est **originale** ou **libre de droits**.
- Vous **certifiez** que votre contribution **respecte** ce notice et le [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Voir le fichier [CONTRIBUTING.md](CONTRIBUTING.md) (si présent) pour les détails.

---

## 11. Contact

| Objet | Contact |
|---|---|
| **Questions générales** | [@Condor2026](https://github.com/Condor2026) |
| **Sécurité** | spectrumsecurity@proton.me |
| **RGPD / suppression** | spectrumsecurity@proton.me |
| **Code de conduite** | Voir [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| **Signalement contenu** | spectrumsecurity@proton.me |

---

## 12. Documents liés

- [README.md](README.md) — Documentation principale
- [DISCLAIMER.md](DISCLAIMER.md) — Avertissement
- [LICENSE](LICENSE) — Licence GPL-3.0-or-later
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Code de conduite
- [CHANGELOG.md](CHANGELOG.md) — Journal des modifications
- [ROADMAP.md](ROADMAP.md) — Feuille de route

---

## 13. Modifications

Ce notice peut être **modifié à tout moment**, sans préavis. La version en vigueur est **toujours celle publiée** dans le dépôt officiel :

👉 **[github.com/Condor2026/diabolic_france/blob/main/LEGAL_ETHICAL_NOTICE.md](https://github.com/Condor2026/diabolic_france/blob/main/LEGAL_ETHICAL_NOTICE.md)**

---

> **🔪 DIABOLIC FRANCE** — *Vigilamus pro tuendo*
>
> **Surveiller pour protéger, jamais pour nuire.**
>
> En utilisant ou en contribuant à DIABOLIC FRANCE, vous reconnaissez avoir lu, compris et accepté l'intégralité de ce notice.

### 2. RESPONSABILIDAD DEL USUARIO

El usuario es el **ÚNICO responsable** del uso que dé a esta herramienta.

**Usos PROHIBIDOS:**

| Categoría | Ejemplos |
|-----------|----------|
| **Discriminación** | Estigmatizar barrios o colectivos por actividad criminal |
| **Acoso** | Hostigar a presuntos delincuentes sin base judicial |
| **Estigmatización** | Señalar a comunidades vulnerables como criminales |
| **Violación de privacidad** | Intentar identificar individuos a partir de datos agregados |
| **Justicia por mano propia** | Usar la herramienta para "cazar" delincuentes |

⚠️ **Nota importante:**
Los datos provienen de fuentes públicas (periódicos y comunicados oficiales). El usuario debe verificar la información antes de tomar cualquier decisión basada en ella.

---

### 3. PROTECCIÓN DE DATOS

**DIABOLIC FRANCE NO almacena ni procesa datos personales** (nombres, direcciones, documentos, IPs, cookies, etc.).

**¿Qué se guarda?** (solo en local, en tu máquina)

| Campo | Descripción |
|-------|-------------|
| 📰 **Título del incidente** | Texto público de la noticia |
| 📅 **Fecha de publicación** | Cuándo se publicó |
| 🏴 **Departamento** | Región geográfica (ej: Paris, Bouches-du-Rhône) |
| 🔪 **Tipo de crimen** | Clasificación automática (drogue, gangs, etc.) |
| 📰 **Fuente** | Nombre del periódico o fuente oficial |

**Lo que NO se guarda:**

| Prohibido | Explicación |
|-----------|-------------|
| ❌ Nombres de personas | No se extraen nombres propios |
| ❌ Direcciones | No se guardan direcciones específicas |
| ❌ Teléfonos | No se almacenan números |
| ❌ IPs | No se registran direcciones IP |
| ❌ Cookies | No se utilizan cookies |
| ❌ Geolocalización precisa | Solo nivel departamental |
| ❌ Información identificable | Cero PII (Personally Identifiable Information) |

**📜 Legislación aplicable (Francia / UE):**

| Normativa | Cumplimiento |
|-----------|--------------|
| **RGPD (UE) 2016/679** | ✅ Fuera de ámbito (no trata datos personales) |
| **Loi Informatique et Libertés (1978)** | ✅ No aplica (datos anónimos agregados) |
| **CNIL** | ✅ Sin necesidad de declaración (uso local) |

Esta herramienta está **FUERA del ámbito de aplicación del RGPD** porque:
- No trata datos personales
- El usuario ejecuta el software localmente
- No hay transferencia a servidores externos
- No hay perfilación automática de individuos

---

### 4. PROPIEDAD INTELECTUAL

**Contenido de noticias:**
Las noticias escaneadas pertenecen a sus respectivos medios de comunicación:

| Fuente | Tipo |
|--------|------|
| Le Monde, Le Figaro, Libération | Presse nationale |
| 20 Minutes, France Info, Le Parisien | Médias grand public |
| Police Nationale, Gendarmerie | Sources officielles |
| (y el resto de fuentes) | Divers |

**DIABOLIC FRANCE** solo extrae titulares y metadatos públicos, sin republicar contenidos completos ni vulnerar derechos de autor.

**Código fuente:**
El código de DIABOLIC FRANCE es open source bajo licencia **GPLv3**.

```
Copyright (C) 2026 Condor2026 / SpectrumSecurity

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

**Reutilización del código:**
Puedes reutilizar, modificar y distribuir el código **SIEMPRE QUE**:

| Requisito | Estado |
|-----------|--------|
| ✅ Mantengas la misma licencia (GPLv3) | Obligatorio |
| ✅ Cites la fuente original (Condor2026 / SpectrumSecurity) | Obligatorio |
| ✅ Mantengas el espíritu ético de análisis criminal | Obligatorio |
| ❌ No lo uses para fines ilegales o discriminatorios | Prohibido |

---

### 5. EXCLUSIÓN DE RESPONSABILIDAD

El desarrollador y los colaboradores **NO son responsables** por el uso indebido por parte de terceros.

La herramienta se proporciona **"TAL CUAL" (AS-IS)**, sin garantías de:

| Sin garantía | Explicación |
|--------------|-------------|
| ⚠️ Funcionamiento continuo | Puede haber errores temporales |
| ⚠️ Ausencia de bugs | Es software en evolución |
| ⚠️ Precisión absoluta | Los datos dependen de fuentes externas |

**Responsabilidad del usuario:**
Cualquier modificación dañina del código (ej: recolección de datos personales, vigilancia ilegal, discriminación, etc.) es responsabilidad **EXCLUSIVA** de quien la realiza, no del desarrollador original.

---

### 6. FILOSOFÍA DEL PROYECTO

> *"L'union fait la force"* - Devise française
> *"Un gran poder conlleva una gran responsabilidad"* - Spider-Man

**DIABOLIC FRANCE** nace con los siguientes principios:

| Principio | Descripción |
|-----------|-------------|
| 🔍 **Transparencia** | Código abierto, sin puertas traseras |
| 🛡️ **Seguridad ciudadana** | Ayudar a prevenir y entender la criminalidad |
| ⚖️ **Respeto a la ley** | Cumplimiento de normativas francesas y europeas |
| 🧠 **Ética inquebrantable** | Sin vigilancia masiva, sin estigmatización |
| 📊 **Datos abiertos** | Información pública para el bien común |
| 🌍 **Multilingüismo** | 3 idiomas (ES/FR/IT) para máxima accesibilidad |

**Creemos en:**

| Valor | Aplicación |
|-------|------------|
| Comunidades más seguras | A través de la información accesible |
| Periodismo de investigación | Como pilar de la democracia |
| Transparencia | Como antídoto contra la desinformación |
| Código abierto | Como herramienta de empoderamiento ciudadano |

**No toleramos:**

| Intolerable | Ejemplo |
|-------------|---------|
| Discriminación | Estigmatizar barrios o comunidades |
| Perfilación racial | Asociar criminalidad con origen étnico |
| Vigilancia no consensuada | Monitorización de personas vulnerables |
| Uso político partidista | Manipulación de datos para fines electorales |

---

### 7. ACEPTACIÓN DE TÉRMINOS

Si no estás de acuerdo con estos principios, por favor **NO utilices esta herramienta**.

El uso de **DIABOLIC FRANCE** implica la aceptación total de este aviso legal y ético.

---

### 8. CONTACTO

Para reportar usos indebidos, vulnerabilidades éticas o preguntas sobre este documento:

| Contacto | Información |
|----------|-------------|
| **GitHub** | @Condor2026 |
| **Proyecto** | DIABOLIC FRANCE |
| **Email** | spectrumsecurity@proton.me |

---

### 9. ACTUALIZACIONES

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Julio 2026 | Documento inicial adaptado para DIABOLIC FRANCE (Francia) |

---

## 🇫🇷 Français (Résumé)

### 1. OBJECTIF DE L'OUTIL

**DIABOLIC FRANCE** est un outil OSINT open source conçu pour analyser les actualités publiques des journaux français et sources officielles, et détecter les **activités criminelles** (drogue, violence des gangs, meurtre, agression, vol, crime organisé, opération police, arme, terrorisme).

### 2. RESPONSABILITÉ DE L'UTILISATEUR

L'utilisateur est le **SEUL responsable** de l'utilisation qu'il fait de cet outil.

**Utilisations INTERDITES :**
- Discrimination par code postal ou situation sociale
- Stigmatisation des personnes vulnérables
- Justice personnelle

### 3. PROTECTION DES DONNÉES

**DIABOLIC FRANCE ne stocke ni ne traite aucune donnée personnelle.**

**Ce qui est stocké (localement) :**
- Titre de l'actualité
- Date de publication
- Département
- Type de crime
- Source

**Ce qui N'EST PAS stocké :**
- Noms, adresses, téléphones
- Adresses IP, cookies
- Géolocalisation précise

### 4. PROPRIÉTÉ INTELLECTUELLE

Code source sous licence **GPLv3**. Les actualités appartiennent à leurs médias respectifs.

### 5. PHILOSOPHIE

> *"L'union fait la force"* - Devise française

**Transparence · Sécurité · Respect · Éthique**

---

## 🇮🇹 Italiano (Riepilogo)

### 1. SCOPO DELLO STRUMENTO

**DIABOLIC FRANCE** è uno strumento OSINT open source progettato per analizzare notizie pubbliche di giornali francesi e fonti ufficiali, e rilevare **attività criminali** (droga, violenza gang, omicidio, aggressione, furto, crimine organizzato, operazione polizia, arma, terrorismo).

### 2. RESPONSABILITÀ DELL'UTENTE

L'utente è l'**UNICO responsabile** dell'uso che fa di questo strumento.

**Usi VIETATI :**
- Discriminazione per codice postale o situazione sociale
- Stigmatizzazione di persone vulnerabili
- Giustizia personale

### 3. PROTEZIONE DEI DATI

**DIABOLIC FRANCE non memorizza né elabora dati personali.**

**Cosa viene memorizzato (localmente) :**
- Titolo della notizia
- Data di pubblicazione
- Dipartimento
- Tipo di crimine
- Fonte

**Cosa NON viene memorizzato :**
- Nomi, indirizzi, telefoni
- Indirizzi IP, cookie
- Geolocalizzazione precisa

### 4. PROPRIETÀ INTELLETTUALE

Codice sorgente sotto licenza **GPLv3**. Le notizie appartengono ai rispettivi media.

### 5. FILOSOFIA

> *"L'unione fa la forza"* - Motto francese

**Trasparenza · Sicurezza · Rispetto · Etica**

---

## 📌 CIERRE / CLÔTURE / CHIUSURA

---

<p align="center">
  <img src="https://img.shields.io/badge/Legal_Notice-v1.0-red?style=flat-square">
  <img src="https://img.shields.io/badge/GDPR-Compliant-brightgreen?style=flat-square">
  <img src="https://img.shields.io/badge/CNIL-Exempted-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Langues-3-orange?style=flat-square">
</p>

<p align="center">
  <b>🛡️ "L'union fait la force" - Devise française</b><br>
  <i>Éthique · Transparence · Respect · Sécurité</i><br>
  <i>Utilisez cet outil avec responsabilité et respect des droits humains.</i>
</p>
