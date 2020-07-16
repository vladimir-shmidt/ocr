
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,

    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)
money_extractor = MoneyExtractor(morph_vocab)
addr_extractor = AddrExtractor(morph_vocab)

text = '''
еуче
'''
text = text.replace('\'', '`')

doc = Doc(text)

doc.segment(segmenter)
# print(doc)
# print(doc.sents[:2])
# print(doc.tokens[:5])

doc.tag_morph(morph_tagger)
doc.parse_syntax(syntax_parser)
# print(doc.tokens[:5])

doc.tag_ner(ner_tagger)
# print(doc.spans[:5])

doc.ner.print()

# sent = doc.sents[0]
# sent.morph.print()


# sent.syntax.print()

for token in doc.tokens:
    token.lemmatize(morph_vocab)
    
{print(_.text, _.lemma) for _ in doc.tokens[:10]}

for span in doc.spans:
    span.normalize(morph_vocab)
    
{print(_.text, _.normal) for _ in doc.spans}

for span in doc.spans:
    if span.type == PER:
        span.extract_fact(names_extractor)
    
{print(_.normal, _.fact.as_dict) for _ in doc.spans if _.fact}