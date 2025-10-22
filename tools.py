# Define tools as classes inheriting from BaseTool
from crewai.tools import BaseTool
import pandas as pd, numpy as np
import requests, json, os
from io import StringIO
import yfinance as yf
from datetime import datetime, timedelta
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

class SP500WikiTool(BaseTool):
    name: str = "Stocks Extractor"
    description: str = "Fetches list of Stocks from S&P500 along with sector information"

    # def _run(self, overweight_sectors: list):
    def _run(self):
        """Use the tool."""
        try:
            # Scrape S&P 500 list from Wikipedia (official source)
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            # tables = pd.read_html(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text)
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            tables = pd.read_html(StringIO(response.text))          # ✅ Wrap HTML in StringIO to avoid pandas deprecation warning
            sp500_df = tables[0][["Symbol", "Security", "GICS Sector"]]
            sp500_df.columns = ["ticker", "name", "sector"]
            return sp500_df.to_dict(orient="records")

        except Exception as e:
            return f"Error fetching S&P500 data: {str(e)}"

class GetFundaments(BaseTool):
    name: str = "Get Fundamentals of Stocks"
    description: str = "Fetches fundamentals of Stocks from Yahoo Finance API"

    def _run(self, stocks_json: str):

        print(stocks_json)
        if isinstance(stocks_json, str):
            try:
                stocks_json = json.loads(stocks_json)
            except json.JSONDecodeError:
                return "Error: stocks_json must be a dict or valid JSON string."

        results = []
        # for ticker in stocks_json.keys():
        for key, value in stocks_json.items():
            ticker = key
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # --- Core Metrics ---
                beta = info.get("beta", np.nan)
                pe_ratio = info.get("trailingPE", np.nan)
                debt_to_equity = info.get("debtToEquity", np.nan)

                # --- Historical Data ---
                hist = stock.history(period="5y", interval="3mo")
                if hist.empty:
                    continue

                # Revenue & EBITDA history from financials
                financials = stock.financials
                if financials is None or financials.empty:
                    continue

                # Compute 5-year average growths if available
                revenue = financials.loc["Total Revenue"].dropna() if "Total Revenue" in financials.index else pd.Series()
                ebitda = financials.loc["Ebitda"].dropna() if "Ebitda" in financials.index else pd.Series()

                def avg_growth(series):
                    if len(series) < 2:
                        return np.nan
                    growth_rates = series.pct_change().dropna()
                    return growth_rates.mean() * 100

                rev_growth_5y = avg_growth(revenue)
                ebitda_growth_5y = avg_growth(ebitda)

                # --- Approximate Alpha ---
                # Using CAPM proxy: alpha = (stock return - beta * market return)
                # market = yf.Ticker("^GSPC")
                # market_hist = market.history(period="5y", interval="1mo")["Close"].pct_change().dropna()
                # stock_hist = hist["Close"].pct_change().dropna()
                # alpha = (stock_hist.mean() - beta * market_hist.mean()) * 100 if beta and not np.isnan(beta) else np.nan

                data = {
                    "ticker": ticker,
                    "name": value['name'],
                    "beta": round(beta, 2) if beta else None,
                    # "alpha": round(alpha, 2) if alpha else None,
                    "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
                    "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else None,
                    "rev_growth_5y_pct": round(rev_growth_5y, 2) if rev_growth_5y else None,
                    "ebitda_growth_5y_pct": round(ebitda_growth_5y, 2) if ebitda_growth_5y else None,
                    "sector": info.get("sector", np.nan)
                }

                # --- Filtering Criteria ---
                # if (
                #     data["pe_ratio"] and data["pe_ratio"] < 30 and
                #     # data["beta"] and data["beta"] <= 1.5 and
                #     # data["alpha"] and 5 <= data["alpha"] <= 200 and
                #     data["rev_growth_5y_pct"] and data["rev_growth_5y_pct"] > 1
                #     # data["ebitda_growth_5y_pct"] and data["ebitda_growth_5y_pct"] > 10 and
                #     # data["debt_to_equity"] and data["debt_to_equity"] <= 50
                # ):
                results.append(data)

            except Exception as e:
                print(f"⚠️ Error fetching data for {ticker}: {e}")
                continue

        return pd.DataFrame(results).to_json(orient="records") if results else "[]"

search = SerperDevTool()

# class WebSearchTool(BaseTool):
#     name: str = "Get Latest Market News of Stocks"
#     description: str = "Fetches Market News of Stocks from web"
#
#     def _run(self, stocks_json: str):
#
#         if isinstance(stocks_json, str):
#             try:
#                 stocks_json = json.loads(stocks_json)
#             except json.JSONDecodeError:
#                 return "Error: stocks_json must be a dict or valid JSON string."
#
#         today = datetime.utcnow()
#         cutoff_date = today - timedelta(days=30)
#         results = []
#
#         for key, value in stocks_json.items():
#             ticker = key
#             name = value["name"]
#             # ticker = s.get("ticker")
#             # name = s.get("name", ticker)
#             query = f"{name} stock news after:{cutoff_date.strftime('%Y-%m-%d')}"
#
#             try:
#                 search_results = search.run(query)
#                 if not search_results or "organic" not in search_results:
#                     continue
#
#                 stock_news = []
#                 for item in search_results["organic"][:10]:
#                     title = item.get("title")
#                     link = item.get("link")
#                     snippet = item.get("snippet", "")
#                     date_str = item.get("date", "")
#
#                     stock_news.append({
#                         "title": title,
#                         "url": link,
#                         "snippet": snippet,
#                         "date": date_str
#                     })
#
#                 if stock_news:
#                     results.append({
#                         "ticker": ticker,
#                         "name": name,
#                         "news_count": len(stock_news),
#                         "articles": stock_news
#                     })
#
#             except Exception as e:
#                 print(f"⚠️ Error fetching news for {ticker}: {e}")
#                 continue
#
#         return json.dumps(results, indent=2)


class WebSearchTool(BaseTool):
    name: str = "Get Latest Market News of Stocks"
    description: str = "Performs a web search using the Tavily Search API."

    def _run(self, stocks_json: str):

        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return json.dumps({"error": "Missing TAVILY_API_KEY environment variable."})

        try:
            # Step 1: Parse the incoming JSON
            stocks = json.loads(stocks_json)
            if not isinstance(stocks, dict):
                return json.dumps({"error": "Input must be a JSON dictionary of stock data."})

            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}

            news_results = {}

            # Step 2: Loop over each stock ticker
            for ticker, details in stocks.items():
                company_name = details.get("name") or ticker
                query = f"latest news about {company_name}"

                payload = {
                    "api_key": api_key,
                    "query": query,
                    "max_results": 5,
                    "include_answer": False
                }

                response = requests.post(url, headers=headers, json=payload, timeout=15)

                if response.status_code != 200:
                    news_results[ticker] = [{
                        "error": f"Request failed ({response.status_code})",
                        "details": response.text
                    }]
                    continue

                data = response.json()
                items = data.get("results", [])

                # Step 3: Extract clean, structured data
                simplified = []
                for item in items:
                    simplified.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "snippet": item.get("snippet", "")
                    })

                news_results[ticker] = simplified

            # Step 4: Return all results as formatted JSON string
            return json.dumps(news_results, indent=2)

        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON input provided."})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})


# Initialize instances of the new BaseTool-derived classes
sp500_wiki_tool = SP500WikiTool()
yfinance_tool = GetFundaments()
# news_extractor_tool = WebSearchTool()
scraper = ScrapeWebsiteTool()
tavily_web_search_tool = WebSearchTool()