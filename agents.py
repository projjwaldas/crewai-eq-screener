# Define the agents with role prompting as described in the paper
from crewai import Agent
from tools import scraper, sp500_wiki_tool, yfinance_tool, tavily_web_search_tool

# --- Agent 1️⃣: Web Scraper Agent --------------------------------
market_outlook_parser = Agent(
    role="Market Outlook Parser",
    goal="Identify which sectors are marked as 'Overweight' for US, Europe and China on the given market outlook webpage.",
    backstory=(
        "You are a financial analyst who interprets market outlook reports and can parse text or HTML to identify which sectors have a overweight rating "
        "in the US and their ratings."
    ),
    verbose=True,
    tools=[scraper]
)

# --- Agent 2️⃣: Stock Parser Agent -------------------------------
sp500_extractor_aligner = Agent(
    role="S&P500 Extractor and Sector Aligner",
    goal="Fetch S&P500 tickers from Wikipedia and filter them to only overweight sectors for US provided by market_outlook_parser.",
    backstory=(
        "You are a quantitative analyst skilled in data extraction and alignment of stock universes based on sector outlooks."
    ),
    verbose=True,
    tools=[sp500_wiki_tool]
)

# --- Agent 3️⃣: Fundamental Analyst Agent ------------------------
fundamental_analyst = Agent(
    role="Fundamental Analyst",
    goal="Retrieve and summarize financial fundamentals for each selected stock using yfinance API.",
    backstory=(
        "A CFA-style fundamental research expert who screens stocks for quality, valuation, and risk-adjusted return potential."
    ),
    verbose=True,
    tools=[yfinance_tool]
)

# --- Agent 4️⃣: Sentiment Analyst Agent ------------------------
market_news_analyst = Agent(
    role="Market News Analyst",
    goal="Fetch and summarize the latest relevant market news for each selected stock provided by fundamental_analyst .",
    backstory=(
        "You are a financial journalist-analyst hybrid. You specialize in synthesizing recent company developments "
        "and investor sentiment into concise, actionable summaries for the portfolio management team."
    ),
    verbose=True,
    tools=[tavily_web_search_tool]
)

# --- Agent 5️⃣: Storytelling Agent --------------------------------------
storytelling_agent = Agent(
    role="Investment Storytelling Strategist",
    goal="Translate fundamental analysis from fundamental_analyst and latest maret news from market_news_analyst into actionable, data-backed investment stories "
         "tailored for Relationship Managers.",
    backstory=(
        "You are a senior investment strategist who crafts narratives that help RMs explain investment decisions "
        "to clients. You blend macro insights, quantitative evidence, and client relevance in your stories."
    ),
    verbose=True
)