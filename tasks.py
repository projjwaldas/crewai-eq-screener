# Define tasks for each agent with risk tolerance consideration
from crewai import Task
from tools import scraper, sp500_wiki_tool, yfinance_tool, tavily_web_search_tool
from agents import market_outlook_parser, sp500_extractor_aligner, fundamental_analyst, market_news_analyst, storytelling_agent

# --- Task 1️⃣: Scrape URL for US Overweight Sectors ---------------
parse_outlook_task = Task(
    description=(
        "Go to the given market outlook webpage: {market_outlook_url}. "
        "Identify which sectors are labeled as 'Overweight' for US, Europe and China. "
        "Return them as a Python dictionary, e.g. {'US': ['Technology','Healthcare']}."
    ),
    expected_output="A Python dictionary of markets and corresponding sectors marked as 'Overweight'.",
    tools=[scraper],
    agent=market_outlook_parser
)

# --- Task 2️⃣: Identify Stocks in Overweight Sectors --------------
extract_and_align_task = Task(
    description=(
        "You are given a list of overweight sectors from the previous task. "
        "Your job is to use the sp500_wiki_tool to fetch the S&P500 company list and sectors, "
        "and identify which of them belong to the overweight sectors from the previous task.\n\n"
        "Each stock dictionary must include the following keys:\n"
        "👉 IMPORTANT: Your final output MUST be a **valid JSON dictionary only**. The JSON must map each stock ticker (string) to its information dictionary."
        "Strictly match this format:\n\n"
        "{\n"
        "  'ABT': {\n"
        "    'name': 'Abbott Laboratories',\n"
        "    'sector': 'Health Care'\n"
        "  },\n"
        "  'ACN': {\n"
        "    'name': 'Accenture',\n"
        "    'sector': 'Information Technology'\n"
        "  }\n"
        "}\n\n"
        "Do NOT include any explanations, markdown formatting, code fences, or text outside this JSON. "
        "Ensure that the JSON is valid and can be parsed by Python's `json.loads()` without modification."
    ),
    expected_output=(
        "A JSON list of dictionaries of each stocks with their ticker, name and sector information. "
        "Only valid JSON should be produced — no markdown or text around it."
    ),
    # description=(
    #     "Use the sp500_wiki_tool to fetch the S&P500 company list and sectors, "
    #     "then filter it to include only those companies whose sectors match the overweight sectors for US from the previous task. "
    #     # "Return the filtered stock list from sp500_wiki_tool with tickers, names, and sectors, e.g. {'ticker': 'ABT', 'name': 'Abbott Laboratories', 'sector': 'Health Care'}"
    # ),

    # expected_output=("JSON of tickers, names, and sectors belonging to overweight sectors. "
    #                  "example of output structure - {'filtered_stocks': [{'ticker': 'ABT', 'name': 'Abbott Laboratories', 'sector': 'Health Care'}, {'ticker': 'ABBV', 'name': 'AbbVie', 'sector': 'Health Care'}]}"),
    tools=[sp500_wiki_tool],
    agent=sp500_extractor_aligner
)

# --- Task 3️⃣: Analyze and Rank Stocks Fundamentally --------------
fundamental_analysis_task = Task(
    description=(
        "You are given a JSON list of dictionaries of each stocks with their ticker, name and sector information, provided as the `previous_task_output`.\n\n"
        "Your goal is to use the `yfinance_tool` to retrieve key financial fundamentals for every stock ticker listed. "
        "You must query each ticker using the tool and aggregate the results into a single JSON object.\n\n"
        "Each stock dictionary must include the following keys:\n"
        "- name\n"
        "- sector\n"
        "- marketCap\n"
        "- pe_ratio\n"
        "- debt_to_equity\n"
        "- rev_growth_5y_pct\n"
        "- ebitda_growth_5y_pct\n"
        # "- forwardPE\n"
        # "- trailingPE\n"
        # "- trailingEps\n"
        # "- dividendYield\n"
        # "- revenueGrowth\n"
        # "- returnOnEquity\n"
        # "- profitMargins\n"
        "- beta\n"
        # "- 52WeekChange\n\n"
        "👉 IMPORTANT:\n"
        "- Your final output MUST be a **valid JSON dictionary only**.\n"
        "- The JSON must map each stock ticker (string) to its fundamentals dictionary.\n"
        "- Example:\n"
        "{\n"
        "  'AAPL': {\n"
        "    'name': 'Apple Inc.',\n"
        "    'sector': 'Technology',\n"
        "    'marketCap': 2.8e12,\n"
        "    'pe_ratio': 39.81,\n"
        "    'debt_to_equity': 154.49,\n"
        "    'rev_growth_5y_pct': -2.11\n"
        "    'ebitda_growth_5y_pct': 0.072\n"
        "    'beta': 1.09\n"
        "  },\n"
        "  'ABT': {\n"
        "    'name': 'Abbott Laboratories',\n"
        "    'sector': 'Health Care',\n"
        "    'marketCap': 4.3e11,\n"
        "    'pe_ratio': 16.02,\n"
        "    'debt_to_equity': 26.5,\n"
        "    'rev_growth_5y_pct': 1.04\n"
        "    'ebitda_growth_5y_pct': 0.072\n"
        "    'beta': 0.7\n"
        "  }\n"
        "}\n\n"
        "Do NOT include any explanations, markdown formatting, code fences, or text outside this JSON. "
        "Ensure that the JSON is valid and can be parsed by Python's `json.loads()` without modification."
    ),
    expected_output=(
        "A JSON dictionary mapping each stock ticker to a sub-dictionary of its financial fundamentals. "
        "Only valid JSON, no extra text."
    ),
    # description=(
    #     "Retrieve financial fundamentals for each stock using the yfinance_tool tool. "
    #     "Focus on key metrics: ticker, name, Sector, Alpha, Beta, PE Ratio, 5 year average historical revenue growth, "
    #     "5 year average historical EBITDA growth, PE Ratio and Debt to Equity ratio"
    #     # "Return a JSON summary per stock."
    #     # "Subset the stocks based on these criteria: "
    #     # "PE<30, Revenue Growth>1%. "
    # ),
    # expected_output="JSON of fundamental metrics for each stock including ticker, name, Sector, Alpha, Beta, PE Ratio, 5 year average historical revenue growth, 5 year average historical EBITDA growth, PE Ratio and Debt to Equity ratio.",
    tools=[yfinance_tool],
    agent=fundamental_analyst
)

