import ephem
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import math

class AdvancedNakshatraCalculator:
    def __init__(self):
        # Complete Nakshatra information
        self.nakshatras = [
            {'name': 'Ashwini', 'lord': 'Ketu', 'range': (0, 13.3333)},
            {'name': 'Bharani', 'lord': 'Venus', 'range': (13.3333, 26.6666)},
            {'name': 'Krittika', 'lord': 'Sun', 'range': (26.6666, 40.0)},
            {'name': 'Rohini', 'lord': 'Moon', 'range': (40.0, 53.3333)},
            {'name': 'Mrigashira', 'lord': 'Mars', 'range': (53.3333, 66.6666)},
            {'name': 'Ardra', 'lord': 'Rahu', 'range': (66.6666, 80.0)},
            {'name': 'Punarvasu', 'lord': 'Jupiter', 'range': (80.0, 93.3333)},
            {'name': 'Pushya', 'lord': 'Saturn', 'range': (93.3333, 106.6666)},
            {'name': 'Ashlesha', 'lord': 'Mercury', 'range': (106.6666, 120.0)},
            {'name': 'Magha', 'lord': 'Ketu', 'range': (120.0, 133.3333)},
            {'name': 'Purva Phalguni', 'lord': 'Venus', 'range': (133.3333, 146.6666)},
            {'name': 'Uttara Phalguni', 'lord': 'Sun', 'range': (146.6666, 160.0)},
            {'name': 'Hasta', 'lord': 'Moon', 'range': (160.0, 173.3333)},
            {'name': 'Chitra', 'lord': 'Mars', 'range': (173.3333, 186.6666)},
            {'name': 'Swati', 'lord': 'Rahu', 'range': (186.6666, 200.0)},
            {'name': 'Vishakha', 'lord': 'Jupiter', 'range': (200.0, 213.3333)},
            {'name': 'Anuradha', 'lord': 'Saturn', 'range': (213.3333, 226.6666)},
            {'name': 'Jyeshtha', 'lord': 'Mercury', 'range': (226.6666, 240.0)},
            {'name': 'Mula', 'lord': 'Ketu', 'range': (240.0, 253.3333)},
            {'name': 'Purva Ashadha', 'lord': 'Venus', 'range': (253.3333, 266.6666)},
            {'name': 'Uttara Ashadha', 'lord': 'Sun', 'range': (266.6666, 280.0)},
            {'name': 'Shravana', 'lord': 'Moon', 'range': (280.0, 293.3333)},
            {'name': 'Dhanishta', 'lord': 'Mars', 'range': (293.3333, 306.6666)},
            {'name': 'Shatabhisha', 'lord': 'Rahu', 'range': (306.6666, 320.0)},
            {'name': 'Purva Bhadrapada', 'lord': 'Jupiter', 'range': (320.0, 333.3333)},
            {'name': 'Uttara Bhadrapada', 'lord': 'Saturn', 'range': (333.3333, 346.6666)},
            {'name': 'Revati', 'lord': 'Mercury', 'range': (346.6666, 360.0)}
        ]
        
        # Mahadasha periods (Vimshottari Dasha)
        self.mahadasha_periods = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }
        
        # Planetary characteristics for market prediction
        self.planet_influences = {
            'Ketu': {'volatility': 0.8, 'direction': 'uncertain', 'impact': 'sudden_changes'},
            'Venus': {'volatility': 0.3, 'direction': 'bullish', 'impact': 'steady_growth'},
            'Sun': {'volatility': 0.6, 'direction': 'bullish', 'impact': 'leadership_moves'},
            'Moon': {'volatility': 0.5, 'direction': 'neutral', 'impact': 'sentiment_driven'},
            'Mars': {'volatility': 0.9, 'direction': 'bearish', 'impact': 'aggressive_moves'},
            'Rahu': {'volatility': 0.7, 'direction': 'uncertain', 'impact': 'unexpected_trends'},
            'Jupiter': {'volatility': 0.2, 'direction': 'bullish', 'impact': 'expansion_growth'},
            'Saturn': {'volatility': 0.4, 'direction': 'bearish', 'impact': 'correction_consolidation'},
            'Mercury': {'volatility': 0.5, 'direction': 'neutral', 'impact': 'news_driven'}
        }

    def calculate_moon_position(self, date_time: datetime) -> float:
        """Calculate precise Moon longitude using ephem"""
        observer = ephem.Observer()
        observer.date = date_time
        moon = ephem.Moon(observer)
        
        # Convert to degrees (0-360)
        moon_long_deg = math.degrees(moon.ra)
        return moon_long_deg % 360

    def get_current_nakshatra(self, moon_longitude: float) -> Dict:
        """Get current Nakshatra based on Moon longitude"""
        for nakshatra in self.nakshatras:
            start, end = nakshatra['range']
            if start <= moon_longitude < end:
                return nakshatra
        # Handle edge case for 360 degrees
        return self.nakshatras[0]

    def calculate_dasha_bhukti(self, birth_date: datetime, current_date: datetime) -> Dict:
        """Calculate current Mahadasha and Bhukti (sub-period)"""
        # Simplified dasha calculation - in production, use precise ayanamsa
        total_days = (current_date - birth_date).days
        total_mahadasha_days = sum(self.mahadasha_periods.values()) * 365.25
        
        # Find current mahadasha
        elapsed_days = total_days % total_mahadasha_days
        current_days = 0
        
        for planet, years in self.mahadasha_periods.items():
            planet_days = years * 365.25
            if current_days <= elapsed_days < current_days + planet_days:
                # Calculate bhukti (sub-period)
                bhukti_elapsed = elapsed_days - current_days
                bhukti_total = planet_days / 9  # Each bhukti is 1/9 of mahadasha
                
                # Find bhukti planet (same sequence as mahadasha)
                bhukti_index = int(bhukti_elapsed / bhukti_total)
                bhukti_planets = list(self.mahadasha_periods.keys())
                current_bhukti = bhukti_planets[bhukti_index]
                
                return {
                    'mahadasha_lord': planet,
                    'bhukti_lord': current_bhukti,
                    'mahadasha_progress': (elapsed_days - current_days) / planet_days,
                    'bhukti_progress': (bhukti_elapsed % bhukti_total) / bhukti_total
                }
            current_days += planet_days
        
        return {'mahadasha_lord': 'Ketu', 'bhukti_lord': 'Ketu', 'progress': 0.0}

    def generate_minute_level_predictions(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Generate per-minute Nakshatra and planetary influences"""
        predictions = []
        current_time = start_time
        
        while current_time <= end_time:
            # Calculate Moon position
            moon_long = self.calculate_moon_position(current_time)
            
            # Get current Nakshatra
            current_nakshatra = self.get_current_nakshatra(moon_long)
            
            # Calculate dasha-bhukti (using a fixed birth date for market)
            market_birth = datetime(1992, 7, 1, 9, 15)  # NSE establishment date
            dasha_info = self.calculate_dasha_bhukti(market_birth, current_time)
            
            # Calculate Nakshatra progress within range
            nakshatra_start, nakshatra_end = current_nakshatra['range']
            nakshatra_progress = (moon_long - nakshatra_start) / (nakshatra_end - nakshatra_start)
            
            # Combined influence score
            mahadasha_influence = self.planet_influences[dasha_info['mahadasha_lord']]
            bhukti_influence = self.planet_influences[dasha_info['bhukti_lord']]
            nakshatra_influence = self.planet_influences[current_nakshatra['lord']]
            
            # Weighted combined influence
            total_volatility = (
                mahadasha_influence['volatility'] * 0.4 +
                bhukti_influence['volatility'] * 0.3 +
                nakshatra_influence['volatility'] * 0.3
            )
            
            # Direction prediction
            direction_weights = {
                'bullish': 0, 'bearish': 0, 'neutral': 0, 'uncertain': 0
            }
            
            for influence in [mahadasha_influence, bhukti_influence, nakshatra_influence]:
                direction_weights[influence['direction']] += 1
            
            predicted_direction = max(direction_weights, key=direction_weights.get)
            
            prediction = {
                'timestamp': current_time,
                'time_str': current_time.strftime('%H:%M'),
                'moon_longitude': moon_long,
                'current_nakshatra': current_nakshatra['name'],
                'nakshatra_lord': current_nakshatra['lord'],
                'nakshatra_progress': nakshatra_progress,
                'mahadasha_lord': dasha_info['mahadasha_lord'],
                'bhukti_lord': dasha_info['bhukti_lord'],
                'mahadasha_progress': dasha_info['mahadasha_progress'],
                'bhukti_progress': dasha_info['bhukti_progress'],
                'predicted_volatility': total_volatility,
                'predicted_direction': predicted_direction,
                'combined_influence_score': self.calculate_combined_score(
                    mahadasha_influence, bhukti_influence, nakshatra_influence
                ),
                'key_events': self.detect_key_events(
                    current_nakshatra, dasha_info, nakshatra_progress
                )
            }
            
            predictions.append(prediction)
            current_time += timedelta(minutes=1)
        
        return predictions

    def calculate_combined_score(self, maha_inf, bhukti_inf, nakshatra_inf) -> float:
        """Calculate combined planetary influence score"""
        base_score = (
            maha_inf['volatility'] * 0.4 +
            bhukti_inf['volatility'] * 0.3 +
            nakshatra_inf['volatility'] * 0.3
        )
        
        # Adjust based on direction alignment
        if maha_inf['direction'] == bhukti_inf['direction'] == nakshatra_inf['direction']:
            base_score *= 1.3  # Strong alignment
        
        return min(1.0, base_score)

    def detect_key_events(self, nakshatra: Dict, dasha_info: Dict, nakshatra_progress: float) -> List[str]:
        """Detect significant astrological events"""
        events = []
        
        # Nakshatra change detection (within next 15 minutes)
        if nakshatra_progress > 0.95:
            events.append(f"Approaching {nakshatra['name']} end")
        
        # Mahadasha lord change detection
        if dasha_info['mahadasha_progress'] > 0.98:
            events.append("Mahadasha change imminent")
        
        # Bhukti lord change detection
        if dasha_info['bhukti_progress'] > 0.98:
            events.append("Bhukti change imminent")
        
        # Specific planetary combinations
        if (dasha_info['mahadasha_lord'] == 'Rahu' and 
            dasha_info['bhukti_lord'] == 'Mars'):
            events.append("Rahu-Mars combination - High volatility expected")
        
        if (nakshatra['lord'] == 'Jupiter' and 
            dasha_info['mahadasha_lord'] == 'Jupiter'):
            events.append("Double Jupiter influence - Bullish bias")
        
        return events

    def get_trading_session_predictions(self, analysis_date: datetime) -> Dict:
        """Generate predictions for entire trading session"""
        # NSE trading hours
        market_open = analysis_date.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = analysis_date.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # Generate minute-level predictions
        minute_predictions = self.generate_minute_level_predictions(market_open, market_close)
        
        # Summarize key periods
        key_periods = self.identify_key_periods(minute_predictions)
        
        # Overall session prediction
        session_prediction = self.predict_session_outcome(minute_predictions)
        
        return {
            'minute_predictions': minute_predictions,
            'key_periods': key_periods,
            'session_prediction': session_prediction,
            'dominant_influences': self.get_dominant_influences(minute_predictions),
            'risk_assessment': self.assess_session_risk(minute_predictions)
        }

    def identify_key_periods(self, predictions: List[Dict]) -> List[Dict]:
        """Identify most significant trading periods"""
        key_periods = []
        
        # Find high volatility periods
        high_vol_periods = [p for p in predictions if p['predicted_volatility'] > 0.7]
        if high_vol_periods:
            key_periods.append({
                'type': 'High Volatility',
                'periods': [p['time_str'] for p in high_vol_periods[:3]],
                'intensity': 'Very High',
                'recommendation': 'Caution - Tight stop losses'
            })
        
        # Find strong directional periods
        strong_bullish = [p for p in predictions if p['predicted_direction'] == 'bullish' 
                         and p['combined_influence_score'] > 0.7]
        strong_bearish = [p for p in predictions if p['predicted_direction'] == 'bearish' 
                         and p['combined_influence_score'] > 0.7]
        
        if strong_bullish:
            key_periods.append({
                'type': 'Strong Bullish Bias',
                'periods': [p['time_str'] for p in strong_bullish[:2]],
                'intensity': 'High',
                'recommendation': 'Good for long entries'
            })
        
        if strong_bearish:
            key_periods.append({
                'type': 'Strong Bearish Bias',
                'periods': [p['time_str'] for p in strong_bearish[:2]],
                'intensity': 'High',
                'recommendation': 'Consider short positions'
            })
        
        return key_periods

    def predict_session_outcome(self, predictions: List[Dict]) -> Dict:
        """Predict overall session outcome"""
        direction_counts = {}
        total_volatility = 0
        
        for pred in predictions:
            direction = pred['predicted_direction']
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
            total_volatility += pred['predicted_volatility']
        
        avg_volatility = total_volatility / len(predictions)
        dominant_direction = max(direction_counts, key=direction_counts.get)
        
        confidence = direction_counts[dominant_direction] / len(predictions)
        
        return {
            'overall_direction': dominant_direction,
            'confidence': confidence,
            'average_volatility': avg_volatility,
            'session_character': self.get_session_character(dominant_direction, avg_volatility)
        }

    def get_session_character(self, direction: str, volatility: float) -> str:
        """Characterize the trading session"""
        if volatility > 0.7:
            return "Highly Volatile"
        elif volatility > 0.5:
            return f"Moderately Volatile {direction.capitalize()}"
        else:
            return f"Stable {direction.capitalize()}"

    def get_dominant_influences(self, predictions: List[Dict]) -> List[Dict]:
        """Get dominant planetary influences for the session"""
        lord_counts = {}
        
        for pred in predictions:
            lords = [pred['mahadasha_lord'], pred['bhukti_lord'], pred['nakshatra_lord']]
            for lord in lords:
                lord_counts[lord] = lord_counts.get(lord, 0) + 1
        
        total = len(predictions) * 3  # 3 lords per prediction
        return [
            {'planet': lord, 'influence_percentage': (count/total)*100}
            for lord, count in sorted(lord_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        ]

    def assess_session_risk(self, predictions: List[Dict]) -> Dict:
        """Assess overall session risk"""
        high_risk_periods = len([p for p in predictions if p['predicted_volatility'] > 0.7])
        risk_ratio = high_risk_periods / len(predictions)
        
        if risk_ratio > 0.3:
            return {'level': 'HIGH', 'advice': 'Reduce position sizing'}
        elif risk_ratio > 0.15:
            return {'level': 'MEDIUM', 'advice': 'Normal caution advised'}
        else:
            return {'level': 'LOW', 'advice': 'Favorable for trading'}
