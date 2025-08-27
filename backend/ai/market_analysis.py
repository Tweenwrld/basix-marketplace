import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json

class MarketAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.price_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.demand_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.trained = False
        
    def analyze_market_trends(self, transaction_data: List[Dict], 
                            asset_data: List[Dict], timeframe: int = 30) -> Dict[str, Any]:
        """Comprehensive market trend analysis"""
        if not transaction_data:
            return self._get_default_market_analysis()
        
        df_transactions = pd.DataFrame(transaction_data)
        df_assets = pd.DataFrame(asset_data)
        
        # Calculate time-based metrics
        cutoff_date = datetime.now() - timedelta(days=timeframe)
        recent_transactions = df_transactions[
            pd.to_datetime(df_transactions['timestamp']) >= cutoff_date
        ] if 'timestamp' in df_transactions.columns else df_transactions
        
        # Volume analysis
        volume_metrics = self._calculate_volume_metrics(recent_transactions)
        
        # Price analysis
        price_metrics = self._calculate_price_metrics(recent_transactions)
        
        # Asset type distribution analysis
        type_distribution = self._analyze_asset_distribution(df_assets)
        
        # Market sentiment
        sentiment_analysis = self._calculate_market_sentiment(recent_transactions)
        
        # Liquidity analysis
        liquidity_metrics = self._analyze_liquidity(recent_transactions, df_assets)
        
        return {
            'volume_metrics': volume_metrics,
            'price_metrics': price_metrics,
            'type_distribution': type_distribution,
            'sentiment': sentiment_analysis,
            'liquidity': liquidity_metrics,
            'market_health_score': self._calculate_market_health(
                volume_metrics, price_metrics, sentiment_analysis
            ),
            'recommendations': self._generate_market_recommendations(
                volume_metrics, price_metrics, sentiment_analysis
            )
        }
    
    def predict_asset_price(self, asset_id: str, asset_features: Dict, 
                          market_conditions: Dict, prediction_days: int = 30) -> Dict[str, Any]:
        """Predict asset price using ML models"""
        if not self.trained:
            self._train_models_with_synthetic_data()
        
        # Prepare feature vector
        features = self._prepare_prediction_features(asset_features, market_conditions)
        
        # Make predictions
        price_prediction = self.price_model.predict([features])[0]
        demand_prediction = self.demand_model.predict([features])[0]
        
        # Calculate confidence intervals
        confidence_interval = self._calculate_confidence_interval(
            price_prediction, asset_features, market_conditions
        )
        
        return {
            'predicted_price': max(0, price_prediction),
            'predicted_demand': max(0, demand_prediction),
            'confidence_interval': confidence_interval,
            'prediction_horizon': prediction_days,
            'risk_factors': self._identify_risk_factors(asset_features, market_conditions),
            'model_confidence': self._calculate_model_confidence(features)
        }
    
    def analyze_competitor_assets(self, asset_data: Dict, 
                                similar_assets: List[Dict]) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        if not similar_assets:
            return {'competitive_score': 50, 'positioning': 'neutral'}
        
        asset_features = self._extract_asset_features(asset_data)
        competitor_features = [self._extract_asset_features(comp) for comp in similar_assets]
        
        # Calculate competitive metrics
        price_positioning = self._analyze_price_positioning(asset_data, similar_assets)
        feature_comparison = self._compare_features(asset_features, competitor_features)
        market_share_estimate = self._estimate_market_share(asset_data, similar_assets)
        
        # Calculate competitive score
        competitive_score = self._calculate_competitive_score(
            price_positioning, feature_comparison, market_share_estimate
        )
        
        # Determine positioning
        if competitive_score > 75:
            positioning = 'market_leader'
        elif competitive_score > 60:
            positioning = 'strong_competitor'
        elif competitive_score > 40:
            positioning = 'average_competitor'
        else:
            positioning = 'needs_improvement'
        
        return {
            'competitive_score': competitive_score,
            'positioning': positioning,
            'price_positioning': price_positioning,
            'feature_comparison': feature_comparison,
            'market_share_estimate': market_share_estimate,
            'recommendations': self._generate_competitive_recommendations(
                competitive_score, price_positioning, feature_comparison
            )
        }
    
    def _calculate_competitive_score(self, price_positioning: Dict, 
                                   feature_comparison: Dict, 
                                   market_share: float) -> float:
        """Calculate overall competitive score"""
        price_score = price_positioning.get('score', 50)
        feature_score = feature_comparison.get('score', 50)
        market_share_score = min(market_share * 100, 100)
        
        # Weighted average
        competitive_score = (price_score * 0.4 + feature_score * 0.4 + market_share_score * 0.2)
        
        return min(max(competitive_score, 0), 100)
    
    def _generate_competitive_recommendations(self, competitive_score: float,
                                            price_positioning: Dict,
                                            feature_comparison: Dict) -> List[str]:
        """Generate recommendations for competitive improvement"""
        recommendations = []
        
        if competitive_score < 60:
            recommendations.append('Focus on improving competitive positioning')
        
        if price_positioning.get('position', 'average') == 'overpriced':
            recommendations.append('Consider price optimization to improve competitiveness')
        
        if feature_comparison.get('score', 50) < 60:
            recommendations.append('Enhance utility features to differentiate from competitors')
        
        if competitive_score > 80:
            recommendations.append('Maintain market leadership position')
        
        return recommendations
    
    def get_market_insights(self, asset_type: str = None, region: str = None) -> Dict[str, Any]:
        """Get comprehensive market insights"""
        try:
            # This would typically query a database or external API
            # For now, return mock insights
            insights = {
                'market_overview': {
                    'total_volume': 1250000.0,
                    'total_transactions': 8500,
                    'active_assets': 3200,
                    'active_creators': 450
                },
                'trends': {
                    'volume_trend': 'increasing',
                    'price_trend': 'stable',
                    'demand_trend': 'high',
                    'supply_trend': 'balanced'
                },
                'opportunities': [
                    'Growing demand for Phygital assets',
                    'Emerging markets in Asia-Pacific',
                    'AI-generated content gaining traction'
                ],
                'risks': [
                    'Market volatility in certain asset types',
                    'Regulatory uncertainty in some regions',
                    'Competition from traditional platforms'
                ],
                'recommendations': [
                    'Focus on utility-rich assets',
                    'Build strong creator relationships',
                    'Diversify across asset types'
                ]
            }
            
            # Filter by asset type if specified
            if asset_type:
                insights['asset_type_specific'] = {
                    'NFT': {'volume_share': 0.4, 'growth_rate': 0.15},
                    'Phygital': {'volume_share': 0.35, 'growth_rate': 0.25},
                    'Digital': {'volume_share': 0.15, 'growth_rate': 0.10},
                    'RealWorldAsset': {'volume_share': 0.10, 'growth_rate': 0.30}
                }.get(asset_type, {})
            
            return insights
            
        except Exception as e:
            return {'error': f'Failed to get market insights: {str(e)}'}
    
    def analyze_user_behavior(self, user_id: str, timeframe: int = 30) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            # This would typically query user transaction and interaction data
            # For now, return mock analysis
            behavior_analysis = {
                'user_id': user_id,
                'timeframe': timeframe,
                'activity_patterns': {
                    'preferred_asset_types': ['NFT', 'Phygital'],
                    'average_transaction_value': 2.5,
                    'transaction_frequency': 'weekly',
                    'peak_activity_hours': [14, 15, 16],  # 2-4 PM
                    'preferred_regions': ['Mumbai', 'Delhi']
                },
                'investment_behavior': {
                    'risk_tolerance': 'moderate',
                    'holding_period': 'medium_term',
                    'diversification_score': 0.7,
                    'market_timing_accuracy': 0.65
                },
                'recommendations': [
                    'Consider diversifying into Digital assets',
                    'Explore opportunities in Bangalore region',
                    'Increase staking participation for better returns'
                ]
            }
            
            return behavior_analysis
            
        except Exception as e:
            return {'error': f'Failed to analyze user behavior: {str(e)}'}
        
        competitive_score = (
            price_positioning['score'] * 0.4 +
            feature_comparison['score'] * 0.4 +
            market_share_estimate * 0.2
        )
        
        return {
            'competitive_score': competitive_score,
            'price_positioning': price_positioning,
            'feature_advantages': feature_comparison['advantages'],
            'feature_gaps': feature_comparison['gaps'],
            'market_share_estimate': market_share_estimate,
            'positioning_strategy': self._recommend_positioning_strategy(competitive_score, price_positioning)
        }
    
    def identify_market_opportunities(self, market_data: Dict, 
                                    user_profile: Dict) -> List[Dict[str, Any]]:
        """Identify investment and creation opportunities"""
        opportunities = []
        
        # Undervalued asset opportunities
        undervalued_assets = self._find_undervalued_assets(market_data)
        for asset in undervalued_assets:
            opportunities.append({
                'type': 'investment',
                'asset_id': asset['id'],
                'opportunity': 'undervalued_asset',
                'potential_return': asset['potential_return'],
                'risk_level': asset['risk_level'],
                'confidence': asset['confidence']
            })
        
        # Emerging trend opportunities
        emerging_trends = self._identify_emerging_trends(market_data)
        for trend in emerging_trends:
            opportunities.append({
                'type': 'creation',
                'opportunity': 'emerging_trend',
                'trend_name': trend['name'],
                'growth_rate': trend['growth_rate'],
                'market_size': trend['market_size'],
                'entry_difficulty': trend['entry_difficulty']
            })
        
        # Collaboration opportunities
        collab_opportunities = self._find_collaboration_opportunities(market_data, user_profile)
        opportunities.extend(collab_opportunities)
        
        # Sort by potential value
        opportunities.sort(key=lambda x: x.get('potential_return', x.get('growth_rate', 0)), reverse=True)
        
        return opportunities[:10]  # Top 10 opportunities
    
    def calculate_portfolio_optimization(self, current_portfolio: List[Dict], 
                                       available_assets: List[Dict], 
                                       risk_tolerance: str) -> Dict[str, Any]:
        """Optimize portfolio allocation"""
        risk_multipliers = {'conservative': 0.5, 'moderate': 1.0, 'aggressive': 1.5}
        risk_factor = risk_multipliers.get(risk_tolerance, 1.0)
        
        # Calculate current portfolio metrics
        current_metrics = self._calculate_portfolio_metrics(current_portfolio)
        
        # Generate optimization suggestions
        optimization_suggestions = []
        
        # Diversification analysis
        diversification_score = self._calculate_diversification_score(current_portfolio)
        if diversification_score < 0.6:
            optimization_suggestions.append({
                'type': 'diversification',
                'action': 'increase_asset_type_diversity',
                'priority': 'high',
                'expected_benefit': 'risk_reduction'
            })
        
        # Risk-adjusted return optimization
        for asset in available_assets:
            expected_return = self._calculate_expected_return(asset, risk_factor)
            if expected_return > current_metrics.get('avg_return', 0.1) * 1.2:
                optimization_suggestions.append({
                    'type': 'opportunity',
                    'asset_id': asset['id'],
                    'action': 'consider_addition',
                    'expected_return': expected_return,
                    'risk_level': asset.get('risk_level', 'medium')
                })
        
        return {
            'current_metrics': current_metrics,
            'diversification_score': diversification_score,
            'optimization_suggestions': optimization_suggestions[:5],
            'recommended_allocation': self._generate_allocation_recommendations(
                current_portfolio, available_assets, risk_tolerance
            )
        }
    
    # Helper methods
    def _get_default_market_analysis(self) -> Dict[str, Any]:
        """Return default market analysis when no data is available"""
        return {
            'volume_metrics': {'total_volume': 0, 'avg_daily_volume': 0, 'volume_trend': 'stable'},
            'price_metrics': {'avg_price': 0, 'price_volatility': 0, 'price_trend': 'stable'},
            'type_distribution': {},
            'sentiment': {'overall': 'neutral', 'confidence': 0.5},
            'liquidity': {'market_depth': 'low', 'spread': 0},
            'market_health_score': 50
        }
    
    def _calculate_volume_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume-related metrics"""
        if df.empty or 'amount' not in df.columns:
            return {'total_volume': 0, 'avg_daily_volume': 0, 'volume_trend': 'stable'}
        
        total_volume = df['amount'].sum()
        daily_volumes = df.groupby(df['timestamp'].dt.date)['amount'].sum() if 'timestamp' in df.columns else [total_volume]
        avg_daily_volume = np.mean(daily_volumes)
        
        # Calculate trend
        if len(daily_volumes) > 1:
            recent_avg = np.mean(list(daily_volumes)[-7:])  # Last 7 days
            earlier_avg = np.mean(list(daily_volumes)[:-7]) if len(daily_volumes) > 7 else recent_avg
            trend = 'increasing' if recent_avg > earlier_avg * 1.1 else 'decreasing' if recent_avg < earlier_avg * 0.9 else 'stable'
        else:
            trend = 'stable'
        
        return {
            'total_volume': float(total_volume),
            'avg_daily_volume': float(avg_daily_volume),
            'volume_trend': trend
        }
    
    def _calculate_price_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate price-related metrics"""
        if df.empty or 'price' not in df.columns:
            return {'avg_price': 0, 'price_volatility': 0, 'price_trend': 'stable'}
        
        prices = df['price'].dropna()
        if prices.empty:
            return {'avg_price': 0, 'price_volatility': 0, 'price_trend': 'stable'}
        
        avg_price = prices.mean()
        price_volatility = prices.std() / avg_price if avg_price > 0 else 0
        
        # Price trend
        if len(prices) > 1:
            price_change = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
            trend = 'increasing' if price_change > 0.05 else 'decreasing' if price_change < -0.05 else 'stable'
        else:
            trend = 'stable'
        
        return {
            'avg_price': float(avg_price),
            'price_volatility': float(price_volatility),
            'price_trend': trend
        }
    
    def _analyze_asset_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze asset type distribution"""
        if df.empty or 'asset_type' not in df.columns:
            return {}
        
        distribution = df['asset_type'].value_counts().to_dict()
        total_assets = len(df)
        
        return {
            'absolute': distribution,
            'percentage': {k: (v/total_assets)*100 for k, v in distribution.items()},
            'diversity_index': len(distribution) / total_assets if total_assets > 0 else 0
        }
    
    def _calculate_market_sentiment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate market sentiment"""
        if df.empty:
            return {'overall': 'neutral', 'confidence': 0.5}
        
        # Simple sentiment based on transaction patterns
        if 'transaction_type' in df.columns:
            purchases = len(df[df['transaction_type'] == 'purchase'])
            sales = len(df[df['transaction_type'] == 'sale'])
            
            if purchases > sales * 1.2:
                sentiment = 'bullish'
                confidence = min((purchases - sales) / len(df), 0.9)
            elif sales > purchases * 1.2:
                sentiment = 'bearish'
                confidence = min((sales - purchases) / len(df), 0.9)
            else:
                sentiment = 'neutral'
                confidence = 0.5
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {'overall': sentiment, 'confidence': float(confidence)}
    
    def _analyze_liquidity(self, transactions_df: pd.DataFrame, assets_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market liquidity"""
        if transactions_df.empty:
            return {'market_depth': 'low', 'spread': 0}
        
        # Calculate basic liquidity metrics
        transaction_frequency = len(transactions_df) / 30  # Transactions per day
        unique_assets_traded = transactions_df['asset_id'].nunique() if 'asset_id' in transactions_df.columns else 0
        total_assets = len(assets_df)
        
        liquidity_ratio = unique_assets_traded / total_assets if total_assets > 0 else 0
        
        market_depth = 'high' if liquidity_ratio > 0.3 else 'medium' if liquidity_ratio > 0.1 else 'low'
        
        return {
            'market_depth': market_depth,
            'liquidity_ratio': float(liquidity_ratio),
            'transaction_frequency': float(transaction_frequency),
            'spread': 0.05  # Mock spread value
        }
    
    def _calculate_market_health(self, volume_metrics: Dict, price_metrics: Dict, sentiment: Dict) -> float:
        """Calculate overall market health score"""
        volume_score = min(volume_metrics.get('total_volume', 0) / 1000, 100)  # Normalize
        volatility_penalty = max(0, 100 - price_metrics.get('price_volatility', 0) * 100)
        sentiment_score = {'bullish': 80, 'neutral': 50, 'bearish': 20}.get(sentiment.get('overall', 'neutral'), 50)
        
        return (volume_score * 0.3 + volatility_penalty * 0.3 + sentiment_score * 0.4)
    
    def _generate_market_recommendations(self, volume_metrics: Dict, price_metrics: Dict, sentiment: Dict) -> List[str]:
        """Generate market-based recommendations"""
        recommendations = []
        
        if volume_metrics.get('volume_trend') == 'increasing':
            recommendations.append("Market volume is increasing - consider increased participation")
        
        if price_metrics.get('price_volatility', 0) > 0.2:
            recommendations.append("High price volatility detected - consider risk management strategies")
        
        if sentiment.get('overall') == 'bullish':
            recommendations.append("Bullish sentiment - favorable conditions for asset creation and investment")
        elif sentiment.get('overall') == 'bearish':
            recommendations.append("Bearish sentiment - consider defensive positioning or value opportunities")
        
        return recommendations
    
    def _train_models_with_synthetic_data(self):
        """Train ML models with synthetic data (for demo purposes)"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: price, utility_count, creator_reputation, market_sentiment, asset_age
        X = np.random.rand(n_samples, 5)
        X[:, 0] *= 10  # price range 0-10
        X[:, 1] *= 5   # utility_count range 0-5
        X[:, 2] *= 100 # creator_reputation range 0-100
        X[:, 3] *= 1   # market_sentiment 0-1
        X[:, 4] *= 365 # asset_age in days
        
        # Target: future price (synthetic relationship)
        y_price = (X[:, 0] * 1.1 +  # base price influence
                  X[:, 1] * 0.3 +   # utility bonus
                  X[:, 2] * 0.01 +  # reputation influence
                  X[:, 3] * 2 +     # sentiment influence
                  np.random.normal(0, 0.5, n_samples))  # noise
        
        # Target: demand (synthetic relationship)
        y_demand = (X[:, 1] * 20 +     # utility drives demand
                   X[:, 2] * 0.1 +    # reputation drives demand
                   (1 - X[:, 4]/365) * 10 +  # newer assets have higher demand
                   X[:, 3] * 15 +     # sentiment drives demand
                   np.random.normal(0, 2, n_samples))  # noise
        
        # Split and train models
        X_train, X_test, y_price_train, y_price_test = train_test_split(X, y_price, test_size=0.2, random_state=42)
        _, _, y_demand_train, y_demand_test = train_test_split(X, y_demand, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train models
        self.price_model.fit(X_train_scaled, y_price_train)
        self.demand_model.fit(X_train_scaled, y_demand_train)
        
        self.trained = True
    
    def _prepare_prediction_features(self, asset_features: Dict, market_conditions: Dict) -> List[float]:
        """Prepare feature vector for prediction"""
        features = [
            float(asset_features.get('price', 1.0)),
            len(asset_features.get('utility_features', [])),
            float(asset_features.get('creator_reputation', 50)),
            self._sentiment_to_numeric(market_conditions.get('sentiment', 'neutral')),
            float(asset_features.get('age_days', 0))
        ]
        
        return self.scaler.transform([features])[0] if self.trained else features
    
    def _sentiment_to_numeric(self, sentiment: str) -> float:
        """Convert sentiment string to numeric value"""
        sentiment_map = {'bearish': 0.2, 'neutral': 0.5, 'bullish': 0.8}
        return sentiment_map.get(sentiment.lower(), 0.5)
    
    def _calculate_confidence_interval(self, prediction: float, asset_features: Dict, market_conditions: Dict) -> Dict[str, float]:
        """Calculate prediction confidence interval"""
        # Base uncertainty
        base_uncertainty = 0.15
        
        # Increase uncertainty for newer assets
        age_days = asset_features.get('age_days', 0)
        age_factor = max(0.05, 1 - age_days / 365) if age_days < 365 else 0.05
        
        # Market volatility factor
        volatility = market_conditions.get('volatility', 0.3)
        
        total_uncertainty = base_uncertainty + age_factor + volatility * 0.2
        
        return {
            'lower_bound': prediction * (1 - total_uncertainty),
            'upper_bound': prediction * (1 + total_uncertainty),
            'confidence_level': max(0.6, 1 - total_uncertainty)
        }
    
    def _identify_risk_factors(self, asset_features: Dict, market_conditions: Dict) -> List[Dict[str, Any]]:
        """Identify key risk factors for the asset"""
        risk_factors = []
        
        # Market volatility risk
        volatility = market_conditions.get('volatility', 0.3)
        if volatility > 0.4:
            risk_factors.append({
                'type': 'market_volatility',
                'severity': 'high' if volatility > 0.6 else 'medium',
                'description': 'High market volatility may impact price stability'
            })
        
        # Liquidity risk
        liquidity = market_conditions.get('liquidity_ratio', 0.5)
        if liquidity < 0.2:
            risk_factors.append({
                'type': 'liquidity',
                'severity': 'medium',
                'description': 'Low liquidity may affect ability to trade asset quickly'
            })
        
        # Creator reputation risk
        reputation = asset_features.get('creator_reputation', 50)
        if reputation < 40:
            risk_factors.append({
                'type': 'creator_reputation',
                'severity': 'medium',
                'description': 'Creator has relatively low reputation score'
            })
        
        # New asset risk
        age_days = asset_features.get('age_days', 0)
        if age_days < 30:
            risk_factors.append({
                'type': 'asset_maturity',
                'severity': 'low',
                'description': 'Asset is relatively new with limited trading history'
            })
        
        return risk_factors
    
    def _calculate_model_confidence(self, features: List[float]) -> float:
        """Calculate model confidence for prediction"""
        # Simple confidence based on feature completeness and ranges
        confidence = 1.0
        
        # Penalize extreme values (outside typical ranges)
        if len(features) >= 5:
            price, utility_count, reputation, sentiment, age = features[:5]
            
            if price < 0.1 or price > 50:
                confidence *= 0.9
            if utility_count > 10:
                confidence *= 0.95
            if reputation < 0 or reputation > 100:
                confidence *= 0.9
            if age > 1000:
                confidence *= 0.95
        
        return max(0.6, confidence)
    
    def _extract_asset_features(self, asset_data: Dict) -> Dict[str, Any]:
        """Extract relevant features from asset data"""
        return {
            'price': float(asset_data.get('price', 0)),
            'utility_features': asset_data.get('utility_features', []),
            'asset_type': asset_data.get('asset_type', 'Digital'),
            'creator_reputation': asset_data.get('creator_reputation', 50),
            'age_days': asset_data.get('age_days', 0),
            'region': asset_data.get('region', 'Global')
        }
    
    def _analyze_price_positioning(self, asset_data: Dict, similar_assets: List[Dict]) -> Dict[str, Any]:
        """Analyze price positioning against competitors"""
        asset_price = float(asset_data.get('price', 0))
        competitor_prices = [float(comp.get('price', 0)) for comp in similar_assets if comp.get('price')]
        
        if not competitor_prices:
            return {'position': 'no_comparison', 'score': 50}
        
        avg_competitor_price = np.mean(competitor_prices)
        price_percentile = len([p for p in competitor_prices if p < asset_price]) / len(competitor_prices)
        
        if price_percentile < 0.25:
            position = 'budget'
            score = 70  # Good for market penetration
        elif price_percentile < 0.5:
            position = 'competitive'
            score = 85  # Sweet spot
        elif price_percentile < 0.75:
            position = 'premium'
            score = 60  # Need strong value proposition
        else:
            position = 'luxury'
            score = 40  # High risk, need exceptional features
        
        return {
            'position': position,
            'score': score,
            'price_percentile': price_percentile * 100,
            'vs_average': ((asset_price - avg_competitor_price) / avg_competitor_price) * 100
        }
    
    def _compare_features(self, asset_features: Dict, competitor_features: List[Dict]) -> Dict[str, Any]:
        """Compare features with competitors"""
        asset_utilities = set(asset_features.get('utility_features', []))
        
        competitor_utilities = set()
        for comp in competitor_features:
            competitor_utilities.update(comp.get('utility_features', []))
        
        advantages = asset_utilities - competitor_utilities
        gaps = competitor_utilities - asset_utilities
        
        feature_score = len(asset_utilities) / max(len(competitor_utilities), 1) * 100
        
        return {
            'score': min(feature_score, 100),
            'advantages': list(advantages),
            'gaps': list(gaps),
            'utility_count_comparison': len(asset_utilities) - (len(competitor_utilities) / max(len(competitor_features), 1))
        }
    
    def _estimate_market_share(self, asset_data: Dict, similar_assets: List[Dict]) -> float:
        """Estimate potential market share"""
        if not similar_assets:
            return 50.0
        
        # Simple market share estimation based on relative strengths
        asset_score = self._calculate_asset_score(asset_data)
        competitor_scores = [self._calculate_asset_score(comp) for comp in similar_assets]
        
        total_score = asset_score + sum(competitor_scores)
        estimated_share = (asset_score / total_score) * 100 if total_score > 0 else 10
        
        return min(estimated_share, 50)  # Cap at 50% for realism
    
    def _calculate_asset_score(self, asset_data: Dict) -> float:
        """Calculate overall asset quality score"""
        price_factor = 1 / max(float(asset_data.get('price', 1)), 0.1)  # Lower price = higher accessibility
        utility_factor = len(asset_data.get('utility_features', [])) * 0.2
        reputation_factor = float(asset_data.get('creator_reputation', 50)) / 100
        
        return price_factor + utility_factor + reputation_factor
    
    def _recommend_positioning_strategy(self, competitive_score: float, price_positioning: Dict) -> Dict[str, Any]:
        """Recommend positioning strategy"""
        strategies = []
        
        if competitive_score < 40:
            strategies.append({
                'type': 'differentiation',
                'action': 'Focus on unique utility features to differentiate from competitors',
                'priority': 'high'
            })
        
        if price_positioning.get('position') == 'luxury' and competitive_score < 60:
            strategies.append({
                'type': 'pricing',
                'action': 'Consider price reduction or add premium features to justify price',
                'priority': 'medium'
            })
        
        if len(strategies) == 0:
            strategies.append({
                'type': 'optimization',
                'action': 'Maintain current positioning while monitoring competitor moves',
                'priority': 'low'
            })
        
        return {
            'strategies': strategies,
            'overall_recommendation': 'strong_position' if competitive_score > 70 else 'needs_improvement'
        }
    
    def _find_undervalued_assets(self, market_data: Dict) -> List[Dict[str, Any]]:
        """Find potentially undervalued assets"""
        assets = market_data.get('assets', [])
        undervalued = []
        
        for asset in assets:
            # Simple undervaluation detection
            price = float(asset.get('price', 0))
            utility_count = len(asset.get('utility_features', []))
            creator_reputation = asset.get('creator_reputation', 50)
            
            # Expected price based on features
            expected_price = (utility_count * 0.5) + (creator_reputation * 0.02) + 1.0
            
            if price < expected_price * 0.7:  # 30% below expected
                potential_return = ((expected_price - price) / price) * 100
                undervalued.append({
                    'id': asset.get('id'),
                    'current_price': price,
                    'expected_price': expected_price,
                    'potential_return': potential_return,
                    'risk_level': 'medium',
                    'confidence': min(potential_return / 50, 0.9)
                })
        
        return sorted(undervalued, key=lambda x: x['potential_return'], reverse=True)[:5]
    
    def _identify_emerging_trends(self, market_data: Dict) -> List[Dict[str, Any]]:
        """Identify emerging market trends"""
        # Mock trend identification - in production, this would use real trend analysis
        trends = [
            {
                'name': 'AI-Generated Content Rights',
                'growth_rate': 45.2,
                'market_size': 'emerging',
                'entry_difficulty': 'medium',
                'confidence': 0.7
            },
            {
                'name': 'Sustainable Digital Assets',
                'growth_rate': 32.1,
                'market_size': 'growing',
                'entry_difficulty': 'low',
                'confidence': 0.8
            },
            {
                'name': 'Cross-Platform Utility NFTs',
                'growth_rate': 28.7,
                'market_size': 'mature',
                'entry_difficulty': 'high',
                'confidence': 0.6
            }
        ]
        
        return trends
    
    def _find_collaboration_opportunities(self, market_data: Dict, user_profile: Dict) -> List[Dict[str, Any]]:
        """Find collaboration opportunities"""
        opportunities = []
        user_skills = user_profile.get('skills', [])
        user_region = user_profile.get('region', 'Global')
        
        # Mock collaboration opportunity finding
        if 'content_creation' in user_skills:
            opportunities.append({
                'type': 'collaboration',
                'opportunity': 'content_creator_partnership',
                'match_score': 85,
                'potential_partners': ['creator_123', 'creator_456'],
                'project_type': 'Phygital NFT Collection',
                'estimated_revenue': 2500
            })
        
        if user_region in ['Mumbai', 'Delhi', 'Bangalore']:
            opportunities.append({
                'type': 'collaboration',
                'opportunity': 'regional_artist_collective',
                'match_score': 78,
                'potential_partners': ['artist_789'],
                'project_type': 'Cultural Heritage NFTs',
                'estimated_revenue': 1800
            })
        
        return opportunities
    
    def _calculate_portfolio_metrics(self, portfolio: List[Dict]) -> Dict[str, Any]:
        """Calculate current portfolio performance metrics"""
        if not portfolio:
            return {'total_value': 0, 'avg_return': 0, 'risk_score': 0}
        
        total_value = sum(float(asset.get('current_value', 0)) for asset in portfolio)
        total_invested = sum(float(asset.get('invested_amount', 0)) for asset in portfolio)
        
        avg_return = ((total_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        
        # Risk calculation based on asset types and diversification
        asset_types = [asset.get('asset_type') for asset in portfolio]
        risk_scores = {'RealWorldAsset': 0.2, 'Phygital': 0.4, 'NFT': 0.6, 'Digital': 0.8}
        avg_risk = np.mean([risk_scores.get(at, 0.5) for at in asset_types])
        
        return {
            'total_value': total_value,
            'total_invested': total_invested,
            'avg_return': avg_return,
            'risk_score': avg_risk,
            'asset_count': len(portfolio)
        }
    
    def _calculate_diversification_score(self, portfolio: List[Dict]) -> float:
        """Calculate portfolio diversification score"""
        if not portfolio:
            return 0.0
        
        # Type diversification
        asset_types = [asset.get('asset_type') for asset in portfolio]
        type_diversity = len(set(asset_types)) / len(asset_types)
        
        # Regional diversification
        regions = [asset.get('region', 'Global') for asset in portfolio]
        region_diversity = len(set(regions)) / len(regions)
        
        # Price range diversification
        prices = [float(asset.get('price', 0)) for asset in portfolio]
        if prices:
            price_std = np.std(prices)
            price_mean = np.mean(prices)
            price_diversity = min(price_std / price_mean, 1.0) if price_mean > 0 else 0
        else:
            price_diversity = 0
        
        return (type_diversity * 0.4 + region_diversity * 0.3 + price_diversity * 0.3)
    
    def _calculate_expected_return(self, asset: Dict, risk_factor: float) -> float:
        """Calculate expected return for an asset"""
        base_return = 0.12  # 12% base return
        
        # Asset type multipliers
        type_multipliers = {
            'RealWorldAsset': 1.5,
            'Phygital': 1.3,
            'NFT': 1.1,
            'Digital': 1.0
        }
        
        asset_type = asset.get('asset_type', 'Digital')
        type_multiplier = type_multipliers.get(asset_type, 1.0)
        
        # Utility feature bonus
        utility_count = len(asset.get('utility_features', []))
        utility_bonus = min(utility_count * 0.05, 0.2)  # Max 20% bonus
        
        # Creator reputation bonus
        reputation = asset.get('creator_reputation', 50)
        reputation_bonus = (reputation - 50) / 500  # Reputation bonus/penalty
        
        expected_return = base_return * type_multiplier * risk_factor + utility_bonus + reputation_bonus
        
        return max(expected_return, 0.02)  # Minimum 2% expected return
    
    def _generate_allocation_recommendations(self, current_portfolio: List[Dict], 
                                           available_assets: List[Dict], 
                                           risk_tolerance: str) -> Dict[str, Any]:
        """Generate portfolio allocation recommendations"""
        risk_allocations = {
            'conservative': {'RealWorldAsset': 40, 'Phygital': 30, 'NFT': 20, 'Digital': 10},
            'moderate': {'RealWorldAsset': 30, 'Phygital': 30, 'NFT': 25, 'Digital': 15},
            'aggressive': {'RealWorldAsset': 20, 'Phygital': 25, 'NFT': 30, 'Digital': 25}
        }
        
        target_allocation = risk_allocations.get(risk_tolerance, risk_allocations['moderate'])
        
        # Calculate current allocation
        current_allocation = {}
        total_value = sum(float(asset.get('current_value', 0)) for asset in current_portfolio)
        
        for asset in current_portfolio:
            asset_type = asset.get('asset_type', 'Digital')
            asset_value = float(asset.get('current_value', 0))
            current_allocation[asset_type] = current_allocation.get(asset_type, 0) + asset_value
        
        # Convert to percentages
        current_percentages = {k: (v/total_value)*100 for k, v in current_allocation.items()} if total_value > 0 else {}
        
        # Generate rebalancing suggestions
        rebalancing_suggestions = []
        for asset_type, target_percent in target_allocation.items():
            current_percent = current_percentages.get(asset_type, 0)
            difference = target_percent - current_percent
            
            if abs(difference) > 5:  # Only suggest if difference > 5%
                action = 'increase' if difference > 0 else 'decrease'
                rebalancing_suggestions.append({
                    'asset_type': asset_type,
                    'action': action,
                    'current_allocation': current_percent,
                    'target_allocation': target_percent,
                    'difference': abs(difference)
                })
        
        return {
            'target_allocation': target_allocation,
            'current_allocation': current_percentages,
            'rebalancing_suggestions': rebalancing_suggestions
        }