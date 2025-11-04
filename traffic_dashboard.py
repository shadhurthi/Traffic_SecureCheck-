import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure Streamlit page
st.set_page_config(page_title="Traffic Police Dashboard", layout="wide")

# Database connection
@st.cache_resource
def get_db_connection():
    engine = create_engine(
        'mysql+pymysql://root:Shadhu123@localhost:3306/traffic_data'
    )
    return engine

engine = get_db_connection()

# ==================== HELPER FUNCTIONS ====================
def execute_query(query):
    try:
        with engine.connect() as conn:
            result = pd.read_sql(text(query), conn)
        return result
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None

def get_all_data():
    query = "SELECT * FROM traffic_stops"
    return execute_query(query)

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", 
    ["Dashboard", "Search Incidents", "Vehicle Search", "Driver Details", 
     "Register New Case", "Medium Level Queries", "Complex Level Queries"])

# ==================== MAIN DASHBOARD ====================
if page == "Dashboard":
    st.title("🚔 Traffic Police Analytics Dashboard")
    st.markdown("---")
    
    df = get_all_data()
    
    if df is not None and len(df) > 0:
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Stops", len(df))
        with col2:
            arrests = df['is_arrested'].sum()
            st.metric("Total Arrests", int(arrests))
        with col3:
            searches = df['search_conducted'].sum()
            st.metric("Searches Conducted", int(searches))
        with col4:
            drug_stops = df['drugs_related_stop'].sum()
            st.metric("Drug-Related Stops", int(drug_stops))
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stops by Country")
            country_stops = df['country_name'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 5))
            country_stops.plot(kind='bar', ax=ax, color='steelblue')
            ax.set_title("Number of Stops by Country")
            ax.set_xlabel("Country")
            ax.set_ylabel("Number of Stops")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        with col2:
            st.subheader("Gender Distribution")
            gender_dist = df['driver_gender'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.pie(gender_dist.values, labels=gender_dist.index, autopct='%1.1f%%')
            ax.set_title("Driver Gender Distribution")
            st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stop Outcomes")
            outcomes = df['stop_outcome'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 5))
            outcomes.plot(kind='barh', ax=ax, color='coral')
            ax.set_title("Stop Outcomes Distribution")
            ax.set_xlabel("Count")
            st.pyplot(fig)
        
        with col2:
            st.subheader("Age Distribution")
            fig, ax = plt.subplots(figsize=(10, 5))
            df['driver_age'].dropna().hist(bins=30, ax=ax, color='green', edgecolor='black')
            ax.set_title("Driver Age Distribution")
            ax.set_xlabel("Age")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

# ==================== SEARCH INCIDENTS ====================
elif page == "Search Incidents":
    st.title("🔍 Search Incidents")
    st.markdown("Filter and view incidents where search was conducted")
    
    df = get_all_data()
    
    if df is not None:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_types = ["All"] + df['search_type'].dropna().unique().tolist()
            selected_search = st.selectbox("Search Type", search_types)
        
        with col2:
            countries = ["All"] + df['country_name'].dropna().unique().tolist()
            selected_country = st.selectbox("Country", countries)
        
        with col3:
            violations = ["All"] + df['violation'].dropna().unique().tolist()
            selected_violation = st.selectbox("Violation", violations)
        
        # Apply filters
        filtered_df = df[df['search_conducted'] == 1].copy()
        
        if selected_search != "All":
            filtered_df = filtered_df[filtered_df['search_type'] == selected_search]
        
        if selected_country != "All":
            filtered_df = filtered_df[filtered_df['country_name'] == selected_country]
        
        if selected_violation != "All":
            filtered_df = filtered_df[filtered_df['violation'] == selected_violation]
        
        st.write(f"Found {len(filtered_df)} incidents")
        st.dataframe(filtered_df, use_container_width=True)

