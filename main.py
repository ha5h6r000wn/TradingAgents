from dotenv import load_dotenv

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

# Load environment variables from .env file
load_dotenv()


# Create a custom config
config = DEFAULT_CONFIG.copy()
config["backend_url"] = "http://llm.smart-zone-dev.gf.com.cn/api/oai/v1"
config["deep_think_llm"] = "internal-qwen3-235b-a22b-think-awq"  # Use a different model
config["quick_think_llm"] = "internal-qwen3-235b-a22b-think-awq"  # Use a different model
config["embedding_model"] = "internal-bge-m3"
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "local",  # Options: yfinance, alpha_vantage, local
    "technical_indicators": "local",  # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",  # Options: openai, alpha_vantage, local
    "news_data": "alpha_vantage",  # Options: openai, alpha_vantage, google, local
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
