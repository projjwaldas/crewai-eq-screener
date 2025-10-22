# Import Modules
from crewai import Crew, Process
from tools import scraper, sp500_wiki_tool, yfinance_tool, tavily_web_search_tool
from agents import market_outlook_parser, sp500_extractor_aligner, fundamental_analyst, market_news_analyst, storytelling_agent
from tasks import parse_outlook_task, extract_and_align_task, fundamental_analysis_task, news_analysis_task, storytelling_task
from dotenv import load_dotenv
load_dotenv()

# -------- CREW --------
crew = Crew(
    agents=[market_outlook_parser, sp500_extractor_aligner, fundamental_analyst, market_news_analyst, storytelling_agent],
    tasks=[parse_outlook_task, extract_and_align_task, fundamental_analysis_task, news_analysis_task, storytelling_task],
    process=Process.sequential,
    memory=True
)

# -------- RUN --------

if __name__ == "__main__":
    result = crew.kickoff(inputs={
        "market_outlook_url": "https://www.sc.com/in/market-outlook/global-market-outlook-26-9-2025/?mvog=1"  # Replace with your actual outlook page
    })
    print("\n\n🎯 Final Overweight-Aligned Stocks:")
    print(type(result))
    print(result)