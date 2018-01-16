from http import HTTPStatus

from flask import (Blueprint, abort, current_app, jsonify, render_template,
                   request)

from ..models import Article
from .models import Tag

tags = Blueprint('tags', __name__)


@tags.route('/suggest/')
def suggest():
    terms = request.args.get('terms')
    if len(terms) < 3:
        abort(HTTPStatus.BAD_REQUEST,
              'Suggestions made available from 3-chars and more.')
    languages = dict(current_app.config['LANGUAGES'])
    language = request.args.get('language')
    if language not in languages:
        abort(HTTPStatus.BAD_REQUEST,
              f'Languages available: {list(languages.keys())}.')
    tags = Tag.objects(language=language, name__istartswith=terms)
    cleaned_tag = [{
        'name': tag.name,
        'slug': tag.slug,
        'language': tag.language,
        'summary': tag.summary or ''
    } for tag in tags]
    return jsonify(cleaned_tag)


@tags.route('/<slug>/')
def detail(slug):
    tag = Tag.objects.get_or_404(slug=slug)
    articles = Article.objects(tags__in=[tag], status='published')
    return render_template('articles/tags/detail.html', tag=tag,
                           articles=articles)
