import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from advanced_nakshatra import AdvancedNakshatraCalculator

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
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-header">⏰ Minute-Level Nakshatra Market Analysis</div>', unsafe_allow_html=True)
        
        # Generate predictions
        with st.spinner("Calculating minute-level Nakshatra influences..."):
            predictions = self.nakshatra_calc.get_trading_session_predictions(analysis_date)
        
        # Overview Section
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Session Direction", 
                     predictions['session_prediction']['overall_direction'].upper(),
                     "Confidence: {:.1f}%".format(predictions['session_prediction']['confidence'] * 100))
        
        with col2:
            st.metric("Volatility Level", 
                     predictions['session_prediction']['average_volatility'],
                     predictions['session_prediction']['session_character'])
        
        with col3:
            st.metric("Risk Assessment", 
                     predictions['risk_assessment']['level'],
                     predictions['risk_assessment']['advice'])
        
        with col4:
            dominant_planet = predictions['dominant_influences'][0]['planet']
            st.metric("Dominant Influence", dominant_planet, 
                     "{}% influence".format(int(predictions['dominant_influences'][0]['influence_percentage'])))
        
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
    
    def create_minute_level_charts(self, minute_predictions):
        """Create minute-level interactive charts"""
        
        df = pd.DataFrame(minute_predictions)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Planetary Influence Score', 'Predicted Volatility', 'Market Direction Bias'),
            vertical_spacing=0.08,
            row_heights=[0.4, 0.3, 0.3]
        )
        
        # 1. Combined Influence Score
        fig.add_trace(
            go.Scatter(x=df['time_str'], y=df['combined_influence_score'],
                      mode='lines', name='Influence Score', line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Add Nakshatra change markers
        nakshatra_changes = self.find_nakshatra_changes(df)
        for change in nakshatra_changes:
            fig.add_vline(x=change['index'], line_dash="dash", line_color="red", 
                         annotation_text=change['nakshatra'], row=1, col=1)
        
        # 2. Volatility
        fig.add_trace(
            go.Scatter(x=df['time_str'], y=df['predicted_volatility'],
                      mode='lines', name='Volatility', line=dict(color='orange', width=2)),
            row=2, col=1
        )
        
        # 3. Direction (encoded numerically)
        direction_map = {'bullish': 1, 'neutral': 0, 'bearish': -1, 'uncertain': 0}
        df['direction_numeric'] = df['predicted_direction'].map(direction_map)
        
        fig.add_trace(
            go.Scatter(x=df['time_str'], y=df['direction_numeric'],
                      mode='lines', name='Direction', line=dict(color='green', width=2)),
            row=3, col=1
        )
        
        # Add horizontal reference lines
        fig.add_hline(y=0, line_dash="dot", line_color="gray", row=3, col=1)
        
        fig.update_layout(height=800, showlegend=True, title_text="Minute-Level Market Predictions")
        fig.update_xaxes(title_text="Time", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional detailed chart
        self.create_planetary_breakdown_chart(df)
    
    def create_planetary_breakdown_chart(self, df):
        """Create detailed planetary influence breakdown"""
        
        fig = go.Figure()
        
        # Add traces for each planetary combination
        unique_combinations = df[['mahadasha_lord', 'bhukti_lord', 'nakshatra_lord']].drop_duplicates()
        
        for _, combo in unique_combinations.iterrows():
            combo_data = df[
                (df['mahadasha_lord'] == combo['mahadasha_lord']) &
                (df['bhukti_lord'] == combo['bhukti_lord']) &
                (df['nakshatra_lord'] == combo['nakshatra_lord'])
            ]
            
            if not combo_data.empty:
                label = f"{combo['mahadasha_lord']}-{combo['bhukti_lord']}-{combo['nakshatra_lord']}"
                fig.add_trace(
                    go.Scatter(x=combo_data['time_str'], y=combo_data['combined_influence_score'],
                              mode='lines', name=label, line=dict(width=2))
                )
        
        fig.update_layout(
            title="Planetary Combination Influences",
            xaxis_title="Time",
            yaxis_title="Influence Score",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def find_nakshatra_changes(self, df):
        """Find Nakshatra transition points"""
        changes = []
        current_nakshatra = None
        
        for i, row in df.iterrows():
            if current_nakshatra is None:
                current_nakshatra = row['current_nakshatra']
            elif row['current_nakshatra'] != current_nakshatra:
                changes.append({
                    'index': i,
                    'time': row['time_str'],
                    'nakshatra': row['current_nakshatra'],
                    'previous': current_nakshatra
                })
                current_nakshatra = row['current_nakshatra']
        
        return changes
    
    def create_planetary_influences_section(self, predictions):
        """Display detailed planetary influences"""
        
        st.markdown("### 🪐 Planetary Influences Analysis")
        
        # Dominant influences
        st.markdown("#### Dominant Planetary Influences")
        for influence in predictions['dominant_influences']:
            planet = influence['planet']
            percentage = influence['influence_percentage']
            info = self.nakshatra_calc.planet_influences[planet]
            
            st.markdown(f"""
            <div class="planet-card">
            <h4>{planet} ({percentage:.1f}%)</h4>
            <p>Direction: {info['direction'].upper()}</p>
            <p>Volatility: {info['volatility']}</p>
            <p>Impact: {info['impact'].replace('_', ' ').title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key periods
        st.markdown("#### 🎯 Key Trading Periods")
        for period in predictions['key_periods']:
            st.markdown(f"""
            <div class="time-slot-card">
            <strong>{period['type']}</strong><br/>
            Times: {', '.join(period['periods'])}<br/>
            Intensity: {period['intensity']}<br/>
            <em>{period['recommendation']}</em>
            </div>
            """, unsafe_allow_html=True)
    
    def create_trading_recommendations(self, predictions):
        """Create trading recommendations"""
        
        st.markdown("### 💡 Trading Strategy")
        
        session_pred = predictions['session_prediction']
        risk_assessment = predictions['risk_assessment']
        
        # Position sizing recommendation
        if risk_assessment['level'] == 'HIGH':
            position_size = "10-15% of capital"
            stop_loss = "Tight (0.5-1%)"
        elif risk_assessment['level'] == 'MEDIUM':
            position_size = "20-25% of capital"
            stop_loss = "Normal (1-2%)"
        else:
            position_size = "30-40% of capital"
            stop_loss = "Wider (2-3%)"
        
        # Strategy based on direction
        if session_pred['overall_direction'] == 'bullish':
            primary_strategy = "Focus on long positions"
            entry_timing = "During pullbacks to support"
        elif session_pred['overall_direction'] == 'bearish':
            primary_strategy = "Focus on short positions"
            entry_timing = "During rallies to resistance"
        else:
            primary_strategy = "Range trading strategy"
            entry_timing = "Buy support, sell resistance"
        
        st.markdown(f"""
        #### Position Management
        - **Position Size**: {position_size}
        - **Stop Loss**: {stop_loss}
        - **Primary Strategy**: {primary_strategy}
        - **Best Entry**: {entry_timing}
        
        #### Session Guidance
        - **Overall Bias**: {session_pred['overall_direction'].upper()}
        - **Confidence**: {session_pred['confidence']:.1%}
        - **Volatility**: {session_pred['average_volatility']:.2f}
        - **Risk Level**: {risk_assessment['level']}
        """)
        
        # Minute-by-minute table for key periods
        st.markdown("#### ⏰ Critical Time Windows")
        df = pd.DataFrame(predictions['minute_predictions'])
        critical_periods = df[df['combined_influence_score'] > 0.7].head(10)
        
        if not critical_periods.empty:
            display_df = critical_periods[['time_str', 'predicted_direction', 'predicted_volatility', 'key_events']]
            st.dataframe(display_df, use_container_width=True)

def main():
    app = MinuteLevelNakshatraApp()
    
    st.sidebar.header("🔮 Advanced Nakshatra Analysis")
    
    analysis_date = st.sidebar.date_input(
        "Analysis Date:",
        datetime.now()
    )
    
    analysis_time = st.sidebar.time_input(
        "Market Open Reference:",
        datetime.now().replace(hour=9, minute=15).time()
    )
    
    if st.sidebar.button("🚀 Generate Minute-Level Analysis", type="primary"):
        combined_datetime = datetime.combine(analysis_date, analysis_time)
        app.create_minute_level_dashboard(combined_datetime)
    
    else:
        st.markdown("""
        ## 🌙 Advanced Minute-Level Nakshatra Analysis
        
        **Professional Features:**
        - ✅ **Minute-level predictions** throughout trading session
        - ✅ **Mahadasha & Bhukti timing** with proportional influences
        - ✅ **Real planetary positions** using astronomical calculations
        - ✅ **Multiple chart types** for comprehensive analysis
        - ✅ **Risk assessment** and position sizing guidance
        - ✅ **Key period identification** for optimal entry/exit
        
        **How it works:**
        1. Select analysis date and time
        2. System calculates precise Moon positions
        3. Determines current Mahadasha-Bhukti periods
        4. Generates per-minute influence predictions
        5. Provides trading recommendations
        
        *Note: Uses NSE establishment date (1992) as market birth chart reference*
        """)

if __name__ == "__main__":
    main()
