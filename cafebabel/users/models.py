import datetime

from flask_security import RoleMixin, UserMixin
from flask_login import current_user
from mongoengine import signals

from ..core.helpers import lang_url_for, slugify
from ..core.mixins import UploadableImageMixin
from .. import db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class UserProfile(db.EmbeddedDocument, UploadableImageMixin):
    name = db.StringField()
    slug = db.StringField()
    socials = db.DictField()
    website = db.StringField()
    about = db.StringField()
    old_pk = db.IntField()  # In use for migrations (references in articles).

    def __str__(self):
        return self.name

    def get_id(self):
        return self._instance.id

    @property
    def upload_subpath(self):
        return 'users'


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    password = db.StringField(max_length=255)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role, reverse_delete_rule=db.PULL),
                         default=[])
    profile = db.EmbeddedDocumentField(UserProfile)

    meta = {
        'indexes': ['profile.old_pk']
    }

    def __str__(self):
        return str(self.profile)

    @property
    def detail_url(self):
        print('profile', self.profile.slug)
        return lang_url_for('users.detail', slug=self.profile.slug,
                            id=self.id)

    def is_me(self):
        return hasattr(current_user, 'id') and self.id == current_user.id

    def has_role(self, role, or_admin=True):
        if super(User, self).has_role('admin') and or_admin:
            return True
        return super(User, self).has_role(role)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created', False) and not document.profile:
            # Create the profile only on creation (vs. update).
            document.profile = UserProfile(name='Anonymous')
            document.save()

    @classmethod
    def store_image(cls, sender, document, **kwargs):
        return UserProfile.store_image(sender=UserProfile,
                                       document=document.profile,
                                       **kwargs)

    @classmethod
    def delete_image_file(cls, sender, document, **kwargs):
        return UserProfile.delete_image_file(sender=UserProfile,
                                             document=document.profile,
                                             **kwargs)

    @classmethod
    def update_slug(cls, sender, document, **kwargs):
        if document.profile and document.profile.name:
            document.profile.slug = slugify(document.profile.name)


signals.pre_save.connect(User.update_slug, sender=User)
signals.post_save.connect(User.post_save, sender=User)
signals.post_save.connect(User.store_image, sender=User)
signals.pre_delete.connect(User.delete_image_file, sender=User)
