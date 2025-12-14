import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utilities.DB_connection import make_sqlalchemy_db_connection
from utilities.utility import get_message, clear_messages
from utilities.manual_upload import handle_manual_upload, cleanup_uploaded_files

# Page config
st.set_page_config(page_title="Skylink Usage Dashboard", layout="wide", page_icon="📈")

# Fetch data from database
@st.cache_resource # Cache the database connection
def get_db_connection():
    return make_sqlalchemy_db_connection()

def load_daily_usage(_connection, start_date, end_date=None):
    query = """
        SELECT * FROM public."USAGE"
        WHERE "timestamp"::date BETWEEN %(start_date)s AND %(end_date)s;
    """
    try:
        @st.cache_data(ttl=600)  # Cache the query result for 10 minutes
        def fetch_data(_connection, query, start_date, end_date):
            return pd.read_sql_query(query, _connection, params={"start_date": start_date, "end_date": end_date or start_date})
        return fetch_data(_connection, query, start_date, end_date)
    except Exception as e:
        return pd.DataFrame()  # Return empty DataFrame on error

db_connection = get_db_connection()

clear_messages()  # Clear previous messages

handle_manual_upload()
if st.session_state.get('etl_completed', False):
    # Show cleanup button
    st.button("OK", on_click=cleanup_uploaded_files)
    uploaded_files = None

#message display
msg = get_message()
if msg.get("info"):
    st.sidebar.info(msg["info"])
if msg.get("warn"):
    st.sidebar.warning(msg["warn"])
if msg.get("error"):
    st.sidebar.error(msg["error"])
if msg.get("success"):
    st.sidebar.success(msg["success"])

# Sidebar filters
st.sidebar.title("🧾 Filters")
date_today = "2025-01-15" # Hardcoded for demo; replace with date.today() for real use if data would cover current date
start_date_input = st.sidebar.date_input("Start Date", value=date_today).strftime('%Y-%m-%d')
end_date_input = st.sidebar.date_input("End Date", value=start_date_input).strftime('%Y-%m-%d')

# Load data
daily_usage = load_daily_usage(db_connection, start_date_input, end_date_input)

if daily_usage.empty:
    st.warning(f"No data available for {date_today}")
    st.stop()

# Convert timestamp to datetime if needed
if 'timestamp' in daily_usage.columns:
    daily_usage['timestamp'] = pd.to_datetime(daily_usage['timestamp'])
    daily_usage['hour'] = daily_usage['timestamp'].dt.hour

# Sidebar filters - Usage threshold
min_usage = st.sidebar.number_input("Min Usage (MB)", min_value=0.0, value=0.0, step=10.0)

# Apply filters
filtered_data = daily_usage.copy()
if min_usage > 0:
    filtered_data = filtered_data[filtered_data['total_usage_mb'] >= min_usage]

# Main Dashboard
date_range = f"{start_date_input} to {end_date_input}" if (end_date_input != start_date_input) else f"{start_date_input}"
st.title(f"📈 Skylink Usage Dashboard {date_range}")
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Data (GB)", f"{filtered_data['total_usage_mb'].sum() / 1024:.2f}")

with col2:
    st.metric("Total Sessions", f"{len(filtered_data):,}")

with col3:
    st.metric("Unique Users", f"{filtered_data['msisdn'].nunique():,}")

with col4:
    avg_throughput = filtered_data['avg_throughput'].mean()
    st.metric("Avg Throughput (Mbps)", f"{avg_throughput:.2f}" if pd.notna(avg_throughput) else "N/A")

with col5:
    avg_latency = filtered_data['latency_ms'].mean()
    st.metric("Avg Latency (ms)", f"{avg_latency:.1f}" if pd.notna(avg_latency) else "N/A")

st.markdown("---")

# Volume Analysis (Top 10 Users)

st.subheader("📈 Top 10 Users by Data Usage")
top_users = filtered_data.groupby('msisdn').agg({
    'total_usage_mb': 'sum',
    'session_id': 'count'
}).reset_index()
top_users.columns = ['MSISDN', 'Total Usage (MB)', 'Sessions']
top_users = top_users.sort_values('Total Usage (MB)', ascending=False).head(10)

fig_top_users = px.bar(
    top_users, 
    x='MSISDN', 
    y='Total Usage (MB)',
    text='Total Usage (MB)',
    color='Total Usage (MB)',
    color_continuous_scale='Blues'
)
fig_top_users.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig_top_users.update_layout(
    showlegend=False, 
    xaxis_title="MSISDN", 
    yaxis_title="Usage (MB)",
    xaxis=dict(
        tickangle=-60,
        type='category',
        categoryorder='array',
        categoryarray=top_users['MSISDN']
    ),
    height=500,
    bargap=0.1
)
st.plotly_chart(fig_top_users, use_container_width=True)

st.markdown("---")

