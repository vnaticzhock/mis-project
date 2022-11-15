python preprocessing.py

if [ ! -f glove.840B.300d.txt ]; then
    wget http://nlp.stanford.edu/data/glove.840B.300d.zip -O glove.840B.300d.zip
    unzip glove.840B.300d.zip
fi
## 幹...glove 好像是英文的
python prepare_glove.py