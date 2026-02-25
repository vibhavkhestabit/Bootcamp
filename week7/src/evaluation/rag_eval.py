import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Evaluator:
    def __init__(self):
        # Everything from here down MUST be indented 8 spaces (or 2 tabs)
        config_path = "src/config/model.yaml"
        
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            
        model_name = config.get("model_name", "gemini-2.5-flash-lite")
        
        # Initialize the Auditor LLM
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)

    def grade_and_refine(self, question, draft_answer, context="N/A"):
        """Grades the draft answer and refines it if it detects hallucinations."""
        
        try:
            # 1. Hallucination & Faithfulness Detection
            eval_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an AI auditor. Score the drafted answer from 0 to 100 based on its faithfulness to the context. Output ONLY the integer score."),
                ("user", "Question: {question}\nContext/Data: {context}\nDraft Answer: {draft_answer}\n\nScore (0-100):")
            ])
            
            chain = eval_prompt | self.llm
            score_response = chain.invoke({
                "question": question,
                "context": context,
                "draft_answer": draft_answer
            })
            score = int(score_response.content.strip())
            
            # 2. Refinement Loop (Self-Correction)
            if score < 80:
                print(f" [System Alert] Low Confidence Score ({score}/100) Detected. Triggering Refinement Loop...")
                refine_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an expert editor. Rewrite the previous answer to be accurate. IMPORTANT: Format EXACTLY like this:\nCRITIQUE: [1 sentence explaining the fix]\nREVISED ANSWER: [The perfect answer with bullet points]"),
                    ("user", "Question: {question}\nFlawed Answer: {draft_answer}")
                ])
                refine_chain = refine_prompt | self.llm
                raw_output = refine_chain.invoke({
                    "question": question,
                    "draft_answer": draft_answer
                }).content
                
                # Split the output safely
                if "REVISED ANSWER:" in raw_output:
                    parts = raw_output.split("REVISED ANSWER:")
                    critique = parts[0].replace("CRITIQUE:", "").strip()
                    final_answer = parts[1].strip()
                else:
                    critique = "Critique formatting failed."
                    final_answer = raw_output
                    
                return final_answer, score, critique
                
            return draft_answer, score, "None (Score was 80+, no refinement needed)"
            
        except Exception as e:
            print(f"\n  [Warning] Evaluation skipped due to API limits or parsing errors: {str(e)[:100]}...")
            return draft_answer, "Skipped (Error)", "Skipped"