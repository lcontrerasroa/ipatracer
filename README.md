# IPA Tracer — entraînement à la transcription phonétique (anglais GA et SSBE)

**IPA Tracer** est une application web légère et interactive destinée aux étudiants en phonétique anglaise.  
Elle permet de s’entraîner à **tracer les symboles de l’Alphabet Phonétique International (API)**, directement depuis un navigateur, en suivant des pochoirs vectoriels générés automatiquement à partir de la police **Andika (SIL)**.

👉 Démo en ligne : [https://lcontrerasroa.github.io/ipatracer/](https://lcontrerasroa.github.io/ipatracer/)


## Fonctionnalités

- **Traçage libre** sur canevas (compatible mobile et tablette)  
- **Pochoirs SVG** de chaque symbole IPA (Andika, échelle uniforme, contours nets)  
- **Interface claire et pastel**, pensée pour la lisibilité et le confort visuel  
- çéglages en temps réel :
  - Épaisseur du trait  
  - Étirement vertical (pour corriger les proportions de certains glyphes)  
  - Seuil de détection du “noir” pour l’évaluation  
- **Évaluation automatique** de la justesse du tracé (Dice coefficient)[^1]
- Compatible avec tous les navigateurs modernes, aucune installation requise  


## Objectifs pédagogiques

- Aider les étudiants en linguistique ou phonétique à mémoriser la forme des symboles IPA.
- Développer la coordination graphomotrice et la reconnaissance visuelle des caractères.
- Favoriser un apprentissage ludique et interactif, proche des applications de traçage de kanji.


## Polices utilisées

| Fonte | Auteurs / Institution | Licence | Lien source |
|:------|:----------------------|:---------|:-------------|
| **Andika** | SIL International | SIL Open Font License (OFL 1.1) | [software.sil.org/andika](https://software.sil.org/andika) |
| **M PLUS 1** | Coz Coz (Japan) | SIL Open Font License (OFL 1.1) | [github.com/coz-m/MPLUS_FONTS](https://github.com/coz-m/MPLUS_FONTS) |
| **Arimo** | Google / Steve Matteson | Apache License 2.0 | [fonts.google.com/specimen/Arimo](https://fonts.google.com/specimen/Arimo) |
| **DejaVu Sans** | DejaVu Fonts project | Bitstream Vera License | [dejavu-fonts.github.io](https://dejavu-fonts.github.io) |
| **CMU Sans Serif** | Carnegie Mellon University | SIL Open Font License (OFL 1.1) | [github.com/CMUTypeDesignResources/cm-unicode](https://github.com/CMUTypeDesignResources/cm-unicode) |

## 🧩 Structure du dépôt
```
ipatracer/
├── docs/
│ ├── index.html ← application web (chargée par GitHub Pages)
│ ├── symbols.json ← liste des symboles et chemins vers les SVG
│ ├── svgs/ ← pochoirs SVG exportés 
│ └── fonts/ ← (optionnel) polices locales .woff2 si hébergées
├── README.md ← you are here
└── ipatrace.py ←script python crée sur Google Colab pour la création des pochoirs
```

> Le site est servi directement depuis le dossier `docs/` grâce à GitHub Pages.


## Technologies

- **Frontend :** HTML5, CSS3, JavaScript vanilla  
- **Canvas API** (dessin et comparaison des tracés)  
- **SVG vectoriels** (pochoirs générés à partir des polices)  
- **GitHub Pages** pour le déploiement statique


## Génération des pochoirs (SVG)

Les SVG ont été exportés automatiquement depuis la police **Andika** à l’aide d’un notebook Python (Colab) utilisant :

- `fonttools` — extraction des contours vectoriels  
- `svgPathPen` — conversion des glyphes en chemins SVG  
- un script d’export qui :
  - ajuste l’échelle **uniformément** (pour éviter les glyphes “aplatis”)  
  - ajoute un fond blanc et un contour noir épais  
  - centre chaque glyphe dans un carré de 1000×1000 unités  

👉 Le script python complet pour régénérer les pochoirs est fourni dans le dossier `/notebooks/` *(ou disponible sur demande)*.


## Assistance IA

Le développement du code HTML, CSS et JavaScript, ainsi que les scripts d’export SVG et les optimisations d’interface, ont été réalisés **avec l’aide de ChatGPT (GPT-5, OpenAI)**.  
Cette collaboration a permis d’automatiser la génération des pochoirs, d’optimiser le rendu graphique et de rendre l’application utilisable directement dans un navigateur, sans dépendances externes.

> L’ensemble du code reste conçu, relu, testé et ajusté par **Leonardo Contreras Roa** pour garantir la cohérence pédagogique et linguistique du projet.


## Public visé

- Étudiants en linguistique, phonétique et phonologie anglaises  
- Enseignants souhaitant proposer des exercices interactifs  
- Toute personne curieuse de visualiser et reproduire les symboles de l’API


## Développement conjoint :

Leonardo Contreras Roa (Université de Picardie Jules Verne) — conception pédagogique et scripts de génération.

ChatGPT (GPT-5) — assistance technique (interface, génération SVG, scoring et intégration web).

## Licence

Le code de l’application est distribué sous licence **MIT**.  
Les polices SIL (Andika, Doulos SIL, Charis SIL…) sont sous licence **SIL Open Font License (OFL)**.

> © 2025 — Projet académique sans visée commerciale.  
> Les symboles de l’Alphabet Phonétique International (IPA) sont propriété de l’International Phonetic Association.

## Comment citer cet outil

Format APA (7ᵉ édition) :

Contreras Roa, L. (2025). IPA Tracer [Application web].
Université de Picardie Jules Verne. Disponible sur https://lcontrerasroa.github.io/ipatracer/

Exemple d’usage dans un mémoire ou article :

Les exercices de traçage ont été réalisés à l’aide de IPA Tracer (Contreras Roa, 2025), une application web open-source développée à partir de fontes IPA libres.

[^1]: Dice, L. R. (1945). *Measures of the amount of ecologic association between species.* *Ecology, 26*(3), 297–302. https://doi.org/10.2307/1932409
