---
phase: 07-generator-llm
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/agentforge/generation/generator.py
autonomous: true
requirements:
  - AI-03

must_haves:
  truths:
    - "Generator calls LLM with Jinja2 template + context"
    - "Returns generated file content strings"
    - "Writes to output/<project-slug>/ directory"
  artifacts:
    - path: "src/agentforge/generation/generator.py"
      provides: "Real LLM file generation"

key_links:
  - from: "src/main.py"
    to: "src/agentforge/generation/generator.py"
    via: "Generator.generate()"
---

<objective>
Connect actual LLM generation for file content instead of template fallback.
</objective>

<tasks>

<task type="auto">
  <name>Task 1: Update Generator to use real LLM</name>
  <files>src/agentforge/generation/generator.py</files>
  <read_first>src/agentforge/generation/generator.py</read_first>
  <action>
1. Update Generator to initialize LLM (Gemini first, then Groq fallback)
2. In _generate_content, call LLM with prompt template
3. Pass compressed_context as research background
4. Handle API failures gracefully, fall back to templates
5. Log warnings when LLM unavailable
  </action>
  <acceptance_criteria>
- grep "ChatGroq" src/agentforge/generation/generator.py
- grep "_generate_content" src/agentforge/generation/generator.py
  </acceptance_criteria>
  <done>Generator uses real LLM for file content</done>
</task>

</tasks>

<verification>
GROQ_API_KEY=xxx TAVILY_API_KEY=xxx python agentforge.py "saas app" && cat output/*/AGENT.md
</verification>

<success_criteria>
Generated files contain real AI-written content, not placeholders
</success_criteria>
