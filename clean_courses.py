import pandas as pd

def clean_courses_file():
    try:
        # Read the CSV file
        df = pd.read_csv('data/courses_cleaned.csv', 
                        delimiter=';', 
                        on_bad_lines='skip')
        
        # Remove extra columns (those with empty headers)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Clean up each column
        for column in df.columns:
            df[column] = df[column].apply(lambda x: str(x).strip().rstrip(',') if pd.notna(x) else '')
        
        # Remove rows with missing essential data
        df = df.dropna(subset=['Course', 'Universities_ID'])
        
        # Remove rows that contain problematic data
        df = df[~df['Course'].str.contains(';', na=False)]
        
        # Save the cleaned file
        df.to_csv('data/courses_cleaned.csv', sep=';', index=False)
        print("Successfully cleaned courses file")
        
    except Exception as e:
        print(f"Error cleaning courses file: {str(e)}")

if __name__ == "__main__":
    clean_courses_file() 