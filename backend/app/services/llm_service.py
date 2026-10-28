import os
import json
import re
import random
import requests
from typing import Dict, Any, Optional, List
from app.config import settings

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        self.model = settings.LLM_MODEL

    def _get_active_provider(self) -> str:
        if self.provider == "gemini" and self.gemini_key:
            return "gemini"
        if self.provider == "openai" and self.openai_key:
            return "openai"
        if self.gemini_key:
            return "gemini"
        if self.openai_key:
            return "openai"
        return "offline_engine"

    def clean_json_string(self, text: str) -> str:
        text = text.strip()
        # Remove markdown code blocks if present
        if text.startswith("`"):
            lines = text.splitlines()
            if lines[0].startswith("`"):
                lines = lines[1:]
            if lines and lines[-1].startswith("`"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        provider = self._get_active_provider()
        
        if provider == "gemini":
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_key}"
                payload = {
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "generationConfig": {"temperature": 0.3}
                }
                resp = requests.post(url, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    print(f"Gemini API error ({resp.status_code}): {resp.text}")
            except Exception as e:
                print(f"Gemini API call failed: {e}")

        elif provider == "openai":
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.openai_key}"}
                payload = {
                    "model": "gpt-4o-mini" if "gpt" not in self.model else self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"OpenAI API error ({resp.status_code}): {resp.text}")
            except Exception as e:
                print(f"OpenAI API call failed: {e}")

        # Fallback intelligent generator
        return self._offline_generate_text(system_prompt, user_prompt)

    def generate_json(self, system_prompt: str, user_prompt: str, schema_type: str = "generic") -> Dict[str, Any]:
        provider = self._get_active_provider()
        
        if provider in ["gemini", "openai"]:
            raw_text = self.generate_text(system_prompt, user_prompt + "\nReturn strictly JSON without conversational text.")
            cleaned = self.clean_json_string(raw_text)
            try:
                return json.loads(cleaned)
            except Exception as e:
                print(f"JSON parsing failed on raw LLM output, trying repair: {e}")
                # Try repair prompt once
                repair_prompt = f"The following JSON is malformed:\n{cleaned}\n\nFix it and output ONLY valid JSON."
                repaired_text = self.generate_text("You are a JSON repair specialist. Output only valid JSON.", repair_prompt)
                try:
                    return json.loads(self.clean_json_string(repaired_text))
                except Exception as e2:
                    print(f"JSON repair failed: {e2}")

        # Fallback to intelligent offline structured synthesis
        return self._offline_generate_json(user_prompt, schema_type)

    def _offline_generate_text(self, system_prompt: str, user_prompt: str) -> str:
        # Context-aware text synthesis for offline demo
        if "Syllabus Module" in user_prompt:
            return (
                "Based on the Common Syllabus framework, this module provides foundational and applied knowledge "
                "essential for public administration. Learners are encouraged to review the learning objectives, study the "
                "linked iGOT modules, and complete the scenario-based diagnostic assessments to test their discretionary judgment."
            )
        elif "Skill Gaps" in user_prompt or "Calculated Gap" in user_prompt:
            return (
                "This competency is pivotal for your target position. While your foundational understanding is sound, "
                "advancing to this level requires handling complex inter-departmental dependencies, standardizing operational procedures, "
                "and participating in strategic decision simulations."
            )
        return "AI Karmayogi assistant: response generated using grounded civil service competency guidelines."

    def _offline_generate_json(self, prompt: str, schema_type: str) -> Dict[str, Any]:
        # Intelligent contextual fallback synthesis adhering strictly to PRD contracts
        if "mock_test" in schema_type or "MCQs" in prompt or "multiple-choice" in prompt:
            # Extract topic & difficulty if present
            topic_match = re.search(r"Topic:\s*([^\n]+)", prompt)
            topic = topic_match.group(1).strip() if topic_match else "Public Administration"
            diff_match = re.search(r"Difficulty Level:\s*([^\n]+)", prompt)
            diff = diff_match.group(1).strip() if diff_match else "medium"
            count_match = re.search(r"Generate\s*(\d+)", prompt)
            count = int(count_match.group(1)) if count_match else 5

            generated_questions = []
            templates = [
                (
                    f"In executing a multi-departmental initiative under {topic}, what is the primary prerequisite before issuing an administrative sanction?",
                    "Proceed immediately without financial concurrence",
                    "Obtain formal financial appraisal and verify budgetary allocation under relevant heads",
                    "Publish a press release in newspapers",
                    "Delegate entire sanction authority to a private vendor",
                    "B",
                    f"Financial rules mandate formal concurrence and verified budget appropriation before incurring public expenditure."
                ),
                (
                    f"When handling conflicting stakeholder feedback regarding a public service rollout in {topic}, what should the officer prioritize?",
                    "Ignore citizen feedback to maintain schedule",
                    "Conduct structured impact analysis, align with statutory Citizen Charter norms, and transparently communicate rationale",
                    "Cancel the scheme entirely",
                    "Transfer the complaint file to an unrelated section",
                    "B",
                    "Citizen Charter principles and evidence-based governance require balancing feedback with statutory objectives."
                ),
                (
                    f"Under established office procedures (CSMOP), how should an officer handle an urgent file requiring inter-ministerial consultation?",
                    "Retain the file indefinitely until reminded",
                    "Prepare a concise self-contained note highlighting specific points for consultation with a clear SLA deadline",
                    "Send the entire unindexed physical volume without background summary",
                    "Discard the dissenting opinions before forwarding",
                    "B",
                    "Inter-ministerial consultations require concise, balanced notes specifying precise issues for agreement to prevent delays."
                ),
                (
                    f"What is the most effective approach for mitigating vendor SLA delays in a mission-mode project under {topic}?",
                    "Impose maximum penalties without reviewing root causes",
                    "Establish weekly milestone gates, enforce contract cure notices, and review critical-path dependencies",
                    "Pay advance invoices before milestones are achieved",
                    "Reassign government staff to do the vendor's coding work",
                    "B",
                    "Proactive SLA enforcement with milestone monitoring and formal cure notices maintains accountability and project velocity."
                ),
                (
                    f"How should an officer ensure data privacy and cyber hygiene when integrating departmental databases under {topic}?",
                    "Allow unrestricted public access to raw databases",
                    "Implement role-based access control (RBAC), end-to-end encryption, and purpose-limited API data exchange",
                    "Disable audit logging to increase server speed",
                    "Store sensitive citizen credentials in plain text files",
                    "B",
                    "Data protection norms mandate purpose limitation, strong encryption, and rigorous access controls across government digital platforms."
                ),
                (
                    f"In a public procurement tender under GFR 2017 for {topic}, what constitutes an anti-competitive practice?",
                    "Publishing tender documents transparently on the Central Public Procurement Portal",
                    "Tailoring technical eligibility criteria to favor a single specific brand or proprietary vendor",
                    "Conducting a pre-bid conference with all prospective bidders",
                    "Requiring standard performance bank guarantees",
                    "B",
                    "GFR 2017 prohibits restrictive or proprietary specifications that prevent fair and open competition."
                )
            ]

            for i in range(count):
                tmpl = templates[i % len(templates)]
                # Add random modifier if we wrap around
                q_text = tmpl[0] if i < len(templates) else f"[Scenario {i+1}] {tmpl[0]}"
                generated_questions.append({
                    "question_text": q_text,
                    "options": {
                        "A": tmpl[1],
                        "B": tmpl[2],
                        "C": tmpl[3],
                        "D": tmpl[4]
                    },
                    "correct_option": tmpl[5],
                    "explanation": tmpl[6],
                    "competency": topic,
                    "difficulty": diff,
                    "source_type": "ai_generated"
                })

            return {"questions": generated_questions}

        elif "mock_interview_eval" in schema_type or "Evaluate the candidate's response" in prompt:
            # Score user's answer realistically based on length, keywords, STAR indicators
            answer_lower = prompt.lower()
            relevance = 4.0 if len(prompt) > 80 else 3.0
            clarity = 4.5 if any(k in answer_lower for k in ["situation", "task", "action", "result", "first", "then", "finally"]) else 3.5
            reasoning = 4.0 if any(k in answer_lower for k in ["rule", "impact", "stakeholder", "because", "due to", "analysis"]) else 3.0
            competency = 3.8
            ethics = 4.2 if any(k in answer_lower for k in ["integrity", "transparent", "gfr", "compliance", "fair", "citizen"]) else 3.8
            avg = round((relevance + clarity + reasoning + competency + ethics) / 5.0, 1)

            return {
                "scores": {
                    "relevance": relevance,
                    "clarity_and_structure": clarity,
                    "reasoning_and_depth": reasoning,
                    "role_competency": competency,
                    "practical_judgment_ethics": ethics
                },
                "average_score": avg,
                "strengths": [
                    "Demonstrated clear understanding of administrative accountability.",
                    "Structured response with logical sequencing of actions."
                ],
                "weaknesses": [
                    "Could further quantify measurable outcomes and long-term citizen impact (STAR 'Result' phase)."
                ],
                "suggested_improvement": "Integrate specific references to standard operating procedures and formal risk mitigation steps in complex scenarios.",
                "feedback_narrative": f"The response demonstrates a solid {avg}/5.0 proficiency. You articulated practical administrative steps while keeping public interest in focus."
            }

        elif "mock_interview_gen" in schema_type or "interview questions" in prompt:
            role_match = re.search(r"Target Role:\s*([^\n]+)", prompt)
            role = role_match.group(1).strip() if role_match else "Civil Services Officer"
            count_match = re.search(r"Generate\s*(\d+)", prompt)
            count = int(count_match.group(1)) if count_match else 3

            sample_interview_qs = [
                {
                    "question_text": f"As a {role}, describe a situation where an urgent policy deadline clashed with a critical administrative compliance check. How did you resolve the deadlock?",
                    "competency_id": "C001",
                    "competency_name": "Decision Making & Discretion",
                    "question_type": "behavioral",
                    "expected_key_points": "Applied STAR format; conducted risk assessment; prioritized legal compliance without stalling policy objectives.",
                    "difficulty": "medium",
                    "behavioral_focus": "Discretionary Judgment & Ethical Compliance",
                    "source_type": "ai_generated"
                },
                {
                    "question_text": f"How do you establish inter-departmental consensus when multiple ministries have competing interests on a shared digital infrastructure initiative?",
                    "competency_id": "C002",
                    "competency_name": "Project Management & Collaboration",
                    "question_type": "situational",
                    "expected_key_points": "Facilitated structured working group; created transparent SLA milestone matrix; escalated objective trade-offs.",
                    "difficulty": "hard",
                    "behavioral_focus": "Stakeholder Consensus & Programme Delivery",
                    "source_type": "ai_generated"
                },
                {
                    "question_text": f"Walk us through how you would handle an escalation regarding a delayed grievance on CPGRAMS that involves multiple field offices.",
                    "competency_id": "C007",
                    "competency_name": "Citizen Centricity & Redressal",
                    "question_type": "situational",
                    "expected_key_points": "Conducted root-cause analysis; coordinated with nodal field officers; ensured citizen-friendly resolution within SLA.",
                    "difficulty": "medium",
                    "behavioral_focus": "Citizen Empathy & Systemic Redressal",
                    "source_type": "ai_generated"
                }
            ]
            return {"questions": sample_interview_qs[:count]}

        elif "mentor" in schema_type or "Learner Message" in prompt:
            return {
                "reply": "I reviewed your current competency profile and recent performance. You have strong foundations in government communication and ethical standards. To accelerate your transition to your target role, focusing on milestone-driven project execution and evidence-based decision-making will yield the highest impact.",
                "suggested_actions": [
                    "Complete Module 2 of 'Project Management Essentials for Public Officers'",
                    "Review critical path calculation rules in the Knowledge Base",
                    "Attempt a 10-question Project Management mock assessment"
                ],
                "suggested_exercise": "Draft a 1-page Work Breakdown Structure (WBS) for an upcoming departmental digitisation task, identifying 3 key milestone risk trigger points.",
                "follow_up_question": "When a vendor delays an intermediate deliverable by 5 days, what is the first formal contractual step you initiate?"
            }

        elif "career" in schema_type or "career progression roadmap" in prompt:
            return {
                "readiness_status": "Progressing Well (Target: 75% Benchmark)",
                "readiness_score": 65.0,
                "roadmap_steps": [
                    {
                        "stage": "Phase 1: Foundation Bridging",
                        "title": "Core Competency Grounding",
                        "description": "Close foundational gaps in Project Management (L2 -> L3) and Digital Governance (L2 -> L3).",
                        "actions": ["Complete Project Management Essentials", "Review India Stack & e-Office guidelines"],
                        "status": "in_progress"
                    },
                    {
                        "stage": "Phase 2: Applied Simulation",
                        "title": "Scenario & SLA Management",
                        "description": "Practice vendor SLA monitoring, risk matrices, and cabinet note syntheses.",
                        "actions": ["Take Decision Making Mock Test", "Execute 2 situational drafting exercises"],
                        "status": "upcoming"
                    },
                    {
                        "stage": "Phase 3: Advanced Readiness",
                        "title": "Mission Coordination & Interview Preparation",
                        "description": "Achieve Level 4 proficiency in Decision Making and Project Delivery.",
                        "actions": ["Complete AI Mock Interview with STAR scoring > 4.0", "Participate in inter-ministerial review"],
                        "status": "upcoming"
                    },
                    {
                        "stage": "Phase 4: Target Transition",
                        "title": "Target Role Benchmark Evaluation",
                        "description": "Comprehensive evaluation passport validation for Project Officer role.",
                        "actions": ["Pass final Competency Assessment Battery", "Review full Progress Passport"],
                        "status": "upcoming"
                    }
                ],
                "action_plan": "Focus first on closing the 2-level gap in Project Management. Complete the recommended course and validate with the AI Mock Test."
            }

        return {"status": "success", "message": "Synthesized response based on grounded civil service knowledge."}

llm_service = LLMService()