# IPA Tracer — entraînement à la transcription phonétique (anglais GA et SSBE)

**IPA Tracer** est une application web légère et interactive destinée aux étudiants en phonétique anglaise.  
Elle permet de s’entraîner à **tracer les symboles de l’Alphabet Phonétique International (API)**, directement depuis un navigateur, en suivant des pochoirs vectoriels générés automatiquement à partir de la police **Andika (SIL)**.

👉 Démo en ligne : [https://lcontrerasroa.github.io/ipatracer/](https://lcontrerasroa.github.io/ipatracer/)

---

## ✨ Fonctionnalités

- 🖊️ **Traçage libre** sur canevas (compatible mobile et tablette)  
- 🪞 **Pochoirs SVG** de chaque symbole IPA (Andika, échelle uniforme, contours nets)  
- 🎨 **Interface claire et pastel**, pensée pour la lisibilité et le confort visuel  
- 📏 Réglages en temps réel :
  - Épaisseur du trait  
  - Étirement vertical (pour corriger les proportions de certains glyphes)  
  - Seuil de détection du “noir” pour l’évaluation  
- 📈 **Évaluation automatique** de la justesse du tracé (Dice coefficient)  
- ⚙️ Compatible avec tous les navigateurs modernes, aucune installation requise  

---

## 🧩 Structure du dépôt

ipatracer/
├── docs/
│ ├── index.html ← application web (chargée par GitHub Pages)
│ ├── symbols.json ← liste des symboles et chemins vers les SVG
│ ├── svgs/ ← pochoirs SVG exportés (police Andika)
│ └── fonts/ ← (optionnel) polices locales .woff2 si hébergées
├── README.md ← you are here
└── ipatrace.py ←script python crée sur Google Colab pour la création des pochoirs


> Le site est servi directement depuis le dossier `docs/` grâce à GitHub Pages.

---

## 🧱 Technologies

- **Frontend :** HTML5, CSS3, JavaScript vanilla  
- **Canvas API** (dessin et comparaison des tracés)  
- **SVG vectoriels** (pochoirs générés à partir des polices)  
- **Andika (SIL)** — police sans sérif claire et pédagogique  
- **GitHub Pages** pour le déploiement statique

---

## 🧮 Génération des pochoirs (SVG)

Les SVG ont été exportés automatiquement depuis la police **Andika** à l’aide d’un notebook Python (Colab) utilisant :

- `fonttools` — extraction des contours vectoriels  
- `svgPathPen` — conversion des glyphes en chemins SVG  
- un script d’export qui :
  - ajuste l’échelle **uniformément** (pour éviter les glyphes “aplatis”)  
  - ajoute un fond blanc et un contour noir épais  
  - centre chaque glyphe dans un carré de 1000×1000 unités  

👉 Le notebook complet pour régénérer les pochoirs est fourni dans le dossier `/notebooks/` *(ou disponible sur demande)*.

---

## 🤖 Assistance IA

Le développement du code HTML, CSS et JavaScript, ainsi que les scripts d’export SVG et les optimisations d’interface, ont été réalisés **avec l’aide de ChatGPT (GPT-5, OpenAI)**.  
Cette collaboration a permis d’automatiser la génération des pochoirs, d’optimiser le rendu graphique et de rendre l’application utilisable directement dans un navigateur, sans dépendances externes.

> L’ensemble du code reste relu, testé et ajusté par **Leonardo Contreras Roa** pour garantir la cohérence pédagogique et linguistique du projet.

---

## 👩‍🏫 Public visé

- Étudiants en linguistique, phonétique et phonologie anglaises  
- Enseignants souhaitant proposer des exercices interactifs  
- Toute personne curieuse de visualiser et reproduire les symboles de l’API

---

## 🪶 Auteur

**Leonardo Contreras Roa**  
Maître de conférences en linguistique et phonétique anglaise  
Université de Picardie Jules Verne (Amiens, France)  
📍 [leonardocontrerasroa.com](https://leonardocontrerasroa.com)

---

## 🪪 Licence

Le code de l’application est distribué sous licence **MIT**.  
Les polices SIL (Andika, Doulos SIL, Charis SIL…) sont sous licence **SIL Open Font License (OFL)**.

> © 2025 — Projet académique sans visée commerciale.  
> Les symboles de l’Alphabet Phonétique International (IPA) sont propriété de l’International Phonetic Association.


