from setuptools import setup, find_packages

setup(
    name="research-agent-system",
    version="0.1.0",
    description="Multi-agent research system using LangChain, Claude Sonnet 4.5, and Parallel.ai",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.3.27",
        "langchain-anthropic>=0.3.21",
        "langchain-community>=0.3.30",
        "langchain-core>=0.3.78",
        "parallel-sdk",
        "pydantic>=2.9.2",
        "pydantic-settings>=2.5.2",
        "python-dotenv>=1.0.1",
        "rich>=13.9.2",
        "aiohttp>=3.10.10",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
