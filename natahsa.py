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
import json

from flask import Flask, request, jsonify, jsonify, make_response
from flask_restx import Resource, Api, reqparse

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

class Response(object):
    def __init__(self):
        self.Persons = []
        self.Organizations = []
        self.Locations = []

app = Flask(__name__)
api = Api(app)

upload_parser = api.parser()
upload_parser.add_argument('text', location='json', required=True)

@api.route('/api/hello')
class Greeting(Resource):
    def get(self):
        '''say hello'''
        return 'Hello world'

# Automatic brightness and contrast optimization with optional histogram clipping
@api.route('/api/fix')
@api.expect(upload_parser)
@api.response(200, description='correct grammar')
@api.produces(['application/json'])
class GrammaCorection(Resource):
    def post(self):
        args = upload_parser.parse_args()
        print(args)
        text = args['text']
        print(text)
        text = text.replace('\'', '')

        doc = Doc(text)

        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)

        for token in doc.tokens:
            token.lemmatize(morph_vocab)
        for span in doc.spans:
            span.normalize(morph_vocab)

        response = Response()
        for x in doc.spans:
            if x.type == 'PER':
                response.Persons.append(x.normal)
            if x.type == 'ORG':
                response.Organizations.append(x.normal)
            if x.type == 'LOC':
                response.Locations.append(x.normal)

        for span in doc.spans:
            if span.type == PER:
                span.extract_fact(names_extractor)
        return make_response(jsonify({
            'persons': response.Persons, 
            'organizations': response.Organizations,
            'locations': response.Locations
        }), 200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')