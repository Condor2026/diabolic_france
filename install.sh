#!/usr/bin/env bash
# =============================================================================
# DIABOLIC FRANCE v3.0 — install.sh
# By Condor2026 · SpectrumSecurity · GPL-3.0-or-later
# =============================================================================
# Installe les dépendances et prépare l'environnement virtuel.
# Ne requiert PAS sudo. Ne modifie PAS le système global.
#
# Usage :
#   ./install.sh              # installation standard (venv)
#   ./install.sh --no-venv    # installation dans l'environnement Python courant
#   ./install.sh --with-mpl   # + matplotlib + networkx (graphiques PNG)
#   ./install.sh --docker     # imprime la commande Docker (pas d'install locale)
#   ./install.sh --help
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Couleurs (désactivées si pas de TTY)
# -----------------------------------------------------------------------------
if [ -t 1 ]; then
  RED=$'\033[91m'; GREEN=$'\033[92m'; YELLOW=$'\033[93m'
  CYAN=$'\033[96m'; GRAY=$'\033[90m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
  RED=""; GREEN=""; YELLOW=""; CYAN=""; GRAY=""; BOLD=""; RESET=""
fi

# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
REQUIRED_PY_MIN="3.8"
RECOMMENDED_PY="3.11"
PYTHON_BIN=""
USE_VENV=1
WITH_MPL=0
MODE="install"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
info()    { printf '%s[*]%s %s\n' "$CYAN" "$RESET" "$*"; }
ok()      { printf '%s[✓]%s %s\n' "$GREEN" "$RESET" "$*"; }
warn()    { printf '%s[!]%s %s\n' "$YELLOW" "$RESET" "$*"; }
err()     { printf '%s[✗]%s %s\n' "$RED" "$RESET" "$*" >&2; }
die()     { err "$*"; exit 1; }

usage() {
  cat <<EOF
${BOLD}DIABOLIC FRANCE v3.0 — install.sh${RESET}

${BOLD}USAGE${RESET}
  ./install.sh [options]

${BOLD}OPTIONS${RESET}
  --no-venv     Installer dans l'environnement Python courant (non recommandé)
  --with-mpl    Installer aussi matplotlib + networkx (graphiques PNG)
  --docker      Afficher la commande Docker au lieu d'installer localement
  --help, -h    Afficher cette aide

${BOLD}SANS SUDO${RESET}
  Ce script ne requiert ni sudo ni accès root. Il crée un venv local (${VENV_DIR}/).
  Les dépendances système (build-essential, libssl-dev…) ne sont PAS installées ;
  si une compilation échoue, installez-les manuellement via votre gestionnaire.

${BOLD}EXEMPLES${RESET}
  ./install.sh
  ./install.sh --with-mpl
  ./install.sh --no-venv
  ./install.sh --docker
EOF
}

# -----------------------------------------------------------------------------
# Parsing args
# -----------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --no-venv)   USE_VENV=0 ;;
    --with-mpl)  WITH_MPL=1 ;;
    --docker)    MODE="docker" ;;
    -h|--help)   usage; exit 0 ;;
    *)           die "Option inconnue : $arg (essayez --help)" ;;
  esac
done

# -----------------------------------------------------------------------------
# Bannière
# -----------------------------------------------------------------------------
printf '\n%s\n' "${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
printf '%s\n'   "${CYAN}║${RESET}  ${BOLD}🔪 DIABOLIC FRANCE v3.0 — Installation${RESET}                    ${CYAN}║${RESET}"
printf '%s\n'   "${CYAN}║${RESET}  ${GRAY}By Condor2026 · SpectrumSecurity · GPL-3.0-or-later${RESET}       ${CYAN}║${RESET}"
printf '%s\n\n' "${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"

# -----------------------------------------------------------------------------
# Mode Docker (aucune installation locale)
# -----------------------------------------------------------------------------
if [ "$MODE" = "docker" ]; then
  info "Mode Docker sélectionné — aucune installation locale."
  cat <<EOF

${BOLD}Option 1 : docker compose (recommandé)${RESET}
  docker compose up -d
  docker compose logs -f

${BOLD}Option 2 : docker run${RESET}
  docker build -t diabolic-france:3.0 .
  docker run -d --name diabolic-france \\
    -p 127.0.0.1:5016:5016 \\
    -e DF_LANG=fr -e DF_SENS=equilibrado \\
    -v diabolic-france-data:/app/data \\
    -v diabolic-france-logs:/app/logs \\
    --restart unless-stopped \\
    diabolic-france:3.0

