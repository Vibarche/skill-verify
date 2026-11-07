---
name: skill-architect
description: >-
  Conçoit, audite, refactore et évalue des skills et prompts de production.
  Utiliser pour créer un nouveau SKILL.md, auditer un skill existant, structurer un system prompt,
  définir une équipe d'agents ou construire un workflow agentique robuste.
version: "1.2.0"
license: MIT
metadata:
  author: agtktID
  repo: https://github.com/agtktID/skill-verify
  updated: 2026-11-07
  tags:
    - skills
    - prompts
    - architecture
    - evals
    - security
    - system-prompt
    - agent-design
    - skillware
allowed-tools:
  - Bash
  - Read
  - Write
  - WebSearch
---

# 🏗️ Skill Architect

Skill de conception, d'audit et d'évaluation de skills, system prompts et workflows agentiques.
Produit des SKILL.md production-ready, des structures de system prompts et des batteries d'evals.

---

## ✅ When to Use

Utiliser ce skill pour :

- **Créer** un nouveau `SKILL.md` pour un skill ou une commande slash.
- **Auditer** un skill existant : cohérence du frontmatter, clarté de la description (trigger), sécurité, outils.
- **Refactorer** un system prompt ou un skill trop verbeux ou mal structuré.
- **Versionner** et documenter les changements de skills.
- **Concevoir** une équipe d'agents ou un workflow agentique multi-skills.
- **Évaluer** les should-trigger / should-not-trigger d'un skill.
- **Convertir un prompt en Skillware** : schéma typé, code déterministe, tests et données embarquées.

Ne pas utiliser pour :

- Exécuter du code ou valider des builds (utiliser `verify` ou `gauntlet-loop-dev` pour ça).
- Tâches sans besoin de conception ou d'architecture.

---

## 🧱 Cadre d'analyse : Goal / Output / Limits / Data / Evaluation

Avant de concevoir ou d'auditer un skill, extraire ces 5 éléments :

| Élément | Question clé |
|---|---|
| **Goal** | Que doit accomplir ce skill exactement ? |
| **Output** | Quel est le livrable attendu (format, structure, longueur) ? |
| **Limits** | Quelles sont les contraintes (périmètre, outils, sécurité, budget tokens) ? |
| **Data** | Quelles données de contexte le skill doit-il utiliser ? |
| **Evaluation** | Comment savoir que le skill fonctionne correctement ? |

---

## 🔁 Procédure

1. **Extraire** Goal / Output / Limits / Data / Evaluation à partir de la demande.
2. **Définir le déclenchement** : quels mots ou contextes activent ce skill, et quels cas l'excluent.
3. **Écrire le frontmatter** :
   - `name` identique au nom du dossier.
   - `description` : courte, précise, contient le trigger et le cas d'usage.
   - `version`, `license`, `metadata`, `allowed-tools`.
4. **Structurer le corps Markdown** :
   - Rôle, mission, procédure détaillée, outils autorisés, politique de sécurité, format de sortie, critères d'arrêt.
5. **Ajouter** références, templates, scripts et evals uniquement s'ils servent le comportement.
6. **Séparer** instructions et données de référence avec des délimiteurs clairs (`###`, balises XML ou sections).
7. **Vérifier la sécurité** : pas de secrets en clair, pas d'actions destructives sans confirmation, pas de prompt injection possible.
8. **Tester** should-trigger et should-not-trigger plusieurs fois avec des cas représentatifs.
9. **Versionner** et documenter chaque changement dans un CHANGELOG ou dans le frontmatter.

---

## 🧩 Mode Skillware (nouveau)

Lorsque l'utilisateur demande de transformer un prompt en capacité déterministe :

1. Définir un contrat d'entrée typé (JSON Schema).
2. Écrire le code déterministe (Python ou TypeScript).
3. Ajouter des tests unitaires.
4. Fournir des exemples de données.
5. Générer le SKILL.md final.

Objectif : réduire la dépendance aux longs prompts, améliorer l'auditabilité et la fiabilité.

---

## 🛡️ Quality Gates

- [ ] Le skill se déclenche au bon moment (bonne description, bon trigger).
- [ ] Les sorties sont directement utilisables sans post-traitement.
- [ ] Les inconnues sont signalées explicitement (refus si contexte insuffisant).
- [ ] Aucun secret en clair dans le frontmatter ou le corps.
- [ ] Les actions externes (push, deploy, delete) exigent confirmation explicite.
- [ ] Le skill refuse ou demande clarification si le contexte est insuffisant.
- [ ] `allowed-tools` est déclaré et limité au strict nécessaire.
- [ ] Le `name` du frontmatter est identique au nom du dossier.
- [ ] La `description` contient les mots-clés qui déclenchent le skill.

---

## 📋 Output attendu

```
## Rapport Skill Architect

### Diagnostic
<état actuel du skill ou du prompt, problèmes identifiés>

### Architecture proposée
<structure du skill, sections, outils, politiques>

### SKILL.md final
<contenu complet prêt à copier>

### Arborescence du dossier skill
<structure de fichiers recommandée>

### Tests should-trigger / should-not-trigger
- ✅ Trigger : "<phrase qui doit activer le skill>"
- ❌ Non-trigger : "<phrase qui ne doit pas l'activer>"

### Limites et risques
<ce que le skill ne couvre pas ou pourrait mal gérer>

### Changelog
- v1.2.0 : ajout du mode Skillware (schéma, code, tests, données).
- v1.1.0 : version initiale enrichie.
```
