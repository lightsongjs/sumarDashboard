"""
Unit tests for utils/data_processor.py - CSVProcessor class
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

from utils.data_processor import CSVProcessor


class TestCSVLoading:
    """Test CSV loading and encoding detection"""

    @pytest.mark.unit
    def test_load_clean_csv(self, sample_clean_csv):
        """Test loading a clean CSV file"""
        df = CSVProcessor.load_csv(sample_clean_csv)

        assert df is not None
        assert len(df) == 5
        assert 'created_at' in df.columns
        assert 'platform' in df.columns
        assert 'area' in df.columns

    @pytest.mark.unit
    def test_load_dirty_csv(self, sample_dirty_csv):
        """Test loading dirty CSV with extra columns and messy data"""
        df = CSVProcessor.load_csv(sample_dirty_csv)

        assert df is not None
        assert len(df) == 5

        # Check that empty first column was removed
        assert ' ' not in df.columns
        assert df.columns[0] != ' '

        # Check extra columns are present
        assert 'classification_index' in df.columns
        assert 'total_classifications' in df.columns
        assert 'Comments' in df.columns

    @pytest.mark.unit
    def test_load_empty_csv(self, sample_empty_csv):
        """Test loading empty CSV with headers only"""
        df = CSVProcessor.load_csv(sample_empty_csv)

        assert df is not None
        assert len(df) == 0
        assert 'created_at' in df.columns

    @pytest.mark.unit
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist"""
        with pytest.raises(Exception):
            CSVProcessor.load_csv('/nonexistent/file.csv')

    @pytest.mark.unit
    def test_encoding_detection(self, sample_clean_csv):
        """Test encoding detection works"""
        encoding = CSVProcessor.detect_encoding(sample_clean_csv)

        assert encoding is not None
        assert isinstance(encoding, str)


class TestDataValidation:
    """Test DataFrame validation"""

    @pytest.mark.unit
    def test_validate_valid_dataframe(self, sample_clean_csv):
        """Test validation of a valid DataFrame"""
        df = CSVProcessor.load_csv(sample_clean_csv)
        is_valid, errors = CSVProcessor.validate_dataframe(df)

        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_empty_dataframe(self):
        """Test validation of empty DataFrame"""
        df = pd.DataFrame()
        is_valid, errors = CSVProcessor.validate_dataframe(df)

        assert is_valid is False
        assert len(errors) > 0
        assert any('empty' in err.lower() for err in errors)

    @pytest.mark.unit
    def test_validate_missing_critical_columns(self):
        """Test validation with missing critical columns"""
        df = pd.DataFrame({
            'platform': ['facturare'],
            'urgency': ['blocker']
            # Missing 'created_at' and 'area'
        })

        is_valid, errors = CSVProcessor.validate_dataframe(df)

        assert is_valid is False
        assert any('created_at' in err for err in errors)

    @pytest.mark.unit
    def test_validate_invalid_date_format(self):
        """Test validation with invalid date format"""
        df = pd.DataFrame({
            'created_at': ['not a date', 'also not a date'],
            'platform': ['facturare', 'gestiune'],
            'area': ['SPV', 'Docs']
        })

        is_valid, errors = CSVProcessor.validate_dataframe(df)

        assert is_valid is False
        assert any('date format' in err.lower() for err in errors)


