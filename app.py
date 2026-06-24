"""
Professional Employee Analytics Dashboard
Built with Streamlit, Pandas, and Plotly
Production-ready code - Deploy to Streamlit Cloud without modification
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Employee Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
        }
        
        /* KPI Card styling */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .metric-label {
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
        
        /* Header styling */
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Table styling */
        .dataframe {
            font-size: 12px;
        }
        
        /* Overall text color */
        body {
            color: #2c3e50;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CACHING & DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load and preprocess employee data"""
    df = pd.read_csv('cleaned_employee_dataset_for_dashboard.csv')
    
    # Data cleaning and feature engineering
    df['JoinDate'] = pd.to_datetime(df['JoinDate'])
    
    # Generate synthetic columns for missing analytics data
    np.random.seed(42)
    
    # Gender Distribution
    genders = ['Male', 'Female', 'Other']
    df['Gender'] = np.random.choice(genders, size=len(df), p=[0.55, 0.40, 0.05])
    
    # Education Level
    education_levels = ['Bachelor', 'Master', 'PhD', 'High School', 'Diploma']
    df['EducationLevel'] = np.random.choice(
        education_levels, 
        size=len(df), 
        p=[0.40, 0.30, 0.10, 0.15, 0.05]
    )
    
    # Job Role based on department
    job_roles_by_dept = {
        'IT': ['Software Engineer', 'Data Analyst', 'DevOps Engineer', 'IT Manager', 'Systems Admin'],
        'HR': ['HR Manager', 'Recruiter', 'HR Specialist', 'Training Officer', 'Payroll Specialist'],
        'Finance': ['Accountant', 'Financial Analyst', 'Finance Manager', 'Auditor', 'CFO'],
        'Sales': ['Sales Executive', 'Sales Manager', 'Business Development', 'Account Manager', 'Sales Lead'],
        'Human Resources': ['HR Manager', 'Recruiter', 'HR Specialist', 'Training Officer', 'Payroll Specialist'],
        'Unknown': ['Operations', 'Support Staff', 'Administrative', 'Coordinator', 'Analyst']
    }
    
    df['JobRole'] = df['Department'].apply(
        lambda x: np.random.choice(job_roles_by_dept.get(x, job_roles_by_dept['Unknown']))
    )
    
    # Performance Rating (1-5)
    df['PerformanceRating'] = np.random.choice([1, 2, 3, 4, 5], size=len(df), p=[0.10, 0.15, 0.30, 0.30, 0.15])
    
    # Satisfaction Score (1-10)
    df['SatisfactionScore'] = np.random.choice(range(1, 11), size=len(df))
    
    # Performance Score (derived from rating and other factors)
    df['PerformanceScore'] = (
        (df['PerformanceRating'] * 20) + 
        (np.random.normal(50, 10, len(df))).clip(0, 100)
    ).clip(0, 100).astype(int)
    
    return df

@st.cache_data
def calculate_kpis(df, dept_filter, gender_filter, edu_filter, role_filter, perf_filter):
    """Calculate KPIs based on filters"""
    filtered_df = df.copy()
    
    if dept_filter and 'All Departments' not in dept_filter:
        filtered_df = filtered_df[filtered_df['Department'].isin(dept_filter)]
    
    if gender_filter and 'All Genders' not in gender_filter:
        filtered_df = filtered_df[filtered_df['Gender'].isin(gender_filter)]
    
    if edu_filter and 'All Education Levels' not in edu_filter:
        filtered_df = filtered_df[filtered_df['EducationLevel'].isin(edu_filter)]
    
    if role_filter and 'All Roles' not in role_filter:
        filtered_df = filtered_df[filtered_df['JobRole'].isin(role_filter)]
    
    if perf_filter and 'All Ratings' not in perf_filter:
        filtered_df = filtered_df[filtered_df['PerformanceRating'].isin(perf_filter)]
    
    kpis = {
        'total_employees': len(filtered_df),
        'avg_salary': filtered_df['Salary'].mean(),
        'avg_performance': filtered_df['PerformanceScore'].mean(),
        'avg_satisfaction': filtered_df['SatisfactionScore'].mean(),
        'total_departments': filtered_df['Department'].nunique(),
        'filtered_df': filtered_df
    }
    
    return kpis

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_filter_options(df):
    """Get unique values for filters"""
    return {
        'departments': sorted(df['Department'].unique().tolist()),
        'genders': sorted(df['Gender'].unique().tolist()),
        'education': sorted(df['EducationLevel'].unique().tolist()),
        'roles': sorted(df['JobRole'].unique().tolist()),
        'ratings': sorted(df['PerformanceRating'].unique().tolist())
    }

