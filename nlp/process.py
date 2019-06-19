import re
import pickle
import pandas as pd
import scipy
import xgboost as xgb
import string
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
import numpy as np

re_tok = re.compile(f'([{string.punctuation}“”¨«»®´·º½¾¿¡§£₤‘’])')

# XGB Model Path
TOXIC_MODEL_PATH = 'nlp/XGB_Models/toxic.pickle'
SEVERE_MODEL_PATH = 'nlp/XGB_Models/severe_toxic.pickle'
OBSCENE_MODEL_PATH = 'nlp/XGB_Models/obscene.pickle'
THREAT_MODEL_PATH = 'nlp/XGB_Models/threat.pickle'
INSULT_MODEL_PATH = 'nlp/XGB_Models/insult.pickle'
HATE_MODEL_PATH = 'nlp/XGB_Models/identity_hate.pickle'
TFIDF_MODEL_PATH = 'nlp/XGB_Models/tfidf.pickle'

# LSTM Model Path
TOKENIZER_PATH = 'nlp/LSTM_Models/tokenizer.pickle'
LSTM_MODEL = 'nlp/LSTM_Models/LSTM_twitter.h5'

# Bad Word Path
TOXIC_WORD_PATH = 'nlp/bad_words/Bad_word_toxic.pickle'
SEVERE_WORD_PATH = 'nlp/bad_words/Bad_word_severe.pickle'
OBSCENE_WORD_PATH = 'nlp/bad_words/Bad_word_obscene.pickle'
THREAT_WORD_PATH = 'nlp/bad_words/Bad_word_threat.pickle'
HATE_WORD_PATH = 'nlp/bad_words/Bad_word_hate.pickle'
INSULT_WORD_PATH = 'nlp/bad_words/Bad_word_insult.pickle'


def tokenize(s):
    return re_tok.sub(' \1 ', s).split()


def preprocessing(text, tfidf=None):
    tf_text = tfidf.transform(pd.Series(text))
    msg = pd.DataFrame({'comment_text': text}, index=[0])

    msg['total_length'] = msg['comment_text'].apply(len)
    msg['capitals'] = msg['comment_text'].apply(lambda comment: sum(1 for c in comment if c.isupper()))
    msg['caps_vs_length'] = msg.apply(lambda row: float(row['capitals']) / float(row['total_length']),
                                      axis=1)
    msg['num_exclamation_marks'] = msg['comment_text'].apply(lambda comment: comment.count('!'))
    msg['num_question_marks'] = msg['comment_text'].apply(lambda comment: comment.count('?'))
    msg['num_punctuation'] = msg['comment_text'].apply(lambda comment: sum(comment.count(w) for w in '.,;:'))
    msg['num_symbols'] = msg['comment_text'].apply(lambda comment: sum(comment.count(w) for w in '*&$%'))
    msg['num_words'] = msg['comment_text'].apply(lambda comment: len(comment.split()))
    msg['num_unique_words'] = msg['comment_text'].apply(lambda comment: len(set(w for w in comment.split())))
    msg['words_vs_unique'] = msg['num_unique_words'] / msg['num_words']
    msg['num_smilies'] = msg['comment_text'].apply(
        lambda comment: sum(comment.count(w) for w in (':-)', ':)', ';-)', ';)')))

    cols = ['total_length', 'capitals', 'caps_vs_length',
            'num_exclamation_marks', 'num_question_marks', 'num_punctuation',
            'num_symbols', 'num_words', 'num_unique_words', 'words_vs_unique',
            'num_smilies']
    msg = scipy.sparse.csr_matrix(msg[cols].values)
    return scipy.sparse.hstack([msg.tocsr(), tf_text.tocsr()])


def predict(comment, model, tfidf, model_path):
    if not model:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    comment = preprocessing(comment, tfidf)
    return round(model.predict(xgb.DMatrix(comment), ntree_limit=model.best_ntree_limit)[0] * 100, 4)


def predict_LSTM(comment, tokenizer=None, model=None):
    if model is None:
        model = tf.contrib.keras.models.load_model(LSTM_MODEL)
    if tokenizer is None:
        with open(TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
    c = tokenizer.texts_to_sequences([comment])
    c = pad_sequences([c[0]], maxlen=100)
    return model.predict([[c[0]]])


def process_comment(comment, path):
    with open(path, 'rb') as f:
        bad_words = pickle.load(f)
    result = dict()
    for word in comment.split():
        if word in bad_words:
            result[word] = bad_words[word]
    sorted_dict = dict(sorted(result.items(), key=lambda kv: kv[1], reverse=True))
    return "\n".join(['%s: %s' % (key, str(value)) for key, value in sorted_dict.items()])
