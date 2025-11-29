import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to path to import our module
sys.path.append(os.path.dirname(__file__))

try:
    from advanced_nakshatra import AdvancedNakshatraCalculator
except ImportError:
    st.error("Advanced Nakshatra module not found. Please ensure advanced_nakshatra.py is in the same directory.")
    st.stop()

class MinuteLevelNakshatraApp:
    def __init__(self):
        self.nakshatra_calc = AdvancedNakshatraCalculator()
        
    def create_minute_level_dashboard(self, analysis_date):
        """Create comprehensive minute-level dashboard"""
        
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(45deg, #1f77b4, #ff7f0e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .planet-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 5px;
        }
        .time-slot-card {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        .warning-card {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-header">⏰ Nakshatra Market Analyst Pro</div>', unsafe_allow_html=True)
        
        # Generate predictions
        with st.spinner("🔮 Calculating minute-level Nakshatra influences..."):
            try:
                predictions = self.nakshatra_calc.get_trading_session_predictions(analysis_date)
            except Exception as e:
                st.error(f"Error in calculations: {str(e)}")
                return
        
        # Overview Section
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            direction = predictions['session_prediction']['overall_direction'].upper()
            confidence = predictions['session_prediction']['confidence'] * 100
            st.metric("Session Direction", direction, f"Confidence: {confidence:.1f}%")
        
        with col2:
            volatility = predictions['session_prediction']['average_volatility']
            character = predictions['session_prediction']['session_character']
            st.metric("Volatility Level", f"{volatility:.2f}", character)
        
        with col3:
            risk_level = predictions['risk_assessment']['level']
            advice = predictions['risk_assessment']['advice']
            st.metric("Risk Assessment", risk_level, advice)
        
        with col4:
            dominant_planet = predictions['dominant_influences'][0]['planet']
            influence_pct = predictions['dominant_influences'][0]['influence_percentage']
            st.metric("Dominant Influence", dominant_planet, f"{influence_pct:.1f}% influence")
        
        st.markdown("---")
        
        # Main Charts Section
        self.create_minute_level_charts(predictions['minute_predictions'])
        
        st.markdown("---")
        
        # Detailed Analysis Section
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            self.create_planetary_influences_section(predictions)
        
        with col_right:
            self.create_trading_recommendations(predictions)
            
        # Disclaimer
        st.markdown("""
        <div class="warning-card">
        <strong>⚠️ Important Disclaimer:</strong><br/>
        This analysis is for educational and research purposes only. Nakshatra-based predictions should be used as one of many tools in your analysis. 
        Always practice proper risk management and consult with financial advisors before making trading decisions.
        Past performance is not indicative of future results.
        </div>
        """, unsafe_allow_html=True)
    
    def create_minute_level_charts(self, minute_predictions):
        """Create minute-level interactive charts"""
        
        df = pd.DataFrame(minute_predictions)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('🪐 Planetary Influence Score', '📈 Predicted Volatility', '🎯 Market Direction Bias'),
            vertical_spacing=0.08,
            row_heights=[0.4, 0.3, 0.3]
        )
        
        # 1. Combined Influence Score
        fig.add_trace(
            go.Scatter(x=df['time_str'], y=df['combined_influence_score'],
                      mode='lines', name='Influence Score', line=dict(color='blue', width=3)),
            row=1, col=1
        )
        
        # Add high influence markers
        high_influence = df[df['combined_influence_score'] > 0.7]
        if not high_influence.empty:
            fig.add_trace(
                go.Scatter(x=high_influence['time_str'], y=high_influence['combined_influence_score'],
                          mode='markers', name='High Influence', marker=dict(color='red', size=8)),
                row=1, col=1
            )
        
        # 2. Volatility
        fig.add_trace(
            go.Scatter(x=df['time_str'], y=df['predicted_volatility'],
                      mode='lines', name='Volatility', line=dict(color='orange', width=3)),
            row=2, col=1
        )
        
        # 3. Direction (encoded numerically)
        direction_map = {'bullish': 1, 'neutral': 0, 'bearish': -1, 'uncertain': 0}
        df['direction_numeric'] = df['predicted_direction'].map(direction_map)
        
        fig.add_trace(
            go.Scatter(x=df['time_str'], y=df['direction_numeric'],
                      mode='lines', name='Direction', line=dict(color='green', width=3)),
            row=3, col=1
        )
        
        # Add horizontal reference lines
        fig.add_hline(y=0, line_dash="dot", line_color="gray", row=3, col=1)
        
        fig.update_layout(
            height=800, 
            showlegend=True, 
            title_text="Minute-Level Market Predictions (9:15 AM - 3:30 PM)",
            template="plotly_white"
        )
        fig.update_xaxes(title_text="Market Time", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional detailed chart
        self.create_planetary_breakdown_chart(df)
    
    def create_planetary_breakdown_chart(self, df):
        """Create detailed planetary influence breakdown"""
        
        st.markdown("### 🔍 Planetary Combination Analysis")
        
        # Simplify by showing only major combinations
        df['planetary_combo'] = df['mahadasha_lord'] + '-' + df['bhukti_lord']
        top_combos = df['planetary_combo'].value_counts().head(5).index
        
        fig = go.Figure()
        
        for combo in top_combos:
            combo_data = df[df['planetary_combo'] == combo]
            if not combo_data.empty:
                fig.add_trace(
                    go.Scatter(x=combo_data['time_str'], y=combo_data['combined_influence_score'],
                              mode='lines', name=combo, line=dict(width=3))
                )
        
        fig.update_layout(
            title="Top Planetary Combination Influences",
            xaxis_title="Market Time",
            yaxis_title="Influence Score",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_planetary_influences_section(self, predictions):
        """Display detailed planetary influences"""
        
        st.markdown("### 🪐 Planetary Influences Analysis")
        
        # Dominant influences
        st.markdown("#### Dominant Planetary Influences")
        for influence in predictions['dominant_influences'][:3]:
            planet = influence['planet']
            percentage = influence['influence_percentage']
            info = self.nakshatra_calc.planet_influences[planet]
            
            # Color code based on direction
            color_map = {
                'bullish': '#28a745',
                'bearish': '#dc3545', 
                'neutral': '#6c757d',
                'uncertain': '#ffc107'
            }
            direction_color = color_map.get(info['direction'], '#6c757d')
            
            st.markdown(f"""
            <div class="planet-card">
            <h4>{planet} ({percentage:.1f}% influence)</h4>
            <p>📊 Direction: <span style="color:{direction_color}">{info['direction'].upper()}</span></p>
            <p>⚡ Volatility: {info['volatility']}</p>
            <p>🎯 Impact: {info['impact'].replace('_', ' ').title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key periods
        st.markdown("#### 🎯 Key Trading Periods")
        if predictions['key_periods']:
            for period in predictions['key_periods']:
                st.markdown(f"""
                <div class="time-slot-card">
                <strong>{period['type']}</strong><br/>
                ⏰ Times: {', '.join(period['periods'])}<br/>
                💪 Intensity: {period['intensity']}<br/>
                <em>💡 {period['recommendation']}</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant key periods identified for this session.")
    
    def create_trading_recommendations(self, predictions):
        """Create trading recommendations"""
        
        st.markdown("### 💡 Trading Strategy")
        
        session_pred = predictions['session_prediction']
        risk_assessment = predictions['risk_assessment']
        
        # Position sizing recommendation
        if risk_assessment['level'] == 'HIGH':
            position_size = "10-15% of capital"
            stop_loss = "Tight (0.5-1%)"
            risk_color = "red"
        elif risk_assessment['level'] == 'MEDIUM':
            position_size = "20-25% of capital"
            stop_loss = "Normal (1-2%)"
            risk_color = "orange"
        else:
            position_size = "30-40% of capital"
            stop_loss = "Wider (2-3%)"
            risk_color = "green"
        
        # Strategy based on direction
        if session_pred['overall_direction'] == 'bullish':
            primary_strategy = "Focus on long positions"
            entry_timing = "During pullbacks to support"
            direction_emoji = "📈"
        elif session_pred['overall_direction'] == 'bearish':
            primary_strategy = "Focus on short positions"
            entry_timing = "During rallies to resistance"
            direction_emoji = "📉"
        else:
            primary_strategy = "Range trading strategy"
            entry_timing = "Buy support, sell resistance"
            direction_emoji = "➡️"
        
        st.markdown(f"""
        #### Position Management
        - **💰 Position Size**: {position_size}
        - **🛡️ Stop Loss**: {stop_loss}
        - **🎯 Primary Strategy**: {primary_strategy} {direction_emoji}
        - **⏰ Best Entry**: {entry_timing}
        
        #### Session Guidance
        - **📊 Overall Bias**: {session_pred['overall_direction'].upper()} {direction_emoji}
        - **🎲 Confidence**: {session_pred['confidence']:.1%}
        - **⚡ Volatility**: {session_pred['average_volatility']:.2f}
        - **⚠️ Risk Level**: <span style="color:{risk_color}">{risk_assessment['level']}</span>
        """, unsafe_allow_html=True)
        
        # Critical periods table
        st.markdown("#### ⏰ Critical Time Windows")
        df = pd.DataFrame(predictions['minute_predictions'])
        critical_periods = df[df['combined_influence_score'] > 0.7].head(8)
        
        if not critical_periods.empty:
            display_df = critical_periods[['time_str', 'predicted_direction', 'predicted_volatility']].copy()
            display_df['predicted_direction'] = display_df['predicted_direction'].str.upper()
            display_df['predicted_volatility'] = display_df['predicted_volatility'].round(3)
            display_df.columns = ['Time', 'Direction', 'Volatility']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No critical periods identified with high influence scores.")

def main():
    app = MinuteLevelNakshatraApp()
    
    st.sidebar.header("🔮 Nakshatra Market Analysis")
    
    # Date input
    analysis_date = st.sidebar.date_input(
        "Analysis Date:",
        datetime.now()
    )
    
    # Info section
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **📖 About This App:**
    
    This application uses advanced Vedic astrology principles to analyze market movements:
    
    - **Mahadasha Timing**: 120-year planetary cycles
    - **Bhukti Periods**: Sub-periods within Mahadasha  
    - **Nakshatra Positions**: Moon's precise constellation
    - **Minute-level Analysis**: Per-minute predictions
    
    *Market Birth Chart: NSE Establishment (1992)*
    """)
    
    if st.sidebar.button("🚀 Generate Market Analysis", type="primary", use_container_width=True):
        # Combine date with market open time
        market_open_time = datetime.strptime("09:15", "%H:%M").time()
        combined_datetime = datetime.combine(analysis_date, market_open_time)
        
        app.create_minute_level_dashboard(combined_datetime)
    
    else:
        # Default landing page
        st.markdown("""
        # 🌙 Nakshatra Market Analyst Pro
        
        ## *Professional Intraday Trading Analysis Using Vedic Astrology*
        
        ### 🎯 What This App Provides:
        
        **📊 Minute-Level Predictions**
        - Per-minute market influence scores throughout trading session (9:15 AM - 3:30 PM)
        - Real-time volatility forecasts
        - Direction bias indicators
        
        **🪐 Advanced Astrological Framework**
        - **Mahadasha-Bhukti System**: Vimshottari dasha with proportional timing
        - **Real Astronomical Calculations**: Precise Moon positions using NASA-grade ephemeris
        - **Multi-layer Analysis**: Combined influence of Mahadasha, Bhukti, and Nakshatra lords
        
        **💼 Professional Trading Tools**
        - Risk assessment with position sizing guidance
        - Key period identification for optimal entries/exits
        - Planetary combination analysis
        - Session characterization and confidence scoring
        
        ### 🚀 How to Use:
        1. **Select** your analysis date in the sidebar
        2. **Click** "Generate Market Analysis" 
        3. **Review** the minute-level charts and predictions
        4. **Implement** the trading recommendations with proper risk management
        
        ### 📈 Sample Analysis Includes:
        - Planetary influence scores throughout the day
        - Volatility expectations per minute
        - Market direction bias (Bullish/Bearish/Neutral)
        - Key trading periods with specific timings
        - Risk assessment and position sizing
        
        *Click the button in the sidebar to begin your analysis!*
        """)
        
        # Sample preview
        st.markdown("---")
        st.markdown("### 📸 Sample Analysis Preview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Session Direction", "BULLISH", "78% Confidence")
        with col2:
            st.metric("Volatility Level", "0.68", "Moderately Volatile")
        with col3:
            st.metric("Risk Assessment", "MEDIUM", "Normal Caution")

if __name__ == "__main__":
    main()
