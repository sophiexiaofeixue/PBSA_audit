import pandas as pd
import os

def read_excel_or_csv(file_path):
    df = pd.read_excel(file_path, skiprows = 1) \
        if file_path.endswith(('.xls', '.xlsx')) \
        else pd.read_csv(file_path, skiprows = 1)
    return df

def get_section_numbers(df):
    print(f"Columns in the file: {df.columns.tolist()}")
    target_col = 'Clause #'
    section_numbers = df[target_col].tolist()
    print(f"Extracted clause numbers: {section_numbers}")
    return section_numbers

def get_clause_text(df, clause_number):
    """Given a df and a clause number, return the description text for that clause."""
    target_col = 'Clause #'
    description_col = 'Potential Verification for Onsite Audit'

    # find the row where 'Clause #' matches clause_number
    match = df[df[target_col] == clause_number] # find the row
    if not match.empty:
        return match.iloc[0][description_col] # return the description text
    else:
        return "No description found for this clause."

'''
# Test function
if __name__ == "__main__":
    # Test with your PDF files
    test_files = [
        '/Users/xiaofeixue/pbsa_audit/uploads/compliance_guidelines/20250727_152259_PBSA Accrditation Clauses and Evidence Required.xlsx'
    ]
    
    print("🚀 Starting excel processing")
    
    for file_path in test_files:
        if os.path.exists(file_path):
            df = read_excel_or_csv(file_path)
            section_numbers = get_section_numbers(df)
            print(f"Section numbers from {file_path}: {section_numbers}")
'''
