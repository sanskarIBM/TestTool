import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, SpatialDropout1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from tensorflow.python.keras.backend import learning_phase

file_path = 'xpaths_clustered.csv'
data = pd.read_csv(file_path)

MAX_VOCAB_SIZE = 10000
MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 128

X = data['XPath']
y = data['Cluster']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

tokenizer = Tokenizer(num_words=MAX_VOCAB_SIZE,filters = '!', oov_token="<OOV>")
tokenizer.fit_on_texts(X_train)

X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq = tokenizer.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')

y_train_cat = to_categorical(y_train, num_classes=9)
y_test_cat = to_categorical(y_test, num_classes=9)

model = Sequential([
    Embedding(MAX_VOCAB_SIZE, EMBEDDING_DIM, input_length=MAX_SEQUENCE_LENGTH),
    SpatialDropout1D(0.2),
    LSTM(64, dropout=0.2, recurrent_dropout=0.2),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(9, activation='softmax')  # 9 output classes
])

optimizer = Adam(learning_rate=0.001)

model.compile(loss='categorical_crossentropy',
              optimizer = optimizer,
              metrics=['accuracy'])

history = model.fit(
    X_train_pad, y_train_cat,
    validation_split=0.1,
    epochs=10,
    batch_size=32,
    verbose=2
)

loss, accuracy = model.evaluate(X_test_pad, y_test_cat, verbose=0)
print(f"Test Accuracy: {accuracy:.2f}")

model.save('xpath_classifier_model.h5')

with open('tokenizer.json', 'w') as f:
    f.write(tokenizer.to_json())
