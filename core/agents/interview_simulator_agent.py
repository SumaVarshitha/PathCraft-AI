import os
import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
import config
from core.adk_agent import ADKAgent
from core.state import EvaluationResult, InterviewTurn

class InterviewSimulatorADKAgent(ADKAgent):
    """
    Google ADK 2.0 Conversational AI Mock Interviewer Agent
    - Conducts multi-turn technical interviews (3, 5, or 10 questions).
    - Tests candidate missing skills (70% weight) + core foundational competencies (30% weight).
    - Evaluates each answer turn-by-turn with a 0-100 rubric score, strengths/gaps analysis,
      and production-grade model answers.
    - Generates a final Comprehensive Interview Scorecard & Readiness Report.
    """
    def __init__(self):
        super().__init__(
            name="InterviewSimulatorADKAgent",
            instruction="Conduct rigorous, realistic multi-turn technical interviews for engineering roles.",
            model=config.MODEL_PRO,
            temperature=0.3
        )

    def generate_next_question(
        self,
        target_role: str,
        missing_skills: List[str],
        verified_skills: List[str],
        turn_index: int,
        total_questions: int = 5,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        difficulty: str = "Senior"
    ) -> Dict[str, str]:
        """
        Generates the next technical interview question in the sequence.
        Focuses on missing skills for 70% of questions and core verified skills / system design for 30%.
        """
        chat_history = chat_history or []
        
        # Decide skill focus
        if turn_index < len(missing_skills) and turn_index < int(total_questions * 0.75):
            focus_skill = missing_skills[turn_index % len(missing_skills)]
            question_type = "Skill Gap Deep Dive"
        else:
            core_pool = verified_skills if verified_skills else ["System Design & Production Architecture"]
            focus_skill = core_pool[turn_index % len(core_pool)]
            question_type = "Core Architecture & Scalability"

        prompt = f"""
        You are a Principal Tech Lead conducting a {difficulty}-level technical interview for a '{target_role}' candidate.
        
        Current Question: #{turn_index + 1} of {total_questions}
        Focus Area: {focus_skill} ({question_type})
        Candidate Skill Gaps: {missing_skills}
        Candidate Strengths: {verified_skills}
        
        Previous Conversation Transcript:
        {json.dumps(chat_history[-4:], indent=2) if chat_history else 'Interview starting.'}

        Ask ONE concise, challenging, production-scenario technical interview question testing their practical understanding of {focus_skill}.
        Avoid generic trivia; ask how they would design, debug, optimize, or implement a solution.
        Do NOT include conversational introductions (e.g. 'Hello', 'Great job on last question'). Ask ONLY the question.
        """
        
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.4)
                )
                question_text = response.text.strip()
                return {
                    "question": question_text,
                    "skill_focus": focus_skill,
                    "question_type": question_type
                }
            except Exception as e:
                print(f"[InterviewSimulator Notice]: {e}", flush=True)

        return {
            "question": f"In a high-throughput production environment for a {target_role}, how would you architect and optimize data consistency and fault-tolerance using {focus_skill}?",
            "skill_focus": focus_skill,
            "question_type": question_type
        }

    def evaluate_answer(
        self,
        question: str,
        candidate_answer: str,
        target_role: str,
        skill_focus: str,
        difficulty: str = "Senior"
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's answer with a 0-100 rubric, constructive feedback,
        actionable advice, and a reference model answer.
        """
        if not candidate_answer or len(candidate_answer.strip()) < 5:
            return {
                "score": 20,
                "feedback": "Answer was too brief to demonstrate technical competence. Provide concrete technical mechanisms and trade-offs.",
                "key_takeaway": "Elaborate with specific code, architectural design patterns, or metrics.",
                "model_answer_snippet": f"A strong answer should outline specific APIs, data partitioning, indexing, and error retry strategies in {skill_focus}."
            }

        prompt = f"""
        Target Role: {difficulty} {target_role}
        Skill Focus: {skill_focus}
        Interview Question: "{question}"
        Candidate Answer: "{candidate_answer}"

        Evaluate this answer as a hiring manager:
        1. Score out of 100 based on technical depth, correctness, production considerations, and edge case handling.
        2. Constructive feedback: 2 sentences highlighting what was good and what critical nuances were missing.
        3. Key takeaway: 1 actionable sentence for real-world interviews.
        4. Model answer snippet: 2 sentences illustrating the ideal technical answer or best practice.

        Return ONLY a JSON object:
        {{
            "score": 85,
            "feedback": "...",
            "key_takeaway": "...",
            "model_answer_snippet": "..."
        }}
        """

        if self.client:
            try:
                eval_agent = ADKAgent(
                    name="EvaluatorSubAgent",
                    instruction="Evaluate technical interview answers strictly with production standards.",
                    model=config.MODEL_FLASH,
                    output_schema=EvaluationResult,
                    temperature=0.1
                )
                return eval_agent.execute(prompt_input=prompt)
            except Exception as e:
                print(f"[Interview Evaluator Notice]: {e}", flush=True)

        # Baseline evaluation
        length = len(candidate_answer.split())
        score = min(92, max(50, 60 + length // 4))
        return {
            "score": score,
            "feedback": f"Demonstrates solid conceptual understanding of {skill_focus}. To reach top percentile, include concrete throughput numbers and failure recovery strategies.",
            "key_takeaway": "Always emphasize trade-offs and monitoring metrics when discussing architecture.",
            "model_answer_snippet": f"In production {skill_focus}, prioritize idempotent operations, backpressure mechanisms, and distributed logging."
        }

    def generate_final_report_card(
        self,
        target_role: str,
        turns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculates cumulative score and generates a final interview report card."""
        if not turns:
            return {"overall_score": 0, "readiness": "Incomplete", "summary": "No completed turns."}

        scores = [t.get("evaluation", {}).get("score", 70) for t in turns if t.get("evaluation")]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        if avg_score >= 85:
            readiness = "🟢 Strong Hire / Staff Ready"
            summary = f"Outstanding performance! The candidate demonstrated deep technical mastery across {target_role} requirements with strong architectural thinking."
        elif avg_score >= 70:
            readiness = "🟡 Hire / Solid Mid-Senior"
            summary = f"Good technical competency. Candidate communicates well and understands fundamentals, with minor opportunities to deepen distributed edge case handling."
        else:
            readiness = "🟠 Needs Dedicated Upskilling"
            summary = f"The candidate has promising potential but needs hands-on project practice with core tools and architectural trade-offs before interviewing."

        return {
            "overall_score": avg_score,
            "readiness": readiness,
            "summary": summary,
            "total_questions_answered": len(turns),
            "scores_history": scores
        }
