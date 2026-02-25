import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Evaluator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    def grade_and_refine(self, question, draft_answer, context="N/A"):
        """Grades the draft answer and refines it if it detects hallucinations."""
        
        try:
            # 1. Hallucination & Faithfulness Detection (No more f-strings!)
            eval_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an AI auditor. Score the drafted answer from 0 to 100 based on its faithfulness to the context. Output ONLY the integer score."),
                ("user", "Question: {question}\nContext/Data: {context}\nDraft Answer: {draft_answer}\n\nScore (0-100):")
            ])
            
            chain = eval_prompt | self.llm
            # Safely pass variables via invoke
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
                    ("system", "You are an expert editor. Rewrite the previous answer to be accurate and directly address the user's question without hallucinating. IMPORTANT: You must explicitly list out the actual data records using bullet points. Do NOT just provide a total count."),
                    ("user", "Question: {question}\nFlawed Answer: {draft_answer}\n\nPlease provide the refined, perfect answer:")
                ])
                refine_chain = refine_prompt | self.llm
                # Safely pass variables via invoke
                final_answer = refine_chain.invoke({
                    "question": question,
                    "draft_answer": draft_answer
                }).content

                
                return final_answer, score
                
            return draft_answer, score
            
        except Exception as e:
            # THE SAFETY NET: Catches API rate limits or grading crashes
            print(f"\n  [Warning] Evaluation skipped due to API limits or parsing errors: {str(e)[:100]}...")
            return draft_answer, "Skipped (Error)"