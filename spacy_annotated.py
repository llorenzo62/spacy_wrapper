import spacy
import streamlit as st
from annotated_text import annotated_text
from  pathlib import Path
from spacy import displacy

def spacy_info():
    languages={'fr':'Français',
               'en':'English',
               'de':'Deutsch',
               'es':'Español',
               'pt':'Portuges',
               'gl':'Galego',
               }



    models={'Galego':'gl_lg'} if (Path.cwd()/'gl_lg').is_dir() else {}
    keys=sorted(list(spacy.info()['pipelines'].keys()))
    for key in keys:
        if (lg:=key.split('_')[0]) in languages.keys():
            models[languages[lg]]=key
        elif lg!='xx':
            models[key]=key

    version=spacy.info()['spacy_version']

    return version, models

def pretty_print(tagged_text,limit=80):
    chunks=[]
    chunk=[]
    counter=0
    for item in tagged_text:
        lenght=len(item[0])+len(item[1]) if isinstance(item,tuple) else len(item)
        if counter+lenght>limit:
            chunks.append(chunk)
            chunk=[item]
            counter=lenght
        else:
            chunk.append(item)
            counter+=lenght
    chunks.append(chunk) #the rest
    for chunk in chunks:
        annotated_text(*chunk)


version, models=spacy_info()
st.title('Spacy Wrapper')
st.sidebar.title(f'Spacy {version}')
model_select=st.sidebar.selectbox('Select language',list(models.keys()),index=0)
nlp=spacy.load(models[model_select])

txt=st.text_area('Sentence to analyze','')

if txt:
    doc=nlp(txt)
    tagged_text=[token.text if token.pos_ in ['PUNCT','SYM'] else (token.text,token.pos_) for token in doc]
    st.markdown('### POS tagging')
    pretty_print(tagged_text)
    st.markdown('### Lemmas')
    tagged_text = [token.text if token.pos_ in ['PUNCT', 'SYM'] else (token.lemma_, token.pos_) for token in doc]
    pretty_print(tagged_text)
    if doc.ents:
        st.markdown('### Entities')
        for token in doc.ents:
            pretty_print([(token.text,token.label_)])
    if doc.noun_chunks:
        st.markdown('### Noun chunks')
        for chunk in doc.noun_chunks:
            pretty_print([(token.text,token.dep_) for token in chunk])

    if st.checkbox('Diagram'):
        svg=displacy.render(doc, style="dep", jupyter=False)

        st.image(svg)

