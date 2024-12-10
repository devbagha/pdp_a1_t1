import dask.dataframe as dd
from datetime import datetime

# Record start time
start_time = datetime.now()

# Placeholder year (assume current year for simplicity)
current_year = datetime.now().year

# Load students and fees data into Dask DataFrames
students_df = dd.read_csv('data/students.csv', encoding='utf-8')
fees_df = dd.read_csv('data/student_fees.csv', encoding='utf-8')

# Ensure "Payment Status" is processed correctly
fees_df['Payment Status'] = fees_df['Payment Status'].str.strip().str.lower()

# Convert "Payment Date" from "Month Day" to a complete date with year
fees_df['Payment Date'] = fees_df['Payment Date'].apply(
    lambda x: f"{x} {current_year}", meta=('x', 'str')
)
fees_df['Payment Date'] = dd.to_datetime(fees_df['Payment Date'], format='%B %d %Y', errors='coerce')

# Filter only paid fees
paid_fees = fees_df[fees_df['Payment Status'] == 'paid']

# Extract the day of the month
paid_fees['Day of Month'] = paid_fees['Payment Date'].dt.day

# Group by Student ID and Day of Month to count occurrences
day_frequency = paid_fees.groupby(['Student ID', 'Day of Month']).size().reset_index()
day_frequency.columns = ['Student ID', 'Day of Month', 'Frequency']  # Rename columns

# Compute the result (triggering parallel computation)
day_frequency = day_frequency.compute()

# Find the most frequent day for each student
most_frequent_days = (
    day_frequency.loc[
        day_frequency.groupby('Student ID')['Frequency'].idxmax()
    ]
)

# Load the student DataFrame into pandas for final merge
students_df = students_df.compute()

# Merge the most frequent day data with the student data
output_data = students_df.merge(
    most_frequent_days[['Student ID', 'Day of Month', 'Frequency']],
    on='Student ID',
    how='left'
)

# Record end time
end_time = datetime.now()

# Calculate total execution time
execution_time = end_time - start_time

# Display results
print("Execution Results:")
print(output_data[['Student ID', 'Day of Month', 'Frequency']])

# Display execution times
print("\nExecution Timing:")
print(f"Start Time: {start_time}")
print(f"End Time: {end_time}")
print(f"Total Execution Time: {execution_time}")
