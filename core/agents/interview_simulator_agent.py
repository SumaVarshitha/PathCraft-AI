from typing import List, Dict, Any
import config
from core.adk_agent import ADKAgent
from core.state import EvaluationResult

class InterviewSimulatorADKAgent(ADKAgent):
    """
    Google ADK 2.0 Interview Simulator Agent
    Conducts interactive technical interview Q&A and evaluates candidate answers.
    """
    def __init__(self):
        super().__init__(
            name="InterviewSimulatorADKAgent",
            instruction="You are an expert Technical Interviewer Agent. Ask direct technical questions testing candidate skill gaps and evaluate candidate answers.",
            model=config.MODEL_FLASH,
            temperature=0.3
        )

    def generate_question(self, target_role: str, missing_skills: List[str], chat_history: List[Dict[str, Any]]) -> str:
        skills_str = ", ".join(missing_skills[:3]) if missing_skills else "software engineering fundamentals"
        prompt = f"""
        Target Role: {target_role}
        Skills to Test: [{skills_str}]
        Chat History: {chat_history}

        Ask the candidate ONE concise, realistic, technical interview question testing knowledge of [{skills_str}].
        """
        try:
            return self.execute(prompt_input=prompt)
        except Exception as e:
            print(f"[ADK 2.0 Interview Simulator Error]: {e}")
            return f"Can you explain how you handle concurrency and error handling in {missing_skills[0] if missing_skills else 'your primary stack'}?"

    def evaluate_answer(self, question: str, candidate_answer: str, target_role: str) -> Dict[str, Any]:
        prompt = f"""
        Target Role: {target_role}
        Question: "{question}"
        Candidate Answer: "{candidate_answer}"

        Evaluate technical accuracy, depth, and clarity.
        Return JSON object with keys:
        {{"score": int (0-100), "feedback": "2-3 sentences", "key_takeaway": "1 sentence advice"}}
        """
        try:
            # Re-initialize runner with EvaluationResult schema for strict response
            eval_agent = ADKAgent(
                name="EvaluatorSubAgent",
                instruction="Evaluate technical interview answers strictly.",
                model=config.MODEL_FLASH,
                output_schema=EvaluationResult,
                temperature=0.1
            )
            return eval_agent.execute(prompt_input=prompt)
        except Exception as e:
            print(f"[ADK 2.0 Evaluator Error]: {e}")
            return {
                "score": 75,
                "feedback": "Solid effort! Provide quantitative metrics and specific tool mechanisms in future answers.",
                "key_takeaway": "Focus on production scalability details."
            }
