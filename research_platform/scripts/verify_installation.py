#!/usr/bin/env python3
"""
Verify that the Multi-Agent Research Platform is properly installed and configured.
"""

import sys
from pathlib import Path
import importlib.util

sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking Python imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "chromadb",
        "arxiv",
        "pymed",
        "scholarly",
        "anthropic",
        "openai",
        "google.generativeai",
        "httpx",
        "pdfplumber",
        "PyPDF2",
        "loguru",
        "sentence_transformers",
    ]
    
    failed = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Missing modules: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required modules installed\n")
    return True


def check_config():
    """Check if configuration is valid."""
    print("Checking configuration...")
    
    try:
        from config import get_settings
        settings = get_settings()
        
        print(f"  ✓ Settings loaded")
        print(f"  - Database: {settings.database_url}")
        print(f"  - Vector DB: {settings.vector_db_type}")
        print(f"  - Max Agents: {settings.max_agents}")
        
        api_keys_found = 0
        if settings.openai_api_keys:
            print(f"  ✓ OpenAI API keys: {len(settings.openai_api_keys)}")
            api_keys_found += len(settings.openai_api_keys)
        
        if settings.anthropic_api_keys:
            print(f"  ✓ Anthropic API keys: {len(settings.anthropic_api_keys)}")
            api_keys_found += len(settings.anthropic_api_keys)
        
        if settings.google_api_keys:
            print(f"  ✓ Google API keys: {len(settings.google_api_keys)}")
            api_keys_found += len(settings.google_api_keys)
        
        if settings.deepseek_api_key:
            print(f"  ✓ DeepSeek API key configured")
            api_keys_found += 1
        
        if settings.qwen_api_key:
            print(f"  ✓ Qwen API key configured")
            api_keys_found += 1
        
        if api_keys_found == 0:
            print("\n  ⚠️  No API keys configured")
            print("  Edit .env file and add at least one LLM provider API key")
            return False
        
        print(f"\n✅ Configuration valid ({api_keys_found} API keys configured)\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}\n")
        return False


def check_directories():
    """Check if required directories exist."""
    print("Checking directory structure...")
    
    base_path = Path(__file__).parent.parent
    
    required_dirs = [
        "agents",
        "extractors",
        "storage",
        "api",
        "config",
        "scripts",
        "tests"
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_exist = False
    
    if all_exist:
        print("\n✅ All directories present\n")
    else:
        print("\n❌ Some directories missing\n")
    
    return all_exist


def check_agents():
    """Check if agents can be created."""
    print("Checking agent creation...")
    
    try:
        from config import get_settings
        from agents import AgentFactory
        
        settings = get_settings()
        
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
        
        if len(agents) == 0:
            print("  ⚠️  No agents created (check API keys)")
            return False
        
        print(f"  ✓ Created {len(agents)} agents:")
        for agent in agents:
            print(f"    - {agent.agent_type.value}")
        
        print(f"\n✅ Agent system functional\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent creation failed: {e}\n")
        return False


def check_extractors():
    """Check if paper extractors work."""
    print("Checking paper extractors...")
    
    try:
        from extractors import (
            ArxivExtractor,
            PubMedExtractor,
            SemanticScholarExtractor,
            CrossRefExtractor,
            GoogleScholarExtractor
        )
        
        extractors = [
            ("arXiv", ArxivExtractor),
            ("PubMed", PubMedExtractor),
            ("Semantic Scholar", SemanticScholarExtractor),
            ("CrossRef", CrossRefExtractor),
            ("Google Scholar", GoogleScholarExtractor),
        ]
        
        for name, ExtractorClass in extractors:
            try:
                extractor = ExtractorClass()
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name}: {e}")
        
        print(f"\n✅ Extractors initialized\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Extractor check failed: {e}\n")
        return False


def check_storage():
    """Check if storage systems work."""
    print("Checking storage systems...")
    
    try:
        from storage import get_database, get_vector_store
        from config import get_settings
        
        settings = get_settings()
        
        db = get_database(settings.database_url)
        print(f"  ✓ Database initialized")
        
        vector_store = get_vector_store(settings.vector_db_type)
        print(f"  ✓ Vector store initialized ({settings.vector_db_type})")
        
        print(f"\n✅ Storage systems functional\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Storage check failed: {e}\n")
        return False


def main():
    print("=" * 80)
    print("Multi-Agent Research Platform - Installation Verification")
    print("=" * 80)
    print()
    
    checks = [
        ("Python Imports", check_imports),
        ("Configuration", check_config),
        ("Directory Structure", check_directories),
        ("Agent System", check_agents),
        ("Paper Extractors", check_extractors),
        ("Storage Systems", check_storage),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}\n")
            results[check_name] = False
    
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print()
    
    if all(results.values()):
        print("✅ All checks passed! Platform is ready to use.")
        print()
        print("Next steps:")
        print("  1. Start the platform: docker-compose up -d")
        print("  2. Check health: curl http://localhost:8000/health")
        print("  3. View API docs: http://localhost:8000/docs")
        print()
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Configure API keys: cp .env.example .env && edit .env")
        print("  - Download spaCy model: python -m spacy download en_core_web_sm")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
