import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv("your_dataset.csv")

# Drop unnecessary columns
df = df.drop(columns=["Transaction_ID"])  # Unique ID not useful for PCA

# Generate Transaction Frequency Feature
df['Transaction_Timestamp'] = pd.to_datetime(df['Time'], unit='s')  # Convert seconds to datetime
df['Transaction_Count_24H'] = df.groupby('User_ID')['Transaction_Timestamp'].transform(
    lambda x: x.rolling('1D', on=x).count()
).fillna(0)  # Fill missing values with 0

# Drop the original 'Time' column after extracting features
df = df.drop(columns=['Time'])

# Handle categorical features (One-Hot Encoding)
categorical_cols = ["Merchant_Category", "Transaction_Location", "Card_Type", "Device_Type",
                    "Authentication_Method", "Payment_Gateway", "User_Age_Group", "Transaction_Channel"]
df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Separate the Transaction Frequency column before PCA
transaction_frequency = df[['Transaction_Count_24H']].values  # Extract as NumPy array

# Normalize numerical features (excluding Transaction Frequency)
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df.drop(columns=['Transaction_Count_24H']))  # Scale all except frequency

# Apply PCA to reduce to 28 principal components
pca = PCA(n_components=28)
df_pca = pca.fit_transform(df_scaled)

# Convert PCA output to DataFrame
columns = [f'V{i+1}' for i in range(28)]
df_pca = pd.DataFrame(df_pca, columns=columns)

# Add the Transaction Frequency column back
df_pca['Transaction_Frequency'] = transaction_frequency

# Save transformed data
df_pca.to_csv("transformed_dataset.csv", index=False)

# Explained Variance Ratio
explained_variance = np.sum(pca.explained_variance_ratio_)
print(f"Total variance explained by 28 components: {explained_variance:.2f}")