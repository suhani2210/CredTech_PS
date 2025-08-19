import feedparser
from transformers import pipeline

sentiment_model = pipeline("text-classification",
                           model="ProsusAI/finbert")
label_to_score = {"positive": 1, "neutral": 0.5, "negative": 0}

def news_sentiment_score(ticker):

    feed = feedparser.parse(f"https://news.google.com/rss/search?q={ticker}+stocks")
    headlines = [entry.title for entry in feed.entries]

    results = sentiment_model(headlines, batch_size=128)
    
    scores = []
    for h, r in zip(headlines, results):
        l=r["label"]
        if l!="neutral":
            scores.append((h, label_to_score[l] * r["score"]))

    if scores:
        daily_sentiment = sum(s for _, s in scores) / len(scores)
    else:
        daily_sentiment = 0.0
    scaled_sentiment = (daily_sentiment+1)/2

    return(scaled_sentiment)