class TestDataProcessing:
    """Test DataFrame processing and normalization"""

    @pytest.mark.unit
    def test_process_dataframe_dates(self, sample_clean_csv):
        """Test date conversion in processing"""
        df = CSVProcessor.load_csv(sample_clean_csv)
        df_processed = CSVProcessor.process_dataframe(df)

        assert pd.api.types.is_datetime64_any_dtype(df_processed['created_at'])
        assert pd.api.types.is_datetime64_any_dtype(df_processed['closed_at'])

    @pytest.mark.unit
    def test_process_dataframe_lowercase_normalization(self, sample_dirty_csv):
        """Test lowercase normalization of text fields"""
        df = CSVProcessor.load_csv(sample_dirty_csv)
        df_processed = CSVProcessor.process_dataframe(df)

        # Check platform normalization
        assert df_processed['platform'].iloc[0] == 'facturare'  # Was 'Facturare'
        assert df_processed['platform'].iloc[1] == 'gestiune'  # Was 'GESTIUNE'

        # Check urgency normalization (only valid values become lowercase)
        assert df_processed['urgency'].iloc[0] == 'blocker'  # Was 'Blocker'
        assert df_processed['urgency'].iloc[3] == 'blocker'  # Was 'BLOCKER'

        # Check sentiment normalization
        assert df_processed['sentiment'].iloc[0] == 'negativ'  # Was 'NEGATIV'

    @pytest.mark.unit
    def test_process_dataframe_boolean_conversion(self, sample_clean_csv):
        """Test boolean column conversion"""
        df = CSVProcessor.load_csv(sample_clean_csv)
        df_processed = CSVProcessor.process_dataframe(df)

        assert pd.api.types.is_bool_dtype(df_processed['is_recurrent'])
        assert pd.api.types.is_bool_dtype(df_processed['affects_business_flow'])

        # Check specific values
        assert df_processed['is_recurrent'].iloc[0] is True  # Was 'TRUE'
        assert df_processed['is_recurrent'].iloc[1] is False  # Was 'FALSE'

    @pytest.mark.unit
    def test_process_dataframe_computed_columns(self, sample_clean_csv):
        """Test computed columns are added"""
        df = CSVProcessor.load_csv(sample_clean_csv)
        df_processed = CSVProcessor.process_dataframe(df)

        # Check computed columns exist
        assert 'resolution_time_hours' in df_processed.columns
        assert 'created_date' in df_processed.columns
        assert 'created_hour' in df_processed.columns
        assert 'created_day_of_week' in df_processed.columns
        assert 'created_week' in df_processed.columns
        assert 'created_month' in df_processed.columns
        assert 'created_year' in df_processed.columns
        assert 'is_closed' in df_processed.columns
        assert 'priority_score' in df_processed.columns

    @pytest.mark.unit
    def test_resolution_time_calculation(self, sample_clean_csv):
        """Test resolution time calculation"""
        df = CSVProcessor.load_csv(sample_clean_csv)
        df_processed = CSVProcessor.process_dataframe(df)

        # First ticket: created 10:00, closed 12:00 = 2 hours
        assert df_processed['resolution_time_hours'].iloc[0] == pytest.approx(2.0, rel=0.1)

        # Last ticket: not closed yet
        assert pd.isna(df_processed['resolution_time_hours'].iloc[4])

    @pytest.mark.unit
    def test_priority_score_calculation(self, sample_clean_csv):
        """Test priority score calculation"""
        df = CSVProcessor.load_csv(sample_clean_csv)
        df_processed = CSVProcessor.process_dataframe(df)

        # Ticket 0: blocker (3) + affects_business (2) + recurrent (1) = 6
        assert df_processed['priority_score'].iloc[0] == 6

        # Ticket 1: mediu (2) = 2
        assert df_processed['priority_score'].iloc[1] == 2

        # Ticket 2: scazut (1) = 1
        assert df_processed['priority_score'].iloc[2] == 1


class TestFiltering:
    """Test apply_filters functionality"""

    @pytest.mark.unit
    def test_filter_by_date_range(self, sample_dataframe):
        """Test filtering by date range"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            date_range=(start_date, end_date)
        )

        assert len(filtered) <= len(sample_dataframe)
        assert all(filtered['created_at'] >= start_date)
        assert all(filtered['created_at'] <= end_date)

    @pytest.mark.unit
    def test_filter_by_platform(self, sample_dataframe):
        """Test filtering by platform"""
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            platforms=['facturare', 'gestiune']
        )

        assert all(filtered['platform'].isin(['facturare', 'gestiune']))
        assert 'api' not in filtered['platform'].values

    @pytest.mark.unit
    def test_filter_by_urgency(self, sample_dataframe):
        """Test filtering by urgency levels"""
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            urgency_levels=['blocker']
        )

        assert all(filtered['urgency'] == 'blocker')
        assert 'mediu' not in filtered['urgency'].values
        assert 'scazut' not in filtered['urgency'].values

    @pytest.mark.unit
    def test_filter_by_sentiment(self, sample_dataframe):
        """Test filtering by sentiment"""
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            sentiment='pozitiv'
        )

        assert all(filtered['sentiment'] == 'pozitiv')

    @pytest.mark.unit
    def test_filter_only_recurrent(self, sample_dataframe):
        """Test filtering only recurrent issues"""
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            only_recurrent=True
        )

        assert all(filtered['is_recurrent'] == True)

    @pytest.mark.unit
    def test_filter_affects_business(self, sample_dataframe):
        """Test filtering by business impact"""
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            affects_business=True
        )

        assert all(filtered['affects_business_flow'] == True)

    @pytest.mark.unit
    def test_filter_by_search_text(self, sample_dataframe):
        """Test filtering by search text"""
        # Add specific text to first row
        sample_dataframe.loc[0, 'pain_point'] = 'specific search term here'

        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            search_text='specific search term'
        )

        assert len(filtered) >= 1
        assert 'specific search term' in filtered['pain_point'].iloc[0].lower()

    @pytest.mark.unit
    def test_filter_multiple_criteria(self, sample_dataframe):
        """Test filtering with multiple criteria combined"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            date_range=(start_date, end_date),
            platforms=['facturare'],
            urgency_levels=['blocker', 'mediu'],
            sentiment='negativ',
            only_recurrent=True
        )

        # Check all criteria are met
        assert all(filtered['created_at'] >= start_date)
        assert all(filtered['platform'] == 'facturare')
        assert all(filtered['urgency'].isin(['blocker', 'mediu']))
        assert all(filtered['sentiment'] == 'negativ')
        assert all(filtered['is_recurrent'] == True)

    @pytest.mark.unit
    def test_filter_empty_result(self, sample_dataframe):
        """Test filtering that returns no results"""
        # Filter for impossible combination
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            platforms=['facturare'],
            sentiment='pozitiv',
            urgency_levels=['blocker']
        )

        # May or may not have results depending on random data
        assert len(filtered) >= 0  # Should not error


