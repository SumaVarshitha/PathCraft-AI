"""
Google ADK 2.0 (Agent Development Kit 2.0) Core Engine
Provides native Google ADK 2.0 Agent, Tool, Runner, and State abstractions powered by Gemini models
with automated retry, rate-limit backoff, and multi-model failover resilience.
"""

import os
import time
import json
from typing import Dict, Any, List, Optional, Type, Union
from google import genai
from google.genai import types
from pydantic import BaseModel
import config

class ADKTool:
    """Represents a tool bound to a Google ADK 2.0 Agent."""
    def __init__(self, name: str, description: str = "", tool_object: Any = None, tool_instance: Any = None):
        self.name = name
        self.description = description
        self.tool_object = tool_instance if tool_instance is not None else tool_object

class ADKAgent:
    """
    Google ADK 2.0 Agent Class
    Encapsulates an autonomous agent powered by Gemini models with instruction,
    tools (e.g. Google Search Grounding), structured output schemas,
    and automatic failover across model tiers when 503 / 429 errors occur.
    """
    def __init__(
        self,
        name: str,
        instruction: str,
        model: str = config.MODEL_FLASH,
        tools: Optional[List[ADKTool]] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1
    ):
        self.name = name
        self.instruction = instruction
        self.model = model
        self.tools = tools or []
        self.output_schema = output_schema
        self.temperature = temperature
        
        api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
        self.client = genai.Client(api_key=api_key) if api_key else None

    def execute(self, prompt_input: Union[str, List[Any]], system_context: str = "") -> Any:
        """
        Executes the ADK Agent with automated retry and multi-model fallback on 503 / 429 errors.
        """
        api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
        if api_key:
            self.client = genai.Client(api_key=api_key)

        if not self.client:
            raise ValueError(f"⚠️ GOOGLE_API_KEY missing for ADK 2.0 Agent '{self.name}'. Please configure your Google Gemini API Key.")

        full_contents = []
        combined_instruction = f"{self.instruction}\n\n{system_context}".strip()
        full_contents.append(combined_instruction)
        
        if isinstance(prompt_input, list):
            full_contents.extend(prompt_input)
        else:
            full_contents.append(str(prompt_input))

        # Build Google Gen AI Types Config
        gen_config = types.GenerateContentConfig(
            temperature=self.temperature
        )

        if self.output_schema:
            gen_config.response_mime_type = "application/json"

        # Bind Tools if configured (e.g. Search Grounding)
        genai_tools = []
        for t in self.tools:
            if t.tool_object:
                genai_tools.append(t.tool_object)
        if genai_tools:
            gen_config.tools = genai_tools

        # Candidate models to try in order of preference
        models_to_try = [self.model]
        for fallback in config.FALLBACK_MODELS:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None

        for model_candidate in models_to_try:
            # Try up to 2 attempts per model with short backoff
            for attempt in range(2):
                try:
                    response = self.client.models.generate_content(
                        model=model_candidate,
                        contents=full_contents,
                        config=gen_config
                    )
                    
                    # If structured schema requested, parse JSON safely
                    if self.output_schema:
                        text = response.text.strip()
                        if "```json" in text:
                            text = text.split("```json")[-1].split("```")[0].strip()
                        elif "```" in text:
                            text = text.split("```")[1].split("```")[0].strip()
                        if "{" in text and "}" in text:
                            text = text[text.find("{"):text.rfind("}")+1]
                        return json.loads(text)
                    
                    return response.text.strip()

                except Exception as e:
                    err_str = str(e)
                    last_error = e
                    # Check for 503 (High Demand / Unavailable) or 429 (Rate Limit / Quota)
                    is_transient = "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str or "RESOURCE_EXHAUSTED" in err_str or "demand" in err_str.lower()
                    
                    if is_transient:
                        print(f"[ADK Resilience Notice] Model '{model_candidate}' experienced transient spike (attempt {attempt+1}/2). Backing off...", flush=True)
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    else:
                        # Non-transient error, try next model candidate
                        break

        print(f"[ADK 2.0 Agent Error] '{self.name}' across all model tiers: {last_error}", flush=True)
        raise last_error

class ADKRunner:
    """
    Google ADK 2.0 Team Runner
    Orchestrates execution sequences across an ADK Agent team.
    """
    def __init__(self, agents: List[ADKAgent]):
        self.agents = {agent.name: agent for agent in agents}

    def get_agent(self, name: str) -> ADKAgent:
        return self.agents[name]