# --- Task 4️⃣: Get Market Sentiments ------------------------
news_analysis_task = Task(
description=(
        "You are given a JSON dictionary mapping each stock ticker to a sub-dictionary of its name, sector information and financial fundamentals, "
        "provided as the `previous_task_output`.\n\n"
        "Your job is to collect and summarize the latest market news for each of these stock tickers.\n\n"
        "You MUST only usr the `tavily_web_search_tool`.\n\n"
        "For each stock ticker:\n"
        "- Retrieve the 3–5 most recent and relevant news articles, headlines, or analyst reports.\n"
        "- Summarize the general market sentiment (e.g., positive, neutral, negative).\n"
        "- Identify key themes such as earnings performance, guidance, regulatory updates, or innovation.\n\n"
        "👉 IMPORTANT OUTPUT REQUIREMENTS:\n"
        "- Your final answer MUST be a **valid JSON object only**, no markdown, no code fences, no explanations.\n"
        "- The JSON must map each stock ticker to a dictionary containing the following keys:\n"
        "- name\n"
        "- sector\n"
        "- pe_ratio\n"
        "- debt_to_equity\n"
        "- rev_growth_5y_pct\n"
        "- ebitda_growth_5y_pct\n"
        "- beta\n"
        "  * 'recent_headlines' → list of 3–5 concise news headlines\n"
        "  * 'summary' → short paragraph (2–3 sentences) summarizing the news context\n"
        "  * 'sentiment' → one of ['positive', 'neutral', 'negative']\n\n"
        "✅ Example JSON structure:\n"
        "{\n"
        "  'AAPL': {\n"
        "   'name': 'Apple Inc.',\n"
        "   'sector': 'Information Technology',\n"
        "   'pe_ratio': 39.81,\n"
        "   'debt_to_equity': 154.49,\n"
        "   'rev_growth_5y_pct': -2.11,\n"
        "   'ebitda_growth_5y_pct': 1.07,\n"
        "   'beta': 1.09,\n"
        "   'recent_headlines': [\n"
        "      'Apple announces new Mac lineup powered by M4 chip',\n"
        "      'Strong Q3 earnings beat Wall Street expectations'\n"
        "    ],\n"
        "   'summary': 'Apple’s latest Mac release and better-than-expected Q3 results boosted investor confidence.',\n"
        "   'sentiment': 'positive'\n"
        "  },\n"
        "  'ABT': {\n"
        "   'name': 'Abbott Laboratories',\n"
        "   'sector': 'Health Care',\n"
        "   'pe_ratio': 16.02,\n"
        "   'debt_to_equity': 26.5,\n"
        "   'rev_growth_5y_pct': 1.04,\n"
        "   'ebitda_growth_5y_pct': 0.8,\n"
        "   'beta': 0.7,\n"
        "    'recent_headlines': [\n"
        "      'Abbott launches groundbreaking glucose monitoring device',\n"
        "      'Reports indicate steady revenue growth amid rising healthcare demand'\n"
        "      'Abbott's new product promises enhanced patient care'\n"
        "    ],\n"
        "    'summary': 'Abbott's recent product innovations and consistent revenue growth reflect a positive outlook, particularly in the healthcare sector where demand is rising.',\n"
        "    'sentiment': 'positive'\n"
        "  }\n"
        "}\n\n"
        "⚠️ DO NOT include any additional commentary, markdown formatting, or text outside of this JSON. "
        "Ensure your JSON is valid and can be parsed directly by Python’s `json.loads()`."
    ),
    expected_output=(
        "A valid JSON dictionary mapping each stock ticker to a sub-dictionary containing recent_headlines, "
        "summary, and sentiment fields. No markdown, explanations, or code fences."
    ),
    # description=(
    #     "Use news_extractor_tool to fetch recent (within last 30 days) news for the list of stocks selected by the fundamental_analyst agent."
    #     "Summarize the key topics, company updates, and market sentiment for each ticker."
    # ),
    # expected_output="A JSON list of stocks with their latest news summaries.",
    tools=[tavily_web_search_tool],
    agent=market_news_analyst
)

