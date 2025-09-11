import pandas as pd

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


