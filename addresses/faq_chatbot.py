"""
doc2vec : 문서를 vector로 변경하는 document embedding 방식
paragraph id(document id)를 하나의 단어(paragraph token)처럼 사용해서 문서를 훈련 데이터로 사용
"""

import os
import warnings
from gensim.models import doc2vec, Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import pandas as pd

import jpype

# 형태소 분석
import jpype
from konlpy.tag import Kkma

# csv 파일 불러오기
df_faqs = pd.read_csv('챗봇데이터.csv', encoding='CP949')  # 파일 읽기

# 순번, 질문, 답 순서의 데이터
faqs = pd.DataFrame(columns=['index', 'Q', 'A'])  # df_faqs 에서 질문에 해당하는 답변과 순번을 한 세트로 묶어 faqs에 저장하기 위해 빈 데이터프레임 생성
for i in range(len(df_faqs)):  # 질문-답변 행 개수만큼 반복
    faqs = faqs.append(pd.DataFrame([[i + 1, df_faqs['Q'][i], df_faqs['A'][i]]], columns=['index', 'Q', 'A']),
                       ignore_index=True)


def tokenize_kkma(doc):  # 전체 형태소 분석
    jpype.attachThreadToJVM()
    token_doc = ['/'.join(word) for word in kkma.pos(doc)]
    return token_doc


def tokenize_kkma_noun(doc):  # 일부 형태소 분석
    jpype.attachThreadToJVM()
    token_doc = ['/'.join(word) for word in kkma.pos(doc) if word[1] in filter_kkma]
    return token_doc


# 파일로부터 모델을 읽는다. 없으면 생성한다.
try:
    d2v_faqs = Doc2Vec.load.load('d2v_faqs_size100_min1_batch50_epoch50_nounonly_dm0')  # 모델 load

except:
    kkma = Kkma()
    filter_kkma = [
        'NNG',  # 보통명사
        'NNP',  # 고유명사
        'OL',  # 외국어
        'VA',  # 형용사
        'VV',  # 동사
    ]
    # 품사 태그 비교표: https://docs.google.com/spreadsheets/d/1OGAjUvalBuX-oZvZ_-9tEfYD2gQe7hTGsgUpiiBSXI8/edit#gid=0

    # 리스트에서 각 문장부분 토큰화
    token_faqs = []
    for i in range(len(faqs)):
        token_faqs.append([tokenize_kkma(faqs['Q'][i]), i])

    # Doc2Vec에서 사용하는 태그문서형으로 변경
    tagged_faqs = [TaggedDocument(d, [c]) for d, c in token_faqs]

    # 모델 생성
    import multiprocessing
    cores = multiprocessing.cpu_count()  # cpu 사용 개수
    d2v_faqs = doc2vec.Doc2Vec(
        vector_size=100,  # 임베딩 벡터의 크기 - 몇차원까지 벡터화 시킬 것인가
        alpha=0.025,  # learning rate
        min_alpha=0.025,  # min learning rate
        hs=1,  # hierarchical softmax
        negative=0,  # negative sample의 개수
        dm=0,  # 0:PV-DBOW(하나를 갖고 여러개 추측), 1:PV-DM(paragraph vector와 앞의 단어를 사용해서 다음에 나오는 단어 유추)
        # window=3,  # 훈련시 앞 뒤로 고려하는 단어의 개수
        dbow_words=1,  # 0:doc-vector만 train, 1:w2v simultaneous with DBOW d2v
        min_count=1,  # 데이터에서 등장하는 단어의 최소빈도수 - 단어의 수가 min_count 보다 작으면 사용하지 않음
        workers=cores,  # 스레드의 개수, cores:multi cpu
        seed=0,  # 난수 생성을 위한 시드
        pochs=100
    )
    d2v_faqs.build_vocab(tagged_faqs)  # 단어 사전을 생성

    d2v_faqs.train(tagged_faqs,
                   total_examples=d2v_faqs.corpus_count,
                   epochs=d2v_faqs.epochs
                   )

    d2v_faqs.save('d2v_faqs_size100_min1_batch50_epoch50_nounonly_dm0')  # 모델 저장


# FAQ 답변
def faq_answer(input):
    # 테스트하는 문장도 같은 전처리를 해준다.
    tokened_test_string = tokenize_kkma(input)

    topn = 5
    test_vector = d2v_faqs.infer_vector(tokened_test_string)
    result = d2v_faqs.docvecs.most_similar([test_vector], topn=5)
    print(result)

    for i in range(topn):
        print("{}위. {}, {} {} → {}".format(i + 1, result[i][1], result[i][0], faqs['Q'][result[i][0]], faqs['A'][result[i][0]]))

    # 대답이 일정 정확도에 못 미치는 경우
    if result[0][1] < 0.75:
        answer = "잘 모르겠어요. 다시 질문해주세요."
    else:
        answer = faqs['A'][result[0][0]]

    return answer