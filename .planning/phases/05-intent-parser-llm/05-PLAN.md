---
phase: 05-intent-parser-llm
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/pipeline/intent_parser.py
autonomous: true
requirements:
  - AI-01

must_haves:
  truths:
    - "Intent parser calls actual Gemini API with prompt"
    - "Returns structured IntentManifest"
    - "Handles API errors gracefully"
  artifacts:
    - path: "src/pipeline/intent_parser.py"
      provides: "Real Gemini LLM intent parser"

key_links:
  - from: "src/main.py"
    to: "src/pipeline/intent_parser.py"
    via: "IntentManifestParser.parse_prompt()"
---

<objective>
Replace test-mode intent parser with real Gemini LLM that parses actual prompts and returns structured IntentManifest.
</objective>

<tasks>

<task type="auto">
  <name>Task 1: Update IntentManifestParser to use real Gemini</name>
  <files>src/pipeline/intent_parser.py</files>
  <read_first>src/pipeline/intent_parser.py</read_first>
  <action>
1. Remove GSD_TEST_MODE check or make it fallback only
2. Install langchain-google-vertexai package
3. Use ChatGoogleGenerativeAI to call Gemini
4. Parse the response into IntentManifest Pydantic model
5. Handle API errors gracefully with try/except
6. Log warnings when API unavailable
  </action>
  <acceptance_criteria>
- grep "ChatGoogleGenerativeAI" src/pipeline/intent_parser.py
- grep "IntentManifest" src/pipeline/intent_parser.py
  </acceptance_criteria>
  <done>Intent parser uses real Gemini API when available</done>
</task>

</tasks>

<verification>
Run: python -c "from src.pipeline.intent_parser import IntentManifestParser; p = IntentManifestParser(); m = p.parse_prompt('a twitter clone'); print(m.project_type)"
</verification>

<success_criteria>
Real Gemini LLM parses prompts and returns IntentManifest
</success_criteria>
