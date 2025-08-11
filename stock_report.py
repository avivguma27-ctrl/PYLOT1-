import yfinance as yf
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import numpy as np
import pandas as pd

# ============================== #
# הגדרות ישירות בקוד - הכנס את הפרטים שלך כאן
TARGET_EMAILS = "avivguma12@gmail.com,swrrmy028@gmail.com"  # מי מקבל דוח
EMAIL_USER = "avivguma12@gmail.com"                          # מייל שולח
EMAIL_PASS = "fxgqtmhqcrszrzyj"                             # סיסמת אפליקציה (App Password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_LIST = [email.strip() for email in TARGET_EMAILS.split(",")]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKERS = [
    "AAPL","MSFT","AMZN","GOOG","GOOGL","FB","TSLA","BRK.B","BRK.A","JNJ",
    "V","WMT","JPM","UNH","NVDA","HD","PG","MA","DIS","BAC",
    "XOM","PYPL","VZ","ADBE","CMCSA","NFLX","T","KO","PFE","NKE",
    "MRK","INTC","PEP","ABT","CVX","CSCO","ORCL","CRM","MCD","ACN",
    "COST","WFC","MDT","TXN","LLY","NEE","HON","QCOM","BMY","LOW",
    "IBM","LIN","SBUX","AMGN","CAT","GE","BKNG","CHTR","USB","INTU",
    "BLK","TMO","MO","MMM","DE","ISRG","ZTS","SPGI","CI","SYK",
    "PLD","LMT","BDX","FIS","CME","GILD","ADI","CB","VRTX","EW",
    "TJX","ATVI","CL","SHW","ICE","MET","GM","SO","ITW","GD",
    "CCI","MCO","EL","NOC","DUK","F","APD","ECL","AON","COF",
    "BSX","PGR","EMR","HCA","AIG","ALL","DD","ADP","REGN","NSC",
    "KLAC","ROST","ADSK","CTSH","EXC","MNST","A","LRCX","MAR","EA",
    "ETN","BIIB","CERN","APH","MCK","MET","MPC","EOG","VLO","KMB",
    "FISV","DHR","BK","BDX","DG","MMC","WBA","TEL","XEL","ORLY",
    "HSY","AFL","KMI","HES","RMD","AEE","ZBRA","VAR","GLW","CINF",
    "FFIV","HOLX","NUE","WRB","CTAS","OKE","PH","AEP","HIG","PSA",
    "NTRS","MTD","TRV","VRSK","STZ","EVRG","WLTW","ABMD","XYL","HWM",
    "PEG","XLNX","LVS","CAG","ESS","XRX","ALGN","SNPS","FLT","MHK",
    "SWK","CBOE","ALB","SRE","ANSS","FTNT","DLR","FMC","TDG","PPL",
    "CNC","HAS","GL","MRO","BKR","NWSA","HLT","MSCI","D","DDOG","DOV",
    "ZBH","TT","WEC","GPN","MGM","XL","HST","TRMB","K","CTXS","COO",
    "GRMN","HPE","ED","PBCT","LYB","ROK","VTR","VRSN","LDOS","NTAP",
    "DTE","INFO","CHRW","EFX","CTRA","MCK","PHM","FRC","SWKS","MTB",
    "OKE","XYL","PEG","PNC","EIX","EBAY","CMA","ALXN","DGX","HBI","LHX",
    "BAX","TTWO","AKAM","ODFL","PXD","WDC","LEN","SYY","STX",
    "CDNS","ALGN","VMC","HSIC","PAYX","MTCH","CPRT","L","CE","KEYS",
    "IT","DHI","CAG","RSG","WAB","HUM","DXC","RJF","ES","NDAQ","WMB",
    "CLX","COG","FANG","JBHT","IRM","NWL","MKC","IEX","MCHP","SIVB",
    "MOS","BWA","MAS","SNA","TXT","VFC","EXPE","ULTA","NLOK","OMC","RCL",
    "GWW","LH","CMS","PAYC","MKTX","DLTR","CNP","PPG","ANET","DRE",
    "KSU","KIM","NWS","PKI","ARE","BEN","BKR","WY","LNT","GPC","AIZ",
    "AVY","PPL","WELL","VAR","PSX","APA","IDXX","WRK","AMCR","PEAK",
    "AOS","WYNN","BXP","FLS","JKHY","LKQ","FAST","TDG","CFG","ADM",
    "BLL","WM","TROW","AVB","O","NLSN","IRM","BXP","PRGO","ABMD","HOLX",
    "ZBRA","NWL","BBY","DD","DOV","PHM","AMT","LEN","HWM","AVB",
    "BABA","TCEHY","PDD","JD","SHOP","SQ","COIN","RIVN","LCID","BYDDY",
    "NIO","XPEV","LI","PLTR","SNOW","NET","CRWD","ZS","OKTA","SMCI",
    "ARM","TSM","ASML","AMD","MU","ON","MRVL","ENPH","SEDG","RUN",
    "BLDP","FCEL","SPWR","DUK","BA","LUV","UAL","DAL","RYAAY","EADSY",
    "CCL","RCL","NCLH","UBER","LYFT","ABNB","EXPE","MAR","HLT","MELI",
    "SE","GRAB","YNDX",
    "NVAX", "INCY", "EDIT", "BLUE", "ACAD", "ALNY", "SGEN", "CELG",
    "BGNE", "DXCM", "MGLN", "NBIX", "XOMA", "VTRS", "VSTM", "VIVO",
    "ZS", "ZM", "DOCU", "TEAM", "TWLO", "MDB", "FVRR", "UPST", "ROKU",
    "AFRM", "RBLX", "U", "PATH", "HOOD", "VTI", "VOO", "SPY", "IVV",
    "QQQ", "DIA", "IWM", "EEM", "VNQ", "XLF", "XLK", "XLY", "XLC",
    "XLI", "XLE", "XLV", "XLB", "XLU", "XBI", "ARKK", "ARKG", "ARKW",
    "ARKF", "ARKQ", "ARKX", "VGT", "VHT", "VFH", "VPU", "VDE", "VDC",
    "VOX", "VCR", "VIS", "VO", "VB", "VBR", "VOE", "VOT", "VUG", "VTV",
    "VYM", "SCHD", "DGRO", "VIG", "DVY", "SPHD", "SPYD", "HDV", "SDY",
    "NOBL", "PFF", "BND", "AGG", "LQD", "HYG", "JNK", "EMB", "MUB",
    "TIP", "GOVT", "SHY", "IEF", "TLT", "GLD", "SLV", "DBC", "USO",
    "UNG", "UUP", "FXE", "FXY"
]