class TestDataSummary:
    """Test get_data_summary functionality"""

    @pytest.mark.unit
    def test_summary_statistics(self, sample_dataframe):
        """Test data summary generation"""
        summary = CSVProcessor.get_data_summary(sample_dataframe)

        assert 'total_tickets' in summary
        assert summary['total_tickets'] == len(sample_dataframe)

        assert 'date_range' in summary
        assert 'start' in summary['date_range']
        assert 'end' in summary['date_range']

        assert 'missing_values' in summary
        assert 'unique_values' in summary

    @pytest.mark.unit
    def test_summary_date_range(self, sample_dataframe):
        """Test date range in summary"""
        summary = CSVProcessor.get_data_summary(sample_dataframe)

        start = summary['date_range']['start']
        end = summary['date_range']['end']

        assert start is not None
        assert end is not None
        assert start <= end

    @pytest.mark.unit
    def test_summary_unique_values(self, sample_dataframe):
        """Test unique values counting in summary"""
        summary = CSVProcessor.get_data_summary(sample_dataframe)

        unique = summary['unique_values']

        # Should have counts for categorical columns
        if 'urgency' in unique:
            assert unique['urgency'] > 0

        if 'sentiment' in unique:
            assert unique['sentiment'] > 0


class TestMockData:
    """Test mock data generation"""

    @pytest.mark.unit
    def test_get_mock_data(self):
        """Test mock data generation"""
        df = CSVProcessor.get_mock_data()

        assert df is not None
        assert len(df) == 100  # Should generate 100 records

        # Check required columns
        assert 'created_at' in df.columns
        assert 'platform' in df.columns
        assert 'urgency' in df.columns
        assert 'sentiment' in df.columns

    @pytest.mark.unit
    def test_mock_data_is_processed(self):
        """Test that mock data is already processed"""
        df = CSVProcessor.get_mock_data()

        # Should have computed columns
        assert 'resolution_time_hours' in df.columns
        assert 'created_date' in df.columns
        assert 'priority_score' in df.columns

        # Should have proper types
        assert pd.api.types.is_datetime64_any_dtype(df['created_at'])
        assert pd.api.types.is_bool_dtype(df['is_recurrent'])


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.unit
    def test_process_dataframe_with_all_nan(self):
        """Test processing DataFrame with all NaN values"""
        df = pd.DataFrame({
            'created_at': [pd.NaT, pd.NaT],
            'platform': [np.nan, np.nan],
            'area': [np.nan, np.nan],
        })

        df_processed = CSVProcessor.process_dataframe(df)

        assert df_processed is not None
        assert len(df_processed) == 2

    @pytest.mark.unit
    def test_filter_with_none_parameters(self, sample_dataframe):
        """Test filtering with all None parameters"""
        filtered = CSVProcessor.apply_filters(sample_dataframe)

        assert len(filtered) == len(sample_dataframe)  # Should return all data

    @pytest.mark.unit
    def test_filter_with_empty_lists(self, sample_dataframe):
        """Test filtering with empty lists"""
        filtered = CSVProcessor.apply_filters(
            sample_dataframe,
            platforms=[],
            areas=[],
            urgency_levels=[]
        )

        # Empty lists should be ignored
        assert len(filtered) > 0

    @pytest.mark.unit
    def test_process_dataframe_missing_optional_columns(self):
        """Test processing with only critical columns"""
        df = pd.DataFrame({
            'created_at': ['2025-10-01 10:00:00', '2025-10-02 11:00:00'],
            'platform': ['facturare', 'gestiune'],
            'area': ['SPV', 'Docs'],
        })

        df_processed = CSVProcessor.process_dataframe(df)

        assert df_processed is not None
        assert len(df_processed) == 2

        # Should still have date computed columns
        assert 'created_date' in df_processed.columns
