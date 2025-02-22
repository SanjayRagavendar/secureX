from kafka import KafkaConsumer
import json
import numpy as np
import tensorflow as tf
from models import db
from models import Account, Transaction
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


model = tf.keras.models.load_model("credit_card_fraud_detect_NN_model.keras")

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

    df_pca["Transaction_Frequency"] = df["Transaction_Count_24H"].values

    # Predict fraud probability using Keras model
    fraud_probability = model.predict(df_pca)[0][0]

    return fraud_probability
    

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'transfer_requests',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🚀 Transfer Consumer Started. Listening for transactions...")

for message in consumer:
    data = message.value
    print(f"Processing transaction: {data}")

    from_account = Account.query.get(data['from_account'])
    to_account = Account.query.get(data['to_account'])
    amount = float(data['amount'])

    transaction_features = preprocess_transaction(data)

    # Predict fraud (Assuming 0 = Legit, 1 = Fraud)
    fraud_prediction = model.predict(np.array([transaction_features]))
    is_fraud = fraud_prediction[0][0] > 0.5  # If prediction > 0.5, it's fraud

    if is_fraud:
        print(f"❌ Fraud detected in transaction {data}")
        continue  # Reject transaction

    # Authorization check
    if from_account.user_id != data["user_id"]:
        print("❌ Unauthorized transaction attempt")
        continue

    # Insufficient funds check
    if from_account.balance < amount:
        print("❌ Insufficient funds")
        continue

    # Process the transaction
    from_account.balance -= amount
    to_account.balance += amount

    transaction = Transaction(
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=amount,
        transaction_type='transfer'
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    print(f"✅ Transfer Completed: {transaction.id}")
