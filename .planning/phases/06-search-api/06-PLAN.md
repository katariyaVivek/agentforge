---
phase: 06-search-api
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/pipeline/search.py
autonomous: true
requirements:
  - AI-02

must_haves:
  truths:
    - "TavilyClient.search() called with manifest-derived queries"
    - "Returns SearchResult objects with title, url, content"
    - "Handles missing API key gracefully"
  artifacts:
    - path: "src/pipeline/search.py"
      provides: "Real Tavily search integration"

key_links:
  - from: "src/main.py"
    to: "src/pipeline/search.py"
    via: "SearchPipeline.search_manifest()"
---

<objective>
Wire up real Tavily search API for web research.
</objective>

<tasks>

<task type="auto">
  <name>Task 1: Update SearchPipeline to use real Tavily API</name>
  <files>src/pipeline/search.py</files>
  <read_first>src/pipeline/search.py</read_first>
  <action>
1. Install tavily package: pip install tavily
2. Update SearchPipeline to use TavilyClient
3. Call search with manifest-derived queries
4. Handle missing API key gracefully (warning + continue)
5. Return SearchResult objects
  </action>
  <acceptance_criteria>
- grep "TavilyClient" src/pipeline/search.py
- grep "TAVILY_API_KEY" src/pipeline/search.py
  </acceptance_criteria>
  <done>SearchPipeline uses real Tavily API when available</done>
</task>

</tasks>

<verification>
TAVILY_API_KEY=your-key python -c "from src.pipeline.search import SearchPipeline; s = SearchPipeline(); print(s.search_manifest({'project_type':'saas','domain':'dev','scale':'solo','stack_hints':[],'files_to_generate':[]}))"
</verification>

<success_criteria>
Real Tavily search returns results for manifest queries
</success_criteria>
