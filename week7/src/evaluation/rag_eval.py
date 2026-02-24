import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Evaluator:
    def __init__(self):
        # We use temperature=0 for strict, mathematical grading
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    def grade_and_refine(self, question, draft_answer, context="N/A"):
        """Grades the draft answer and refines it if it detects hallucinations."""
        
        # 1. Hallucination & Faithfulness Detection
        eval_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI auditor. Score the drafted answer from 0 to 100 based on its faithfulness to the context and lack of hallucination. Output ONLY the integer score."),
            ("user", f"Question: {question}\nContext/Data: {context}\nDraft Answer: {draft_answer}\n\nScore (0-100):")
        ])
        
        chain = eval_prompt | self.llm
        try:
            score_response = chain.invoke({})
            score = int(score_response.content.strip())
        except:
            score = 50 # Default safe score if parsing fails

        # 2. Refinement Loop (Self-Correction)
        if score < 80:
            print(f"⚠️ [System Alert] Low Confidence Score ({score}/100) Detected. Triggering Refinement Loop...")
            refine_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert editor. The previous answer was graded poorly. Rewrite it to be accurate, concise, and directly address the user's question without hallucinating."),
                ("user", f"Question: {question}\nFlawed Answer: {draft_answer}\n\nPlease provide the refined, perfect answer:")
            ])
            refine_chain = refine_prompt | self.llm
            final_answer = refine_chain.invoke({}).content
            return final_answer, score
            
        return draft_answer, score