${BOLD}Panneau web${RESET} : http://localhost:5016

${GRAY}Consultez DISCLAIMER.md et LEGAL_ETHICAL_NOTICE.md avant tout déploiement public.${RESET}
EOF
  exit 0
fi

# -----------------------------------------------------------------------------
# Détection OS
# -----------------------------------------------------------------------------
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then OS="windows"
fi
info "Système détecté : ${BOLD}${OS}${RESET}"

# -----------------------------------------------------------------------------
# Détection Python
# -----------------------------------------------------------------------------
find_python() {
  for candidate in python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
    if command -v "$candidate" &>/dev/null; then
      if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' &>/dev/null; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

if ! PYTHON_BIN="$(find_python)"; then
  err "Aucun Python >= ${REQUIRED_PY_MIN} trouvé."
  cat >&2 <<EOF

${BOLD}Installation de Python${RESET}
  Ubuntu/Debian : sudo apt update && sudo apt install -y python3 python3-venv python3-pip
  Fedora        : sudo dnf install -y python3 python3-pip
  Arch          : sudo pacman -S --noconfirm python python-pip
  macOS         : brew install python@3.11
  Windows       : https://www.python.org/downloads/

Après installation, relancez : ./install.sh
EOF
  exit 1
fi

PY_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
ok "Python trouvé : ${PYTHON_BIN} (${PY_VERSION})"

# Vérification de la version recommandée (avertissement seulement)
if ! "$PYTHON_BIN" -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" &>/dev/null; then
  warn "Python ${RECOMMENDED_PY}+ recommandé (vous avez ${PY_VERSION}). Le projet fonctionne dès 3.8."
fi

# -----------------------------------------------------------------------------
# Vérification des fichiers du projet
# -----------------------------------------------------------------------------
if [ ! -f "diabolic_france.py" ]; then
  die "diabolic_france.py introuvable. Êtes-vous dans le bon dossier ? (${SCRIPT_DIR})"
fi
ok "Fichier diabolic_france.py détecté"

# requirements.txt : généré s'il est absent (cohérent avec le code v3)
if [ ! -f "requirements.txt" ]; then
  warn "requirements.txt absent — génération automatique minimale"
  cat > requirements.txt <<'REQ'
flask>=3.0,<4
requests>=2.31,<3
beautifulsoup4>=4.12,<5
REQ
  ok "requirements.txt créé (dépendances minimales)"
fi

# -----------------------------------------------------------------------------
# Environnement virtuel
# -----------------------------------------------------------------------------
if [ "$USE_VENV" -eq 1 ]; then
  if [ -d "$VENV_DIR" ]; then
    info "Environnement virtuel existant détecté : ${VENV_DIR}/"
  else
    info "Création de l'environnement virtuel : ${VENV_DIR}/"
    if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
      err "Échec de la création du venv."
      cat >&2 <<EOF

${BOLD}Sur Debian/Ubuntu${RESET}, le module venv peut manquer :
  sudo apt install -y python3-venv

${BOLD}Sur Fedora${RESET} :
  sudo dnf install -y python3-virtualenv

Puis relancez : ./install.sh
EOF
      exit 1
    fi
    ok "Environnement virtuel créé"
  fi

  # Activation
  # shellcheck disable=SC1091
  if [ -f "${VENV_DIR}/bin/activate" ]; then
    source "${VENV_DIR}/bin/activate"
  elif [ -f "${VENV_DIR}/Scripts/activate" ]; then
    source "${VENV_DIR}/Scripts/activate"
  else
    die "Impossible d'activer le venv (bin/activate ou Scripts/activate introuvable)"
  fi
  PYTHON_BIN="python"
  ok "Environnement virtuel activé"
else
  warn "--no-venv : installation dans l'environnement Python courant"
  warn "Assurez-vous d'être dans un venv déjà activé ou dans un conteneur."
fi

# -----------------------------------------------------------------------------
# Mise à jour pip
# -----------------------------------------------------------------------------
info "Mise à jour de pip..."
"$PYTHON_BIN" -m pip install --upgrade pip --quiet || warn "Échec de la mise à jour de pip (on continue)"

# -----------------------------------------------------------------------------
# Installation des dépendances
# -----------------------------------------------------------------------------
info "Installation des dépendances obligatoires (flask, requests, beautifulsoup4)..."
if ! "$PYTHON_BIN" -m pip install --quiet -r requirements.txt; then
  err "Échec de l'installation des dépendances obligatoires."
  cat >&2 <<EOF

${BOLD}Pistes de résolution${RESET}
  - Vérifiez votre connexion Internet.
  - Sur Debian/Ubuntu, certaines wheels nécessitent :
      sudo apt install -y build-essential python3-dev libssl-dev libffi-dev
  - Sur macOS avec Apple Silicon, forcez l'architecture :
      arch -arm64 ./install.sh
  - Réessayez avec plus de verbosité :
      pip install -r requirements.txt -v
EOF
  exit 1
fi
ok "Dépendances obligatoires installées"

# -----------------------------------------------------------------------------
# Dépendances optionnelles (graphiques PNG)
# -----------------------------------------------------------------------------
if [ "$WITH_MPL" -eq 1 ]; then
  info "Installation des dépendances optionnelles (matplotlib, networkx)..."
  if "$PYTHON_BIN" -m pip install --quiet "matplotlib>=3.7,<4" "networkx>=3.0,<4"; then
    ok "matplotlib + networkx installés"
  else
    warn "Échec de l'installation de matplotlib/networkx (non bloquant)"
    warn "Les graphiques statiques PNG resteront indisponibles."
    warn "Installation manuelle : pip install matplotlib networkx"
  fi
else
  info "Dépendances optionnelles ignorées (utilisez --with-mpl pour les installer)"
fi

# -----------------------------------------------------------------------------
# Vérification finale — imports
# -----------------------------------------------------------------------------
info "Vérification des imports..."
if ! "$PYTHON_BIN" -c 'import flask, requests, bs4' 2>/dev/null; then
  err "Les modules Python ne se chargent pas correctement."
  "$PYTHON_BIN" -c 'import flask, requests, bs4' || true
  exit 1
fi
ok "Imports OK (flask, requests, beautifulsoup4)"

# -----------------------------------------------------------------------------
# Résumé et prochaines étapes
# -----------------------------------------------------------------------------
printf '\n%s\n' "${GREEN}══════════════════════════════════════════════════════════════${RESET}"
printf '%s\n'   "${GREEN}  ✅ Installation terminée${RESET}"
printf '%s\n\n' "${GREEN}══════════════════════════════════════════════════════════════${RESET}"

cat <<EOF
${BOLD}Prochaines étapes${RESET}

  1) Activer l'environnement (si nouveau terminal) :
       ${CYAN}source ${VENV_DIR}/bin/activate${RESET}        # Linux / macOS
       ${CYAN}${VENV_DIR}\\Scripts\\activate${RESET}          # Windows (PowerShell)

  2) Lancer le menu interactif :
       ${CYAN}python diabolic_france.py${RESET}

  3) Ou lancer directement le panneau web :
       ${CYAN}python diabolic_france.py --web${RESET}
       → ouvrir ${BOLD}http://localhost:5016${RESET}

  4) Vérifier les sources (recommandé au premier lancement) :
       menu option ${BOLD}8${RESET} ou bouton ${BOLD}🔍 Vérifier sources${RESET}

  5) Diagnostic d'une source spécifique :
       ${CYAN}python diabolic_france.py --debug-fuente "Le Monde"${RESET}

${BOLD}Options utiles${RESET}
  --lang {fr,es,en,it,de}            Langue de l'interface
  --port 5016 --host 127.0.0.1       Bind (défaut : localhost uniquement)
  --auto 30                          Scan automatique toutes les 30 min
  --sens {amplio,equilibrado,estricto} Sensibilité du filtre
  --robots                           Respecter robots.txt
  --scan {all,fd,cyber,gov}          Scan CLI puis sortie
  --pages 1-8                        Pages par source

${BOLD}Documentation${RESET}
  README.md                  Guide utilisateur complet
  CHANGELOG.md               Historique des versions
  ROADMAP.md                 Feuille de route
  DISCLAIMER.md              Avertissement légal
  LEGAL_ETHICAL_NOTICE.md    Notice légale et éthique
  CODE_OF_CONDUCT.md         Code de conduite

${GRAY}⚠️  Projet OSINT défensif. Consultez DISCLAIMER.md et LEGAL_ETHICAL_NOTICE.md
   avant tout usage. Ne collecte aucune donnée personnelle.${RESET}

${GRAY}🔪 DIABOLIC FRANCE — Vigilamus pro tuendo${RESET}
EOF
