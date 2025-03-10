
import random
import os
import sys
from models.bert import BERT_Model
from models.bilstm_crf_ import BiLSTM_CRF_Model
from data import build_corpus
from config import ModelPathConfig,ResultPathConfig
from datetime import datetime
from utils import extend_map_bert,save_model,load_model,extend_map,add_label_for_lstmcrf
from evaluate import evaluate_entity_label,evaluate_multiclass,evaluate_single_label,unitstopd
from tabulate import tabulate
import pandas as pd

def bert_test():
    model_is_exitsed=os.path.exists(ModelPathConfig.bert)

    print("upload data!")

    word_lists,tag_lists,word2id,tag2id=build_corpus("train")
    test_word_lists,test_tag_lists,_,_=build_corpus("test")

    labels=list(tag2id.keys())

    dev_indices=random.sample(range(len(word_lists)),len(word_lists)//5)
    train_indices=[i for i in range(len(word_lists)) if i not in dev_indices]

    dev_word_lists=[ word_lists[ind] for ind in dev_indices]
    dev_tag_lists=[tag_lists[ind] for ind in dev_indices]
    train_word_lists=[word_lists[ind] for ind in train_indices]
    train_tag_lists=[tag_lists[ind] for ind in train_indices]

    bert_tag2id=extend_map_bert(tag2id)
    
    if not model_is_exitsed:
        print('start to training')
        start=datetime.now()
        vocab_size=len(word2id)
        out_size=len(bert_tag2id)
        bert_model=BERT_Model(vocab_size,out_size)
        bert_model.train(train_word_lists,train_tag_lists,\
            word2id,bert_tag2id,dev_word_lists,dev_tag_lists)

        deltatime=datetime.now()-start
        print("Training is finished, {} second".format(deltatime.seconds))
        try:
            print("Save the model")
            save_model(bert_model,ModelPathConfig.bert)
        except:
            print("fail to save model")
        
    else:
        try:
            print("load model")
            bert_model=load_model(ModelPathConfig.bert)
        except:
            print("fail to load model")
            sys.exit(0)

    print("test the model")
    pred_tag_lists=bert_model.test(test_word_lists,test_tag_lists,word2id,bert_tag2id)

    label_tag_lists=test_tag_lists

    units=evaluate_entity_label(pred_tag_lists,label_tag_lists,labels)
    df=unitstopd(units)
    df.to_csv(ResultPathConfig.bert_entity)
    print(tabulate(df,headers='keys',tablefmt='psql'))

    units=evaluate_single_label(pred_tag_lists,label_tag_lists,labels)
    df=unitstopd(units)
    df.to_csv(ResultPathConfig.bert_model)
    print(tabulate(df,headers='keys',tablefmt='psql'))



def _bilstm_crf_test(if_train=True):
    model_is_existed=os.path.exists(ModelPathConfig._bilstm_crf)

    print("upload data!")
    word_lists,tag_lists,word2id,tag2id=build_corpus("train")
    test_word_lists,test_tag_lists,_,_=build_corpus("test")
    labels=list(tag2id.keys())
    dev_indices=random.sample(range(len(word_lists)),len(word_lists)//5)
    train_indices=[i for i in range(len(word_lists)) if i not in dev_indices]

    dev_word_lists=[ word_lists[ind] for ind in dev_indices]
    dev_tag_lists=[tag_lists[ind] for ind in dev_indices]
    train_word_lists=[word_lists[ind] for ind in train_indices]
    train_tag_lists=[tag_lists[ind] for ind in train_indices]
    # bilstm_crf_word2id,bilstm_crf_tag2id=extend_map(word2id,tag2id,crf=True)
    bilstm_crf_word2id,bilstm_crf_tag2id=extend_map(word2id,tag2id,crf=False)
    if if_train or not model_is_existed:
        print('start to training')
        # sample_print_test(train_word_lists,train_tag_lists)

        start=datetime.now()
        vocab_size=len(bilstm_crf_word2id)
        out_size=len(tag2id)

        bilstm_model=BiLSTM_CRF_Model(vocab_size,out_size)
        bilstm_model.train(train_word_lists,train_tag_lists,\
            word2id,bilstm_crf_tag2id,dev_word_lists,dev_tag_lists)
        deltatime=datetime.now()-start

        print("Training is finished, {} second".format(deltatime.seconds))
        save_model(bilstm_model,ModelPathConfig._bilstm_crf)
        print("Save the model")
    else:
        print("load model")
        bilstm_model=load_model(ModelPathConfig._bilstm_crf)


    print("test the model")
    pred_tag_lists,label_tag_lists,=bilstm_model.test(test_word_lists,test_tag_lists,word2id,tag2id)


    units=evaluate_entity_label(pred_tag_lists,label_tag_lists,labels)
    df=unitstopd(units)
    df.to_csv(ResultPathConfig._bilstm_crf_entity)
    print(tabulate(df,headers='keys',tablefmt='psql'))

    units=evaluate_single_label(pred_tag_lists,label_tag_lists,labels)
    df=unitstopd(units)
    df.to_csv(ResultPathConfig._bilstm_crf_model)
    print(tabulate(df,headers='keys',tablefmt='psql'))


def mrc_bert_test(if_train=True):
    pass


if __name__=='__main__':
    pass