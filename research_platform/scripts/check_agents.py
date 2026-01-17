#!/usr/bin/env python3
"""
Check which agents are available based on configured API keys.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings
from agents import AgentFactory


def main():
    print("=" * 80)
    print("Agent Availability Check")
    print("=" * 80)
    print()
    
    settings = get_settings()
    
    print("API Key Configuration:")
    print(f"  OpenAI Keys: {len(settings.openai_api_keys)}")
    print(f"  Anthropic Keys: {len(settings.anthropic_api_keys)}")
    print(f"  Google Keys: {len(settings.google_api_keys)}")
    print(f"  DeepSeek: {'✓' if settings.deepseek_api_key else '✗'}")
    print(f"  Qwen: {'✓' if settings.qwen_api_key else '✗'}")
    print(f"  X.AI (Grok): {'✓' if settings.xai_api_key else '✗'}")
    print(f"  Yi: {'✓' if settings.yi_api_key else '✗'}")
    print()
    
    print("Creating agent pool...")
    agents = AgentFactory.create_agent_pool(
        openai_keys=settings.openai_api_keys,
        anthropic_keys=settings.anthropic_api_keys,
        google_keys=settings.google_api_keys,
        deepseek_key=settings.deepseek_api_key,
        qwen_key=settings.qwen_api_key,
        xai_key=settings.xai_api_key,
        yi_key=settings.yi_api_key,
        max_agents=settings.max_agents
    )
    
    print(f"\n✓ Successfully initialized {len(agents)} agents:")
    print()
    
    for i, agent in enumerate(agents, 1):
        print(f"{i:2d}. {agent.agent_type.value:25s} | Model: {agent.config.model_name:30s} | Thinking: {agent.config.enable_thinking}")
    
    print()
    print("=" * 80)
    print(f"Total Agents: {len(agents)}/{settings.max_agents}")
    print("=" * 80)


if __name__ == "__main__":
    main()
