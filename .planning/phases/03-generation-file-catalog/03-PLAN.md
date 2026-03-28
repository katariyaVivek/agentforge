---
phase: 03-generation-file-catalog
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - file_definitions/catalog.py
  - src/agentforge/catalog/__init__.py
  - src/agentforge/catalog/models.py
  - src/agentforge/catalog/registry.py
  - src/agentforge/catalog/conditions.py
autonomous: true
requirements:
  - CAT-01
  - CAT-02

must_haves:
  truths:
    - "Core files (AGENT.md, RULES.md, STRUCTURE.md) are always generated"
    - "Conditional files appear only when catalog conditions evaluate to true"
    - "Catalog is defined in file_definitions/catalog.py as central registry"
  artifacts:
    - path: "file_definitions/catalog.py"
      provides: "Central file catalog with CAT-01 entries"
      contains: "CatalogEntry, FileType, CATALOG"
    - path: "src/agentforge/catalog/models.py"
      provides: "Pydantic models for catalog entries"
      contains: "class CatalogEntry"
    - path: "src/agentforge/catalog/registry.py"
      provides: "Catalog registry and file selection logic"
      contains: "get_files_to_generate"
    - path: "src/agentforge/catalog/conditions.py"
      provides: "Condition evaluation for catalog entries"
      contains: "evaluate_condition"
  key_links:
    - from: "src/agentforge/catalog/registry.py"
      to: "file_definitions/catalog.py"
      via: "import CATALOG"
    - from: "src/agentforge/catalog/registry.py"
      to: "src/agentforge/catalog/conditions.py"
      via: "evaluate_condition function"
---

<objective>
Create the file catalog system that drives conditional file generation.

Purpose: Implement CAT-01 (central catalog) and CAT-02 (core always, conditional on demand)
Output: Catalog registry with Pydantic models, condition evaluation, and file selection logic
</objective>

<context>
@.planning/ROADMAP.md
@.planning/phases/03-generation-file-catalog/03-RESEARCH.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create file_definitions/catalog.py with catalog entries</name>
  <files>file_definitions/catalog.py</files>
  <action>
Create central file catalog defining all available file types:
1. Define FileType enum with: AGENT, RULES, STRUCTURE, TESTING, DEPLOY
2. Create CATALOG list with CatalogEntry objects for each file type
3. Core files (is_core=True): AGENT.md, RULES.md, STRUCTURE.md
4. Conditional files (is_core=False): TESTING.md (scale=='large'), DEPLOY.md (domain=='web')
5. Export CATALOG constant for registry import

Reference 03-RESEARCH.md Pattern 2 for exact structure.
  </action>
  <verify>
    <automated>python -c "from file_definitions.catalog import CATALOG, FileType; print(f'Entries: {len(CATALOG)}'); print(f'Core: {sum(1 for e in CATALOG if e.is_core)}')"</automated>
  </verify>
  <done>Catalog has 5 entries: 3 core (always), 2 conditional</done>
</task>

<task type="auto">
  <name>Task 2: Create Pydantic models for catalog entries</name>
  <files>src/agentforge/catalog/models.py</files>
  <action>
Create Pydantic models for catalog system:
1. Create FileType enum matching file_definitions/catalog.py
2. Create CatalogEntry Pydantic model with fields: name, filename, template, is_core, condition, priority, context_keys
3. Add Field descriptions for documentation
4. Set sensible defaults (is_core=True, priority=0)

Reference 03-RESEARCH.md Pattern 2 for exact structure.
  </action>
  <verify>
  <automated>python -c "from src.agentforge.catalog.models import CatalogEntry, FileType; e = CatalogEntry(name='test', filename='test.md', template='test.j2'); print('Models OK')"</automated>
  </verify>
  <done>CatalogEntry Pydantic model validates correctly</done>
</task>

<task type="auto">
  <name>Task 3: Implement condition evaluation logic</name>
  <files>src/agentforge/catalog/conditions.py</files>
  <action>
Create safe condition evaluator:
1. Implement evaluate_condition(condition: str, context: dict) -> bool
2. Use eval() with restricted globals (empty __builtins__)
3. Allow access to: project_type, domain, scale, requirements from context
4. Return False on any evaluation error (fail-safe)
5. Add docstring with usage examples

