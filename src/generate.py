import re
import os
import numpy as np
import Arabycia.pyaramorph as pam


def createFile(filename, content, wmode='w'):
    try:
        with open(filename, wmode) as file:
            file.write(content)
    except Exception as e:
        return "Error :", e
    return True


def readFile(filename, rmode='r'):
    try:
        with open(filename, rmode) as file:
            content = file.read()
    except Exception as e:
        return "Error :", e
    return content


def removeNumber(text):
    return re.sub(r'\d+', '', text)


def removeUnnecessaryChar(text):
    text = " ".join(text.split()) # Remove all whitespace in a string
    text = re.sub(r'[،؛﴾﴿٪]+', '', text)
    text = re.sub(r'[\r\t ]+', ' ', text)
    return removeNumber(text)


def removeNonArabicChar(text):
    text = re.sub(
        r'[^0-9\u0600-\u06ff\u0750-\u077f\ufb50-\ufbc1\ufbd3-\ufd3f\ufd50-\ufd8f\ufd50-\ufd8f\ufe70-\ufefc\uFDF0-\uFDFD.0-9]+',
        ' ', text)
    return text


def sentTokenize(text):
    text = re.sub(r'[.؟!,,]', '\n', text)
    return text


def clean(text):
    text = removeUnnecessaryChar(text)
    text = removeNonArabicChar(text)
    return sentTokenize(text)


def scan_directory(dirname):
    files = []
    for filename in os.listdir(dirname):
        files.append(os.path.join(dirname, filename))
    return files


def MED(A, B):
    m = len(A)
    n = len(B)
    D = np.zeros((m + 1, n + 1))
    for i in range(1, m + 1):
        D[i, 0] = i
    for j in range(1, n + 1):
        D[0, j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if A[i - 1] == B[j - 1]:
                alpha = 0
            else:
                alpha = 2

            D[i, j] = min(D[i - 1, j] + 1,
                          D[i, j - 1] + 1, D[i - 1, j - 1] + alpha)
    # print(D[1:])
    return D[m, n]


def find_best_series(all_solution, text):
    word=text.split()
    # print(word)
    final_pos = ""

    for i in range(0, len(word)):
        best_solution_index = -1
        best_solution_diff = 1000
        # print(all_solution[i])
        if len(all_solution[i]['solution']) == 0 :
            final_pos += "[Unidentified] "
            continue
        else:
            current_word_sol = all_solution[i]['solution']
        for index in range(0, len(current_word_sol)):
            dif = MED(current_word_sol[index]['word'][0], word[i])
            if dif < best_solution_diff:
                best_solution_diff = dif
                best_solution_index = index
        pos = current_word_sol[best_solution_index]['pos']
        word_trans = current_word_sol[best_solution_index]['word'][1]
        word_res = []
        for part in pos:
            if part != "":
                word_res.append(part.split('/')[1])
        final_pos += word_trans + ':' + "/".join(word_res) + " "
    return final_pos


def analyze_text(text_list, pam = pam.Analyzer()):
    result =""
    for sent in text_list:
        if sent not in [" ", "\n", " \n"]:
            all_sol = pam.analyze_text(sent)
            pos = find_best_series(all_sol, sent)
            result += pos + "\n"
    print("Done")
    return result


def remove_dub(text_list):
    text_set = set(text_list)
    print(len(text_list) - len(text_set), " Duplicates")
    text = list(text_set)
    text = "\n".join(text)
    return text


def cleanDir(path):
    files = scan_directory(path)
    cnt = 1
    sz = len(files)
    for file in files:
        print("{}\{} - {}".format(cnt, sz, file))
        text = readFile(file, "r")
        clean_text = clean(text)
        analyzed_text = analyze_text(clean_text.split("\n"))
        analyzed_text = remove_dub(analyzed_text.split("\n"))
        createFile(str(cnt)+".txt", analyzed_text, "w")
        cnt += 1


