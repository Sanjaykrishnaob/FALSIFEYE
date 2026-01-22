import json
import os
import torch
from sentence_transformers import SentenceTransformer, util

class ForensicKnowledgeBase:
    def __init__(self, kb_path=None):
        print("Importing AI libraries and loading model...")
        if kb_path is None:
            # Use absolute path relative to this file
            self.kb_path = os.path.join(os.path.dirname(__file__), 'forensic_knowledge.json')
        else:
            self.kb_path = kb_path
            
        self.model = None
        self.corpus_embeddings = None
        self.kb_data = []

        try:
            # Force CPU to avoid potential CUDA/GPU crashes on startup if GPU is problematic
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            print("SentenceTransformer model loaded on CPU.")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to load SentenceTransformer model: {e}")
            return

        # Load Knowledge Base
        if os.path.exists(self.kb_path):
            try:
                with open(self.kb_path, 'r') as f:
                    self.kb_data = json.load(f)
                print(f"Knowledge base loaded from {self.kb_path} with {len(self.kb_data)} entries.")
            except Exception as e:
                print(f"ERROR: Failed to read knowledge base file: {e}")
                self.kb_data = []
        else:
            print(f"WARNING: Knowledge base file not found at {self.kb_path}")
            self.kb_data = []
            
        # Pre-compute embeddings for all KB entries
        if self.kb_data and self.model:
            try:
                print("Computing embeddings for knowledge base...")
                self.corpus_embeddings = self.model.encode(
                    [entry['response'] for entry in self.kb_data], 
                    convert_to_tensor=True
                )
                print("Embeddings computed successfully.")
            except Exception as e:
                print(f"ERROR: Failed to compute embeddings: {e}")

    def find_best_match(self, query):
        """
        Uses Semantic Search to find the most relevant expert response.
        """
        if self.model is None or self.corpus_embeddings is None:
            print("DEBUG: Model or embeddings not initialized.")
            return None

        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            
            # Compute cosine similarity
            cos_scores = util.cos_sim(query_embedding, self.corpus_embeddings)[0]
            top_result = torch.topk(cos_scores, k=1)
            
            score = top_result.values[0].item()
            idx = top_result.indices[0].item()
            
            print(f"DEBUG: Best match score: {score}")

            if score > 0.35: # Confidence threshold
                return self.kb_data[idx]['response']
        except Exception as e:
            print(f"ERROR in find_best_match: {e}")
            
        return None

# Initialize Global Instance (Load model once)
# This might take a few seconds on startup, but subsequent queries are instant.
kb_engine = None
try:
    print("Loading Forensic AI Chatbot Model...")
    kb_engine = ForensicKnowledgeBase()
    if kb_engine.model is None:
         print("WARNING: Forensic AI Chatbot Model failed to initialize properly (model is None).")
    else:
        print("Forensic AI Chatbot Model Loaded Successfully.")
except Exception as e:
    print(f"ERROR loading Forensic AI Chatbot Model: {e}")
    kb_engine = None

def get_chat_response(user_query, context):
    """
    AI-Powered Forensic Chatbot using Semantic Search (RAG).
    """
    print(f"DEBUG: Chat Request: {user_query}")
    
    # Extract context variables
    score = context.get('score', 0)
    details = context.get('details', 'No specific details found.')
    evidence_type = context.get('type', 'unknown')
    file_hash = context.get('file_hash', 'N/A')
    
    print(f"DEBUG: Context - Score: {score}, Type: {evidence_type}")

    # 1. Check for Context-Specific Queries (Dynamic Injection)
    query = user_query.lower()
    if "score" in query or "rating" in query:
        verdict = "High Probability of Manipulation" if score > 50 else "Likely Authentic"
        return f"The forensic analysis score is **{score}/100**. Verdict: **{verdict}**. {details}"
        
    if "why" in query and ("fake" in query or "flag" in query):
        return f"The system flagged this file based on the following anomalies: {details}"

    # 2. Semantic Search in Knowledge Base
    if kb_engine:
        print("DEBUG: Running Semantic Search...")
        try:
            expert_response = kb_engine.find_best_match(query)
            print(f"DEBUG: Expert Response Found: {expert_response is not None}")
        except Exception as e:
            print(f"DEBUG: Semantic Search Failed: {e}")
            expert_response = None
        
        if expert_response:
            # Inject dynamic variables into the static expert response
            try:
                return expert_response.format(
                    score=score,
                    ela_diff="Detected", # Placeholder, ideally passed from context
                    fft_score="High",    # Placeholder
                    file_hash=file_hash[:10] + "...",
                    mfcc_var="Low"       # Placeholder
                )
            except KeyError as e:
                print(f"DEBUG: Formatting Error: {e}")
                return expert_response
            except Exception as e:
                 # Fallback if format fails for other reasons
                 return expert_response

    # 3. Fallback
    return "I am a specialized Forensic AI. I can explain terms like **ELA**, **FFT**, **Chain of Custody**, or interpret the **Score** for you. Please ask a specific legal or technical question."
