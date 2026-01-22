from textblob import TextBlob

def verify_statement(text):
    """
    Analyzes witness statements for sentiment and potential contradictions.
    """
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity # -1 to 1
    subjectivity = blob.sentiment.subjectivity # 0 to 1
    
    score = 0
    details = []
    
    details.append(f"Sentiment Polarity: {sentiment:.2f} (Negative < 0 < Positive)")
    details.append(f"Subjectivity: {subjectivity:.2f} (0=Objective, 1=Subjective)")
    
    if subjectivity > 0.7:
        score += 40
        details.append("High subjectivity detected. Statement may be biased or emotional rather than factual.")
    
    if sentiment < -0.5 or sentiment > 0.5:
        details.append("Strong emotional language detected.")
        
    # Simple contradiction check (very basic)
    sentences = blob.sentences
    if len(sentences) > 1:
        # Check if sentiment flips drastically between sentences
        prev_sent = sentences[0].sentiment.polarity
        for i in range(1, len(sentences)):
            curr_sent = sentences[i].sentiment.polarity
            if (prev_sent > 0.5 and curr_sent < -0.5) or (prev_sent < -0.5 and curr_sent > 0.5):
                score += 30
                details.append(f"Potential tonal contradiction detected between sentence {i} and {i+1}.")
            prev_sent = curr_sent

    return {
        'score': min(100, score),
        'details': " | ".join(details)
    }
