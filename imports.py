import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool, PDFSearchTool
from langchain_openai import ChatOpenAI
import getpass
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from langchain_community.tools.tavily_search import TavilySearchResults
from crewai_tools import ScrapeWebsiteTool, PDFSearchTool