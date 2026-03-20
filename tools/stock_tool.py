from crewai.tools import tool
import yfinance as yf
import json


@tool
def get_stock_data(ticker: str) -> str:
    """Fetch latest stock price and 30-day history for a given ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty:
            return json.dumps({"error": f"No data found for ticker: {ticker}"})

        latest_price = round(float(hist["Close"].iloc[-1]), 2)
        prev_price   = round(float(hist["Close"].iloc[-2]), 2)
        change_pct   = round(((latest_price - prev_price) / prev_price) * 100, 2)
        prices       = [round(float(p), 2) for p in hist["Close"].tolist()]
        volumes      = [int(v) for v in hist["Volume"].tolist()]

        return json.dumps({
            "ticker":      ticker.upper(),
            "latest_price": latest_price,
            "prev_price":   prev_price,
            "change_pct":   change_pct,
            "prices_30d":   prices,
            "volumes_30d":  volumes,
            "dates":        [str(d.date()) for d in hist.index.tolist()],
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_technical_indicators(ticker: str) -> str:
    """Calculate RSI, MACD, Bollinger Bands, SMA20, SMA50 for a given ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="3mo")
        if hist.empty or len(hist) < 26:
            return json.dumps({"error": f"Not enough data for {ticker}"})

        close = hist["Close"]

        # SMA
        sma20 = round(float(close.rolling(20).mean().iloc[-1]), 2)
        sma50 = round(float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else close.mean(), 2)

        # RSI
        delta = close.diff()
        gain  = delta.where(delta > 0, 0.0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
        rsi   = round(float(100 - (100 / (1 + gain.iloc[-1] / loss.iloc[-1]))), 2)

        # MACD
        ema12       = close.ewm(span=12, adjust=False).mean()
        ema26       = close.ewm(span=26, adjust=False).mean()
        macd_line   = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_val    = round(float(macd_line.iloc[-1]), 4)
        signal_val  = round(float(signal_line.iloc[-1]), 4)

        # Bollinger Bands
        rm      = close.rolling(20).mean()
        rs      = close.rolling(20).std()
        bb_upper = round(float((rm + 2 * rs).iloc[-1]), 2)
        bb_lower = round(float((rm - 2 * rs).iloc[-1]), 2)
        bb_mid   = round(float(rm.iloc[-1]), 2)

        return json.dumps({
            "ticker":         ticker.upper(),
            "latest_price":   round(float(close.iloc[-1]), 2),
            "sma20":          sma20,
            "sma50":          sma50,
            "rsi":            rsi,
            "macd":           macd_val,
            "macd_signal":    signal_val,
            "macd_histogram": round(macd_val - signal_val, 4),
            "bb_upper":       bb_upper,
            "bb_mid":         bb_mid,
            "bb_lower":       bb_lower,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_stock_news(ticker: str) -> str:
    """Fetch recent news headlines for a given stock ticker."""
    try:
        stock = yf.Ticker(ticker)
        news  = stock.news[:5] if stock.news else []
        if not news:
            return json.dumps({"ticker": ticker, "headlines": []})

        headlines = []
        for item in news:
            content = item.get("content", {})
            headlines.append({
                "title":    content.get("title", "No title"),
                "summary":  content.get("summary", ""),
                "provider": content.get("provider", {}).get("displayName", "Unknown"),
                "pubDate":  content.get("pubDate", ""),
            })
        return json.dumps({"ticker": ticker.upper(), "headlines": headlines})
    except Exception as e:
        return json.dumps({"error": str(e)})
