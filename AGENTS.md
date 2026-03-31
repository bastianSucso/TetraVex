# AGENTS.md (Code-First)

## Objetivo
Guía operativa para agentes que trabajen en este repositorio del taller TetraVex.
Prioridad: implementación correcta en Python + miniKanren, sin hard-code.

## Estado del repo (actual)
- Archivo principal: `tetravex.py`
- No hay carpeta `tests/`
- No hay `pyproject.toml`, `setup.cfg`, `tox.ini`, `Makefile`
- No se encontraron reglas adicionales:
  - `.cursorrules`
  - `.cursor/rules/`
  - `.github/copilot-instructions.md`

## Dependencias mínimas
- Python 3.10+ (recomendado 3.11)
- `miniKanren`
- `matplotlib` (solo benchmark/gráfico)

Instalación rápida:
- `pip install miniKanren matplotlib`

---

## Comandos de trabajo

### Ejecutar solver + ejemplo
- `python tetravex.py`

### Verificación de sintaxis
- `python -m py_compile tetravex.py`

### Lint/format (si están instalados)
- `ruff check tetravex.py`
- `black tetravex.py`

### Tests (cuando exista pytest)
- Todos: `pytest -q`
- Un archivo: `pytest tests/test_tetravex.py -q`
- Un test: `pytest tests/test_tetravex.py::test_example_solution -q`

Nota: hoy no hay tests formales; usar smoke test con `python tetravex.py`.

---

## Contrato funcional del solver

### Entrada
El solver debe aceptar:
1. Puzzle plano: tupla/lista de `n^2` piezas
2. Puzzle anidado `n x n` (como enunciado)

Cada pieza representa lados en orden:
- `(izquierda, derecha, superior, inferior)`

### Salida
- Una solución válida en formato tablero `n x n` (o `None` si no existe)
- Mantener consistencia del orden de lados en toda la ejecución

### Restricciones obligatorias
- Coincidencia horizontal: derecha de celda izquierda == izquierda de celda derecha
- Coincidencia vertical: inferior de celda superior == superior de celda inferior
- Cada pieza se usa exactamente una vez

---

## Estilo de implementación (obligatorio)

### Enfoque
- Declarativo / CSP con miniKanren
- Evitar resolver "solo" con bucles imperativos hard-codeados
- Mantener solución general para `n x n` (sin tamaños fijos)

### miniKanren esperado
Usar explícitamente:
- `var`, `run`, `lall`, `lany` o `conde`, `membero`
- `neq` para restricciones de diferencia
- (Opcional) `Zzz` si se requiere recursión lógica

Patrón recomendado:
- Variables = celdas del tablero
- Dominio = piezas disponibles
- Restricciones = adyacencia + no repetición

### Representación recomendada
Para manejar piezas duplicadas en valores:
- Representación interna con id único: `(id, l, r, u, d)`
- Salida final volver a `(l, r, u, d)`

---

## Convenciones de código Python

### Imports
Orden:
1. stdlib
2. terceros
3. locales

Eliminar imports no usados.

### Formato
- PEP 8
- 4 espacios
- Líneas ~88-100 chars
- Funciones pequeñas y con responsabilidad clara

### Nombres
- `snake_case` para funciones/variables
- Nombres descriptivos (`board_vars`, `indexed_pieces`, `candidate_tiles`)
- Evitar abreviaturas ambiguas

### Tipos
Agregar type hints en funciones públicas clave.
Aliases sugeridos:
- `Tile = tuple[int, int, int, int]`
- `IndexedTile = tuple[int, int, int, int, int]`

### Errores
- Validar entrada tempranamente
- Levantar `ValueError` con mensajes claros
- No silenciar excepciones sin razón

### Comentarios/docstrings
- Explicar lógica no obvia
- Evitar comentarios redundantes
- Mantener docstrings breves y útiles

---

## Reglas de cambios para agentes

1. No romper API principal sin necesidad.
2. No introducir hard-code de tamaño o piezas.
3. Mantener orden de lados `(l, r, u, d)` intacto.
4. Si se optimiza rendimiento, no sacrificar claridad CSP.
5. Si no hay tests, reportar exactamente qué se verificó por consola.

Checklist antes de terminar:
- [ ] `python -m py_compile tetravex.py` pasa
- [ ] `python tetravex.py` ejecuta ejemplo sin error
- [ ] Restricciones de adyacencia y unicidad siguen correctas
- [ ] No hay imports muertos
- [ ] Entrada plana y anidada soportadas (si se implementó adaptación)

---

## Alcance académico mínimo para este repo
El código debe demostrar:
- modelado CSP claro
- uso real de miniKanren en el solver
- generalidad (`n x n`)
- ausencia de hard-code ad hoc
- salida correcta para el caso del enunciado