# Row 2: Time Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏰ Hourly Usage Distribution")
    if 'hour' in filtered_data.columns:
        hourly_usage = filtered_data.groupby('hour').agg({
            'total_usage_mb': 'sum',
            'session_id': 'count'
        }).reset_index()
        hourly_usage.columns = ['Hour', 'Total Usage (MB)', 'Sessions']
        
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Bar(
            x=hourly_usage['Hour'], 
            y=hourly_usage['Total Usage (MB)'],
            name='Usage (MB)',
            marker_color='steelblue'
        ))
        fig_hourly.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Total Usage (MB)",
            xaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    st.subheader("📊 Session Count by Hour")
    if 'hour' in filtered_data.columns:
        fig_sessions = px.line(
            hourly_usage, 
            x='Hour', 
            y='Sessions',
            markers=True,
            line_shape='spline'
        )
        fig_sessions.update_traces(line_color='coral', marker=dict(size=8))
        fig_sessions.update_layout(xaxis_title="Hour of Day", yaxis_title="Number of Sessions")
        st.plotly_chart(fig_sessions, use_container_width=True)

st.markdown("---")

# Row 3: Network Performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Throughput Distribution")
    fig_throughput = px.histogram(
        filtered_data, 
        x='avg_throughput',
        nbins=30,
        labels={'avg_throughput': 'Throughput (Mbps)'},
        color_discrete_sequence=['teal']
    )
    fig_throughput.update_layout(xaxis_title="Throughput (Mbps)", yaxis_title="Frequency")
    st.plotly_chart(fig_throughput, use_container_width=True)

with col2:
    st.subheader("📡 Latency Distribution")
    fig_latency = px.box(
        filtered_data, 
        y='latency_ms',
        labels={'latency_ms': 'Latency (ms)'},
        color_discrete_sequence=['salmon']
    )
    fig_latency.update_layout(yaxis_title="Latency (ms)")
    st.plotly_chart(fig_latency, use_container_width=True)

st.markdown("---")

# Row 4: Session Analytics
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Session Duration Distribution")
    filtered_data['duration_sec'] = filtered_data['duration_ms'] / 1000
    fig_duration = px.histogram(
        filtered_data, 
        x='duration_sec',
        nbins=30,
        labels={'duration_sec': 'Duration (seconds)'},
        color_discrete_sequence=['purple']
    )
    fig_duration.update_layout(xaxis_title="Duration (seconds)", yaxis_title="Frequency")
    st.plotly_chart(fig_duration, use_container_width=True)

with col2:
    st.subheader("📱 Sessions per User")
    sessions_per_user = filtered_data.groupby('msisdn').size().reset_index(name='Sessions')
    fig_sessions_user = px.histogram(
        sessions_per_user, 
        x='Sessions',
        nbins=20,
        labels={'Sessions': 'Number of Sessions'},
        color_discrete_sequence=['orange']
    )
    fig_sessions_user.update_layout(xaxis_title="Sessions per User", yaxis_title="Number of Users")
    st.plotly_chart(fig_sessions_user, use_container_width=True)

st.markdown("---")

# Summary Statistics
st.subheader("📋 Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Data Usage**")
    if 'download_mb' in filtered_data.columns and 'upload_mb' in filtered_data.columns:
        st.write(f"- Total Download: {filtered_data['download_mb'].sum():.2f} MB")
        st.write(f"- Total Upload: {filtered_data['upload_mb'].sum():.2f} MB")
    if 'total_usage_mb' in filtered_data.columns:
        st.write(f"- Total Usage: {filtered_data['total_usage_mb'].sum():.2f} MB")
        st.write(f"- Avg per Session: {filtered_data['total_usage_mb'].mean():.2f} MB")

with col2:
    st.markdown("**Session Metrics**")
    if 'duration_ms' in filtered_data.columns:
        st.write(f"- Avg Duration: {filtered_data['duration_ms'].mean() / 1000:.1f} sec")
        st.write(f"- Max Duration: {filtered_data['duration_ms'].max() / 1000:.1f} sec")
        st.write(f"- Min Duration: {filtered_data['duration_ms'].min() / 1000:.1f} sec")

with col3:
    st.markdown("**Network Performance**")
    if 'avg_throughput' in filtered_data.columns:
        st.write(f"- Max Throughput: {filtered_data['avg_throughput'].max():.2f} Mbps")
        st.write(f"- Avg Throughput: {filtered_data['avg_throughput'].mean():.2f} Mbps")
    if 'latency_ms' in filtered_data.columns:
        st.write(f"- Min Latency: {filtered_data['latency_ms'].min():.1f} ms")
        st.write(f"- Max Latency: {filtered_data['latency_ms'].max():.1f} ms")

st.markdown("---")

# Data Table
st.subheader("📄 Detailed Usage Data")
st.dataframe(
    filtered_data[['msisdn', 'timestamp', 'total_usage_mb', 
                   'avg_throughput', 'latency_ms', 'duration_ms']].sort_values('timestamp', ascending=False),
    use_container_width=True,
    height=400
)

# Download Section
st.markdown("---")
st.subheader("💾 Download Data")
col1, col2 = st.columns(2)

with col1:
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"usage_data_{date_range}.csv",
        mime="text/csv"
    )

with col2:
    # Summary stats download
    summary_stats = pd.DataFrame({
        'Metric': ['Total Sessions', 'Total Data (MB)', 'Unique Users', 'Avg Throughput (Mbps)', 'Avg Latency (ms)'],
        'Value': [
            len(filtered_data),
            filtered_data['total_usage_mb'].sum(),
            filtered_data['msisdn'].nunique(),
            filtered_data['avg_throughput'].mean(),
            filtered_data['latency_ms'].mean()
        ]
    })
    summary_csv = summary_stats.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Download Summary Statistics",
        data=summary_csv,
        file_name=f"summary_stats_{date_range}.csv",
        mime="text/csv"
    )
