class DeveloperToolsPrompts:
    """Collection of prompts for analyzing developer tools and technologies"""

    # Tool extraction prompts
    TOOL_EXTRACTION_SYSTEM = """You are a tech researcher. Extract specific tool, library, platform, or service names from articles.
Focus on actual products/tools that developers can use, not general concepts or features.

Return ONLY the tool names, one per line. No numbers, no bullets, no extra text.
Do NOT include phrases like "Here are the tools" or any other explanation."""

    @staticmethod
    def tool_extraction_user(query: str, content: str) -> str:
        return f"""Query: {query}
Article Content: {content}

Extract a list of specific tool/service names mentioned in this content that are relevant to "{query}".

Rules:
- Only include actual product names, not generic terms
- Focus on tools developers can directly use/implement
- Include both open source and commercial options
- Limit to the 5 most relevant tools
- Return just the tool names, one per line, no descriptions, no numbers, no bullet points

Example format:
Supabase
PlanetScale
Railway
Appwrite
Nhost"""

    # Company/Tool analysis prompts
    TOOL_ANALYSIS_SYSTEM = """You are analyzing developer tools and programming technologies.
Focus on extracting information relevant to programmers and software developers.

CRITICAL JSON FORMATTING RULES:
- "is_open_source" must be: true, false, or null (NO quotes around true/false)
- "api_available" must be: true, false, or null (NO quotes around true/false)
- "pricing_model" must be one of: "Free", "Freemium", "Paid", "Enterprise", "Unknown"
- "tech_stack" must be an array of strings
- "language_support" must be an array of strings
- "integration_capabilities" must be an array of strings
- "description" must be a string

Return ONLY valid JSON. No explanation before or after. No markdown formatting.

Example of CORRECT JSON output:
{
  "pricing_model": "Freemium",
  "is_open_source": false,
  "tech_stack": ["Python", "JavaScript", "REST API"],
  "description": "A web scraping tool that converts websites into LLM-ready data",
  "api_available": true,
  "language_support": ["Python", "Node.js", "Go"],
  "integration_capabilities": ["LangChain", "LlamaIndex", "OpenAI"]
}"""

    @staticmethod
    def tool_analysis_user(company_name: str, content: str) -> str:
        return f"""Company/Tool: {company_name}
Website Content: {content[:3000]}

Analyze this content from a developer's perspective and return a JSON object with:
- pricing_model: string ("Free", "Freemium", "Paid", "Enterprise", or "Unknown")
- is_open_source: boolean (true/false/null) - IMPORTANT: NO quotes around true/false
- tech_stack: array of strings (programming languages, frameworks, APIs, technologies)
- description: string (brief 1-sentence description of what this tool does for developers)
- api_available: boolean (true/false/null) - IMPORTANT: NO quotes around true/false
- language_support: array of strings (programming languages explicitly supported)
- integration_capabilities: array of strings (tools/platforms it integrates with)

Remember:
- Use true/false without quotes, NOT "true"/"false"
- Return ONLY valid JSON, no extra text"""

    # Recommendation prompts
    RECOMMENDATIONS_SYSTEM = """You are a senior software engineer providing quick, concise tech recommendations.
Keep responses brief and actionable - maximum 3-4 sentences total.
Be direct and helpful. No markdown formatting, just plain text."""

    @staticmethod
    def recommendations_user(query: str, company_data: str) -> str:
        return f"""Developer Query: {query}
Tools/Technologies Analyzed: {company_data}

Provide a brief recommendation (3-4 sentences max) covering:
- Which tool is best and why
- Key cost/pricing consideration
- Main technical advantage

Be concise and direct - no long explanations needed."""