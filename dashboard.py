import streamlit as st
import pandas as pd
import plotly.express as px

import plotly.graph_objects as go
import altair as alt 
st.set_page_config(layout="wide")  #
def main():
    st.title("Coil Failure Analysis")
    
    # Upload file through Streamlit
    uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Read the uploaded file
        try:
            df = read_file(uploaded_file)
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return

        # Display the dataframe
        st.subheader("Uploaded Data:")
        st.write(df)

        # Analyze the data
       
        # Clustered Failure Types
        # Group by 'Description Required' and count occurrences
        count_failures = df.groupby('failure')['Description Repaired'].count().reset_index()
        # Sort the DataFrame in ascending order
        count_failures = count_failures.sort_values(by='Description Repaired', ascending=False)
        fig = px.bar(count_failures, x='failure', y='Description Repaired')
        fig.update_layout(xaxis_title='Failure Type', yaxis_title='Count of Failures')

        
        
            
        st.subheader("Metric Chart for Count of Failure Types:")
          # Group by 'failure' and count occurrences
        count_failures = df['failure'].value_counts().reset_index()
        count_failures.columns = ['Failure Type', 'Count']
        num_columns = len(count_failures['Failure Type'].unique())

    # Calculate the number of rows needed
        num_rows = -(-len(count_failures) // num_columns)

        # Create a container for metrics
        with st.container():
            cols = st.columns(int(num_columns/2))
            i=0
            
            for j in range(0,num_columns-1,2):
                row=count_failures.iloc[j]
                row1=count_failures.iloc[j+1]
                cols[i].metric(label=row['Failure Type'], value=row['Count'])
                cols[i].metric(label=row1['Failure Type'], value=row1['Count'])
                i=i+1
                    

            
        with st.container():
            col1,col2=st.columns(2)
            col1.subheader("Count of Failures by Type")
            col1.plotly_chart(fig)
            col2.subheader("Count of Failures Table:")
            col2.table(count_failures)        
           

        


        # Bar chart for Count of Failures by Type
       
        # Group by 'failure' and 'Description Repaired' and count occurrences
        count_data = df.groupby(['failure', 'Description Repaired']).size().reset_index(name='Count')

        # Sort the DataFrame by 'failure' and 'Count' in ascending order
        count_data = count_data.sort_values(by=['failure', 'Count'], ascending=[True, True])

        # Bar chart for Count of Failures by Type and Description Repaired
        fig_failures = px.bar(count_data, x='failure', y='Count', color='Description Repaired',
                              title='Count of Failures by Type and Description Repaired')
        fig_failures.update_layout(xaxis_title='Failure Type', yaxis_title='Count of Failures')

        with st.container():
            col1,col2=st.columns(2)
            col1.subheader("Count of Failures by Type")
            col1.plotly_chart(fig_failures)
            col2.subheader("Count of Failures Table:")
            # col2.table(count_data)
        # analyze_data(df)
        pareto_analysis(df)

def pareto_analysis(df):
    st.subheader("Pareto Analysis of Coils Based on Failure")

    # Group by 'Description Repaired' and count occurrences
    coil_failure_counts = df.groupby(['Description Repaired', 'failure']).size().reset_index(name='Count')

    # Calculate the total count for each coil
    total_counts = coil_failure_counts.groupby('Description Repaired')['Count'].sum().reset_index()

    # Sort coils by total count in descending order
    total_counts = total_counts.sort_values(by='Count', ascending=False)

    # Perform Pareto analysis
    cumulative_percentage = 0
    pareto_data = pd.DataFrame(columns=['Coil', 'Failure', 'Count', 'Cumulative Percentage'])

    for index, row in total_counts.iterrows():
        coil = row['Description Repaired']
        failure_counts = coil_failure_counts[coil_failure_counts['Description Repaired'] == coil]

        # Sort failures by count in descending order
        failure_counts = failure_counts.sort_values(by='Count', ascending=False)

        # Calculate cumulative percentage for each coil
        failure_counts['Cumulative Percentage'] = (failure_counts['Count'] / row['Count']).cumsum() * 100

        # Append to Pareto data
        pareto_data = pd.concat([pareto_data, failure_counts])


        # Check if cumulative percentage exceeds 80%
        if pareto_data['Cumulative Percentage'].max() >= 80:
            break

    # Plot Pareto chart
    fig = px.bar(pareto_data, x='Description Repaired', y='Count', color='failure',
                 title='Pareto Analysis of Coils Based on Failure',
                 labels={'Description Repaired': 'Coil', 'Count': 'Failure Count'})
    
    fig.update_layout(xaxis_title='Coils', yaxis_title='Failure Count')

    # Show the chart using Plotly
    st.plotly_chart(fig)

def read_file(uploaded_file):
    # Check file type and read accordingly
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")

    return df

def analyze_data(df):
    # Allow user to select columns for analysis
    st.sidebar.subheader("Select Columns for Analysis:")
    columns = st.sidebar.multiselect("Select Columns", df.columns)

    if not columns:
        st.warning("Please select at least one column for analysis.")
        return

    # Display selected columns
    st.subheader("Selected Columns:")
    st.write(columns)
    
    # Analyze and visualize the data
    for column in columns:
        st.subheader(f"Analysis for {column}:")

        ## Count unique values
        value_counts = df[column].value_counts()

        # Display unique values count
        st.write("Unique Values Count:")


        # Create a bar chart
        fig = px.bar(value_counts, x=value_counts.index, y=value_counts.values, labels={'x': column, 'y': 'Count'})
        with st.container():
            col1,col2=st.columns(2)
            col1.subheader(f"Count Chart of {column}")
            col1.plotly_chart(fig)
            col2.subheader(f"Count Table of {column}")
            col2.table(value_counts.reset_index().rename(columns={"index": column, column: "Count"}))

if __name__ == "__main__":
    main()
