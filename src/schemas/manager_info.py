from pydantic import BaseModel
from typing import List, Tuple
from src.account_manger_db.account_manager import load_account_managers_info
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import pandas as pd
import numpy as np
from pathlib import Path


class Manager(BaseModel):
    name: str
    location: str
    expertise: str
    current_accounts: int
    performance_rating: float
    workload: int
    experience: int
    satisfaction_score: int

    def __repr__(self) -> str:
        """Return a concise string representation of the Manager."""
        return f"{self.name} ({self.location}, {self.expertise})"


def create_managers_from_df(df: pd.DataFrame) -> List[Manager]:
    """Create a list of Manager objects from a pandas DataFrame.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the manager information.

    Returns:
        List[Manager]: A list of Manager objects.
    """
    return [
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


def train_model(file_path: str) -> Tuple[GradientBoostingClassifier, List[Manager]]:
    """
    Train a GradientBoostingClassifier model to predict which managers can accept new accounts.

    Args:
        file_path (str): The path to the CSV file containing the manager information.

    Returns:
        Tuple[GradientBoostingClassifier, List[Manager]]: A tuple containing the trained model and a list of Manager objects.
    """
    # Load the manager information from a CSV file into a DataFrame
    df = load_account_managers_info(file_path)
    # Create a list of Manager objects from the DataFrame
    managers = create_managers_from_df(df)

    # Construct a DataFrame of features for each manager
    features = pd.DataFrame(
        {
            # Number of accounts currently managed
            "current_accounts": [manager.current_accounts for manager in managers],
            # Current workload in hours per week
            "workload": [manager.workload for manager in managers],
            # Performance rating of the manager
            "performance_rating": [manager.performance_rating for manager in managers],
            # Industry experience in years
            "experience": [manager.experience for manager in managers],
            # Client satisfaction score
            "satisfaction_score": [manager.satisfaction_score for manager in managers],
            "workload_per_account": [  # Workload divided by the number of accounts
                manager.workload / manager.current_accounts if manager.current_accounts else 0
                for manager in managers
            ],
            # Location of the manager
            "location": [manager.location for manager in managers],
        }
    )

    # One-hot encode the location feature
    location_dummies = pd.get_dummies(features["location"], prefix="location")
    features = pd.concat([features, location_dummies], axis=1)
    features.drop("location", axis=1, inplace=True)

    # Define the target variable: 1 if the manager is overloaded (5 or more accounts), else 0
    target = np.where(features["current_accounts"] >= 5, 1, 0)

    # Initialize the GradientBoostingClassifier with specific hyperparameters
    model = GradientBoostingClassifier(
        n_estimators=100,  # Number of boosting stages to perform
        max_depth=3,  # Maximum depth of the individual regression estimators
        learning_rate=5.0,  # Learning rate shrinks the contribution of each tree


    )
    for epoch in range(10):
        model.fit(features, target)
        print(
            f"Epoch {epoch + 1} - Training accuracy: {model.score(features, target) * 100:.2f}%")
        # Decrease the learning rate after each epoch
        learning_rate = 5.0 / (epoch + 2)
        model.learning_rate = learning_rate
        
    # Fit the model on the features and target to train it
    model.fit(features, target)

    # Return the trained model and the list of Manager objects
    return model, managers


def select_manager(managers: List[Manager], model: GradientBoostingClassifier) -> Manager:
    """
    Select the best manager based on the model's predictions.

    This function takes in a list of managers and a GradientBoostingClassifier model. It uses the model to predict the
    probability of each manager being able to accept a new account. The manager with the highest probability is selected.

    Args:
        managers (List[Manager]): The list of managers to select from.
        model (GradientBoostingClassifier): The model to use to make predictions.

    Returns:
        Manager: The best manager to select.
    """
    # Create a single numpy array to hold all the data for the managers.
    # This is done to make it easier to get the predictions from the model.
    X = np.array([[manager.current_accounts, manager.workload, manager.performance_rating, manager.experience,
                 manager.satisfaction_score, manager.workload / (manager.current_accounts or 1)] for manager in managers])

    # Get the predictions from the model. The model will return the probability of each manager being able to accept a new account.
    predictions = model.predict_proba(X)[:, 1]

    # Find the index of the manager with the highest probability.
    best_manager_index = np.argmax(predictions)

    # Return the manager with the highest probability.
    return managers[best_manager_index]


def assign_manager(file_path: Path, manager_name: str) -> None:
    """
    Assign a new account to the given manager by incrementing their current accounts count.

    Args:
        file_path (Path): The path to the CSV file containing the manager information.
        manager_name (str): The name of the manager to assign the account to.

    Returns:
        None
    """
    df: pd.DataFrame = pd.read_csv(file_path, index_col='Manager')
    df.loc[manager_name, 'Current Accounts'] += 1
    df.to_csv(file_path, index=True)
