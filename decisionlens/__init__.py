"""DecisionLens: local evidence and decision support, extended from Rag_chatbot."""
import os
from pathlib import Path
os.environ.setdefault('HF_HOME',str(Path(__file__).resolve().parents[1]/'.cache/huggingface'))
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY','1')
__version__ = '0.1.0'