Reference 03-RESEARCH.md Pattern 2 for exact structure.
  </action>
  <verify>
  <automated>python -c "from src.agentforge.catalog.conditions import evaluate_condition; ctx = {'project_type': 'web', 'domain': 'api', 'scale': 'medium', 'requirements': []}; print(evaluate_condition(\"domain == 'api'\", ctx)); print(evaluate_condition(\"scale == 'large'\", ctx))"</automated>
  </verify>
  <done>Conditions evaluate correctly: domain=='api' returns True, scale=='large' returns False</done>
</task>

<task type="auto">
  <name>Task 4: Create catalog registry with file selection</name>
  <files>src/agentforge/catalog/registry.py, src/agentforge/catalog/__init__.py</files>
  <action>
Create catalog registry that ties everything together:
1. Import CATALOG from file_definitions.catalog
2. Import evaluate_condition from conditions
3. Implement get_files_to_generate(manifest: dict) -> list[CatalogEntry]
   - Return all core files (is_core=True)
   - Add conditional files where condition evaluates to True
4. Export get_files_to_generate in __init__.py
5. Handle import errors gracefully (catalog may not exist during early dev)

Reference 03-RESEARCH.md Pattern 2 for exact structure.
  </action>
  <verify>
  <automated>python -c "from src.agentforge.catalog import get_files_to_generate; manifest = {'project_type': 'web', 'domain': 'api', 'scale': 'medium', 'requirements': []}; files = get_files_to_generate(manifest); print(f'Files: {[f.filename for f in files]}')"</automated>
  </verify>
  <done>Returns core 3 files + conditional files based on manifest</done>
</task>

</tasks>

<verification>
- [ ] Catalog imports work without errors
- [ ] Core files always included in output
- [ ] Conditional files included only when conditions match manifest
- [ ] Condition evaluation is safe (no code injection)
</verification>

<success_criteria>
Central file catalog drives generation:
- file_definitions/catalog.py defines all file types with conditions
- Pydantic models validate catalog entries
- get_files_to_generate() filters based on manifest metadata
- Core files always generated, conditional files on-demand
</success_criteria>

<output>
After completion, create `.planning/phases/03-generation-file-catalog/03-01-SUMMARY.md`
</output>

---

---
phase: 03-generation-file-catalog
plan: 02
type: execute
wave: 2
depends_on:
  - "03-01"
files_modified:
  - src/agentforge/generation/fallback.py
  - src/agentforge/generation/generator.py
  - src/agentforge/generation/prompts/agent_md.j2
  - src/agentforge/generation/prompts/rules_md.j2
  - src/agentforge/generation/prompts/structure_md.j2
  - src/agentforge/output/writer.py
  - src/agentforge/generation/__init__.py
autonomous: true
requirements:
  - GEN-01
  - REL-01

must_haves:
  truths:
    - "Generator creates AGENT.md, RULES.md, STRUCTURE.md in output/<project-slug>/"
    - "Model fallback circuit tries Gemini first, then Groq, then OpenRouter"
    - "Unified style prompt ensures consistent formatting regardless of model"
  artifacts:
    - path: "src/agentforge/generation/fallback.py"
      provides: "Model fallback circuit (REL-01)"
      contains: "create_model_with_fallback"
    - path: "src/agentforge/generation/generator.py"
      provides: "Main generation orchestrator (GEN-01)"
      contains: "class Generator"
    - path: "src/agentforge/generation/prompts/"
      provides: "Jinja2 templates for file generation"
      contains: "agent_md.j2, rules_md.j2, structure_md.j2"
    - path: "src/agentforge/output/writer.py"
      provides: "File writing utilities"
      contains: "write_file"
  key_links:
    - from: "src/agentforge/generation/generator.py"
      to: "src/agentforge/generation/fallback.py"
      via: "import create_model_with_fallback"
    - from: "src/agentforge/generation/generator.py"
      to: "src/agentforge/catalog"
      via: "import get_files_to_generate"
    - from: "src/agentforge/generation/generator.py"
      to: "src/agentforge/output/writer.py"
      via: "write_file function"
---

<objective>
Implement the generator with model fallback circuit.

Purpose: Implement GEN-01 (generator orchestrator) and REL-01 (resilient fallback)
Output: Generator that creates files using catalog + compressed context with automatic model failover
</objective>

<context>
@.planning/ROADMAP.md
@.planning/phases/03-generation-file-catalog/03-RESEARCH.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement model fallback circuit</name>
  <files>src/agentforge/generation/fallback.py</files>
  <action>
