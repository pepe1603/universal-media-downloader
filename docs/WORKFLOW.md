# Workflow de trabajo — Universal Media Downloader

Este documento define el flujo de trabajo de Git que deben seguir los agentes de IA y los desarrolladores. **Léelo completo antes de hacer cualquier cambio.**

## 1. Estructura de ramas

```
main ────────────────────────► (releases estables)
  └── develop ──────────────► (integración de cambios)
        ├── termux  ────────► (fixes de entorno Termux/Android)
        └── terminal ───────► (fixes de terminal de escritorio: Windows/Linux/macOS)
```

| Rama      | Propósito                                                        | ¿Se hace push directo? |
|-----------|------------------------------------------------------------------|------------------------|
| `main`    | Única rama de release. Solo se actualiza desde `develop`.        | No                    |
| `develop` | Integración de los fixes de `termux` y `terminal`.               | Sí (merges)           |
| `termux`  | Corregir bugs marcados como entorno Termux en `docs/BUGS.md`.    | Sí (commits)          |
| `terminal`| Corregir bugs marcados como Terminal en `docs/BUGS.md`.           | Sí (commits)          |

## 2. Reglas obligatorias

1. **Nunca** se hace commit/push directo a `main`. Siempre se llega por merge desde `develop`.
2. Cada fix se trabaja **únicamente** en su rama de entorno según el bug a resolver:
   - Bugs **Termux** (BUG-01 a BUG-05) → rama `termux`.
   - Bugs **Terminal** (BUG-06 a BUG-15) → rama `terminal`.
3. Antes de trabajar, actualizar la rama con `develop`:
   ```bash
   git checkout <rama> && git merge --ff-only develop
   ```
4. **Un commit por bug.** El mensaje debe referenciar el ID del bug: `fix(BUG-01): <descripción corta>`.
5. Tras cada fix, marcar el bug en `docs/BUGS.md` como **"Resuelto"** en la tabla de estado (misma rama, mismo commit si es posible).
6. Ejecutar las verificaciones de la sección 4 antes de hacer push.
7. No se suben archivos a `cookies/` (ignorados) ni secretos.

## 3. Ciclo de vida de un fix

```mermaid
flowchart LR
    A[Elegir bug de BUGS.md] --> B[Crear/actualizar rama del entorno]
    B --> C[Implementar fix]
    C --> D[Verificar: tests + syntax check]
    D --> E[Commit: fix(BUG-XX): ...]
    E --> F[Actualizar estado en BUGS.md]
    F --> G[Push de la rama]
    G --> H[Merge a develop]
    H --> I[Push develop]
    I --> J[¿Release? Sí → merge develop a main]
```

### Pasos detallados

1. **Elegir bug:** lee `docs/BUGS.md`, toma el bug con estado `Pendiente` y de mayor severidad (🔴 > 🟡 > 🟢).
2. **Cambiar a la rama correcta:** `git checkout termux` o `git checkout terminal` según el entorno del bug.
3. **Implementar** el fix siguiendo las convenciones del código existente (estilo, imports, etc.).
4. **Verificar** (sección 4).
5. **Commit** con el formato: `fix(BUG-XX): mensaje corto` (p. ej. `fix(BUG-01): fallback a ruta local sin permisos de almacenamiento`).
6. **Actualizar BUGS.md:** cambiar el estado del bug de `Pendiente` a `Resuelto` (si el fix fue a otro archivo, commit aparte: `docs(BUGS): marcar BUG-XX como resuelto`).
7. **Push:** `git push -u origin <rama>`.
8. **Merge a develop:**
   ```bash
   git checkout develop
   git merge <rama>          # normalmente fast-forward
   git push origin develop
   ```
9. **Release (cuando se decida):** desde `develop`, merge a `main`:
   ```bash
   git checkout main
   git merge --ff-only develop
   git push origin main
   ```

## 4. Verificaciones antes de push

- **Compilar:** `python -m py_compile src/main.py src/core/*.py src/storage/*.py src/platforms/*.py`
- **Tests:** `python -m pytest tests` (si existe suite).
- Revisar que no quedaron archivos sin trackear de más (`git status`).

## 5. Convención de commits

| Tipo    | Uso                                   | Ejemplo |
|---------|---------------------------------------|---------|
| `fix`   | Corrección de bug                     | `fix(BUG-01): ...` |
| `docs`  | Documentación                         | `docs(BUGS): marcar BUG-02 como resuelto` |
| `feat`  | Nueva funcionalidad                   | `feat: ...` |
| `chore` | Tareas de mantenimiento               | `chore: ...` |

Reglas de mensaje:
- Formato: `tipo(alcance): descripción` en minúsculas.
- Verbos en infinitivo o imperativo, sin puntuación final.
- Máximo ~72 caracteres en la primera línea.

## 6. Bugs activos (docs/BUGS.md)

La fuente de verdad de bugs es **`docs/BUGS.md`**. Cada bug tiene: severidad, entorno, archivo/línea, descripción, solución propuesta y estado.

- Tabla de estado al final del archivo: actualizar siempre tras resolver un bug.
- Bugs de Termux → rama `termux`. Bugs de Terminal → rama `terminal`.

## 7. Recordatorios para el agente IA

- No hacer push a `main`.
- No inventar ramas nuevas: si necesitas una rama temporal, crea `fix/<bug>` y bórrala tras merge.
- Preguntar al usuario antes de hacer un merge a `main` (release).
- Mantener `docs/BUGS.md` y `docs/WORKFLOW.md` siempre actualizados.
