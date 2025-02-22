# SecureX

Welcome to SecureX, a collection of projects focused on enhancing security in the financial technology (FinTech) sector. Below, you will find detailed information about two of our key projects: the **Fintech RAG Quiz Generator** and **Credit Card Fraud Detection with Neural Network**.

## Credit Card Fraud Detection with Deep Neural Network

This project detects credit card fraud using a **neural network**. The notebook is optimized to run on **Kaggle with GPU acceleration**, ensuring efficient training and evaluation of the model.

### Overview
Credit card fraud detection is crucial in the financial industry. This project leverages a neural network to classify transactions as **fraudulent** or **legitimate**. The model is trained on the **Credit Card Fraud Detection dataset** available on Kaggle.

### Features
- **Handles Imbalanced Data**: Uses techniques like undersampling/oversampling.
- **Neural Network with TensorFlow/Keras**: Ensures high accuracy.
- **Visualization**: Confusion matrices and ROC curves.

### Requirements
#### Software
- Python 3.10+
- TensorFlow, NumPy, Pandas, Scikit-learn, Matplotlib, Seaborn
- Jupyter Notebook (for interactive execution)

#### Hardware
- **GPU** (Recommended): Kaggle provides free GPU resources for faster training.

#### Dataset
- Available on Kaggle: [Credit Card Fraud Detection dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- Contains **284,807 transactions**, of which **492 are fraudulent**.

### Installation & Setup
```sh
git clone github.com/SanjayRagavendar/secureX
pip install -r secureX/requirements.txt
cd secureX/BackingApp/Backend
python3 main.py
```

### Usage
1. **Import Dataset**: Load data into a Pandas DataFrame.
2. **Preprocess Data**:
   - Handle missing values.
   - Scale features using standardization.
   - Split data into training and testing sets.
3. **Train Neural Network**:
   - Define network using TensorFlow/Keras.
   - Train the model.
4. **Evaluate Model**:
   - Use confusion matrix & ROC curve for evaluation.
5. **Interpret Results**:
   - Analyze accuracy, precision, recall, and F1-score.

### Kafka Integration
To enable real-time fraud detection using Kafka:
1. **Set up Kafka**:
   ```sh
   zookeeper-server-start.sh config/zookeeper.properties
   kafka-server-start.sh config/server.properties
   ```
2. **Run Kafka Producer (API)** to send transaction data:
   ```python
   producer.send('fraud_detection_requests', transaction_data)
   ```
3. **Kafka Consumer (Fraud Detection Model)**:
   ```python
   consumer = KafkaConsumer('fraud_detection_requests', bootstrap_servers='localhost:9092')
   for message in consumer:
       transaction = preprocess_transaction(message.value)
       prediction = model.predict(transaction)
       if prediction > 0.5:
           print("Fraud detected!")
   ```
4. **Log and handle fraudulent transactions.**

### Files
- `transaction_fraudlent.ipynb`: Jupyter notebook with the complete fraud detection code.
- `requirements.txt`: Lists required Python packages.
- `card_transaction.csv`: Dataset file (download manually from Kaggle).

### Key Features
✅ **99.4% Accuracy**: Achieves high precision in fraud detection.
✅ **GPU Acceleration**: Optimized for Kaggle’s free GPU resources.
✅ **Handles Imbalanced Data**: Uses techniques to balance fraud vs. non-fraud cases.
✅ **Visualization**: Includes confusion matrix and ROC curve.

### SHAP Documentation for the model
#### Summary Plot 
![image](https://github.com/user-attachments/assets/7f03005e-192c-4b05-a666-aa97b6c78a74)

#### Kernel Explainer of the model
![download](https://github.com/user-attachments/assets/2b4825fc-3246-4a5f-b62e-d28fa964ea22)

#### Confusion matrix
![image](https://github.com/user-attachments/assets/f930c0da-47ea-4598-9280-568a9e8f2dca)

---

## Fintech RAG Quiz Generator

The **Fintech RAG Quiz Generator** is a Python-based application designed to generate educational quiz questions about financial scams and fraud prevention. It uses **Retrieval-Augmented Generation (RAG)** with a combination of **Hugging Face embeddings, Google Gemini AI, and a MySQL database** to create contextually relevant multiple-choice questions.

### Features
- **Dynamic Quiz Generation**: Generates quiz questions based on user-provided scenarios or pre-loaded financial scam knowledge.
- **Retrieval-Augmented Generation (RAG)**: Combines embeddings-based retrieval with Google Gemini AI for question generation.
- **MySQL Integration**: Stores knowledge base, scenarios, and generated questions in a MySQL database.
- **Fallback Mechanism**: Ensures question generation even if the AI model fails.
- **Customizable**: Allows customization of the number of questions, embedding models, and database configurations.

### Requirements
- Python 3.8+
- Google Gemini API Key
- Hugging Face Transformers Library

### Installation
```sh
git clone https://github.com/sanjayragavendar/secureX.git
pip install -r secureX/requirements.txt
cd secureX/ScamQuiz/Backend
```

### Environment Setup
Create a `.env` file and add your Google Gemini API key:
```plaintext
GOOGLE_API_KEY=your_api_key_here
```

### Usage
```sh
python3 quiz_generator.py 
```
open new terminal

```sh
curl http://127.0.0.1:5000/generate_quiz_job
```

- Modify `sample_texts` in `main()` for additional scenarios.
- The app generates n multiple-choice questions based on user-provided financial fraud scenarios.

### Example Output
```
Question 1: What is a common red flag of a phishing attempt?
A) Requests for personal information
B) Professional email address
C) Proper spelling and grammar
D) Clear company logo

Correct Answer: A
Explanation: Legitimate organizations typically don't ask for personal information via email.
```

### Contributing
Contributions are welcome! Open an issue or submit a pull request.

### License
This project is licensed under the MIT License. See the LICENSE file for details.