Create resilient model fallback circuit:
1. Import ChatGoogleGenerativeAI, ChatGroq, ChatOpenRouter
2. Define create_model_with_fallback() function that:
   - Creates primary model: gemini-2.0-flash with temperature=0.7, max_tokens=4096
   - Creates fallback_groq: llama-3.3-70b-versatile
   - Creates fallback_openrouter: anthropic/claude-3.5-sonnet
   - Wraps primary with .with_fallbacks([fallback_groq, fallback_openrouter])
3. Add exceptions_to_handle=[Exception] for robustness
4. Return RunnableWithFallbacks compatible with LangChain
5. Load API keys from environment (GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY)

Reference 03-RESEARCH.md Pattern 1 for exact structure.
  </action>
  <verify>
  <automated>python -c "from src.agentforge.generation.fallback import create_model_with_fallback; print('Fallback module OK')"</automated>
  </verify>
  <done>Model fallback chain created with all three providers</done>
</task>

<task type="auto">
  <name>Task 2: Create Jinja2 templates for file generation</name>
  <files>
    - src/agentforge/generation/prompts/agent_md.j2
    - src/agentforge/generation/prompts/rules_md.j2
    - src/agentforge/generation/prompts/structure_md.j2
  </files>
  <action>
Create Jinja2 templates for each core file type:
1. agent_md.j2: Agent configuration with role, tools, constraints sections
2. rules_md.j2: Coding rules and conventions
3. structure_md.j2: Project structure organization
Each template should:
- Use manifest context (project_type, domain, scale)
- Use compressed context (research_summary)
- Follow consistent Markdown style with clear headings
- Include no placeholder text like [TODO]

Reference 03-RESEARCH.md Pattern 3 for structure.
  </action>
  <verify>
    <automated>python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('src/agentforge/generation/prompts')); print([env.list_templates()])"</automated>
  </verify>
  <done>All three templates exist and are valid Jinja2</done>
</task>

<task type="auto">
  <name>Task 3: Implement file writer utility</name>
  <files>src/agentforge/output/writer.py</files>
  <action>
Create file writing utility:
1. Implement write_file(path: Path, content: str) -> None
2. Ensure parent directories exist (mkdir parents=True)
3. Write content with UTF-8 encoding
4. Return None (or return path for chaining)
5. Add type hints and docstring

Simple, focused function - no async needed for MVP.
  </action>
  <verify>
  <automated>python -c "from src.agentforge.output.writer import write_file; from pathlib import Path; import tempfile; p = Path(tempfile.gettempdir()) / 'test.md'; write_file(p, '# Test'); print(p.exists())"</automated>
  </verify>
  <done>Files written correctly to disk</done>
</task>

<task type="auto">
  <name>Task 4: Implement generator orchestrator</name>
  <files>src/agentforge/generation/generator.py, src/agentforge/generation/__init__.py</files>
  <action>
Create main generator orchestrator:
1. Import create_model_with_fallback from fallback
2. Import get_files_to_generate from catalog
3. Import write_file from output.writer
4. Import Jinja2 Environment
5. Implement Generator class:
   - __init__: stores model and output_dir
   - generate(manifest, compressed_context) -> dict
     - Call get_files_to_generate(manifest) for file list
     - Create output/<project_slug> directory
     - For each file: generate content via model + template
     - Write to output directory
     - Return dict of {filename: filepath}
   - _generate_content(entry, manifest, context) -> str
     - Build prompt with unified style
     - Invoke model
     - Return content
   - _build_prompt(entry, manifest, context) -> str
     - Template the generation prompt
6. Export Generator class in __init__.py

Reference 03-RESEARCH.md Pattern 4 for structure.
  </action>
  <verify>
  <automated>python -c "from src.agentforge.generation import Generator; print('Generator import OK')"</automated>
  </verify>
  <done>Generator orchestrates catalog + model + templates + output</done>
</task>

</tasks>

<verification>
- [ ] Model fallback works (Gemini → Groq → OpenRouter)
- [ ] All three templates render correctly
- [ ] Generator creates files in output/<project-slug>/
- [ ] Files contain project-specific content from manifest
</verification>

<success_criteria>
Generator with fallback integrated:
- Generator consumes manifest + compressed context via catalog
- Files written to output/<project-slug>/ in Markdown format
- Model fallback circuit provides resilience against quota/availability
- Unified style prompt ensures consistent formatting
</success_criteria>

<output>
After completion, create `.planning/phases/03-generation-file-catalog/03-02-SUMMARY.md`
</output>
