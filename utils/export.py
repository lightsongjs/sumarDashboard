"""
Export Module for SmartBill Support Analytics
Handles export to various formats (Excel, PDF, CSV)
"""

import pandas as pd
import io
from datetime import datetime
from typing import Optional
import streamlit as st


def export_to_excel(df: pd.DataFrame, sheet_name: str = 'Data') -> bytes:
    """
    Export DataFrame to Excel format

    Args:
        df: DataFrame to export
        sheet_name: Name of the Excel sheet

    Returns:
        Bytes of Excel file
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#10B981',
            'font_color': 'white',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.set_column(i, i, min(max_length + 2, 50))

    output.seek(0)
    return output.getvalue()


def export_to_excel_multiple_sheets(data_dict: dict) -> bytes:
    """
    Export multiple DataFrames to Excel with different sheets

    Args:
        data_dict: Dictionary with sheet_name as key and DataFrame as value

    Returns:
        Bytes of Excel file
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#10B981',
                'font_color': 'white',
                'border': 1
            })

            # Format header row
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.set_column(i, i, min(max_length + 2, 50))

    output.seek(0)
    return output.getvalue()


def export_to_csv(df: pd.DataFrame) -> str:
    """
    Export DataFrame to CSV format

    Args:
        df: DataFrame to export

    Returns:
        CSV string
    """
    return df.to_csv(index=False, encoding='utf-8-sig')


def create_summary_report(df: pd.DataFrame) -> dict:
    """
    Create a summary report dictionary

    Args:
        df: DataFrame to summarize

    Returns:
        Dictionary with summary statistics
    """
    report = {
        'Metadata': {
            'Generated At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Total Records': len(df),
            'Date Range': f"{df['created_at'].min()} to {df['created_at'].max()}" if 'created_at' in df.columns else 'N/A'
        },
        'Key Metrics': {}
    }

    # Add key metrics
    if 'urgency' in df.columns:
        report['Key Metrics']['Blockers'] = len(df[df['urgency'] == 'blocker'])

    if 'sentiment' in df.columns:
        positive = len(df[df['sentiment'] == 'pozitiv'])
        report['Key Metrics']['Satisfaction %'] = f"{(positive/len(df)*100):.1f}%" if len(df) > 0 else "0%"

    if 'resolution_time_hours' in df.columns:
        report['Key Metrics']['Avg Resolution Time'] = f"{df['resolution_time_hours'].mean():.1f}h"

    if 'platform' in df.columns:
        report['Key Metrics']['Top Platform'] = df['platform'].value_counts().idxmax()

    return report


def generate_excel_report(df: pd.DataFrame, summary_stats: dict) -> bytes:
    """
    Generate comprehensive Excel report with multiple sheets

    Args:
        df: Main DataFrame
        summary_stats: Dictionary with additional statistics

    Returns:
        Bytes of Excel file
    """
    sheets = {
        'Summary': pd.DataFrame([summary_stats]),
        'All Tickets': df,
    }

    # Add platform breakdown if available
    if 'platform' in df.columns:
        platform_summary = df.groupby('platform').agg({
            'created_at': 'count'
        }).reset_index()
        platform_summary.columns = ['Platform', 'Count']
        sheets['By Platform'] = platform_summary

    # Add urgency breakdown
    if 'urgency' in df.columns:
        urgency_summary = df.groupby('urgency').agg({
            'created_at': 'count'
        }).reset_index()
        urgency_summary.columns = ['Urgency', 'Count']
        sheets['By Urgency'] = urgency_summary

    # Add blockers only
    if 'urgency' in df.columns:
        blockers = df[df['urgency'] == 'blocker']
        if len(blockers) > 0:
            sheets['Blockers Only'] = blockers

    return export_to_excel_multiple_sheets(sheets)


def create_download_button(data: bytes, filename: str, label: str, mime_type: str):
    """
    Create a Streamlit download button

    Args:
        data: File data as bytes
        filename: Name of the file to download
        label: Button label
        mime_type: MIME type of the file
    """
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type
    )


def export_charts_data(df: pd.DataFrame) -> dict:
    """
    Export data prepared for charts

    Args:
        df: DataFrame to process

    Returns:
        Dictionary with chart-ready data
    """
    chart_data = {}

    # Daily trend
    if 'created_date' in df.columns:
        chart_data['Daily Trend'] = df.groupby('created_date').size().reset_index(name='count')

    # Platform distribution
    if 'platform' in df.columns:
        chart_data['Platform Distribution'] = df['platform'].value_counts().reset_index()
        chart_data['Platform Distribution'].columns = ['Platform', 'Count']

    # Urgency distribution
    if 'urgency' in df.columns:
        chart_data['Urgency Distribution'] = df['urgency'].value_counts().reset_index()
        chart_data['Urgency Distribution'].columns = ['Urgency', 'Count']

    # Hourly distribution
    if 'created_hour' in df.columns:
        chart_data['Hourly Distribution'] = df.groupby('created_hour').size().reset_index(name='count')

    return chart_data
