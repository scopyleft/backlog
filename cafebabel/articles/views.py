from http import HTTPStatus

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)

from ..core.exceptions import ValidationError
from ..core.helpers import lang_url_for, editor_required
from .models import Article
from .translations.models import Translation

articles = Blueprint('articles', __name__)


# Only route with the slug for SEO purpose.
@articles.route('/<slug>-<regex("\w{24}"):article_id>/')
def detail(slug, article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    if article.slug != slug:
        return redirect(article.detail_url, code=HTTPStatus.MOVED_PERMANENTLY)
    if article.is_translation:
        translations = Translation.objects(
            original_article=article.original_article.id)
    else:
        translations = Translation.objects(original_article=article.id)
    translations_langs = [translation.language for translation in translations]
    translations_drafts = [translation for translation in translations
                           if translation.is_draft]
    translations_publisheds = [translation for translation in translations
                               if translation.is_published and
                               translation.id != article.id]
    return render_template('articles/detail.html', article=article,
                           translations=translations,
                           translations_langs=translations_langs,
                           translations_drafts=translations_drafts,
                           translations_publisheds=translations_publisheds)


@articles.route(
    '/<regex("\w{24}"):article_id>/edit/', methods=['get', 'post'])
@editor_required
def edit(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')

    if request.method == 'POST':
        try:
            article.save_from_request(request)
        except ValidationError as e:
            # TODO: see https://github.com/cafebabel/cafebabel.com/issues/187
            message = f'There was an error in your article submission: {e}'
            flash(message, 'error')
            return redirect(
                lang_url_for('articles.edit', article_id=article.id))
        flash('Your article has been updated')
        return redirect(article.detail_url)

    return render_template('articles/edit.html', article=article)


@articles.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@editor_required()
def delete(article_id):
    article = Article.objects.get_or_404(id=article_id)
    article.delete()
    flash('Article was deleted', 'success')
    return redirect(url_for('cores.home_lang', lang=article.language))


@articles.route('/to-translate/')
def to_translate():
    languages = dict(current_app.config['LANGUAGES'])
    languages_keys = list(languages.keys())
    from_language = request.args.get('from', languages_keys[0])
    to_language = request.args.get('to', languages_keys[1])
    if (from_language not in languages_keys or
            to_language not in languages_keys):
        abort(HTTPStatus.BAD_REQUEST,
              (f'You must specify valid languages. '
               f'`{from_language}` or `{to_language}` are not allowed, '
               f'only {languages_keys} are allowed for now.'))
    # PERF: `select_related` drastically reduces the number of queries.
    articles = (Article.objects.filter(language=from_language,
                                       original_article=None)
                .hard_limit().select_related(max_depth=1))
    return render_template(
        'articles/to-translate.html', articles=articles,
        from_language_code=from_language,
        to_language_code=to_language, to_language_label=languages[to_language])
