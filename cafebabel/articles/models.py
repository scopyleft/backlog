import datetime

from flask import current_app, url_for
from flask_login import current_user
from mongoengine import signals

from .. import db
from ..core.helpers import slugify
from ..core.mixins import UploadableImageMixin
from ..users.models import User


class Article(db.Document, UploadableImageMixin):
    title = db.StringField(required=True)
    slug = db.StringField(required=True)
    language = db.StringField(max_length=2, required=True)
    category = db.StringField()
    summary = db.StringField(required=True)
    body = db.StringField(required=True)
    status = db.StringField(default='draft')
    editor = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    author = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    publication_date = db.DateTimeField()

    meta = {
        'allow_inheritance': True
    }

    def __str__(self):
        return self.title

    def get_images_url(self):
        return current_app.config.get('ARTICLES_IMAGES_URL')

    def get_images_path(self):
        return current_app.config.get('ARTICLES_IMAGES_PATH')

    @property
    def detail_url(self):
        if self.is_draft:
            return url_for('drafts.detail', draft_id=self.id)
        else:
            return url_for('articles.detail', slug=self.slug,
                           article_id=self.id)

    @property
    def is_draft(self):
        return self.status == 'draft'

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def is_translation(self):
        return False

    def is_translated_in(self, language):
        """This implementation is quite naive and inefficient

        given that it performs one query per language.
        TODO: turn into a cacheable list of translations when necessary.
        """
        from .translations.models import Translation  # NOQA: circular :/
        return bool(Translation.objects
                    .filter(original_article=self, language=language).count())

    @classmethod
    def update_publication_date(cls, sender, document, **kwargs):
        if document.is_published and not document.publication_date:
            document.publication_date = datetime.datetime.utcnow()

    @classmethod
    def update_slug(cls, sender, document, **kwargs):
        document.slug = slugify(document.title)

    def save_from_request(self, request):
        data = request.form.to_dict()
        files = request.files
        if current_user.has_role('editor'):
            if not self.editor:
                data['editor'] = current_user.id
            data['author'] = User.objects.get(id=data['author'])
        else:
            if data.get('author'):
                del data['author']
            if data.get('editor'):
                del data['editor']
        for field, value in data.items():
            setattr(self, field, value)
        if data.get('delete-image'):
            self.delete_image()
        image = files.get('image')
        if image:
            self.attach_image(image)
        return self.save()


signals.pre_save.connect(Article.update_publication_date, sender=Article)
signals.pre_save.connect(Article.update_slug, sender=Article)
signals.post_save.connect(Article.store_image, sender=Article)
signals.pre_delete.connect(Article.delete_image_file, sender=Article)
