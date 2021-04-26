############################################  NOTE  ########################################################
#
#           Creates NER training data in Spacy format from JSON downloaded from Dataturks.
#
#           Outputs the Spacy training data which can be used for Spacy training.
#
############################################################################################################
import json
import random
import logging
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from sklearn.metrics import accuracy_score
def convert_dataturks_to_spacy(dataturks_JSON_FilePath):
    try:
        training_data = []
        lines=[]
        with open(dataturks_JSON_FilePath, 'r') as f:
            lines = f.readlines()
        t=5
        w=1
        if dataturks_JSON_FilePath=="patent.json":
            t=1
            w=0
        if dataturks_JSON_FilePath=="datatrainnew.json":
            t=2
            w=1
        for i in range(w,t):
            
            data = json.loads(lines[i])
            text = data['content']
            print(i)
            print(len(data['annotation']))
            entities = []
            for an in range(0,len(data['annotation'])):
                #only a single point in text annotation.
                annotation=data['annotation'][an]
                point = annotation['points'][0]
                labels = annotation['label']
                #list=["computertechnology","electrical","telecommunication"]
                # handle both list of labels or a single label.
                if not isinstance(labels, list):
                    labels = [labels]
                

                for label in labels:
                    
                    #dataturks indices are both inclusive [start, end] but spacy is not [start, end)
                    entities.append((point['start'], point['end'] + 1 ,label))


            training_data.append((text, {"entities" : entities}))
        #print(training_data[1])
        return training_data
    except Exception as e:
        logging.exception("Unable to process " + dataturks_JSON_FilePath + "\n" + "error = " + str(e))
        return None

import spacy
################### Train Spacy NER.###########
def train_spacy():

    TRAIN_DATA = convert_dataturks_to_spacy("datatrainnew.json")
    nlp = spacy.blank('en') 
    
    # create blank Language class
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
       

    # add labels
    for _, annotations in TRAIN_DATA:
         for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(20):
            print("Statring iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update(
                    [text],  # batch of texts
                    [annotations],  # batch of annotations
                    drop=0.0,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)
    #test the model and evaluate it
    examples = convert_dataturks_to_spacy("patent.json")
    tp=0
    tr=0
    tf=0

    ta=0
    c=0        
    for text,annot in examples:

        f=open("resume"+str(c)+".txt","w")
        doc_to_test=nlp(text)
        d={}
        for ent in doc_to_test.ents:
            d[ent.label_]=[]
        for ent in doc_to_test.ents:
            d[ent.label_].append(ent.text)
        #print(d[ent.label_])
        for i in set(d.keys()):

            f.write("\n\n")
            f.write(i +":"+"\n")
            for j in set(d[i]):
                f.write(j.replace('\n','')+"\n")
        d={}
        for ent in doc_to_test.ents:
            d[ent.label_]=[0,0,0,0,0,0]
        #print("jiiiiiiiiiiiiii")
        #print(doc_to_test.ents)
        e=0
        ct=0
        t=0
        for ent in doc_to_test.ents:
            doc_gold_text= nlp.make_doc(text)
            gold = GoldParse(doc_gold_text, entities=annot.get("entities"))
            #print(gold)
            y_true = [ent.label_ if ent.label_ in x else 'Not '+ent.label_ for x in gold.ner]
            
            y_pred = [x.ent_type_ if x.ent_type_ ==ent.label_ else 'Not '+ent.label_ for x in doc_to_test]  
            #print((y_pred))
            for lh in range(0,len(y_pred)):
                    if y_pred[lh]=="telecommunication":
                        t=t+1
                    if y_pred[lh]=="electrical":
                        e=e+1  
                    if y_pred[lh]=="computertechnology":
                        ct=ct+1
            if(d[ent.label_][0]==0):
                #f.write("For Entity "+ent.label_+"\n")   
                #f.write(classification_report(y_true, y_pred)+"\n")
                (p,r,f,s)= precision_recall_fscore_support(y_true,y_pred,average='weighted')
                a=accuracy_score(y_true,y_pred)
                d[ent.label_][0]=1
                d[ent.label_][1]+=p
                d[ent.label_][2]+=r
                d[ent.label_][3]+=f
                d[ent.label_][4]+=a
                d[ent.label_][5]+=1
        c+=1
    print(t,e,ct)
    tot=t+e+ct
    for i in d:
        print("\n For Entity "+i+"\n")
        print("Accuracy : "+str((d[i][4]/d[i][5])*100)+"%")
        print("Precision : "+str(d[i][1]/d[i][5]))        print("Recall : "+str(d[i][2]/d[i][5]))
        print("F-score : "+str(d[i][3]/d[i][5]))
        
    
    if tot!=0:
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.title('com %={} ele %={} tele %={}'.format(t*100/tot,e*100/tot,ct*100/tot))
        ax = fig.add_axes([0,0,1,1])
        langs = ['tele', 'ele', 'com']
        students = [t/tot,e/tot,ct/tot]
        ax.bar(langs,students)
        #plt.title('{}'.format(t)
        plt.title('com %={} ele %={} tele %={}'.format(ct*100/tot,e*100/tot,t*100/tot))

        plt.show()
    else:
        print("graph not valid for enpty predictions")
    
    
train_spacy()