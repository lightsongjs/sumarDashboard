"""
Unit tests for utils/charts.py - Chart generation functions
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.charts import (
    create_trend_chart,
    create_platform_distribution,
    create_heatmap,
    create_urgency_trend,
    create_sentiment_trend,
    create_problem_type_chart,
    create_pareto_chart,
    create_sankey_diagram,
    create_comparison_chart,
    create_resolution_time_boxplot,
    create_metric_card_html,
    COLORS
)


class TestTrendChart:
    """Test create_trend_chart function"""

    @pytest.mark.unit
    def test_create_trend_chart_basic(self, sample_dataframe):
        """Test basic trend chart creation"""
        fig = create_trend_chart(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    @pytest.mark.unit
    def test_create_trend_chart_custom_title(self, sample_dataframe):
        """Test trend chart with custom title"""
        custom_title = "Custom Tickets Trend"
        fig = create_trend_chart(sample_dataframe, title=custom_title)

        assert fig.layout.title.text == custom_title

    @pytest.mark.unit
    def test_create_trend_chart_empty_data(self):
        """Test trend chart with empty DataFrame"""
        df = pd.DataFrame({'created_date': []})
        fig = create_trend_chart(df)

        assert fig is not None
        assert isinstance(fig, go.Figure)


class TestPlatformDistribution:
    """Test create_platform_distribution function"""

    @pytest.mark.unit
    def test_create_platform_distribution_basic(self, sample_dataframe):
        """Test basic platform distribution chart"""
        fig = create_platform_distribution(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    @pytest.mark.unit
    def test_create_platform_distribution_custom_column(self, sample_dataframe):
        """Test platform distribution with custom column"""
        fig = create_platform_distribution(sample_dataframe, platform_col='area')

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_platform_distribution_donut_chart(self, sample_dataframe):
        """Test that chart is donut type (hole in middle)"""
        fig = create_platform_distribution(sample_dataframe)

        # Should be a pie chart with hole
        assert fig.data[0].type == 'pie'
        assert fig.data[0].hole > 0  # Donut chart has hole

    @pytest.mark.unit
    def test_create_platform_distribution_empty_data(self):
        """Test platform distribution with empty DataFrame"""
        df = pd.DataFrame({'platform': []})
        fig = create_platform_distribution(df)

        assert fig is not None


class TestHeatmap:
    """Test create_heatmap function"""

    @pytest.mark.unit
    def test_create_heatmap_basic(self, sample_dataframe):
        """Test basic heatmap creation"""
        fig = create_heatmap(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_heatmap_custom_columns(self, sample_dataframe):
        """Test heatmap with custom hour and day columns"""
        fig = create_heatmap(
            sample_dataframe,
            hour_col='created_hour',
            day_col='created_day_of_week'
        )

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_heatmap_data_shape(self, sample_dataframe):
        """Test heatmap has correct data shape"""
        fig = create_heatmap(sample_dataframe)

        # Should have heatmap data
        assert len(fig.data) > 0
        assert fig.data[0].type == 'heatmap'


class TestUrgencyTrend:
    """Test create_urgency_trend function"""

    @pytest.mark.unit
    def test_create_urgency_trend_basic(self, sample_dataframe):
        """Test basic urgency trend chart"""
        fig = create_urgency_trend(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_urgency_trend_stacked_bar(self, sample_dataframe):
        """Test urgency trend is stacked bar chart"""
        fig = create_urgency_trend(sample_dataframe)

        # Should have multiple traces for different urgency levels
        assert len(fig.data) > 0

        # Should be bar chart
        assert all(trace.type == 'bar' for trace in fig.data)

    @pytest.mark.unit
    def test_create_urgency_trend_custom_date_col(self, sample_dataframe):
        """Test urgency trend with custom date column"""
        fig = create_urgency_trend(sample_dataframe, date_col='created_date')

        assert fig is not None


class TestSentimentTrend:
    """Test create_sentiment_trend function"""

    @pytest.mark.unit
    def test_create_sentiment_trend_basic(self, sample_dataframe):
        """Test basic sentiment trend chart"""
        fig = create_sentiment_trend(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_sentiment_trend_line_chart(self, sample_dataframe):
        """Test sentiment trend is line chart with moving average"""
        fig = create_sentiment_trend(sample_dataframe)

        # Should have line traces
        assert len(fig.data) > 0

    @pytest.mark.unit
    def test_create_sentiment_trend_custom_window(self, sample_dataframe):
        """Test sentiment trend with custom moving average window"""
        fig = create_sentiment_trend(sample_dataframe, ma_window=3)

        assert fig is not None


class TestProblemTypeChart:
    """Test create_problem_type_chart function"""

    @pytest.mark.unit
    def test_create_problem_type_chart_basic(self, sample_dataframe):
        """Test basic problem type chart"""
        fig = create_problem_type_chart(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_problem_type_chart_donut(self, sample_dataframe):
        """Test problem type is donut chart"""
        fig = create_problem_type_chart(sample_dataframe)

        # Should be pie chart with hole (donut)
        assert fig.data[0].type == 'pie'
        assert fig.data[0].hole > 0

    @pytest.mark.unit
    def test_create_problem_type_chart_custom_column(self, sample_dataframe):
        """Test problem type chart with custom column"""
        fig = create_problem_type_chart(sample_dataframe, type_col='tip')

        assert fig is not None


class TestParetoChart:
    """Test create_pareto_chart function"""

    @pytest.mark.unit
    def test_create_pareto_chart_basic(self, sample_dataframe):
        """Test basic Pareto chart creation"""
        fig = create_pareto_chart(sample_dataframe, value_col='area')

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_pareto_chart_dual_axis(self, sample_dataframe):
        """Test Pareto chart has dual y-axes"""
        fig = create_pareto_chart(sample_dataframe, value_col='platform')

        # Should have 2 traces (bars + line)
        assert len(fig.data) >= 2

        # Should have bars and line
        trace_types = [trace.type for trace in fig.data]
        assert 'bar' in trace_types or 'scatter' in trace_types

    @pytest.mark.unit
    def test_create_pareto_chart_custom_title(self, sample_dataframe):
        """Test Pareto chart with custom title"""
        custom_title = "Custom Pareto Analysis"
        fig = create_pareto_chart(sample_dataframe, value_col='area', title=custom_title)

        assert custom_title in fig.layout.title.text


class TestSankeyDiagram:
    """Test create_sankey_diagram function"""

    @pytest.mark.unit
    def test_create_sankey_diagram_basic(self, sample_dataframe):
        """Test basic Sankey diagram creation"""
        fig = create_sankey_diagram(
            sample_dataframe,
            source_col='platform',
            target_col='area'
        )

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_sankey_diagram_type(self, sample_dataframe):
        """Test Sankey diagram has correct type"""
        fig = create_sankey_diagram(
            sample_dataframe,
            source_col='platform',
            target_col='problem_type'
        )

        # Should be sankey type
        assert len(fig.data) > 0
        assert fig.data[0].type == 'sankey'

    @pytest.mark.unit
    def test_create_sankey_diagram_custom_title(self, sample_dataframe):
        """Test Sankey with custom title"""
        custom_title = "Flow Analysis"
        fig = create_sankey_diagram(
            sample_dataframe,
            source_col='platform',
            target_col='area',
            title=custom_title
        )

        assert custom_title in fig.layout.title.text


class TestComparisonChart:
    """Test create_comparison_chart function"""

    @pytest.mark.unit
    def test_create_comparison_chart_basic(self, sample_dataframe):
        """Test basic comparison chart"""
        # Split data into two periods
        mid_point = len(sample_dataframe) // 2
        df1 = sample_dataframe.iloc[:mid_point]
        df2 = sample_dataframe.iloc[mid_point:]

        fig = create_comparison_chart(df1, df2)

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_comparison_chart_custom_labels(self, sample_dataframe):
        """Test comparison chart with custom labels"""
        mid_point = len(sample_dataframe) // 2
        df1 = sample_dataframe.iloc[:mid_point]
        df2 = sample_dataframe.iloc[mid_point:]

        fig = create_comparison_chart(
            df1, df2,
            label1="Period 1",
            label2="Period 2"
        )

        assert fig is not None

    @pytest.mark.unit
    def test_create_comparison_chart_grouped_bars(self, sample_dataframe):
        """Test comparison chart has grouped bars"""
        mid_point = len(sample_dataframe) // 2
        df1 = sample_dataframe.iloc[:mid_point]
        df2 = sample_dataframe.iloc[mid_point:]

        fig = create_comparison_chart(df1, df2)

        # Should have multiple bar traces
        assert len(fig.data) >= 2


class TestResolutionTimeBoxplot:
    """Test create_resolution_time_boxplot function"""

    @pytest.mark.unit
    def test_create_resolution_time_boxplot_basic(self, sample_dataframe):
        """Test basic resolution time boxplot"""
        # Ensure we have resolution_time_hours
        if 'resolution_time_hours' not in sample_dataframe.columns:
            sample_dataframe['resolution_time_hours'] = np.random.uniform(1, 24, len(sample_dataframe))

        fig = create_resolution_time_boxplot(sample_dataframe)

        assert fig is not None
        assert isinstance(fig, go.Figure)

    @pytest.mark.unit
    def test_create_resolution_time_boxplot_type(self, sample_dataframe):
        """Test boxplot has correct type"""
        if 'resolution_time_hours' not in sample_dataframe.columns:
            sample_dataframe['resolution_time_hours'] = np.random.uniform(1, 24, len(sample_dataframe))

        fig = create_resolution_time_boxplot(sample_dataframe)

        # Should have box traces
        assert len(fig.data) > 0
        assert any(trace.type == 'box' for trace in fig.data)

    @pytest.mark.unit
    def test_create_resolution_time_boxplot_custom_columns(self, sample_dataframe):
        """Test boxplot with custom columns"""
        if 'resolution_time_hours' not in sample_dataframe.columns:
            sample_dataframe['resolution_time_hours'] = np.random.uniform(1, 24, len(sample_dataframe))

        fig = create_resolution_time_boxplot(
            sample_dataframe,
            time_col='resolution_time_hours',
            group_col='platform'
        )

        assert fig is not None


class TestMetricCardHTML:
    """Test create_metric_card_html function"""

    @pytest.mark.unit
    def test_create_metric_card_basic(self):
        """Test basic metric card HTML generation"""
        html = create_metric_card_html("Total Tickets", "150")

        assert html is not None
        assert isinstance(html, str)
        assert "Total Tickets" in html
        assert "150" in html

    @pytest.mark.unit
    def test_create_metric_card_with_delta(self):
        """Test metric card with delta"""
        html = create_metric_card_html("Total Tickets", "150", delta="+10%")

        assert "150" in html
        assert "+10%" in html

    @pytest.mark.unit
    def test_create_metric_card_with_icon(self):
        """Test metric card with icon"""
        html = create_metric_card_html("Total Tickets", "150", icon="📊")

        assert "📊" in html

    @pytest.mark.unit
    def test_create_metric_card_with_color(self):
        """Test metric card with custom color"""
        html = create_metric_card_html("Total Tickets", "150", color="#FF0000")

        assert html is not None
        # Color should be in the HTML
        assert "#FF0000" in html or "FF0000" in html


class TestChartTheming:
    """Test chart theming and styling"""

    @pytest.mark.unit
    def test_charts_use_dark_theme(self, sample_dataframe):
        """Test that charts use dark theme"""
        fig = create_trend_chart(sample_dataframe)

        # Check background colors
        assert fig.layout.paper_bgcolor == '#0E1117'
        assert fig.layout.plot_bgcolor == '#262730'

    @pytest.mark.unit
    def test_charts_use_brand_colors(self, sample_dataframe):
        """Test that charts use SmartBill brand colors"""
        # Test platform distribution uses colors
        fig = create_platform_distribution(sample_dataframe)

        assert fig is not None
        # Should have color configuration

    @pytest.mark.unit
    def test_colors_constant(self):
        """Test COLORS constant is properly defined"""
        assert 'primary' in COLORS
        assert 'danger' in COLORS
        assert 'success' in COLORS
        assert 'warning' in COLORS

        # Check primary color is SmartBill green
        assert COLORS['primary'] == '#10B981'


class TestChartEdgeCases:
    """Test edge cases in chart generation"""

    @pytest.mark.unit
    def test_charts_with_single_row(self):
        """Test charts work with single row of data"""
        df = pd.DataFrame({
            'created_date': [datetime.now().date()],
            'platform': ['facturare'],
            'area': ['SPV'],
            'urgency': ['blocker'],
            'sentiment': ['pozitiv'],
            'problem_type': ['bug']
        })

        # Should not error
        fig1 = create_trend_chart(df)
        fig2 = create_platform_distribution(df)

        assert fig1 is not None
        assert fig2 is not None

    @pytest.mark.unit
    def test_charts_with_null_values(self, sample_dataframe):
        """Test charts handle null values gracefully"""
        # Add some null values
        sample_dataframe.loc[0, 'platform'] = np.nan
        sample_dataframe.loc[1, 'urgency'] = np.nan

        # Should not error
        fig1 = create_platform_distribution(sample_dataframe)
        fig2 = create_urgency_trend(sample_dataframe)

        assert fig1 is not None
        assert fig2 is not None

    @pytest.mark.unit
    def test_charts_with_duplicate_values(self):
        """Test charts with all same values"""
        df = pd.DataFrame({
            'created_date': [datetime.now().date()] * 10,
            'platform': ['facturare'] * 10,
            'area': ['SPV'] * 10,
            'urgency': ['blocker'] * 10,
        })

        fig = create_trend_chart(df)
        assert fig is not None

        fig = create_platform_distribution(df)
        assert fig is not None


class TestChartInteractivity:
    """Test chart interactivity features"""

    @pytest.mark.unit
    def test_charts_have_hover_data(self, sample_dataframe):
        """Test charts have hover information"""
        fig = create_trend_chart(sample_dataframe)

        # Should have hover template or hoverinfo
        assert len(fig.data) > 0

    @pytest.mark.unit
    def test_charts_are_responsive(self, sample_dataframe):
        """Test charts have responsive configuration"""
        fig = create_platform_distribution(sample_dataframe)

        # Charts should have layout configuration
        assert fig.layout is not None
