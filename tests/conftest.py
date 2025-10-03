"""
Pytest configuration and shared fixtures for SmartBill Analytics tests
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor


@pytest.fixture
def sample_clean_csv(tmp_path):
    """Create a clean sample CSV file for testing"""
    csv_path = tmp_path / "clean_tickets.csv"

    data = {
        'created_at': [
            '2025-10-01 10:00:00',
            '2025-10-01 11:30:00',
            '2025-10-02 09:15:00',
            '2025-10-02 14:45:00',
            '2025-10-03 08:30:00',
        ],
        'closed_at': [
            '2025-10-01 12:00:00',
            '2025-10-01 15:00:00',
            '2025-10-02 11:00:00',
            '2025-10-02 16:30:00',
            '',  # Not closed yet
        ],
        'platform': ['facturare', 'gestiune', 'api', 'spv', 'facturare'],
        'area': ['SPV', 'Documente', 'Sincronizare', 'Rapoarte', 'Clienti'],
        'urgency': ['blocker', 'mediu', 'scazut', 'blocker', 'mediu'],
        'sentiment': ['negativ', 'neutru', 'pozitiv', 'negativ', 'pozitiv'],
        'is_recurrent': ['TRUE', 'FALSE', 'FALSE', 'TRUE', 'FALSE'],
        'affects_business_flow': ['TRUE', 'FALSE', 'FALSE', 'TRUE', 'FALSE'],
        'problem_type': ['bug', 'feature_gap', 'usability', 'bug', 'documentation'],
        'pain_point': [
            'Aplicatia se blocheaza',
            'Lipseste functionalitate export PDF',
            'Interfata confuza pentru rapoarte',
            'Eroare la sincronizare',
            'Documentatie incompleta'
        ],
        'summary': [
            'Blocare aplicatie la export',
            'Cerere export PDF',
            'Probleme UI rapoarte',
            'Sync failure',
            'Docs missing info'
        ],
        'tip': ['problema tehnica', 'feature request', 'problema tehnica', 'problema tehnica', 'intrebare contabila/fiscala'],
        'ticket_url': [f'https://smartbill.com/ticket/{i}' for i in range(1, 6)],
        'customer_email_extracted': [f'user{i}@test.com' for i in range(1, 6)],
    }

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

    return str(csv_path)


@pytest.fixture
def sample_dirty_csv(tmp_path):
    """Create a dirty CSV file with real-world messy data"""
    csv_path = tmp_path / "dirty_tickets.csv"

    data = {
        ' ': [0, 1, 2, 3, 4],  # Empty index column
        'created_at': [
            '2025-10-01 10:00:00',
            '2025-10-01 11:30:00',
            '2025-10-02 09:15:00',
            '2025-10-02 14:45:00',
            '2025-10-03 08:30:00',
        ],
        'closed_at': [
            '2025-10-01 12:00:00',
            '',
            '2025-10-02 11:00:00',
            '',
            '',
        ],
        'platform': ['Facturare', 'GESTIUNE', 'api', '1', 'Conta'],  # Mixed case, unexpected values
        'area': ['SPV', 'Documente', 'Sincronizare', 'Rapoarte', 'Clienti'],
        'urgency': [
            'Blocker',  # Mixed case
            'Fisierul bon.txt nu poate fi creat',  # Full sentence instead of category
            'scazut',
            'BLOCKER',
            'mediu'
        ],
        'sentiment': [
            'NEGATIV',  # Uppercase
            'Clientul a intampinat o eroare la tipărirea bonului si este foarte suparat',  # Full paragraph
            'pozitiv',
            'Negativ',
            'neutru'
        ],
        'is_recurrent': ['true', 'False', 'YES', '1', '0'],  # Mixed formats
        'affects_business_flow': ['TRUE', 'no', 'yes', 'TRUE', 'FALSE'],  # Mixed formats
        'problem_type': ['Bug', 'FALSE', 'usability', 'bug', 'No info - cere sa fie contactat'],  # Mixed data
        'pain_point': [
            'Aplicatia se blocheaza',
            'Lipseste functionalitate export PDF',
            'Interfata confuza pentru rapoarte',
            '',  # Missing
            'Documentatie incompleta'
        ],
        'summary': [
            'Blocare aplicatie la export',
            '',  # Missing
            'Probleme UI rapoarte',
            'Sync failure',
            'Docs missing info'
        ],
        'tip': ['Problema Tehnica', 'Feature Request', 'FALSE', 'problema tehnica', 'Feedback General'],
        'ticket_url': [f'https://smartbill.com/ticket/{i}' for i in range(1, 6)],
        'customer_email_extracted': [f'user{i}@test.com' for i in range(1, 6)],
        'classification_index': [1, 2, 1, 3, 1],  # Extra columns
        'total_classifications': [1, 2, 1, 3, 1],
        'Comments': ['', 'Urgent', '', 'Check with dev team', '']
    }

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

    return str(csv_path)


@pytest.fixture
def sample_empty_csv(tmp_path):
    """Create an empty CSV with headers only"""
    csv_path = tmp_path / "empty_tickets.csv"

    data = {
        'created_at': [],
        'platform': [],
        'area': [],
    }

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

    return str(csv_path)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    np.random.seed(42)
    n = 50

    now = datetime.now()

    data = {
        'created_at': [now - timedelta(days=np.random.randint(0, 90)) for _ in range(n)],
        'closed_at': [now - timedelta(days=np.random.randint(0, 85)) if i % 3 != 0 else pd.NaT for i in range(n)],
        'platform': np.random.choice(['facturare', 'gestiune', 'api', 'spv'], n),
        'area': np.random.choice(['SPV', 'Documente', 'Clienti', 'Rapoarte'], n),
        'urgency': np.random.choice(['blocker', 'mediu', 'scazut'], n),
        'sentiment': np.random.choice(['pozitiv', 'neutru', 'negativ'], n),
        'is_recurrent': np.random.choice([True, False], n),
        'affects_business_flow': np.random.choice([True, False], n),
        'problem_type': np.random.choice(['bug', 'feature_gap', 'usability', 'documentation'], n),
        'pain_point': [f'Pain point {i}' for i in range(n)],
        'summary': [f'Summary {i}' for i in range(n)],
        'tip': np.random.choice(['problema tehnica', 'feature request'], n),
    }

    df = pd.DataFrame(data)
    return CSVProcessor.process_dataframe(df)


@pytest.fixture
def mock_streamlit_session_state(monkeypatch):
    """Mock Streamlit session state for testing"""
    class MockSessionState:
        def __init__(self):
            self._state = {}

        def __getattr__(self, name):
            return self._state.get(name)

        def __setattr__(self, name, value):
            if name == '_state':
                object.__setattr__(self, name, value)
            else:
                self._state[name] = value

        def __contains__(self, name):
            return name in self._state

        def get(self, name, default=None):
            return self._state.get(name, default)

    session_state = MockSessionState()

    # Mock st.session_state
    import streamlit as st
    monkeypatch.setattr(st, 'session_state', session_state)

    return session_state


@pytest.fixture
def date_range_fixture():
    """Provide a standard date range for testing"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return (start_date, end_date)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure Playwright browser context for E2E tests"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
    }
