"""
PM Analytics Module
Funcții de analiză pentru Product Manager insights
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class PMAnalytics:
    """Analytics pentru Product Manager decision making"""

    @staticmethod
    def calculate_nps_score(df: pd.DataFrame) -> float:
        """Calculate NPS score din apreciere_parere_support"""
        if 'apreciere_parere_support' not in df.columns:
            return 0.0

        # Map: Excelent/Bun = Promoters (9-10), Mediu = Passive (7-8), Slab = Detractors (0-6)
        promoters = len(df[df['apreciere_parere_support'].str.lower().isin(['excelent', 'bun'])])
        detractors = len(df[df['apreciere_parere_support'].str.lower().isin(['slab', 'foarte slab'])])
        total = len(df[df['apreciere_parere_support'].notna()])

        if total == 0:
            return 0.0

        nps = ((promoters - detractors) / total) * 100
        return round(nps, 2)

    @staticmethod
    def get_feature_gaps(df: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
        """Extract top Feature Gaps cu priority scoring"""
        feature_gaps = df[df['problem_type'] == 'feature_gap'].copy()

        if feature_gaps.empty:
            return pd.DataFrame()

        # Calculate priority score
        feature_gaps['priority_score'] = 0
        feature_gaps.loc[feature_gaps['urgency'] == 'blocker', 'priority_score'] += 3
        feature_gaps.loc[feature_gaps['urgency'] == 'mediu', 'priority_score'] += 2
        feature_gaps.loc[feature_gaps['urgency'] == 'scazut', 'priority_score'] += 1
        feature_gaps.loc[feature_gaps['affects_business_flow'] == True, 'priority_score'] += 2
        feature_gaps.loc[feature_gaps['is_recurrent'] == True, 'priority_score'] += 1
        feature_gaps.loc[feature_gaps['sentiment'] == 'negativ', 'priority_score'] += 1

        # Group and aggregate
        grouped = feature_gaps.groupby('pain_point').agg({
            'priority_score': 'sum',
            'pain_point': 'count',
            'platform': lambda x: ', '.join(x.dropna().unique()),
            'user_goal': lambda x: ', '.join(x.dropna().unique()[:3])
        }).rename(columns={'pain_point': 'count'})

        grouped = grouped.sort_values('priority_score', ascending=False).head(limit)
        return grouped.reset_index()

    @staticmethod
    def get_critical_bugs(df: pd.DataFrame) -> pd.DataFrame:
        """Get active critical bugs (Blockers + recurente)"""
        bugs = df[
            (df['problem_type'] == 'bug') &
            ((df['urgency'] == 'blocker') | (df['is_recurrent'] == True))
        ].copy()

        if bugs.empty:
            return pd.DataFrame()

        # Handle timezone-aware datetime
        now = pd.Timestamp.now(tz='UTC') if bugs['created_at'].dt.tz is not None else pd.Timestamp.now()
        bugs['days_open'] = (now - bugs['created_at']).dt.days

        result = bugs[[
            'pain_point', 'platform', 'urgency', 'is_recurrent',
            'affects_business_flow', 'specific_error_messages', 'days_open'
        ]].sort_values('urgency', ascending=False)

        return result

    @staticmethod
    def calculate_sentiment_score(df: pd.DataFrame) -> Dict:
        """Calculate sentiment distribution and score"""
        if 'sentiment' not in df.columns:
            return {}

        total = len(df[df['sentiment'].notna()])
        if total == 0:
            return {}

        sentiments = df['sentiment'].value_counts()

        return {
            'pozitiv': sentiments.get('pozitiv', 0),
            'pozitiv_pct': round((sentiments.get('pozitiv', 0) / total) * 100, 2),
            'neutru': sentiments.get('neutru', 0),
            'neutru_pct': round((sentiments.get('neutru', 0) / total) * 100, 2),
            'negativ': sentiments.get('negativ', 0),
            'negativ_pct': round((sentiments.get('negativ', 0) / total) * 100, 2),
            'total': total,
            'sentiment_score': round(((sentiments.get('pozitiv', 0) - sentiments.get('negativ', 0)) / total) * 100, 2)
        }

    @staticmethod
    def get_business_impact_issues(df: pd.DataFrame) -> pd.DataFrame:
        """Get issues affecting business flow"""
        business_impact = df[df['affects_business_flow'] == True].copy()

        if business_impact.empty:
            return pd.DataFrame()

        # Calculate risk score
        business_impact['risk_score'] = 0
        business_impact.loc[business_impact['urgency'] == 'blocker', 'risk_score'] += 5
        business_impact.loc[business_impact['urgency'] == 'mediu', 'risk_score'] += 3
        business_impact.loc[business_impact['urgency'] == 'scazut', 'risk_score'] += 1
        business_impact.loc[business_impact['is_recurrent'] == True, 'risk_score'] += 3
        business_impact.loc[business_impact['sentiment'] == 'negativ', 'risk_score'] += 2

        result = business_impact.groupby('pain_point').agg({
            'risk_score': 'sum',
            'pain_point': 'count',
            'platform': lambda x: ', '.join(x.dropna().unique()),
            'urgency': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'mediu'
        }).rename(columns={'pain_point': 'count'})

        return result.sort_values('risk_score', ascending=False).reset_index()

    @staticmethod
    def get_recurring_patterns(df: pd.DataFrame) -> pd.DataFrame:
        """Analyze recurring issues and patterns"""
        recurring = df[df['is_recurrent'] == True].copy()

        if recurring.empty:
            return pd.DataFrame()

        patterns = recurring.groupby(['pain_point', 'platform']).agg({
            'pain_point': 'count',
            'urgency': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'mediu',
            'problem_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown',
            'specific_error_messages': lambda x: ', '.join([str(i) for i in x.dropna().unique()[:3]])
        }).rename(columns={'pain_point': 'occurrences'})

        return patterns.sort_values('occurrences', ascending=False).reset_index()

    @staticmethod
    def get_platform_health(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate health metrics per platform"""
        if 'platform' not in df.columns:
            return pd.DataFrame()

        platforms = []

        for platform in df['platform'].dropna().unique():
            platform_df = df[df['platform'] == platform]

            total_tickets = len(platform_df)
            bugs = len(platform_df[platform_df['problem_type'] == 'bug'])
            blockers = len(platform_df[platform_df['urgency'] == 'blocker'])
            negative = len(platform_df[platform_df['sentiment'] == 'negativ'])

            # Resolution time
            closed = platform_df[platform_df['resolution_time_hours'].notna()]
            avg_resolution = closed['resolution_time_hours'].mean() if len(closed) > 0 else 0

            # Health score (0-100, higher is better)
            bug_rate = (bugs / total_tickets) * 100 if total_tickets > 0 else 0
            blocker_rate = (blockers / total_tickets) * 100 if total_tickets > 0 else 0
            negative_rate = (negative / total_tickets) * 100 if total_tickets > 0 else 0

            health_score = max(0, 100 - (bug_rate * 0.3 + blocker_rate * 0.5 + negative_rate * 0.2))

            platforms.append({
                'platform': platform,
                'total_tickets': total_tickets,
                'bugs': bugs,
                'blockers': blockers,
                'negative_sentiment': negative,
                'avg_resolution_hours': round(avg_resolution, 2),
                'health_score': round(health_score, 2)
            })

        return pd.DataFrame(platforms).sort_values('health_score', ascending=False)

    @staticmethod
    def calculate_operational_metrics(df: pd.DataFrame) -> Dict:
        """Calculate operational efficiency metrics"""
        metrics = {}

        # Resolution time per urgency
        if 'resolution_time_hours' in df.columns:
            for urgency in ['blocker', 'mediu', 'scazut']:
                urgency_df = df[(df['urgency'] == urgency) & (df['resolution_time_hours'].notna())]
                if len(urgency_df) > 0:
                    metrics[f'avg_resolution_{urgency}'] = round(urgency_df['resolution_time_hours'].mean(), 2)

        # Agent intervention rate
        if 'agent_intervention_needed' in df.columns:
            total = len(df)
            intervention = len(df[df['agent_intervention_needed'] == True])
            metrics['agent_intervention_rate'] = round((intervention / total) * 100, 2) if total > 0 else 0

        # SLA compliance (assume <24h for blockers)
        blockers = df[(df['urgency'] == 'blocker') & (df['resolution_time_hours'].notna())]
        if len(blockers) > 0:
            sla_met = len(blockers[blockers['resolution_time_hours'] <= 24])
            metrics['sla_compliance'] = round((sla_met / len(blockers)) * 100, 2)

        return metrics

    @staticmethod
    def get_user_journey_gaps(df: pd.DataFrame) -> pd.DataFrame:
        """Analyze where user goals fail"""
        journey_data = df[
            (df['user_goal'].notna()) &
            (df['pain_point'].notna())
        ].copy()

        if journey_data.empty:
            return pd.DataFrame()

        gaps = journey_data.groupby('user_goal').agg({
            'pain_point': lambda x: ' | '.join(x.dropna().unique()[:3]),
            'user_goal': 'count',
            'platform': lambda x: ', '.join(x.dropna().unique()),
            'problem_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown'
        }).rename(columns={'user_goal': 'failure_count'})

        return gaps.sort_values('failure_count', ascending=False).reset_index()

    @staticmethod
    def get_integration_health(df: pd.DataFrame) -> pd.DataFrame:
        """Analyze third-party integration issues"""
        if 'integration' not in df.columns:
            return pd.DataFrame()

        integrations = []

        for integration in df['integration'].dropna().unique():
            int_df = df[df['integration'] == integration]

            total = len(int_df)
            outage_terti = len(int_df[int_df['tip'] == 'outage terti'])
            blockers = len(int_df[int_df['urgency'] == 'blocker'])
            business_impact = len(int_df[int_df['affects_business_flow'] == True])

            reliability_score = max(0, 100 - ((outage_terti / total) * 50 + (blockers / total) * 30)) if total > 0 else 100

            integrations.append({
                'integration': integration,
                'total_issues': total,
                'outage_terti': outage_terti,
                'blockers': blockers,
                'business_impact': business_impact,
                'reliability_score': round(reliability_score, 2)
            })

        return pd.DataFrame(integrations).sort_values('reliability_score', ascending=False)

    @staticmethod
    def generate_executive_summary(df: pd.DataFrame) -> Dict:
        """Generate executive summary with key metrics"""
        summary = {}

        # Total tickets
        summary['total_tickets'] = len(df)

        # Critical issues
        summary['critical_issues'] = len(df[df['urgency'] == 'blocker'])

        # Top 3 pain points
        top_pain = df['pain_point'].value_counts().head(3)
        summary['top_pain_points'] = list(top_pain.index)

        # Customer satisfaction
        nps = PMAnalytics.calculate_nps_score(df)
        sentiment = PMAnalytics.calculate_sentiment_score(df)
        summary['nps_score'] = nps
        summary['sentiment_score'] = sentiment.get('sentiment_score', 0)

        # Business impact
        summary['business_impact_issues'] = len(df[df['affects_business_flow'] == True])

        # Trend (last 7 days vs previous 7 days)
        if 'created_at' in df.columns:
            # Handle timezone-aware datetime
            now = pd.Timestamp.now(tz='UTC') if df['created_at'].dt.tz is not None else pd.Timestamp.now()
            last_7_days = df[df['created_at'] >= (now - timedelta(days=7))]
            prev_7_days = df[(df['created_at'] >= (now - timedelta(days=14))) & (df['created_at'] < (now - timedelta(days=7)))]

            summary['last_7_days_count'] = len(last_7_days)
            summary['prev_7_days_count'] = len(prev_7_days)

            if len(prev_7_days) > 0:
                summary['trend_pct'] = round(((len(last_7_days) - len(prev_7_days)) / len(prev_7_days)) * 100, 2)
            else:
                summary['trend_pct'] = 0

        return summary
