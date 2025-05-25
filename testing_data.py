import yfinance as yf  
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import Sequential, Input
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 50)

df = yf.download("AAPL", start="2005-01-01", end="2025-05-17")

df['Return'] = df['Close'].pct_change()
df['Lag_1'] = df['Close'].shift(1)
df['Ret_1'] = df['Return'].shift(1)
df['SMA_20'] = df['Close'].rolling(window=20).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['StandardDeviation'] = df['Close'].rolling(window=20).std()
df['Variance'] = df['Close'].rolling(window=20).var()
df['EMA'] = df['Close'].ewm(span=3).mean()
df['MACD'] = df['SMA_20']-df['SMA_50']
df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)


df.fillna(0, inplace=True)

features = ['Open', 'Low', 'High', 'Close', 'Return', 'Lag_1', 'Ret_1', 'SMA_20', 'SMA_50', 'StandardDeviation', 'Variance', 'EMA', 'MACD']

scaler = StandardScaler()
tscv = TimeSeriesSplit(n_splits=5)

for fold, (train_index, test_index) in enumerate(tscv.split(df)):
    train_df = df.iloc[train_index]
    test_df = df.iloc[test_index]

    X_train = scaler.fit_transform(train_df[features])
    y_train = train_df['Target']
    X_test = scaler.transform(test_df[features])
    y_test = test_df['Target']

    # Build the model
    model = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

    y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()
    acc = accuracy_score(y_test, y_pred)
    print(f"Fold {fold + 1} Accuracy: {acc:.4f}")