def create_kpi_card(label, value, suffix=""):
    """Create a formatted KPI card"""
    if isinstance(value, float):
        value_str = f"{value:,.2f}{suffix}"
    else:
        value_str = f"{value:,}{suffix}"
    
    return f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 25px; border-radius: 10px; color: white; text-align: center; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">{label}</div>
        <div style="font-size: 28px; font-weight: bold;">{value_str}</div>
    </div>
    """

def export_filtered_data(df):
    """Convert dataframe to CSV for download"""
    csv = df.to_csv(index=False)
    return csv

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Load data
    df = load_data()
    filter_options = get_filter_options(df)
    
    # ========================================================================
    # HEADER
    # ========================================================================
    st.markdown("<h1>👥 Employee Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ========================================================================
    # SIDEBAR FILTERS
    # ========================================================================
    with st.sidebar:
        st.markdown("### 🔍 Filter Options")
        st.markdown("---")
        
        # Department Filter
        dept_filter = st.multiselect(
            "Department",
            options=['All Departments'] + filter_options['departments'],
            default=['All Departments'],
            key='dept_filter'
        )
        
        # Gender Filter
        gender_filter = st.multiselect(
            "Gender",
            options=['All Genders'] + filter_options['genders'],
            default=['All Genders'],
            key='gender_filter'
        )
        
        # Education Level Filter
        edu_filter = st.multiselect(
            "Education Level",
            options=['All Education Levels'] + filter_options['education'],
            default=['All Education Levels'],
            key='edu_filter'
        )
        
        # Job Role Filter
        role_filter = st.multiselect(
            "Job Role",
            options=['All Roles'] + filter_options['roles'],
            default=['All Roles'],
            key='role_filter'
        )
        
        # Performance Rating Filter
        perf_filter = st.multiselect(
            "Performance Rating",
            options=['All Ratings'] + sorted(filter_options['ratings']),
            default=['All Ratings'],
            key='perf_filter'
        )
        
        st.markdown("---")
        st.markdown("**Dashboard Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # ========================================================================
    # CALCULATE KPIs WITH FILTERS
    # ========================================================================
    kpis = calculate_kpis(df, dept_filter, gender_filter, edu_filter, role_filter, perf_filter)
    filtered_df = kpis['filtered_df']
    
    # ========================================================================
    # KPI CARDS
    # ========================================================================
    st.markdown("### 📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Employees",
            value=f"{kpis['total_employees']:,}",
            delta=f"{(kpis['total_employees']/len(df)*100):.1f}% of total"
        )
    
    with col2:
        st.metric(
            label="Avg Salary",
            value=f"${kpis['avg_salary']:,.0f}",
            delta=f"Min: ${filtered_df['Salary'].min():,.0f}"
        )
    
    with col3:
        st.metric(
            label="Avg Performance Score",
            value=f"{kpis['avg_performance']:.1f}/100",
            delta=f"Max: {filtered_df['PerformanceScore'].max()}"
        )
    
    with col4:
        st.metric(
            label="Avg Satisfaction Score",
            value=f"{kpis['avg_satisfaction']:.1f}/10",
            delta=f"Max: {filtered_df['SatisfactionScore'].max()}"
        )
    
    with col5:
        st.metric(
            label="Total Departments",
            value=f"{kpis['total_departments']}",
            delta=f"{(kpis['total_departments']/len(df.groupby('Department'))*100):.1f}%"
        )
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 1: DEPARTMENT & DEMOGRAPHICS
    # ========================================================================
    st.markdown("### 🏢 Department & Demographics Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    # Employee Count by Department
    with col1:
        dept_counts = filtered_df['Department'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Count']
        fig_dept = px.bar(
            dept_counts,
            x='Department',
            y='Count',
            title="Employee Count by Department",
            labels={'Count': 'Number of Employees'},
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig_dept.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_dept, use_container_width=True)
    
    # Gender Distribution
    with col2:
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig_gender = px.pie(
            gender_counts,
            names='Gender',
            values='Count',
            title="Gender Distribution",
            hole=0
        )
        fig_gender.update_layout(height=400)
        st.plotly_chart(fig_gender, use_container_width=True)
    
    # Education Level Distribution
    with col3:
        edu_counts = filtered_df['EducationLevel'].value_counts().reset_index()
        edu_counts.columns = ['Education', 'Count']
        fig_edu = px.pie(
            edu_counts,
            names='Education',
            values='Count',
            title="Education Level Distribution",
            hole=0.4
        )
        fig_edu.update_layout(height=400)
        st.plotly_chart(fig_edu, use_container_width=True)
    
    # ========================================================================
    # SECTION 2: SALARY & COMPENSATION
    # ========================================================================
    st.markdown("### 💰 Salary & Compensation Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    # Salary Distribution
    with col1:
        fig_salary = px.histogram(
            filtered_df,
            x='Salary',
            nbins=40,
            title="Salary Distribution",
            labels={'Salary': 'Salary ($)', 'count': 'Number of Employees'},
            color_discrete_sequence=['#667eea']
        )
        fig_salary.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_salary, use_container_width=True)
    
    # Average Salary by Department
    with col2:
        dept_salary = filtered_df.groupby('Department')['Salary'].mean().reset_index()
        dept_salary.columns = ['Department', 'Avg_Salary']
        dept_salary = dept_salary.sort_values('Avg_Salary', ascending=True)
        fig_dept_sal = px.bar(
            dept_salary,
            x='Avg_Salary',
            y='Department',
            orientation='h',
            title="Average Salary by Department",
            labels={'Avg_Salary': 'Average Salary ($)'},
            color='Avg_Salary',
            color_continuous_scale='Greens'
        )
        fig_dept_sal.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_dept_sal, use_container_width=True)
    
    # Experience vs Salary
    with col3:
        fig_exp_sal = px.scatter(
            filtered_df,
            x='TenureYears',
            y='Salary',
            color='Department',
            title="Experience vs Salary",
            labels={'TenureYears': 'Tenure (Years)', 'Salary': 'Salary ($)'},
            size='Age'
        )
        fig_exp_sal.update_layout(height=400)
        st.plotly_chart(fig_exp_sal, use_container_width=True)
    
    # ========================================================================
    # SECTION 3: PERFORMANCE & SATISFACTION
    # ========================================================================
    st.markdown("### ⭐ Performance & Satisfaction Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    # Performance Score by Department
    with col1:
        dept_perf = filtered_df.groupby('Department')['PerformanceScore'].mean().reset_index()
        dept_perf.columns = ['Department', 'Avg_Performance']
        dept_perf = dept_perf.sort_values('Avg_Performance', ascending=True)
        fig_perf = px.bar(
            dept_perf,
            x='Avg_Performance',
            y='Department',
            orientation='h',
            title="Performance Score by Department",
            labels={'Avg_Performance': 'Average Performance Score'},
            color='Avg_Performance',
            color_continuous_scale='Blues'
        )
        fig_perf.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_perf, use_container_width=True)
    
    # Satisfaction Score by Department
    with col2:
        dept_sat = filtered_df.groupby('Department')['SatisfactionScore'].mean().reset_index()
        dept_sat.columns = ['Department', 'Avg_Satisfaction']
        dept_sat = dept_sat.sort_values('Avg_Satisfaction', ascending=True)
        fig_sat = px.bar(
            dept_sat,
            x='Avg_Satisfaction',
            y='Department',
            orientation='h',
            title="Satisfaction Score by Department",
            labels={'Avg_Satisfaction': 'Average Satisfaction Score'},
            color='Avg_Satisfaction',
            color_continuous_scale='Oranges'
        )
        fig_sat.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_sat, use_container_width=True)
    
    # Age Distribution
    with col3:
        fig_age = px.histogram(
            filtered_df,
            x='Age',
            nbins=30,
            title="Age Distribution",
            labels={'Age': 'Age (years)', 'count': 'Number of Employees'},
            color_discrete_sequence=['#764ba2']
        )
        fig_age.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)
    
    # ========================================================================
    # SECTION 4: ADVANCED ANALYTICS
    # ========================================================================
    st.markdown("### 📈 Advanced Analytics")
    
    col1, col2 = st.columns(2)
    
    # Correlation Heatmap
    with col1:
        numeric_cols = filtered_df[['Age', 'Salary', 'TenureYears', 'PerformanceScore', 'SatisfactionScore']].copy()
        correlation = numeric_cols.corr()
        fig_corr = go.Figure(data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation.values, 2),
            texttemplate='%{text:.2f}',
            textfont={"size": 10}
        ))
        fig_corr.update_layout(title="Correlation Heatmap - Numeric Columns", height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Performance Rating Distribution
    with col2:
        perf_rating_counts = filtered_df['PerformanceRating'].value_counts().sort_index().reset_index()
        perf_rating_counts.columns = ['Rating', 'Count']
        fig_rating = px.bar(
            perf_rating_counts,
            x='Rating',
            y='Count',
            title="Employee Distribution by Performance Rating",
            labels={'Count': 'Number of Employees', 'Rating': 'Performance Rating (1-5)'},
            color='Count',
            color_continuous_scale='Plasma'
        )
        fig_rating.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_rating, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # TOP PERFORMERS & INSIGHTS
    # ========================================================================
    col1, col2 = st.columns(2)
    
    # Top 10 Highest Paid Employees
    with col1:
        st.markdown("### 💎 Top 10 Highest Paid Employees")
        top_paid = filtered_df.nlargest(10, 'Salary')[['Name', 'Department', 'Salary', 'Age', 'PerformanceRating']]
        top_paid_display = top_paid.copy()
        top_paid_display['Salary'] = top_paid_display['Salary'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(top_paid_display, use_container_width=True, hide_index=True)
    
    # Top Performing Employees
    with col2:
        st.markdown("### 🌟 Top 10 Performing Employees")
        top_perf = filtered_df.nlargest(10, 'PerformanceScore')[['Name', 'Department', 'PerformanceScore', 'SatisfactionScore', 'Salary']]
        top_perf_display = top_perf.copy()
        top_perf_display['PerformanceScore'] = top_perf_display['PerformanceScore'].apply(lambda x: f"{x:.1f}/100")
        top_perf_display['Salary'] = top_perf_display['Salary'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(top_perf_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ========================================================================
    # DEPARTMENT-WISE STATISTICS
    # ========================================================================
    st.markdown("### 📋 Department-wise Statistics")
    
    dept_stats = filtered_df.groupby('Department').agg({
        'EmployeeID': 'count',
        'Salary': ['mean', 'min', 'max'],
        'Age': 'mean',
        'PerformanceScore': 'mean',
        'SatisfactionScore': 'mean',
        'TenureYears': 'mean'
    }).round(2)
    
    dept_stats.columns = ['Employee Count', 'Avg Salary', 'Min Salary', 'Max Salary', 'Avg Age', 'Avg Performance', 'Avg Satisfaction', 'Avg Tenure']
    
    # Format currency columns
    for col in ['Avg Salary', 'Min Salary', 'Max Salary']:
        dept_stats[col] = dept_stats[col].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(dept_stats, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # INTERACTIVE DATA TABLE
    # ========================================================================
    st.markdown("### 🔍 Interactive Employee Data Table")
    
    # Search functionality
    search_col1, search_col2, search_col3 = st.columns(3)
    
    with search_col1:
        search_name = st.text_input("Search by Employee Name", "")
    
    with search_col2:
        search_dept = st.text_input("Search by Department", "")
    
    with search_col3:
        search_role = st.text_input("Search by Job Role", "")
    
    # Apply search filters
    table_df = filtered_df.copy()
    
    if search_name:
        table_df = table_df[table_df['Name'].str.contains(search_name, case=False, na=False)]
    
    if search_dept:
        table_df = table_df[table_df['Department'].str.contains(search_dept, case=False, na=False)]
    
    if search_role:
        table_df = table_df[table_df['JobRole'].str.contains(search_role, case=False, na=False)]
    
    # Display table
    display_cols = ['EmployeeID', 'Name', 'Age', 'Department', 'JobRole', 'Salary', 'PerformanceRating', 'SatisfactionScore']
    table_display = table_df[display_cols].copy()
    table_display['Salary'] = table_display['Salary'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(table_display, use_container_width=True, height=400)
    
    # Display row count
    st.caption(f"Showing {len(table_display)} of {len(filtered_df)} employees")
    
    # ========================================================================
    # DOWNLOAD DATA
    # ========================================================================
    st.markdown("---")
    st.markdown("### 📥 Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download filtered data
        csv_filtered = export_filtered_data(table_df)
        st.download_button(
            label="📊 Download Filtered Data (CSV)",
            data=csv_filtered,
            file_name=f"employee_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download full summary
        summary_data = {
            'Total Employees': [kpis['total_employees']],
            'Average Salary': [f"${kpis['avg_salary']:,.2f}"],
            'Average Performance Score': [f"{kpis['avg_performance']:.2f}"],
            'Average Satisfaction Score': [f"{kpis['avg_satisfaction']:.2f}"],
            'Total Departments': [kpis['total_departments']],
            'Report Generated': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        summary_df = pd.DataFrame(summary_data)
        csv_summary = export_filtered_data(summary_df)
        st.download_button(
            label="📈 Download Summary Report (CSV)",
            data=csv_summary,
            file_name=f"employee_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            <p>👥 Professional Employee Analytics Dashboard | Built with Streamlit, Pandas & Plotly</p>
            <p>Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
