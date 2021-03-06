import os
import numpy as np
import random
from src.features import character_specific_features
from src.features import syntactic_features
from src.features import word_specific_features


def create_features_vector(text, label, author, book, filename, features_mask):
    """
    Create a feature vector for the given text over all the public functions in all modules.
    :param text: text to vectorize
    :param label: the label of the text (mainly the author)
    :param features_mask: represent a combination of features class to work with
    :return: the vector
    """
    feature_vector = []
    if features_mask[0]:
        feature_vector += character_specific_features.get_feature_vector(text)
    if features_mask[1]:
        feature_vector += syntactic_features.calculate_syntactic_feature_vector(text, author, book, filename)
    if features_mask[2]:
        feature_vector += word_specific_features.calculate_words_feature_vector(text)
    return [feature_vector, label, book]


def feature_names_vector(features_mask=[1] * 3):
    """
    :param features_mask: represent a combination of features class to work with
    :return: vector with the corresponding name of each feature
    """
    feature_names = []
    if features_mask[0]:
        feature_names += character_specific_features.get_feature_names()
    if features_mask[1]:
        feature_names += syntactic_features.get_feature_names()
    if features_mask[2]:
        feature_names += word_specific_features.get_feature_names()
    return feature_names


def create_corpus_vector(authors_num, features_mask):
    """
    Iterate over all authors and their books  and create a vector for each chapter
    :return: vectors with corresponding features values.
    """
    vectors = []
    for author in os.listdir("corpus/data")[:authors_num]:
        if author.startswith("."):  # It's needed just on mac (but will not create problems on other OS)
            continue
        for book in os.listdir("corpus/data/" + author):
            if book.startswith("."):  # It's needed just on mac (but will not create problems on other OS)
                continue
            for filename in os.listdir("corpus/data/" + author + "/" + book):
                if filename.endswith(".txt"):
                    with open("corpus/data/" + author + "/" + book + "/" + filename, 'r', encoding='utf-8', errors='ignore') as file:
                        text = file.read()
                        if not text:
                            continue
                        vectors.append(create_features_vector(text, author, author, book, filename, features_mask))
    return np.asarray(vectors)


def save_corpus_vector(data):
    """
    :param data: includes all the features' vectors
    :returns a file with the data
    """
    f = open("corpus/pre_calculated_vector.txt", "w+", encoding='utf-8', errors='ignore')
    np.savetxt('corpus/pre_calculated_vector.txt', data, fmt='%s', delimiter=';')
    f.close()
    return f


def load_corpus_vector():
    """
    Loads the vectors from a file to an array
    :return: array with the feature vectors
    """
    a = np.genfromtxt("corpus/pre_calculated_vector.txt", delimiter=';', dtype=str)
    vectors = []
    lists = np.ndarray.tolist(a[:, 0])
    for i in range(a.shape[0]):
        splitted = lists[i][1:-1].split(', ')
        vectors.append([[float(x) for x in splitted], a[i][1], a[i][2]])
    return np.asarray(vectors)


def get_corpus_vector(pre_calc, authors_num=10, features_mask=[1] * 3):
    """
    If the corpus has been calculated before, the function loads the vector from a file.
    Else, it creates the features vectors.
    :param pre_calc: indicates if the corpus has been calculated before
    :param authors_num: how many authors should be considered in the corpus
    :param features_mask: how many features should be considered in the corpus
    :return: the features vector
    """
    if pre_calc:
        return load_corpus_vector()
    return create_corpus_vector(authors_num, features_mask)


def split_train_test(data):
    """
    Split the data to train-test where a entirely new book is only in the test part.
    :param data: data to split.
    :return: numpy arrays of training and test split of the data.
    """
    test_data = []
    training_data = []
    test_books = []
    for author in os.listdir("corpus/data"):
        if author.startswith("."):
            continue
        num_of_books = len(os.listdir("corpus/data/" + author))
        test_book_index = random.randint(0, num_of_books - 1)
        while os.listdir("corpus/data/" + author)[test_book_index].startswith("."):
            test_book_index = random.randint(0, num_of_books - 1)  # This is needed only on mac
        test_book = os.listdir("corpus/data/" + author)[test_book_index]
        test_books.append(test_book)
    for item in data:
        if item[2] in test_books:
            test_data.append(item)
        else:
            training_data.append(item)
    return np.asarray(training_data), np.asarray(test_data)
