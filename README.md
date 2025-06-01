# 📚 Planejeel - Seu Organizador de Matrículas da EEL

## 🎯 Objetivo

O **Planejeel** resolve um drama comum dos estudantes da **Escola de Engenharia de Lorena (EEL/USP)**:

> *"Reprovei em uma disciplina e agora não sei quais matérias posso cursar por causa dos pré-requisitos bloqueados!"*

### ✨ Funcionalidades
- 🔍 Visualize todas as disciplinas do seu curso por semestre
- ⚠️ Identifique disciplinas travadas por reprovação em requisitos
- 📅 Planeje seu semestre de forma estratégica
- 🆕 Dados sempre atualizados automaticamente

## 🛠️ Como Funciona?

```mermaid
graph TB
    A[PyJupiter] -->|arquivos JSON| B(Processamento Python)
    B --> C{Geração de Páginas}
    C --> D[Visualização Interativa]
    C --> E[GitHub Pages]
