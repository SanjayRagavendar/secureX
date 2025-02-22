import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

fraud_model = tf.keras.models.load_model("credit_card_fraud_detect_NN_model.keras")

def preprocess_transaction(transaction_data, transaction_count):
    """
    Preprocesses a transaction and predicts fraud probability using the Keras model.

    Args:
        transaction_data (dict): A dictionary containing transaction details.

    Returns:
        float: Fraud probability score (0 to 1).
    """

    # Convert transaction data to DataFrame
    df = pd.DataFrame([transaction_data])

    # Convert 'Time' to datetime and calculate 'Transaction_Count_24H'
    df['Transaction_Timestamp'] = pd.to_datetime(df['Time'], unit='s')
    df['Transaction_Count_24H'] = transaction_count
    df = df.drop(columns=['Time'])  # Drop raw time column

    # One-Hot Encode categorical features
    categorical_cols = ["Merchant_Category", "Transaction_Location", "Card_Type",
                        "Device_Type", "Authentication_Method", "Payment_Gateway",
                        "User_Age_Group", "Transaction_Channel"]

    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # StandardScaler for numerical features (excluding Transaction Count)
    scaler = StandardScaler()
    numerical_features = df.drop(columns=['Transaction_Count_24H'])
    features_scaled = scaler.fit_transform(numerical_features)  # Fit & Transform

    # Apply PCA to reduce dimensions to 28
    pca = PCA(n_components=28)
    pca_features = pca.fit_transform(features_scaled)  # Fit & Transform

    # Convert PCA output to DataFrame
    pca_columns = [f"V{i+1}" for i in range(28)]
    df_pca = pd.DataFrame(pca_features, columns=pca_columns)

    # Add Transaction Frequency back
    df_pca["Transaction_Frequency"] = df["Transaction_Count_24H"].values

    # Predict fraud probability using Keras model
    fraud_probability = fraud_model.predict(df_pca)[0][0]

    return fraud_probability
