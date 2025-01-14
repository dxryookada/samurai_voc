from textblob import TextBlob

def analyze_free_text(text):
    if not text:
        return None  # テキストが空の場合
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    # ポジティブ、ネガティブ、ニュートラルを5段階評価に変換
    if polarity > 0.5:
        return 5
    elif polarity > 0.2:
        return 4
    elif polarity > -0.2:
        return 3
    elif polarity > -0.5:
        return 2
    else:
        return 1