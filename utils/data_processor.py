"""
Data Processor Module for SmartBill Support Analytics
Handles CSV loading, parsing, validation and caching
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import chardet
from typing import Optional, Dict, List, Tuple


class CSVProcessor:
    """Process and validate SmartBill support ticket CSV files"""

    # Expected columns from the CSV structure (actual CSV has extra: classification_index, total_classifications, Comments)
    EXPECTED_COLUMNS = [
        'created_at', 'closed_at', 'ticket_url', 'mailbox_name',
        'customer_email_extracted', 'conversation', 'taxonomy',
        'tip', 'area', 'sentiment', 'apreciere_parere_support',
        'urgency', 'is_recurrent', 'agent_intervention_needed',
        'summary', 'user_goal', 'pain_point', 'problem_type',
        'affects_business_flow', 'platform', 'integration',
        'mentioned_features', 'specific_error_messages',
        'classification_index', 'total_classifications', 'Comments'  # Extra columns in actual CSV
    ]

    # Data types and their valid values (lowercase for consistency)
    VALID_VALUES = {
        'tip': ['problema tehnica', 'feature request', 'cerere administrativa/comerciala', 'intrebare contabila/fiscala'],
        'sentiment': ['pozitiv', 'neutru', 'negativ'],
        'urgency': ['blocker', 'mediu', 'scazut'],
        'platform': ['facturare', 'gestiune', 'api', 'aplicatie mobil', 'spv', 'niciunul'],
        'problem_type': ['feature_gap', 'usability', 'documentation', 'bug', 'performance', 'integration']
    }

    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Auto-detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read(100000))  # Read first 100KB
                return result['encoding'] or 'utf-8'
        except Exception as e:
            st.warning(f"Encoding detection failed: {e}. Using UTF-8.")
            return 'utf-8'

    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_csv(file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Load and parse CSV file with automatic encoding detection

        Args:
            file_path: Path to CSV file
            encoding: Optional encoding (auto-detected if None)

        Returns:
            Parsed DataFrame
        """
        try:
            # Auto-detect encoding if not provided
            if encoding is None:
                encoding = CSVProcessor.detect_encoding(file_path)

            # Try multiple encodings if first fails
            encodings_to_try = [encoding, 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

            df = None
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, encoding=enc, low_memory=False)

                    # Remove unnamed/empty first column if exists (index column from export)
                    if df.columns[0] in ['', ' ', 'Unnamed: 0']:
                        df = df.drop(columns=[df.columns[0]])

                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise ValueError("Could not decode file with any encoding")

            return df

        except Exception as e:
            st.error(f"Error loading CSV: {str(e)}")
            raise

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame structure and content (relaxed validation for real-world messy data)

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check for empty DataFrame
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors

        # Check for critical columns only (not all EXPECTED_COLUMNS - CSV may vary)
        critical_columns = ['created_at', 'platform', 'area']
        missing_critical = [col for col in critical_columns if col not in df.columns]
        if missing_critical:
            errors.append(f"Missing critical columns: {', '.join(missing_critical)}")

        # Check data types for created_at
        if 'created_at' in df.columns:
            try:
                pd.to_datetime(df['created_at'].head())
            except:
                errors.append("'created_at' column is not in valid date format")

        # Warnings for missing optional columns (not errors)
        optional_missing = set(CSVProcessor.EXPECTED_COLUMNS) - set(df.columns)
        if optional_missing:
            import streamlit as st
            st.warning(f"ℹ️ Optional columns missing: {', '.join(list(optional_missing)[:5])}")

        return len(errors) == 0, errors

    @staticmethod
    def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and process the DataFrame

        Processing steps:
        - Convert dates to datetime
        - Normalize text fields
        - Handle missing values
        - Add computed columns
        """
        df = df.copy()

        # Convert date columns
        date_columns = ['created_at', 'closed_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Normalize text fields (trim whitespace, lowercase for consistent filtering, handle NaN)
        text_columns = ['tip', 'area', 'sentiment', 'urgency', 'platform', 'problem_type']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
                df[col] = df[col].replace('nan', np.nan)

        # Convert boolean columns
        bool_columns = ['is_recurrent', 'agent_intervention_needed', 'affects_business_flow']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper().isin(['TRUE', 'YES', '1', 'T'])

        # Add computed columns
        df = CSVProcessor._add_computed_columns(df)

        return df

    @staticmethod
    def _add_computed_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add useful computed columns"""

        # Resolution time in hours
        if 'created_at' in df.columns and 'closed_at' in df.columns:
            df['resolution_time_hours'] = (
                (df['closed_at'] - df['created_at']).dt.total_seconds() / 3600
            )

        # Date components for grouping
        if 'created_at' in df.columns:
            df['created_date'] = df['created_at'].dt.date
            df['created_hour'] = df['created_at'].dt.hour
            df['created_day_of_week'] = df['created_at'].dt.day_name()
            df['created_week'] = df['created_at'].dt.isocalendar().week
            df['created_month'] = df['created_at'].dt.month
            df['created_year'] = df['created_at'].dt.year

        # Is closed flag
        if 'closed_at' in df.columns:
            df['is_closed'] = df['closed_at'].notna()

        # Priority score (custom calculation)
        df['priority_score'] = 0
        if 'urgency' in df.columns:
            df.loc[df['urgency'] == 'blocker', 'priority_score'] = 3
            df.loc[df['urgency'] == 'mediu', 'priority_score'] = 2
            df.loc[df['urgency'] == 'scazut', 'priority_score'] = 1

        if 'affects_business_flow' in df.columns:
            df.loc[df['affects_business_flow'] == True, 'priority_score'] += 2

        if 'is_recurrent' in df.columns:
            df.loc[df['is_recurrent'] == True, 'priority_score'] += 1

        return df

    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict:
        """Get summary statistics about the dataset"""
        summary = {
            'total_tickets': len(df),
            'date_range': {
                'start': df['created_at'].min() if 'created_at' in df.columns else None,
                'end': df['created_at'].max() if 'created_at' in df.columns else None
            },
            'missing_values': df.isnull().sum().to_dict(),
            'unique_values': {
                col: df[col].nunique()
                for col in df.columns
                if col in CSVProcessor.VALID_VALUES.keys()
            }
        }

        return summary

    @staticmethod
    def apply_filters(
        df: pd.DataFrame,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        platforms: Optional[List[str]] = None,
        areas: Optional[List[str]] = None,
        urgency_levels: Optional[List[str]] = None,
        sentiment: Optional[str] = None,
        only_recurrent: bool = False,
        affects_business: bool = False,
        search_text: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Apply filters to the DataFrame

        Args:
            df: DataFrame to filter
            date_range: Tuple of (start_date, end_date)
            platforms: List of platforms to include
            areas: List of areas to include
            urgency_levels: List of urgency levels to include
            sentiment: Sentiment filter ('toate', 'pozitiv', 'neutru', 'negativ')
            only_recurrent: Show only recurrent issues
            affects_business: Show only issues affecting business flow
            search_text: Text to search in pain_point and summary fields

        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()

        # Date range filter
        if date_range and 'created_at' in filtered_df.columns:
            # Validate date_range is a proper 2-tuple
            if not isinstance(date_range, tuple) or len(date_range) != 2:
                # Skip invalid date range
                pass
            else:
                start_date, end_date = date_range
                # Make timestamps timezone-aware if the column has timezone info
                start_ts = pd.Timestamp(start_date)
                end_ts = pd.Timestamp(end_date)
            if filtered_df['created_at'].dt.tz is not None:
                start_ts = start_ts.tz_localize('UTC')
                end_ts = end_ts.tz_localize('UTC')
            filtered_df = filtered_df[
                (filtered_df['created_at'] >= start_ts) &
                (filtered_df['created_at'] <= end_ts)
            ]

        # Platform filter
        if platforms and 'platform' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['platform'].isin(platforms)]

        # Area filter
        if areas and 'area' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['area'].isin(areas)]

        # Urgency filter
        if urgency_levels and 'urgency' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['urgency'].isin(urgency_levels)]

        # Sentiment filter
        if sentiment and sentiment != 'toate' and 'sentiment' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['sentiment'] == sentiment]

        # Recurrent filter
        if only_recurrent and 'is_recurrent' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['is_recurrent'] == True]

        # Business flow filter
        if affects_business and 'affects_business_flow' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['affects_business_flow'] == True]

        # Text search filter
        if search_text:
            search_text = search_text.lower()
            search_columns = ['pain_point', 'summary', 'user_goal']
            mask = False
            for col in search_columns:
                if col in filtered_df.columns:
                    mask |= filtered_df[col].astype(str).str.lower().str.contains(search_text, na=False)
            filtered_df = filtered_df[mask]

        return filtered_df

    @staticmethod
    def get_mock_data() -> pd.DataFrame:
        """Generate mock data for testing when no CSV is uploaded"""
        np.random.seed(42)

        n_records = 100
        now = datetime.now()

        data = {
            'created_at': [now - timedelta(days=np.random.randint(0, 90)) for _ in range(n_records)],
            'closed_at': [now - timedelta(days=np.random.randint(0, 85)) for _ in range(n_records)],
            'ticket_url': [f'https://smartbill.com/ticket/{i}' for i in range(n_records)],
            'mailbox_name': np.random.choice(['Support', 'Sales', 'Technical'], n_records),
            'customer_email_extracted': [f'user{i}@example.com' for i in range(n_records)],
            'conversation': [f'Conversation {i}' for i in range(n_records)],
            'taxonomy': np.random.choice(['Question', 'Problem', 'Request'], n_records),
            'tip': np.random.choice(CSVProcessor.VALID_VALUES['tip'], n_records),
            'area': np.random.choice(['SPV', 'Facturare', 'Gestiune', 'API', 'Mobile'], n_records),
            'sentiment': np.random.choice(CSVProcessor.VALID_VALUES['sentiment'], n_records),
            'apreciere_parere_support': np.random.choice(['Bun', 'Excelent', 'Mediu'], n_records),
            'urgency': np.random.choice(CSVProcessor.VALID_VALUES['urgency'], n_records),
            'is_recurrent': np.random.choice([True, False], n_records),
            'agent_intervention_needed': np.random.choice([True, False], n_records),
            'summary': [f'Summary of issue {i}' for i in range(n_records)],
            'user_goal': [f'User wants to {i}' for i in range(n_records)],
            'pain_point': [f'Pain point {i}' for i in range(n_records)],
            'problem_type': np.random.choice(CSVProcessor.VALID_VALUES['problem_type'], n_records),
            'affects_business_flow': np.random.choice([True, False], n_records),
            'platform': np.random.choice(CSVProcessor.VALID_VALUES['platform'], n_records),
            'integration': np.random.choice(['Sync', 'WooCommerce', 'None'], n_records),
            'mentioned_features': [f'Feature {i}' for i in range(n_records)],
            'specific_error_messages': [f'Error {i}' if i % 3 == 0 else '' for i in range(n_records)]
        }

        df = pd.DataFrame(data)
        return CSVProcessor.process_dataframe(df)


def auto_load_default_csv():
    """
    Auto-load default CSV file (tickets.csv) if it exists.
    Loads only once per session - subsequent calls do nothing.

    This function should be called at the beginning of each page's main()
    to ensure data is available regardless of which page is opened first.
    """
    # If data is already loaded, do nothing
    if st.session_state.get('data_loaded') and st.session_state.get('df_original') is not None:
        return

    # Check if default CSV exists
    from pathlib import Path
    default_csv_path = Path(__file__).parent.parent / "tickets.csv"

    if not default_csv_path.exists():
        return  # No default CSV, nothing to load

    try:
        # Load and process the CSV
        df = CSVProcessor.load_csv(str(default_csv_path))
        df_processed = CSVProcessor.process_dataframe(df)

        # Store in session state
        st.session_state.df_original = df_processed
        st.session_state.data_loaded = True
        st.session_state.csv_file_path = str(default_csv_path)

    except Exception as e:
        # Silently fail - pages will show "no data" message
        pass
