from pydantic import BaseModel
from typing import List, Tuple
from src.account_manger_db.account_manager import load_account_managers_info
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
import pandas as pd
import numpy as np

class Manager(BaseModel):
    name: str
    location: str
    expertise: str
    current_accounts: int
    performance_rating: float
    workload: int
    experience: int
    satisfaction_score: int

    def __repr__(self):
        return f"{self.name} ({self.location}, {self.expertise})"

def create_managers_from_df(df: pd.DataFrame) -> List[Manager]:
    managers = [
        Manager(
            name=row['Manager'],
            location=row['Location'],
            expertise=row['Expertise'],
            current_accounts=int(row['Current Accounts']),
            performance_rating=float(row['Performance Rating']),
            workload=int(row['Workload (hrs/week)']),
            experience=int(row['Industry Experience (years)']),
            satisfaction_score=int(row['Client Satisfaction Score'])
        )
        for _, row in df.iterrows()
    ]
    return managers

def train_model(file_path: str) -> Tuple[GradientBoostingClassifier, List[Manager]]:
    df = load_account_managers_info(file_path)
    managers = create_managers_from_df(df)
    
    data = {
        "Current Accounts": [manager.current_accounts for manager in managers],
        "Workload": [manager.workload for manager in managers],
        "Performance Rating": [manager.performance_rating for manager in managers],
        "Experience": [manager.experience for manager in managers],
        "Satisfaction Score": [manager.satisfaction_score for manager in managers],
        "Workload_per_account": [manager.workload / manager.current_accounts if manager.current_accounts else 0 for manager in managers],
    }
    df = pd.DataFrame(data)
    X = df[["Current Accounts", "Workload", "Performance Rating", "Experience", "Satisfaction Score", "Workload_per_account"]]
    y = [1 if x >= 5 else 0 for x in df['Current Accounts']]  
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model, managers

def select_manager(managers: List[Manager], model: GradientBoostingClassifier) -> Manager:
    data = {
        "Current Accounts": [manager.current_accounts for manager in managers],
        "Workload": [manager.workload for manager in managers],
        "Performance Rating": [manager.performance_rating for manager in managers],
        "Experience": [manager.experience for manager in managers],
        "Satisfaction Score": [manager.satisfaction_score for manager in managers],
        "Workload_per_account": [manager.workload / manager.current_accounts if manager.current_accounts else 0 for manager in managers],
    }
    df = pd.DataFrame(data)
    X = df[["Current Accounts", "Workload", "Performance Rating", "Experience", "Satisfaction Score", "Workload_per_account"]]

     # Use the probabilities directly
    predictions = model.predict_proba(X)[:, 1]  
    best_manager_index = np.argmax(predictions)
    return managers[best_manager_index]
   

def assign_manager(file_path: str, manager_name: str):
    df = pd.read_csv(file_path)
    df.loc[df['Manager'] == manager_name, 'Current Accounts'] += 1
    df.to_csv(file_path, index=False)
