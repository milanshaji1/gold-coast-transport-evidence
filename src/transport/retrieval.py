"""Small lexical baseline. Returned passages are untrusted evidence, never commands."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Retriever:
    def __init__(self,documents):
        self.documents=[d for d in documents if d.get('status')=='current']
        self.vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2))
        self.matrix=self.vectorizer.fit_transform([d['title']+' '+d['text'] for d in self.documents]) if self.documents else None

    def search(self,query,limit=5):
        if not isinstance(query,str) or not 1<=len(query.strip())<=500: raise ValueError('query must contain 1–500 characters')
        if type(limit) is not int or not 1<=limit<=5: raise ValueError('limit must be 1–5')
        if self.matrix is None: return []
        scores=cosine_similarity(self.vectorizer.transform([query]),self.matrix)[0]
        return [{**self.documents[i],'score':float(scores[i]),'trust':'untrusted_source_text'} for i in sorted(range(len(scores)),key=lambda i:(-scores[i],self.documents[i]['id']))[:limit] if scores[i]>=.08]
