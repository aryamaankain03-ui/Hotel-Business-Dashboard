import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hotel Performance & Revenue Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM INJECTED STYLING (Modern Dashboard Design) ---
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 5px;
    }
    .metric-sub {
        font-size: 0.75rem;
        margin-top: 8px;
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .badge-positive { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
    .badge-warning { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .badge-danger { background-color: rgba(244, 63, 94, 0.15); color: #f43f5e; }
    
    /* Plotly Chart Container Customization */
    .stPlotlyChart {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING & PREPROCESSING ---
@st.cache_data
def load_data():
    df = pd.read_csv("hotel_bookings_data.csv")
    
    df['children'] = df['children'].fillna(0)
    df['city'] = df['city'].fillna('Unknown')
    df['total_stay'] = df['stays_in_weekend_nights'] + df['stays_in_weekdays_nights']
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['cancellation_label'] = df['is_canceled'].map({0: 'Not Canceled', 1: 'Canceled'})
    
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=month_order, ordered=True)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}. Please ensure 'hotel_bookings_data.csv' is placed in the project directory.")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🏨 Analytics Control Center")
    st.markdown("---")
    
    # Filter 1: Hotel Type
    hotel_types = df['hotel'].unique().tolist()
    selected_hotels = st.multiselect("Hotel Category", options=hotel_types, default=hotel_types)
    
    # Filter 2: Arrival Year
    available_years = sorted(df['arrival_date_year'].unique().tolist())
    selected_years = st.multiselect("Arrival Year", options=available_years, default=available_years)
    
    # Filter 3: Market Segment
    market_segments = df['market_segment'].dropna().unique().tolist()
    selected_segments = st.multiselect("Market Segment", options=market_segments, default=market_segments)
    
    # Filter 4: Lead Time Slider
    max_lead = int(df['lead_time'].max())
    selected_lead_time = st.slider("Lead Time Range (Days)", 0, max_lead, (0, max_lead))
    
    st.markdown("---")
    st.caption("✨ Interactive Filters automatically update figures across all analysis modules.")

# Apply Filters
filtered_df = df[
    (df['hotel'].isin(selected_hotels)) &
    (df['arrival_date_year'].isin(selected_years)) &
    (df['market_segment'].isin(selected_segments)) &
    (df['lead_time'].between(selected_lead_time[0], selected_lead_time[1]))
]

# --- PLOTLY COLOR PALETTE & THEME ---
CHART_THEME = "plotly_dark"
COLOR_PRIMARY = "#6366f1"
COLOR_SECONDARY = "#38bdf8"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#f43f5e"
COLOR_ACCENT = "#f59e0b"

# --- MAIN DASHBOARD HEADER ---
st.title("🏨 Hotel Business & Revenue Intelligence")
st.markdown("Real-time executive dashboard analyzing operational efficiency, booking velocity, and customer behavior.")

if filtered_df.empty:
    st.warning("⚠️ No records match the current filter selection. Please adjust your criteria in the left panel.")
    st.stop()

# --- EXECUTIVE SUMMARY KPI METRICS ---
total_bookings = len(filtered_df)
cancellation_rate = (filtered_df['is_canceled'].sum() / total_bookings) * 100 if total_bookings > 0 else 0
avg_adr = filtered_df['adr'].mean()
avg_lead_time = filtered_df['lead_time'].mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Bookings</div>
            <div class="metric-value">{total_bookings:,}</div>
            <span class="metric-sub badge-positive">✓ Active Filter Subset</span>
        </div>
    """, unsafe_allow_html=True)

with c2:
    badge_class = "badge-danger" if cancellation_rate > 30 else "badge-positive"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cancellation Rate</div>
            <div class="metric-value">{cancellation_rate:.1f}%</div>
            <span class="metric-sub {badge_class}">⚡ Industry Benchmark ~30%</span>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average ADR</div>
            <div class="metric-value">${avg_adr:.2f}</div>
            <span class="metric-sub badge-positive">📈 Yield / Room Night</span>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Lead Time</div>
            <div class="metric-value">{avg_lead_time:.0f} <span style="font-size: 1rem;">Days</span></div>
            <span class="metric-sub badge-warning">⏱️ Booking Window</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Demand & Revenue", 
    "🚫 Cancellation Analytics", 
    "🌍 Guest Segments", 
    "🔍 Data Explorer"
])

# --- TAB 1: DEMAND & REVENUE ---
with tab1:
    st.markdown("### Booking Patterns & Revenue Dynamics")
    col1, col2 = st.columns(2)
    
    with col1:
        hotel_counts = filtered_df.groupby(['hotel', 'cancellation_label']).size().reset_index(name='count')
        fig_hotel = px.bar(
            hotel_counts, 
            x='hotel', 
            y='count', 
            color='cancellation_label',
            barmode='group',
            title='Booking Volume by Property Type & Status',
            labels={'count': 'Bookings', 'hotel': '', 'cancellation_label': 'Status'},
            color_discrete_map={'Not Canceled': COLOR_SUCCESS, 'Canceled': COLOR_DANGER},
            template=CHART_THEME
        )
        fig_hotel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title_text='')
        st.plotly_chart(fig_hotel, use_container_width=True)
        
    with col2:
        monthly_df = filtered_df.groupby(['arrival_date_month', 'hotel'], observed=False).size().reset_index(name='bookings')
        fig_monthly = px.line(
            monthly_df, 
            x='arrival_date_month', 
            y='bookings', 
            color='hotel',
            markers=True,
            title='Monthly Seasonality Trends',
            labels={'arrival_date_month': '', 'bookings': 'Arrivals', 'hotel': 'Property'},
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY],
            template=CHART_THEME
        )
        fig_monthly.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_monthly, use_container_width=True)

    # ADR Breakdown
    st.markdown("### Average Daily Rate (ADR) Distribution")
    fig_adr = px.box(
        filtered_df[(filtered_df['adr'] > 0) & (filtered_df['adr'] < 600)], 
        x='hotel', 
        y='adr', 
        color='cancellation_label',
        title='Yield Distribution Across Room Bookings ($)',
        labels={'adr': 'Rate ($)', 'hotel': ''},
        color_discrete_map={'Not Canceled': COLOR_SECONDARY, 'Canceled': COLOR_ACCENT},
        template=CHART_THEME
    )
    fig_adr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title_text='')
    st.plotly_chart(fig_adr, use_container_width=True)

# --- TAB 2: CANCELLATION ANALYTICS ---
with tab2:
    st.markdown("### Root Cause & Risk Analysis for Cancellations")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_lead = px.histogram(
            filtered_df, 
            x='lead_time', 
            color='cancellation_label', 
            nbins=35,
            title='Lead Time Horizon vs. Cancellation Risk',
            labels={'lead_time': 'Lead Time (Days)', 'count': 'Bookings'},
            barmode='overlay',
            opacity=0.75,
            color_discrete_map={'Not Canceled': COLOR_SUCCESS, 'Canceled': COLOR_DANGER},
            template=CHART_THEME
        )
        fig_lead.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title_text='')
        st.plotly_chart(fig_lead, use_container_width=True)
        
    with col2:
        stay_cancel = filtered_df.groupby('total_stay')['is_canceled'].agg(['count', 'mean']).reset_index()
        stay_cancel = stay_cancel[(stay_cancel['count'] > 50) & (stay_cancel['total_stay'] <= 14)]
        stay_cancel['cancellation_rate'] = stay_cancel['mean'] * 100
        
        fig_stay = px.bar(
            stay_cancel, 
            x='total_stay', 
            y='cancellation_rate',
            title='Cancellation Propensity by Length of Stay (Nights)',
            labels={'total_stay': 'Length of Stay (Nights)', 'cancellation_rate': 'Cancellation Rate (%)'},
            color='cancellation_rate',
            color_continuous_scale='Reds',
            template=CHART_THEME
        )
        fig_stay.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_stay, use_container_width=True)

    # Deposit Type Impact
    st.markdown("### Deposit Policy Impact on Completion")
    deposit_df = filtered_df.groupby(['deposit_type', 'cancellation_label']).size().reset_index(name='count')
    fig_deposit = px.bar(
        deposit_df, 
        x='deposit_type', 
        y='count', 
        color='cancellation_label',
        title='Booking Outcomes by Deposit Policy',
        barmode='stack',
        color_discrete_map={'Not Canceled': COLOR_SUCCESS, 'Canceled': COLOR_DANGER},
        template=CHART_THEME
    )
    fig_deposit.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title_text='')
    st.plotly_chart(fig_deposit, use_container_width=True)

# --- TAB 3: GUEST SEGMENTS ---
with tab3:
    st.markdown("### Origin Locations & Channel Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        top_cities = filtered_df['city'].value_counts().head(10).reset_index()
        top_cities.columns = ['city', 'count']
        fig_city = px.bar(
            top_cities, 
            y='city', 
            x='count', 
            orientation='h',
            title='Top 10 Guest Origin Locations',
            labels={'city': '', 'count': 'Guests'},
            color='count',
            color_continuous_scale='Teal',  # Valid Plotly colorscale string
            template=CHART_THEME
        )
        fig_city.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_city, use_container_width=True)
        
    with col2:
        segment_df = filtered_df['market_segment'].value_counts().reset_index()
        segment_df.columns = ['market_segment', 'count']
        fig_segment = px.pie(
            segment_df, 
            values='count', 
            names='market_segment',
            title='Market Segment Share',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template=CHART_THEME
        )
        fig_segment.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_segment, use_container_width=True)

# --- TAB 4: RAW DATA EXPLORER ---
with tab4:
    st.markdown("### Interactive Dataset Inspection")
    
    # Quick Summary Expander
    with st.expander("📌 Summary Dataset Statistics"):
        st.write(filtered_df.describe())
        
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download Action
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_data,
        file_name="filtered_hotel_analytics.csv",
        mime="text/csv"
    )