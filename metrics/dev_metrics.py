from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base import BaseMetricCollector
from ..utils.error_handler import ValidationError

class DevelopmentMetrics(BaseMetricCollector):
    """Collector for development-related metrics"""
    
    REQUIRED_FIELDS = [
        'forks',
        'stars',
        'subscribers',
        'total_issues',
        'closed_issues',
        'pull_requests_merged',
        'pull_request_contributors',
        'commit_count_4_weeks'
    ]
    
    def __init__(self):
        super().__init__()
        self.coingecko_service = 'coingecko'
        self.github_service = 'github'
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate development metrics data"""
        self.data_processor.validate_required_fields(data, self.REQUIRED_FIELDS)
        
        for field in self.REQUIRED_FIELDS:
            try:
                value = data.get(field, 0)
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValidationError(f'Invalid value for {field}: must be a non-negative number')
            except (ValueError, TypeError) as e:
                raise ValidationError(f'Invalid value for {field}: {str(e)}')
    
    async def get_github_repo_data(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Get detailed GitHub repository data"""
        endpoint = f'repos/{repo_owner}/{repo_name}'
        
        try:
            return await self.api_handler.get(
                service=self.github_service,
                endpoint=endpoint
            )
        except Exception as e:
            self.logger.error(f'Failed to fetch GitHub data: {str(e)}')
            return {}
    
    async def get_commit_activity(self, repo_owner: str, repo_name: str) -> List[Dict[str, Any]]:
        """Get commit activity for the repository"""
        endpoint = f'repos/{repo_owner}/{repo_name}/stats/commit_activity'
        
        try:
            response = await self.api_handler.get(
                service=self.github_service,
                endpoint=endpoint
            )
            return response if isinstance(response, list) else []
        except Exception as e:
            self.logger.error(f'Failed to fetch commit activity: {str(e)}')
            return []
    
    async def get_code_frequency(self, repo_owner: str, repo_name: str) -> List[List[int]]:
        """Get code frequency statistics"""
        endpoint = f'repos/{repo_owner}/{repo_name}/stats/code_frequency'
        
        try:
            response = await self.api_handler.get(
                service=self.github_service,
                endpoint=endpoint
            )
            return response if isinstance(response, list) else []
        except Exception as e:
            self.logger.error(f'Failed to fetch code frequency: {str(e)}')
            return []
    
    def calculate_velocity_metrics(self, commit_activity: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate development velocity metrics"""
        if not commit_activity:
            return {
                'weekly_commit_average': 0,
                'commit_trend': 0,
                'active_days_per_week': 0
            }
        
        # Get weekly commits for the last 4 weeks
        recent_weeks = commit_activity[-4:] if len(commit_activity) >= 4 else commit_activity
        weekly_commits = [week.get('total', 0) for week in recent_weeks]
        
        # Calculate metrics
        weekly_average = sum(weekly_commits) / len(weekly_commits) if weekly_commits else 0
        
        # Calculate trend (comparing last week to average of previous weeks)
        if len(weekly_commits) > 1:
            previous_avg = sum(weekly_commits[:-1]) / len(weekly_commits[:-1])
            trend = self.data_processor.calculate_percentage_change(
                previous_avg, weekly_commits[-1]
            )
        else:
            trend = 0
        
        # Calculate average active days per week
        active_days = [sum(1 for day in week.get('days', []) if day > 0)
                      for week in recent_weeks]
        avg_active_days = sum(active_days) / len(active_days) if active_days else 0
        
        return {
            'weekly_commit_average': weekly_average,
            'commit_trend': trend,
            'active_days_per_week': avg_active_days
        }
    
    def calculate_code_impact_metrics(self, code_frequency: List[List[int]]) -> Dict[str, Any]:
        """Calculate code impact metrics from additions/deletions"""
        if not code_frequency:
            return {
                'net_code_change': 0,
                'code_churn': 0,
                'change_impact': 0
            }
        
        # Get recent weeks' data
        recent_weeks = code_frequency[-4:] if len(code_frequency) >= 4 else code_frequency
        
        # Calculate metrics
        additions = sum(week[1] for week in recent_weeks)
        deletions = sum(abs(week[2]) for week in recent_weeks)
        
        net_change = additions - deletions
        code_churn = additions + deletions
        change_impact = net_change / code_churn if code_churn > 0 else 0
        
        return {
            'net_code_change': net_change,
            'code_churn': code_churn,
            'change_impact': change_impact
        }
    
    async def collect(self, coin_id: str) -> Dict[str, Any]:
        """Collect development metrics for a specific coin"""
        # Get developer data from CoinGecko
        endpoint = f'coins/{coin_id}'
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'false',
            'community_data': 'false'
        }
        
        response = await self.api_handler.get(
            service=self.coingecko_service,
            endpoint=endpoint,
            params=params
        )
        
        developer_data = response.get('developer_data', {})
        repos_url = response.get('links', {}).get('repos_url', {})
        
        # Validate basic metrics
        self.validate(developer_data)
        
        github_metrics = {}
        velocity_metrics = {}
        code_impact_metrics = {}
        
        # If GitHub repository is available, get detailed metrics
        if repos_url.get('github', []):
            github_url = repos_url['github'][0]
            repo_parts = github_url.split('github.com/')[-1].split('/')
            
            if len(repo_parts) >= 2:
                repo_owner, repo_name = repo_parts[:2]
                
                # Get detailed GitHub metrics
                repo_data = await self.get_github_repo_data(repo_owner, repo_name)
                commit_activity = await self.get_commit_activity(repo_owner, repo_name)
                code_frequency = await self.get_code_frequency(repo_owner, repo_name)
                
                # Calculate metrics
                velocity_metrics = self.calculate_velocity_metrics(commit_activity)
                code_impact_metrics = self.calculate_code_impact_metrics(code_frequency)
                
                github_metrics = {
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0),
                    'open_issues': repo_data.get('open_issues_count', 0),
                    'watchers': repo_data.get('subscribers_count', 0)
                }
        
        return {
            'basic_metrics': {
                'forks': developer_data['forks'],
                'stars': developer_data['stars'],
                'subscribers': developer_data['subscribers'],
                'total_issues': developer_data['total_issues'],
                'closed_issues': developer_data['closed_issues'],
                'pull_requests_merged': developer_data['pull_requests_merged'],
                'pull_request_contributors': developer_data['pull_request_contributors'],
                'commit_count_4_weeks': developer_data['commit_count_4_weeks']
            },
            'github_metrics': github_metrics,
            'velocity_metrics': velocity_metrics,
            'code_impact_metrics': code_impact_metrics,
            'development_activity_score': self.calculate_activity_score(developer_data)
        }
    
    def calculate_activity_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall development activity score"""
        # Weights for different metrics
        weights = {
            'commit_count_4_weeks': 0.3,
            'pull_requests_merged': 0.2,
            'pull_request_contributors': 0.2,
            'total_issues': 0.15,
            'closed_issues': 0.15
        }
        
        max_values = {
            'commit_count_4_weeks': 500,  # Assuming 500 commits/month is very active
            'pull_requests_merged': 100,   # Assuming 100 PRs/month is very active
            'pull_request_contributors': 50,  # Assuming 50 contributors is very active
            'total_issues': 200,          # Assuming 200 total issues is significant
            'closed_issues': 150          # Assuming 150 closed issues is significant
        }
        
        score = 0
        for metric, weight in weights.items():
            value = data.get(metric, 0)
            max_value = max_values[metric]
            normalized_value = min(value / max_value, 1)  # Cap at 1
            score += normalized_value * weight
        
        return round(score * 100, 2)  # Return as percentage