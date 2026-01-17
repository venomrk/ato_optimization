from typing import List, Optional
from loguru import logger
from .base import Agent, AgentConfig, AgentType
from .claude_agent import ClaudeAgent
from .openai_agent import OpenAIAgent
from .gemini_agent import GeminiAgent
from .generic_agent import GenericAgent


class AgentFactory:
    @staticmethod
    def create_agent(config: AgentConfig) -> Agent:
        if config.agent_type in [AgentType.CLAUDE_3, AgentType.CLAUDE_3_SONNET]:
            return ClaudeAgent(config)
        elif config.agent_type in [AgentType.GPT4_TURBO, AgentType.GPT4O, AgentType.O1, AgentType.O3]:
            return OpenAIAgent(config)
        elif config.agent_type == AgentType.GEMINI_2:
            return GeminiAgent(config)
        else:
            return GenericAgent(config)
    
    @staticmethod
    def create_agent_pool(
        openai_keys: List[str],
        anthropic_keys: List[str],
        google_keys: List[str],
        deepseek_key: Optional[str] = None,
        qwen_key: Optional[str] = None,
        xai_key: Optional[str] = None,
        yi_key: Optional[str] = None,
        max_agents: int = 15
    ) -> List[Agent]:
        agents = []
        
        if anthropic_keys:
            for i, key in enumerate(anthropic_keys[:2]):
                configs = [
                    AgentConfig(
                        agent_type=AgentType.CLAUDE_3,
                        api_key=key,
                        model_name="claude-3-opus-20240229",
                        enable_thinking=True
                    ),
                    AgentConfig(
                        agent_type=AgentType.CLAUDE_3_SONNET,
                        api_key=key,
                        model_name="claude-3-5-sonnet-20241022",
                        enable_thinking=True
                    ),
                ]
                for config in configs:
                    if len(agents) < max_agents:
                        agents.append(AgentFactory.create_agent(config))
        
        if openai_keys:
            for i, key in enumerate(openai_keys[:3]):
                configs = [
                    AgentConfig(
                        agent_type=AgentType.GPT4O,
                        api_key=key,
                        model_name="gpt-4o",
                        temperature=0.7
                    ),
                    AgentConfig(
                        agent_type=AgentType.O1,
                        api_key=key,
                        model_name="o1-preview",
                        temperature=1.0
                    ),
                ]
                for config in configs:
                    if len(agents) < max_agents:
                        agents.append(AgentFactory.create_agent(config))
        
        if google_keys:
            for key in google_keys[:2]:
                config = AgentConfig(
                    agent_type=AgentType.GEMINI_2,
                    api_key=key,
                    model_name="gemini-2.0-flash-thinking-exp",
                    enable_thinking=True
                )
                if len(agents) < max_agents:
                    agents.append(AgentFactory.create_agent(config))
        
        if deepseek_key and len(agents) < max_agents:
            config = AgentConfig(
                agent_type=AgentType.DEEPSEEK_R1,
                api_key=deepseek_key,
                model_name="deepseek-reasoner",
                enable_thinking=True
            )
            agents.append(AgentFactory.create_agent(config))
        
        if qwen_key and len(agents) < max_agents:
            config = AgentConfig(
                agent_type=AgentType.QWEN_QWQ,
                api_key=qwen_key,
                model_name="qwq-32b-preview",
                enable_thinking=True
            )
            agents.append(AgentFactory.create_agent(config))
        
        if xai_key and len(agents) < max_agents:
            config = AgentConfig(
                agent_type=AgentType.GROK_2,
                api_key=xai_key,
                model_name="grok-2-latest",
                temperature=0.8
            )
            agents.append(AgentFactory.create_agent(config))
        
        if yi_key and len(agents) < max_agents:
            config = AgentConfig(
                agent_type=AgentType.YI_LIGHTNING,
                api_key=yi_key,
                model_name="yi-lightning",
                enable_thinking=True
            )
            agents.append(AgentFactory.create_agent(config))
        
        logger.info(f"Created agent pool with {len(agents)} agents")
        return agents
