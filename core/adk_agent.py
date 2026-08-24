"""
Google ADK 2.0 (Agent Development Kit 2.0) Core Engine
Provides native Google ADK 2.0 Agent, Tool, Runner, and State abstractions powered by Gemini 2.5 models.
"""

import os
import json
from typing import Dict, Any, List, Optional, Type, Union
from google import genai
from google.genai import types
from pydantic import BaseModel
import config

class ADKTool:
    """Represents a tool bound to a Google ADK 2.0 Agent."""
    def __init__(self, name: str, description: str, tool_object: Any = None):
        self.name = name
        self.description = description
        self.tool_object = tool_object

class ADKAgent:
    """
    Google ADK 2.0 Agent Class
    Encapsulates an autonomous agent powered by Gemini 2.5 models with instruction,
    tools (e.g. Google Search Grounding), and structured output schemas.
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
        """Executes the ADK Agent using Gemini 2.5 with configured tools and output schemas."""
        if not self.client:
            api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
            if not api_key:
                raise ValueError(f"GOOGLE_API_KEY missing for ADK 2.0 Agent '{self.name}'")
            self.client = genai.Client(api_key=api_key)

        full_contents = []
        
        # Add system context if provided
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

        # Bind Output Schema if configured
        if self.output_schema:
            gen_config.response_mime_type = "application/json"
            gen_config.response_schema = self.output_schema

        # Bind Tools if configured (e.g. Search Grounding)
        genai_tools = []
        for t in self.tools:
            if t.tool_object:
                genai_tools.append(t.tool_object)
        if genai_tools:
            gen_config.tools = genai_tools

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_contents,
                config=gen_config
            )
            
            # If structured schema, parse JSON
            if self.output_schema:
                try:
                    return json.loads(response.text)
                except Exception:
                    text = response.text.strip()
                    if "```json" in text:
                        text = text.split("```json")[-1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                    return json.loads(text)
            
            return response.text.strip()

        except Exception as e:
            print(f"[ADK 2.0 Agent Error] '{self.name}': {e}")
            raise e


class ADKRunner:
    """
    Google ADK 2.0 Team Runner
    Orchestrates execution sequences across an ADK Agent team.
    """
    def __init__(self, agents: List[ADKAgent]):
        self.agents = {agent.name: agent for agent in agents}

    def get_agent(self, name: str) -> ADKAgent:
        return self.agents[name]
