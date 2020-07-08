
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

text = '000 «ИМПУЛЬС» ИНН 7810789812. КПП 781001001, ОКПО 43613173. ОГРН 1207800028303 полное наименование организации, идентификационные коды (ИНН, КПП, ОКПО; ОГРН) СПРАВКА. исх № 89 0т07 Мая 2020: с Санкт-Петербург выдана Шмидт Марине Михайловне, работающей в должности генерального `директора ООО «Импульс», в том, что она не получала единовременное пособие при рождении ребенка — своего сына Шмидт Дениса Владимировича (дата. рождения —23 Марта 2020 года), (Справка дана для представления по месту работы отца ребенка.'
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