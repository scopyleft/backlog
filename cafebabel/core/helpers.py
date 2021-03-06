import json
import random
import re
import unicodedata
from functools import partial, wraps
from http import HTTPStatus

import markdown as markdownlib
from flask import Markup, abort, current_app, g, request, url_for
from flask_login import current_user, fresh_login_required, login_required
from flask_resize import exc
from unidecode import unidecode


def obfuscate_email(value):
    return value.replace('.', '&#46;').replace('a', '&#x61;')


def slugify(value):
    value = unidecode(value)
    value = (unicodedata.normalize('NFKD', str(value))
             .encode('ascii', 'ignore').decode('ascii'))
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def to_json_filter(value):
    return Markup(json.dumps(value))


def markdown(value):
    return Markup(markdownlib.markdown(value))


def editor_required(func=None, fresh=False):
    """Decorator which ensure that the current user's has an editor role.

    The optional `fresh` parameter will ensure that a `fresh_login_required`
    is applied, otherwise a regular `login_required` check will be performed
    *before* checking the role to ensure the appropriated redirection.
    """
    if callable(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.has_role('editor'):
                abort(HTTPStatus.FORBIDDEN,
                      'An editor is required to perform this action.')
            return func(*args, **kwargs)
        _login_required = fresh and fresh_login_required or login_required
        return _login_required(decorated_view)
    else:
        return partial(editor_required, fresh=fresh)


def file_exceeds(file_, size):
    blob = file_.read()
    file_.seek(0)
    return len(blob) > size


def current_language():
    return g.get('lang', current_app.config['DEFAULT_LANGUAGE'])


def lang_url_for(*args, **kwargs):
    return url_for(lang=current_language(), *args, **kwargs)


def absolute(url):
    if not url:
        return ''
    if url.startswith('/'):
        url = url[1:]
    return f'{request.url_root}{url}'


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower()
            in current_app.config['ALLOWED_EXTENSIONS'])


def rewrite_img_src(content):
    media_url = current_app.config.get('MEDIA_URL')
    if media_url:
        return Markup(str(content).replace('src="/', f'src="{media_url}/'))
    return content


def static_pages_for(language):
    from ..articles.models import Article  # Circular imports.
    static_pages_slugs = current_app.config.get('STATIC_PAGES_SLUGS')
    default_language = current_app.config.get('DEFAULT_LANGUAGE')
    static_pages = {slug: '#' for slug in static_pages_slugs}  # Defaults.
    articles = Article.objects.static_pages(default_language)
    for article in articles:
        if language == default_language:
            static_pages[article.slug] = article.detail_url
        else:
            translation = article.get_translation(language)
            original_slug = translation.original_article.slug
            static_pages[original_slug] = translation.detail_url
    return static_pages


def articles_for_tag(tag_slug, limit=5, only_published=True):
    from ..articles.models import Article  # Circular imports.
    from ..articles.tags.models import Tag  # Circular imports.
    language = current_language()
    try:
        tag = Tag.objects.get(slug=tag_slug, language=language)
    except Tag.DoesNotExist:
        return None, []
    if not limit:
        return tag, []
    articles = Article.objects.filter(tags__in=[tag], language=language)
    if only_published:
        articles = articles.published(language=language)
    # PERF: `select_related` drastically reduces the number of queries.
    return tag, articles.limit(limit).select_related(max_depth=1)


def social_network_url_for(kind):
    social_networks = current_app.config.get('SOCIAL_NETWORKS')
    return social_networks[kind].get(current_language(),
                                     social_networks[kind]['en'])


def get_categories():
    from ..articles.tags.models import Tag  # Circular imports.
    return Tag.objects.categories(language=current_language())


def shuffle(sequence):
    sequence = list(sequence)
    random.shuffle(sequence)
    return sequence


def resize(image_url, dimensions, **kwargs):
    """Proxy to deal with unhandled exceptions from Flask-Resize."""
    try:
        return current_app.resize(image_url, dimensions, **kwargs)
    except (exc.UnsupportedImageFormatError, IOError, TypeError):
        return image_url
