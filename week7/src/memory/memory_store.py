import json
import os
from datetime import datetime

class MemoryStore:
    def __init__(self, log_file="CHAT-LOGS.json"):
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def append_message(self, endpoint, user_query, ai_response, score=None, critique="None", feedback="None"):
        """Saves the interaction to the local JSON log."""
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        if isinstance(score, (int, float)):
            faithfulness_label = "Faithful" if score >= 80 else "Unfaithful"
        else:
            faithfulness_label = "Unknown (Error)"
            
        entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "user_query": user_query,
            "ai_response": ai_response,
            "critique": critique,  
            "confidence_score": score,
            "faithfulness_status": faithfulness_label,
            "human_feedback": feedback # <--- Boom! Saved to the audit log.
        }
        
        logs.append(entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)

    def get_last_n_messages(self, n=5):
        """Retrieves the last N messages to inject as conversational memory."""
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        # Grab the last N items, format them as a memory string
        recent_logs = logs[-n:]
        memory_string = "Conversation History:\n"
        for log in recent_logs:
            memory_string += f"User: {log['user_query']}\nAI: {log['ai_response']}\n---\n"
            
        return memory_string if recent_logs else "Conversation History: None\n"