# --- Task 5️⃣: Create Investment Narrative ------------------------
storytelling_task = Task(
description=(
        "You are given a structured JSON object as input (available in `previous_task_output`).\n\n"
        "This JSON maps each stock ticker to its company details, financial fundamentals, and recent market news.\n\n"
        "The JSON input follows this structure:\n"
        "{\n"
        "  'AAPL': {\n"
        "   'name': 'Apple Inc.',\n"
        "   'sector': 'Information Technology',\n"
        "   'pe_ratio': 39.81,\n"
        "   'debt_to_equity': 154.49,\n"
        "   'rev_growth_5y_pct': -2.11,\n"
        "   'ebitda_growth_5y_pct': 1.07,\n"
        "   'beta': 1.09,\n"
        "   'recent_headlines': [\n"
        "      'Apple announces new Mac lineup powered by M4 chip',\n"
        "      'Strong Q3 earnings beat Wall Street expectations'\n"
        "    ],\n"
        "   'summary': 'Apple’s latest Mac release and better-than-expected Q3 results boosted investor confidence.',\n"
        "   'sentiment': 'positive'\n"
        "  },\n"
        "  'XOM': { ... }\n"
        "}\n\n"
        "### Your Task\n"
        "- DO NOT perform any web search or call any external APIs.\n"
        "- DO NOT use information outside the provided JSON.\n"
        "- Carefully analyze each company’s fundamentals and news data.\n"
        "- Write a **compelling investment narrative** for each company.\n"
        "- Focus on:\n"
        "  * How the fundamentals reflect the company’s financial strength.\n"
        "  * How the news supports or challenges its investment case.\n"
        "  * Whether the current market sentiment aligns with fundamentals.\n"
        "- Maintain a professional tone suitable for an investment research report.\n\n"
        "### Output Format\n"
        "Your final answer MUST be a markdown-formatted document, with **one section per stock**.\n"
        "Follow this structure exactly:\n\n"
        "## Company Name (Ticker)\n"
        "**Sector:**\n\n"
        "**Financial Overview:**\n"
        "- pe_ratio\n"
        "- debt_to_equity\n"
        "- beta\n"
        "- rev_growth_5y_pct\n"
        "- ebitda_growth_5y_pct\n\n"
        "**Recent News Highlights:**\n"
        "- News 1\n"
        "- News 2\n"
        "- News 3\n\n"
        "**Narrative Summary:**\n"
        "Write 2–3 paragraphs explaining why this stock may or may not represent a strong investment opportunity.\n"
        "Base your reasoning **solely** on the provided fundamentals and news sentiment.\n\n"
        "⚠️ Do NOT include any commentary or information not found in the input JSON.\n"
        "⚠️ Do NOT output any JSON, only markdown text following the above format."
    ),
    expected_output=(
        "A markdown-formatted investment report containing one section per stock, "
        "each including fundamentals, summarized news, and a 2–3 paragraph narrative analysis."
        "Cover all th stocks provided within the input JSON."
    ),
    # description=(
    #     "Create a detailed investment report for Relationship Managers using the sector-level data provided. "
    #     "For each sector:\n"
    #     "1. Briefly summarize why the sector is overweight according to market outlook and recent performance.\n"
    #     "2. For each stock, list down the sector, alpha, beta, average 5 year revenue growth, debt to equity ratio, average PE"
    #     "3. For each stock, explain why it stands out using quantitative data such as alpha, beta, average 5 year revenue growth, debt to equity ratio, average PE etc. to justify the view. Give a macro view as well.\n"
    #     "4. For each stock, provide a one line summary of the latest news from the market_news_analyst agent supporting the above view.\n"
    #     "Structure the report with markdown headers per sector.\n"
    #     "All statements must be backed by numerical or factual data where available."
    # ),
    # expected_output="A markdown investment report with data-backed rationale and insights for each sector and stock.",
    agent=storytelling_agent,
    async_execution=False,
    output_file="investment_story_detailed.md"
)