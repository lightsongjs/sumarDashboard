"""
Data Processor Module
Handles CSV loading, validation, cleaning, and normalization
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Tuple, Optional, List
import chardet


class CSVProcessor:
    """
    Intelligent CSV processor for HelpScout support tickets
    """

    # Expected columns from CSV
    EXPECTED_COLUMNS = [
        'created_at', 'closed_at', 'ticket_url', 'mailbox_name',
        'customer_email_extracted', 'conversation', 'taxonomy',
        'tip', 'area', 'sentiment', 'apreciere_parere_support',
        'urgency', 'is_recurrent', 'agent_intervention_needed',
        'summary', 'user_goal', 'pain_point', 'problem_type',
        'affects_business_flow', 'platform', 'integration',
        'mentioned_features', 'specific_error_messages'
    ]

    # Required columns (minimum for basic functionality)
    REQUIRED_COLUMNS = [
        'created_at', 'tip', 'area', 'urgency', 'platform'
    ]

    @staticmethod
    @st.cache_data(show_spinner=False)
    def load_csv(file_path: str = None, uploaded_file=None) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        """
        Load CSV with automatic encoding detection

        Args:
            file_path: Path to CSV file
            uploaded_file: Uploaded file object from Streamlit

        Returns:
            Tuple of (DataFrame, encoding, error_message)
        """
        try:
            # List of encodings to try
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

            df = None
            successful_encoding = None

            for encoding in encodings:
                try:
                    if uploaded_file is not None:
                        uploaded_file.seek(0)  # Reset file pointer
                        df = pd.read_csv(uploaded_file, encoding=encoding)
                    elif file_path is not None:
                        df = pd.read_csv(file_path, encoding=encoding)

                    if df is not None:
                        successful_encoding = encoding
                        break

                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception as e:
                    return None, None, f"Error with encoding {encoding}: {str(e)}"

            if df is None:
                return None, None, "Could not load CSV with any supported encoding"

            return df, successful_encoding, None

        except Exception as e:
            return None, None, f"Unexpected error: {str(e)}"

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """
        Validate CSV columns

        Returns:
            Tuple of (is_valid, missing_required, available_columns)
        """
        available_columns = df.columns.tolist()
        missing_required = [col for col in CSVProcessor.REQUIRED_COLUMNS if col not in available_columns]

        is_valid = len(missing_required) == 0

        return is_valid, missing_required, available_columns

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize data

        - Trim whitespace from text columns
        - Normalize text fields
        - Handle missing values
        - Convert boolean fields
        """
        df_clean = df.copy()

        # Text columns to clean
        text_columns = ['tip', 'area', 'sentiment', 'urgency', 'platform',
                       'problem_type', 'integration', 'taxonomy']

        for col in text_columns:
            if col in df_clean.columns:
                # Trim whitespace and handle NaN
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace('nan', pd.NA)
                df_clean[col] = df_clean[col].replace('', pd.NA)

        # Boolean columns
        boolean_columns = ['is_recurrent', 'affects_business_flow', 'agent_intervention_needed']

        for col in boolean_columns:
            if col in df_clean.columns:
                # Convert to boolean
                df_clean[col] = df_clean[col].map({
                    'TRUE': True, 'True': True, 'true': True, True: True, 1: True, '1': True,
                    'FALSE': False, 'False': False, 'false': False, False: False, 0: False, '0': False
                })

        return df_clean

    @staticmethod
    def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse datetime columns
        """
        df_dates = df.copy()

        date_columns = ['created_at', 'closed_at']

        for col in date_columns:
            if col in df_dates.columns:
                try:
                    df_dates[col] = pd.to_datetime(df_dates[col], errors='coerce')
                except Exception as e:
                    st.warning(f"Could not parse dates in column {col}: {str(e)}")

        # Add derived date columns
        if 'created_at' in df_dates.columns and df_dates['created_at'].notna().any():
            df_dates['created_date'] = df_dates['created_at'].dt.date
            df_dates['created_hour'] = df_dates['created_at'].dt.hour
            df_dates['created_day_of_week'] = df_dates['created_at'].dt.day_name()
            df_dates['created_week'] = df_dates['created_at'].dt.isocalendar().week
            df_dates['created_month'] = df_dates['created_at'].dt.month
            df_dates['created_year'] = df_dates['created_at'].dt.year

        # Calculate resolution time
        if 'created_at' in df_dates.columns and 'closed_at' in df_dates.columns:
            df_dates['resolution_time_hours'] = (
                (df_dates['closed_at'] - df_dates['created_at']).dt.total_seconds() / 3600
            )

        return df_dates

    @staticmethod
    def add_computed_fields(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add computed fields for analytics
        """
        df_computed = df.copy()

        # Add sentiment score
        if 'sentiment' in df_computed.columns:
            sentiment_map = {
                'Pozitiv': 1,
                'Neutru': 0,
                'Negativ': -1
            }
            df_computed['sentiment_score'] = df_computed['sentiment'].map(sentiment_map)

        # Add urgency score
        if 'urgency' in df_computed.columns:
            urgency_map = {
                'Blocker': 3,
                'Mediu': 2,
                'Scazut': 1
            }
            df_computed['urgency_score'] = df_computed['urgency'].map(urgency_map)

        return df_computed

    @staticmethod
    def process_csv(file_path: str = None, uploaded_file=None) -> Tuple[Optional[pd.DataFrame], dict]:
        """
        Complete CSV processing pipeline

        Returns:
            Tuple of (processed_dataframe, info_dict)
        """
        info = {
            'success': False,
            'encoding': None,
            'rows': 0,
            'columns': 0,
            'missing_columns': [],
            'errors': [],
            'warnings': []
        }

        # Step 1: Load CSV
        df, encoding, error = CSVProcessor.load_csv(file_path, uploaded_file)

        if df is None:
            info['errors'].append(error or "Failed to load CSV")
            return None, info

        info['encoding'] = encoding
        info['rows'] = len(df)
        info['columns'] = len(df.columns)

        # Step 2: Validate columns
        is_valid, missing_required, available_columns = CSVProcessor.validate_columns(df)

        if not is_valid:
            info['errors'].append(f"Missing required columns: {', '.join(missing_required)}")
            info['missing_columns'] = missing_required
            return None, info

        # Step 3: Clean data
        df = CSVProcessor.clean_data(df)

        # Step 4: Parse dates
        df = CSVProcessor.parse_dates(df)

        # Step 5: Add computed fields
        df = CSVProcessor.add_computed_fields(df)

        # Calculate missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            info['warnings'].append(f"Found {missing_counts.sum()} missing values across all columns")

        info['success'] = True

        return df, info

    @staticmethod
    def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
        """
        Get detailed column information
        """
        info_data = []

        for col in df.columns:
            info_data.append({
                'Column': col,
                'Type': str(df[col].dtype),
                'Non-Null': df[col].notna().sum(),
                'Null': df[col].isna().sum(),
                'Unique': df[col].nunique(),
                'Sample': str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else 'N/A'
            })

        return pd.DataFrame(info_data)

    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> dict:
        """
        Get summary statistics
        """
        stats = {
            'total_tickets': len(df),
            'date_range': None,
            'platforms': {},
            'urgency_levels': {},
            'sentiments': {},
            'areas': {},
            'problem_types': {}
        }

        # Date range
        if 'created_at' in df.columns:
            min_date = df['created_at'].min()
            max_date = df['created_at'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                stats['date_range'] = {
                    'from': min_date.strftime('%Y-%m-%d'),
                    'to': max_date.strftime('%Y-%m-%d'),
                    'days': (max_date - min_date).days
                }

        # Distributions
        if 'platform' in df.columns:
            stats['platforms'] = df['platform'].value_counts().to_dict()

        if 'urgency' in df.columns:
            stats['urgency_levels'] = df['urgency'].value_counts().to_dict()

        if 'sentiment' in df.columns:
            stats['sentiments'] = df['sentiment'].value_counts().to_dict()

        if 'area' in df.columns:
            stats['areas'] = df['area'].value_counts().to_dict()

        if 'problem_type' in df.columns:
            stats['problem_types'] = df['problem_type'].value_counts().to_dict()

        return stats
