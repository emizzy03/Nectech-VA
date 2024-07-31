import pandas as pd

def load_account_managers_info(csv_path: str):
    
    account_managers_info = pd.read_csv(csv_path)
    return account_managers_info
