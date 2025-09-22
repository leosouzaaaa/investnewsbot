import math, requests, numpy as np, pandas as pd
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
from .config import NEWSAPI_KEY, MONTHS_BACK
try:
    from transformers import pipeline
    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except Exception:
    VADER_AVAILABLE = False
cg = CoinGeckoAPI()
hf_classifier = None; vader = None
if HF_AVAILABLE:
    try: hf_classifier = pipeline('sentiment-analysis')
    except Exception: hf_classifier = None
if VADER_AVAILABLE:
    vader = SentimentIntensityAnalyzer()
def analyze_sentiment(texts):
    if not texts: return 0.0
    scores = []
    if hf_classifier:
        try:
            for i in range(0,len(texts),16):
                batch = texts[i:i+16]
                results = hf_classifier(batch)
                for r in results:
                    label = r.get('label','')
                    s = r.get('score',0.5)
                    scores.append(-s if label.upper().startswith('NEG') else s)
        except Exception:
            pass
    if not scores and vader:
        for t in texts:
            v = vader.polarity_scores(t); scores.append(v['compound'])
    if not scores:
        for t in texts:
            t_low = t.lower(); s = 0
            for w in ['gain','growth','bull','surge','up','record','positive','buy']:
                if w in t_low: s += 0.3
            for w in ['fall','drop','bear','down','crash','loss','negative','sell','plunge']:
                if w in t_low: s -= 0.3
            scores.append(max(-1,min(1,s)))
    return float(np.mean(scores))
def fetch_news(query, from_dt, to_dt, page_size=100):
    if not NEWSAPI_KEY: return []
    url = 'https://newsapi.org/v2/everything'
    params = {'q': query, 'from': from_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
              'to': to_dt.strftime('%Y-%m-%dT%H:%M:%SZ'), 'language':'en', 'pageSize':page_size, 'sortBy':'relevancy', 'apiKey': NEWSAPI_KEY}
    try:
        r = requests.get(url, params=params, timeout=15); r.raise_for_status(); return r.json().get('articles',[])
    except Exception:
        return []
def extract_texts(articles):
    texts = []
    for a in articles:
        parts = []
        for k in ['title','description','content']:
            v = a.get(k)
            if v: parts.append(v)
        if parts: texts.append('. '.join(parts))
    return texts
def compute_volatility(series):
    if series is None or series.empty or len(series)<2: return 0.0
    returns = series.pct_change().dropna(); return float(returns.std()*math.sqrt(252))
def fetch_stock_history(ticker, period='6mo'):
    try:
        import yfinance as yf
        t = yf.Ticker(ticker); hist = t.history(period=period)
        if hist.empty: return pd.Series(dtype=float)
        return hist['Close'].astype(float)
    except Exception:
        return pd.Series(dtype=float)
def fetch_crypto_history(slug, days=180):
    try:
        data = cg.get_coin_market_chart_by_id(id=slug, vs_currency='usd', days=days)
        prices = data.get('prices',[])
        if not prices: return pd.Series(dtype=float)
        df = pd.DataFrame(prices, columns=['ts','price']); df['ts']=pd.to_datetime(df['ts'], unit='ms'); df.set_index('ts', inplace=True)
        return df['price'].astype(float)
    except Exception:
        return pd.Series(dtype=float)
class AssetRecommendation:
    def __init__(self,symbol,asset_type,sentiment_score,volatility,news_volume,risk_score,recommendation,confidence):
        self.symbol=symbol; self.asset_type=asset_type; self.sentiment_score=sentiment_score; self.volatility=volatility
        self.news_volume=news_volume; self.risk_score=risk_score; self.recommendation=recommendation; self.confidence=confidence
def compute_risk_score(sentiment,volatility,news_volume):
    s_factor=(1-sentiment)/2; vol_factor=min(1.0,volatility/1.5); news_factor=1-1/(1+math.log1p(news_volume))
    raw=0.5*s_factor+0.3*vol_factor+0.2*news_factor; return float(max(0,min(100,raw*100)))
def decide_recommendation(opportunity):
    if opportunity>70: return 'Strong Buy', min(0.99,(opportunity-60)/40+0.6)
    elif opportunity>50: return 'Buy', min(0.9,(opportunity-40)/30+0.5)
    elif opportunity>35: return 'Hold', 0.5
    elif opportunity>20: return 'Reduce', 0.4
    else: return 'Sell', 0.3
def aggregate_metrics_for_asset(asset,asset_type,months_back=MONTHS_BACK):
    to_dt=datetime.utcnow(); from_dt=to_dt - timedelta(days=30*months_back)
    articles = fetch_news(asset, from_dt, to_dt)
    texts = extract_texts(articles); sentiment = analyze_sentiment(texts); news_volume=len(articles)
    if asset_type=='stock': prices=fetch_stock_history(asset, period=f'{months_back}mo')
    else: prices=fetch_crypto_history(asset, days=30*months_back)
    volatility=compute_volatility(prices); trend_score=0.0
    if not prices.empty and len(prices)>=2:
        ret=(prices.iloc[-1]/prices.iloc[0])-1; trend_score=float(np.tanh(ret*3))*50+50
    sentiment_score_mapped=(sentiment+1)/2*100
    opportunity=0.5*sentiment_score_mapped + 0.3*trend_score + 0.2*(1-min(1.0,volatility/1.5))*100
    risk=compute_risk_score(sentiment,volatility,news_volume)
    recommendation,confidence=decide_recommendation(opportunity)
    return AssetRecommendation(asset,asset_type,sentiment,volatility,news_volume,round(risk,2),recommendation,round(confidence,2))
def generate_suggestions(stocks, cryptos, max_daily=5):
    assets=[]
    for s in stocks: assets.append(aggregate_metrics_for_asset(s,'stock'))
    for c in cryptos: assets.append(aggregate_metrics_for_asset(c,'crypto'))
    df = pd.DataFrame([a.__dict__ for a in assets])
    def score_row(r):
        rec_val = {'Strong Buy':100,'Buy':80,'Hold':50,'Reduce':30,'Sell':10}.get(r['recommendation'],50)
        return rec_val - r['risk_score']/5
    if not df.empty:
        df['sort_score'] = df.apply(score_row, axis=1); df.sort_values('sort_score', ascending=False, inplace=True)
    daily = df.head(max_daily).to_dict(orient='records') if not df.empty else []
    weekly = df.head(max_daily*2).to_dict(orient='records') if not df.empty else []
    monthly = df.head(max_daily*4).to_dict(orient='records') if not df.empty else []
    return {'daily':daily,'weekly':weekly,'monthly':monthly,'12_months':df.to_dict(orient='records') if not df.empty else []}