# ==================== VEHICLE SEARCH ====================
elif page == "Vehicle Search":
    st.title("🚗 Vehicle Search")
    st.markdown("Search for specific vehicle incidents")
    
    df = get_all_data()
    
    if df is not None:
        vehicle_num = st.text_input("Enter Vehicle Number:")
        
        if vehicle_num:
            vehicle_data = df[df['vehicle_number'].str.contains(vehicle_num, case=False, na=False)]
            st.write(f"Found {len(vehicle_data)} records for vehicle: {vehicle_num}")
            st.dataframe(vehicle_data, use_container_width=True)
            
            if len(vehicle_data) > 0:
                st.subheader("Vehicle Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Stops", len(vehicle_data))
                with col2:
                    st.metric("Arrests", int(vehicle_data['is_arrested'].sum()))
                with col3:
                    st.metric("Searches", int(vehicle_data['search_conducted'].sum()))

# ==================== DRIVER DETAILS ====================
elif page == "Driver Details":
    st.title("👤 Driver Details")
    st.markdown("Search and view driver information")
    
    df = get_all_data()
    
    if df is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            age_min = int(df['driver_age'].min())
            age_max = int(df['driver_age'].max())
            age_range = st.slider("Driver Age Range", age_min, age_max, (age_min, age_max))
        
        with col2:
            genders = ["All"] + df['driver_gender'].dropna().unique().tolist()
            selected_gender = st.selectbox("Gender", genders)
        
        filtered_df = df[(df['driver_age'] >= age_range[0]) & (df['driver_age'] <= age_range[1])]
        
        if selected_gender != "All":
            filtered_df = filtered_df[filtered_df['driver_gender'] == selected_gender]
        
        st.write(f"Found {len(filtered_df)} drivers")
        st.dataframe(filtered_df, use_container_width=True)
        
        if len(filtered_df) > 0:
            st.subheader("Driver Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(filtered_df))
            with col2:
                arrest_rate = (filtered_df['is_arrested'].sum() / len(filtered_df) * 100)
                st.metric("Arrest Rate %", f"{arrest_rate:.2f}%")
            with col3:
                search_rate = (filtered_df['search_conducted'].sum() / len(filtered_df) * 100)
                st.metric("Search Rate %", f"{search_rate:.2f}%")
            with col4:
                avg_age = filtered_df['driver_age'].mean()
                st.metric("Average Age", f"{avg_age:.1f}")

# ==================== REGISTER NEW CASE ====================
elif page == "Register New Case":
    st.title("📝 Register New Case")
    st.markdown("Add a new traffic stop record to the database")
    
    with st.form("new_case_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            stop_date = st.date_input("Stop Date")
            stop_time = st.time_input("Stop Time")
            country_name = st.text_input("Country Name")
            driver_gender = st.selectbox("Driver Gender", ["M", "F", "Other"])
            driver_age = st.number_input("Driver Age", min_value=0, max_value=120, step=1)
            driver_race = st.text_input("Driver Race")
        
        with col2:
            violation = st.text_input("Violation")
            violation_raw = st.text_input("Violation (Raw)")
            search_conducted = st.selectbox("Search Conducted", [0, 1])
            search_type = st.selectbox("Search Type", ["None", "Vehicle", "Person", "Both"])
            stop_outcome = st.selectbox("Stop Outcome", ["Citation", "Warning", "Arrest", "Release"])
            is_arrested = st.selectbox("Is Arrested", [0, 1])
        
        col1, col2 = st.columns(2)
        
        with col1:
            stop_duration = st.text_input("Stop Duration (e.g., 15 mins)")
            drugs_related = st.selectbox("Drugs Related Stop", [0, 1])
        
        with col2:
            vehicle_number = st.text_input("Vehicle Number")
        
        submit_button = st.form_submit_button("Register Case")
        
        if submit_button:
            try:
                insert_query = """
                INSERT INTO traffic_stops 
                (stop_date, stop_time, country_name, driver_gender, driver_age_raw, 
                 driver_age, driver_race, violation_raw, violation, search_conducted, 
                 search_type, stop_outcome, is_arrested, stop_duration, drugs_related_stop, 
                 vehicle_number)
                VALUES 
                (:stop_date, :stop_time, :country_name, :driver_gender, :driver_age, 
                 :driver_age, :driver_race, :violation_raw, :violation, :search_conducted, 
                 :search_type, :stop_outcome, :is_arrested, :stop_duration, :drugs_related, 
                 :vehicle_number)
                """
                
                with engine.connect() as conn:
                    conn.execute(text(insert_query), {
                        'stop_date': str(stop_date),
                        'stop_time': str(stop_time),
                        'country_name': country_name,
                        'driver_gender': driver_gender,
                        'driver_age': driver_age,
                        'driver_race': driver_race,
                        'violation_raw': violation_raw,
                        'violation': violation,
                        'search_conducted': search_conducted,
                        'search_type': search_type if search_conducted == 1 else None,
                        'stop_outcome': stop_outcome,
                        'is_arrested': is_arrested,
                        'stop_duration': stop_duration,
                        'drugs_related': drugs_related,
                        'vehicle_number': vehicle_number
                    })
                    conn.commit()
                
                st.success("✅ Case registered successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ==================== MEDIUM LEVEL QUERIES ====================
elif page == "Medium Level Queries":
    st.title("📊 SQL QUERIES - Medium Level")
    st.markdown("Select a query to execute from the dropdown below")
    
    queries = {
        "Top 10 Vehicles in Drug-Related Stops": """
            SELECT vehicle_number, COUNT(*) as stop_count
            FROM traffic_stops
            WHERE drugs_related_stop = 1 AND vehicle_number IS NOT NULL
            GROUP BY vehicle_number
            ORDER BY stop_count DESC
            LIMIT 10;
        """,
        
        "Most Frequently Searched Vehicles": """
            SELECT vehicle_number, COUNT(*) as search_count
            FROM traffic_stops
            WHERE search_conducted = 1 AND vehicle_number IS NOT NULL
            GROUP BY vehicle_number
            ORDER BY search_count DESC
            LIMIT 15;
        """,
        
        "Age Group with Highest Arrest Rate": """
            SELECT 
                CASE 
                    WHEN driver_age < 25 THEN '<25'
                    WHEN driver_age < 35 THEN '25-34'
                    WHEN driver_age < 45 THEN '35-44'
                    WHEN driver_age < 55 THEN '45-54'
                    ELSE '55+'
                END as age_group,
                COUNT(*) as total_stops,
                SUM(is_arrested) as arrests,
                ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate
            FROM traffic_stops
            WHERE driver_age IS NOT NULL
            GROUP BY age_group
            ORDER BY arrest_rate DESC;
        """,
        
        "Gender Distribution by Country": """
            SELECT country_name, driver_gender, COUNT(*) as count
            FROM traffic_stops
            WHERE country_name IS NOT NULL AND driver_gender IS NOT NULL
            GROUP BY country_name, driver_gender
            ORDER BY country_name, count DESC;
        """,
        
        "Race & Gender Combination - Highest Search Rate": """
            SELECT 
                driver_race, driver_gender, 
                COUNT(*) as total_stops,
                SUM(search_conducted) as searches,
                ROUND(SUM(search_conducted) / COUNT(*) * 100, 2) as search_rate
            FROM traffic_stops
            WHERE driver_race IS NOT NULL AND driver_gender IS NOT NULL
            GROUP BY driver_race, driver_gender
            HAVING total_stops >= 5
            ORDER BY search_rate DESC
            LIMIT 10;
        """,
        
        "Most Traffic Stops by Time of Day": """
            SELECT 
                CASE 
                    WHEN HOUR(CAST(stop_time AS TIME)) >= 6 AND HOUR(CAST(stop_time AS TIME)) < 12 THEN 'Morning (6AM-12PM)'
                    WHEN HOUR(CAST(stop_time AS TIME)) >= 12 AND HOUR(CAST(stop_time AS TIME)) < 18 THEN 'Afternoon (12PM-6PM)'
                    WHEN HOUR(CAST(stop_time AS TIME)) >= 18 AND HOUR(CAST(stop_time AS TIME)) < 24 THEN 'Evening (6PM-12AM)'
                    ELSE 'Night (12AM-6AM)'
                END as time_period,
                COUNT(*) as stops
            FROM traffic_stops
            WHERE stop_time IS NOT NULL
            GROUP BY time_period
            ORDER BY stops DESC;
        """,
        
        "Average Stop Duration by Violation": """
            SELECT violation, COUNT(*) as stop_count, 
                   ROUND(AVG(CAST(SUBSTRING_INDEX(stop_duration, ' ', 1) AS DECIMAL)), 2) as avg_duration_mins
            FROM traffic_stops
            WHERE violation IS NOT NULL AND stop_duration IS NOT NULL
            GROUP BY violation
            ORDER BY avg_duration_mins DESC
            LIMIT 15;
        """,
        
        "Night Stops vs Arrests": """
            SELECT 
                CASE 
                    WHEN HOUR(CAST(stop_time AS TIME)) >= 20 OR HOUR(CAST(stop_time AS TIME)) < 6 THEN 'Night (8PM-6AM)'
                    ELSE 'Day (6AM-8PM)'
                END as period,
                COUNT(*) as total_stops,
                SUM(is_arrested) as arrests,
                ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate
            FROM traffic_stops
            WHERE stop_time IS NOT NULL
            GROUP BY period
            ORDER BY arrest_rate DESC;
        """,
        
        "Violations Associated with Searches/Arrests": """
            SELECT violation,
                   COUNT(*) as total_stops,
                   SUM(search_conducted) as search_count,
                   SUM(is_arrested) as arrest_count,
                   ROUND(SUM(search_conducted) / COUNT(*) * 100, 2) as search_rate,
                   ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate
            FROM traffic_stops
            WHERE violation IS NOT NULL
            GROUP BY violation
            ORDER BY search_rate DESC
            LIMIT 15;
        """,
        
        "Most Common Violations Among Younger Drivers (<25)": """
            SELECT violation, COUNT(*) as violation_count
            FROM traffic_stops
            WHERE driver_age < 25 AND violation IS NOT NULL
            GROUP BY violation
            ORDER BY violation_count DESC
            LIMIT 10;
        """,
        
        "Violations Rarely Resulting in Search/Arrest": """
            SELECT violation,
                   COUNT(*) as total_stops,
                   SUM(search_conducted) as searches,
                   SUM(is_arrested) as arrests,
                   ROUND(SUM(search_conducted) / COUNT(*) * 100, 2) as search_rate,
                   ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate
            FROM traffic_stops
            WHERE violation IS NOT NULL
            GROUP BY violation
            HAVING searches = 0 AND arrests = 0
            ORDER BY total_stops DESC;
        """,
        
        "Countries with Highest Drug-Related Stops Rate": """
            SELECT country_name,
                   COUNT(*) as total_stops,
                   SUM(drugs_related_stop) as drug_stops,
                   ROUND(SUM(drugs_related_stop) / COUNT(*) * 100, 2) as drug_stop_rate
            FROM traffic_stops
            WHERE country_name IS NOT NULL
            GROUP BY country_name
            ORDER BY drug_stop_rate DESC;
        """,
        
        "Arrest Rate by Country and Violation": """
            SELECT country_name, violation,
                   COUNT(*) as total_stops,
                   SUM(is_arrested) as arrests,
                   ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate
            FROM traffic_stops
            WHERE country_name IS NOT NULL AND violation IS NOT NULL
            GROUP BY country_name, violation
            HAVING total_stops >= 3
            ORDER BY arrest_rate DESC
            LIMIT 20;
        """,
        
        "Country with Most Stops - Search Conducted": """
            SELECT country_name,
                   COUNT(*) as total_stops,
                   SUM(search_conducted) as searches_conducted,
                   ROUND(SUM(search_conducted) / COUNT(*) * 100, 2) as search_rate
            FROM traffic_stops
            WHERE country_name IS NOT NULL
            GROUP BY country_name
            ORDER BY searches_conducted DESC;
        """
    }
    
    selected_query = st.selectbox(
        "Select a Query",
        list(queries.keys())
    )
    
    if st.button("Execute Query"):
        result = execute_query(queries[selected_query])
        if result is not None:
            st.success("Query executed successfully!")
            st.dataframe(result, use_container_width=True)
            
            # Download option
            csv = result.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# ==================== COMPLEX LEVEL QUERIES ====================
elif page == "Complex Level Queries":
    st.title("🔬 SQL QUERIES - Complex Level")
    st.markdown("Advanced analytical queries with window functions and subqueries")
    
    complex_queries = {
        "Yearly Breakdown of Stops and Arrests by Country": """
            SELECT 
                YEAR(CAST(stop_date AS DATE)) as year,
                country_name,
                COUNT(*) as total_stops,
                SUM(is_arrested) as total_arrests,
                ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate,
                RANK() OVER (PARTITION BY YEAR(CAST(stop_date AS DATE)) ORDER BY COUNT(*) DESC) as rank_by_stops
            FROM traffic_stops
            WHERE country_name IS NOT NULL AND stop_date IS NOT NULL
            GROUP BY year, country_name
            ORDER BY year DESC, total_stops DESC;
        """,
        
        "Driver Violation Trends - Age and Race": """
            SELECT 
                driver_race,
                CASE 
                    WHEN driver_age < 25 THEN '<25'
                    WHEN driver_age < 35 THEN '25-34'
                    WHEN driver_age < 45 THEN '35-44'
                    WHEN driver_age < 55 THEN '45-54'
                    ELSE '55+'
                END as age_group,
                violation,
                COUNT(*) as violation_count,
                SUM(is_arrested) as arrests,
                ROW_NUMBER() OVER (PARTITION BY driver_race ORDER BY COUNT(*) DESC) as violation_rank
            FROM traffic_stops
            WHERE driver_race IS NOT NULL AND driver_age IS NOT NULL AND violation IS NOT NULL
            GROUP BY driver_race, age_group, violation
            ORDER BY driver_race, violation_count DESC;
        """,
        
        "Time Period Analysis - Stops by Year, Month, Hour": """
            SELECT 
                YEAR(CAST(stop_date AS DATE)) as year,
                MONTH(CAST(stop_date AS DATE)) as month,
                HOUR(CAST(stop_time AS TIME)) as hour_of_day,
                COUNT(*) as stops,
                SUM(is_arrested) as arrests,
                ROUND(AVG(driver_age), 1) as avg_driver_age
            FROM traffic_stops
            WHERE stop_date IS NOT NULL AND stop_time IS NOT NULL
            GROUP BY year, month, hour_of_day
            ORDER BY year DESC, month DESC, hour_of_day;
        """,
        
        "Violations with High Search and Arrest Rates": """
            SELECT 
                violation,
                COUNT(*) as total_stops,
                SUM(search_conducted) as searches,
                SUM(is_arrested) as arrests,
                ROUND(SUM(search_conducted) / COUNT(*) * 100, 2) as search_rate,
                ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate,
                RANK() OVER (ORDER BY SUM(search_conducted) / COUNT(*) DESC) as search_rank,
                RANK() OVER (ORDER BY SUM(is_arrested) / COUNT(*) DESC) as arrest_rank
            FROM traffic_stops
            WHERE violation IS NOT NULL
            GROUP BY violation
            HAVING total_stops >= 5
            ORDER BY search_rate DESC, arrest_rate DESC;
        """,
        
        "Driver Demographics by Country": """
            SELECT 
                country_name,
                driver_race,
                driver_gender,
                COUNT(*) as driver_count,
                ROUND(AVG(driver_age), 1) as avg_age,
                MIN(driver_age) as min_age,
                MAX(driver_age) as max_age,
                SUM(is_arrested) as total_arrests,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY country_name), 2) as pct_by_country
            FROM traffic_stops
            WHERE country_name IS NOT NULL AND driver_race IS NOT NULL AND driver_gender IS NOT NULL
            GROUP BY country_name, driver_race, driver_gender
            ORDER BY country_name, pct_by_country DESC;
        """,
        
        "Top 5 Violations with Highest Arrest Rates": """
            SELECT 
                violation,
                COUNT(*) as total_stops,
                SUM(is_arrested) as arrests,
                ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) as arrest_rate,
                RANK() OVER (ORDER BY ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) DESC) as rank
            FROM traffic_stops
            WHERE violation IS NOT NULL
            GROUP BY violation
            HAVING COUNT(*) >= 5
            ORDER BY arrest_rate DESC
            LIMIT 5;
        """
    }
    
    selected_complex = st.selectbox(
        "Select Complex Query",
        list(complex_queries.keys())
    )
    
    if st.button("Execute Complex Query"):
        result = execute_query(complex_queries[selected_complex])
        if result is not None:
            st.success("Complex query executed successfully!")
            st.dataframe(result, use_container_width=True)
            
            # Download option
            csv = result.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"complex_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

st.markdown("---")
st.markdown("*Traffic Police Analytics Dashboard v1.0*")