analyzer = SentimentIntensityAnalyzer()

# --- פונקציות אינדיקטורים טכניים ---

def compute_rsi(close_prices, window=14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def compute_macd(close_prices, fast=12, slow=26, signal=9):
    exp1 = close_prices.ewm(span=fast, adjust=False).mean()
    exp2 = close_prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - signal_line
    return macd.iloc[-1], signal_line.iloc[-1], macd_hist.iloc[-1]

def compute_bollinger_bands(close_prices, window=20, num_std=2):
    rolling_mean = close_prices.rolling(window=window).mean()
    rolling_std = close_prices.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean.iloc[-1], upper_band.iloc[-1], lower_band.iloc[-1]

# --- שליפת נתוני מניה עם אינדיקטורים נוספים ---

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        if len(hist) < 60:
            logging.warning(f"Not enough data for {ticker}")
            return None

        today_close = hist['Close'][-1]
        yesterday_close = hist['Close'][-2]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        today_volume = hist['Volume'][-1]
        avg_volume = hist['Volume'][-30:].mean()
        ma10 = hist['Close'][-10:].mean()
        ma50 = hist['Close'][-50:].mean()

        # אינדיקטורים חדשים
        rsi = compute_rsi(hist['Close'])
        macd_val, macd_signal, macd_hist = compute_macd(hist['Close'])
        bb_mid, bb_upper, bb_lower = compute_bollinger_bands(hist['Close'])

        return {
            "ticker": ticker,
            "today_close": today_close,
            "change_pct": change_pct,
            "today_volume": today_volume,
            "avg_volume": avg_volume,
            "ma10": ma10,
            "ma50": ma50,
            "rsi": rsi,
            "macd": macd_val,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "bb_mid": bb_mid,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "hist": hist
        }
    except Exception as e:
        logging.error(f"Error getting stock data for {ticker}: {e}")
        return None

# --- ניתוח סנטימנט חדשות ---

def get_news_sentiment(ticker, max_items=5):
    try:
        rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        sentiments = []
        for entry in feed.entries[:max_items]:
            vs = analyzer.polarity_scores(entry.title)
            sentiments.append(vs['compound'])
        return sum(sentiments) / len(sentiments) if sentiments else 0.0
    except Exception as e:
        logging.error(f"Error getting news sentiment for {ticker}: {e}")
        return 0.0

# --- ניתוח סנטימנט מטוויטר (באמצעות RSS חיפוש טוויטר) ---

def get_twitter_sentiment(ticker, max_items=5):
    try:
        rss_url = f"https://twitrss.me/twitter_search_to_rss/?term=%24{ticker}&count={max_items}"
        feed = feedparser.parse(rss_url)
        sentiments = []
        for entry in feed.entries[:max_items]:
            vs = analyzer.polarity_scores(entry.title)
            sentiments.append(vs['compound'])
        return sum(sentiments) / len(sentiments) if sentiments else 0.0
    except Exception as e:
        logging.error(f"Error getting twitter sentiment for {ticker}: {e}")
        return 0.0

# --- סנטימנט משולב (70% חדשות, 30% טוויטר) ---

def combined_sentiment(ticker):
    news_sent = get_news_sentiment(ticker)
    twitter_sent = get_twitter_sentiment(ticker)
    combined = news_sent * 0.7 + twitter_sent * 0.3
    return combined

# --- פונקציית ניקוד משודרגת עם אינדיקטורים וסנטימנט ---

def score_stock(stock_data, sentiment):
    score = 0.0

    change_pct = stock_data['change_pct']
    today_volume = stock_data['today_volume']
    avg_volume = stock_data['avg_volume']
    ma10 = stock_data['ma10']
    ma50 = stock_data['ma50']
    rsi = stock_data['rsi']
    macd = stock_data['macd']
    macd_signal = stock_data['macd_signal']
    bb_upper = stock_data['bb_upper']
    bb_lower = stock_data['bb_lower']
    today_close = stock_data['today_close']

    # 1. שינוי אחוזי במחיר (עד 20 נקודות)
    abs_change = min(abs(change_pct), 10)
    score += (abs_change / 10) * 20

    # 2. נפח מסחר (עד 20 נקודות)
    volume_ratio = today_volume / avg_volume if avg_volume > 0 else 0
    if volume_ratio > 1:
        score += min((volume_ratio - 1) / 2 * 20, 20)

    # 3. מגמת ממוצעים נעים (עד 10 נקודות)
    if ma10 > ma50:
        score += 10
    else:
        score += 5

    # 4. סנטימנט חדשות משולב (עד 20 נקודות)
    sentiment_score = max(min((sentiment + 1) / 2, 1), 0)
    score += sentiment_score * 20

    # 5. אינדיקטור RSI (עד 10 נקודות) - יעד: בין 30 ל-70 זה טוב
    if 30 < rsi < 70:
        score += 10
    elif rsi >= 70:
        score += max(0, 10 - (rsi - 70))
    else:
        score += max(0, 10 - (30 - rsi))

    # 6. אינדיקטור MACD (עד 10 נקודות)
    if macd > macd_signal:
        score += 10
    else:
        score += 5

    # 7. מיקום מחיר ביחס לבולינגר בנדס (עד 10 נקודות)
    if today_close < bb_lower:
        score += 10
    elif today_close > bb_upper:
        score += 5
    else:
        score += 8

    # תיקון ניקוד בין 0 ל-100
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return round(score, 2)

# --- פונקציית שליחת מייל ---

def send_email(subject, body, to_email, html=False):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        part = MIMEText(body, "html" if html else "plain")
        msg.attach(part
