from __future__ import absolute_import, division, print_function, unicode_literals
from first_keyword_extraction.ner_model.net import KobertCRF
from gluonnlp.data import SentencepieceTokenizer
from data_utils.utils import Config
from data_utils.vocab_tokenizer import Tokenizer
from data_utils.pad_sequence import keras_pad_fn
from pathlib import Path

from first_keyword_extraction.keybert_model import KeyBERT
from transformers import BertModel
from konlpy.tag import *

import torch
import pickle
import json


class DecoderFromNamedEntitySequence():
    def __init__(self, tokenizer, index_to_ner):
        self.tokenizer = tokenizer
        self.index_to_ner = index_to_ner

    def __call__(self, list_of_input_ids, list_of_pred_ids):
        input_token = self.tokenizer.decode_token_ids(list_of_input_ids)[0]
        pred_ner_tag = [self.index_to_ner[pred_id] for pred_id in list_of_pred_ids[0]]

        # ----------------------------- parsing list_of_ner_word ----------------------------- #
        list_of_ner_word = []
        entity_word, entity_tag, prev_entity_tag = "", "", ""
        for i, pred_ner_tag_str in enumerate(pred_ner_tag):
            if "B-" in pred_ner_tag_str:
                entity_tag = pred_ner_tag_str[-3:]

                if prev_entity_tag != "":
                    list_of_ner_word.append(entity_word.replace("▁", " ").lstrip())

                entity_word = input_token[i]
                prev_entity_tag = entity_tag
            elif "I-"+entity_tag in pred_ner_tag_str:
                entity_word += input_token[i]
            else:
                if entity_word != "" and entity_tag != "":
                    list_of_ner_word.append(entity_word.replace("▁", " ").lstrip())
                entity_word, entity_tag, prev_entity_tag = "", "", ""


        # ----------------------------- parsing decoding_ner_sentence ----------------------------- #
        decoding_ner_sentence = ""
        is_prev_entity = False
        prev_entity_tag = ""
        is_there_B_before_I = False

        for token_str, pred_ner_tag_str in zip(input_token, pred_ner_tag):
            token_str = token_str.replace('▁', ' ')  # '▁' 토큰을 띄어쓰기로 교체

            if 'B-' in pred_ner_tag_str:
                if is_prev_entity is True:
                    decoding_ner_sentence += ':' + prev_entity_tag+ '>'

                if token_str[0] == ' ':
                    token_str = list(token_str)
                    token_str[0] = ' <'
                    token_str = ''.join(token_str)
                    decoding_ner_sentence += token_str
                else:
                    decoding_ner_sentence += '<' + token_str
                is_prev_entity = True
                prev_entity_tag = pred_ner_tag_str[-3:] # 첫번째 예측을 기준으로 하겠음
                is_there_B_before_I = True

            elif 'I-' in pred_ner_tag_str:
                decoding_ner_sentence += token_str

                if is_there_B_before_I is True: # I가 나오기전에 B가 있어야하도록 체크
                    is_prev_entity = True
            else:
                if is_prev_entity is True:
                    decoding_ner_sentence += ':' + prev_entity_tag+ '>' + token_str
                    is_prev_entity = False
                    is_there_B_before_I = False
                else:
                    decoding_ner_sentence += token_str

        return list_of_ner_word, decoding_ner_sentence


class ner():
    def __init__(self):
        model_dir = './first_keyword_extraction/ner_model'

        model_dir = Path(model_dir)
        model_config = Config(json_path=model_dir / 'config.json')

        tok_path = "./first_keyword_extraction/ner_model/tokenizer_78b3253a26.model"
        ptr_tokenizer = SentencepieceTokenizer(tok_path)

        with open("./first_keyword_extraction/vocab.pkl", 'rb') as f:
            vocab = pickle.load(f)

        self.tokenizer = Tokenizer(vocab=vocab, split_fn=ptr_tokenizer, pad_fn=keras_pad_fn, maxlen=model_config.maxlen)

        with open(model_dir / "ner_to_index.json", 'rb') as f:
            ner_to_index = json.load(f)
            index_to_ner = {v: k for k, v in ner_to_index.items()}

        self.model = KobertCRF(config=model_config, num_classes=len(ner_to_index), vocab=vocab)
        model_dict = self.model.state_dict()
        checkpoint = torch.load("/opt/ml/level2_mrc_nlp-level2-nlp-01/level3test/pytorch-bert-crf-ner/experiments/base_model_with_crf_val/best-epoch-12-step-1000-acc-0.960.bin", map_location="cuda")
        convert_keys = {}
        for k, v in checkpoint['model_state_dict'].items():
            new_key_name = k.replace("module.", '')
            if new_key_name not in model_dict:
                print("{} is not int model_dict".format(new_key_name))
                continue
            convert_keys[new_key_name] = v
        
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        
        self.model.load_state_dict(convert_keys, strict=False)
        self.model.to(device)
        self.model.eval()

        self.decoder_from_res = DecoderFromNamedEntitySequence(tokenizer=self.tokenizer, index_to_ner=index_to_ner)
    
    def extraction(self, doc):
        input_text = doc
        list_of_input_ids = self.tokenizer.list_of_string_to_list_of_cls_sep_token_ids([input_text])
        x_input = torch.tensor(list_of_input_ids).long().to(torch.device('cuda'))

        list_of_pred_ids = self.model(x_input)

        list_of_ner_word, decoding_ner_sentence = self.decoder_from_res(list_of_input_ids=list_of_input_ids, list_of_pred_ids=list_of_pred_ids)

        return(list_of_ner_word)


def get_nouns(old_input):
    new_input = []

    for i in old_input:
        tagged = Mecab().pos(i)
        flag = 1
        for _, t in tagged:
            if(t=='JKS' or t=='JKC' or t=='JKG' or t=='JKO' or t=='JKB' or t=='JKV' or t=='JKG' or t=='JC' or t=='JX'):# and len(s)>1:
                flag = 0
                break
        if(flag):
            new_input.append(i)

    return new_input

def get_nouns_sentence(text):
    tokenized_doc = Mecab().pos(text)
    nouns_sentence = ' '.join([word[0] for word in tokenized_doc if (word[1] == 'NNG' or word[1] == 'NNP')])
    return nouns_sentence

def main_extraction(docs):
    stopwords = []
    with open('./first_keyword_extraction/stopwords.txt', 'r', encoding='UTF-8') as f:
        for line in f:
            stopwords.append(line.replace('\n',''))

    #ner model
    ner_model = ner()

    #keybert model
    kw_model = KeyBERT(BertModel.from_pretrained('sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens'))

    list_of_key_word = []

    for sen_list in docs:
        temp_output = []
        doc = sen_list

        #ner output
        for i in sen_list.split('.'):
            i = i+"."
            if '?' in i:
                for j in i.split('?'):
                    temp_output += ner_model.extraction(j)
            else:
                temp_output += ner_model.extraction(i)
        
        #ner output 조사 제거
        temp_output = get_nouns(temp_output)
        
        output = []
        # 한글자 제거 
        for i, j in enumerate(temp_output):
            if len(j)>1:
                output.append(temp_output[i])

        # keybert output
        keywords = kw_model.extract_keywords(get_nouns_sentence(doc), keyphrase_ngram_range=(1,1), top_n=10)

        for i in keywords:
            output.append(i[0])

        # 중복 제거
        temp = set(output)
        output = list(temp)

        # 불용어 제거
        result = []
        for token in output: 
            if token not in stopwords: 
                result.append(token) 

        list_of_key_word.append({"context" : doc, "keyword": result})

    return list_of_key_word