import urllib.parse
from urllib.parse import urlparse

from django.conf import settings

from django import forms
from django.core.files.storage import default_storage
from django.utils.html import format_html
from django.db import models
import cloudinary.uploader


class MultiBackendImageField(models.ImageField):
    """Custom ImageField that correctly generates URLs based on storage backend.
    Since for compatibility with ImageField, the Full URL is stored in the database,
    and accessed as Field.name not Field.url.

    Field.name = Full URL to the image
    Field.url = double full name of the image, not used.
    Can use str(image) for representation of the image Field.name
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)

    @staticmethod
    def add_preview_url(url: str, transform: str = None) -> str | None:
        if r".cloudinary.com/" in url:
            transform = transform or getattr(
                settings, "CLOUDINARY_PREVIEW_TRANSFORMATION"
            )
            if transform:
                return url.replace("/image/upload/", f"/image/upload/{transform}/")
        return url if url.startswith("http") else None

    def formfield(self, **kwargs):
        """Use custom form field with an image preview in Django Admin."""
        kwargs["form_class"] = MultiBackendImageFormField
        return super().formfield(**kwargs)

    def get_full_image_url(self, image, add: bool = False):
        if not image:
            return None  # No image uploaded

        image_name = image.name  # File path stored in DB
        if image_name and image_name.startswith("http"):
            return image_name

        default_file_storage = settings.STORAGES["default"]["BACKEND"]

        # Generate full URL based on storage backend
        if default_file_storage.startswith("storages.backends."):
            full_url = image.url
        elif "cloudinary" in default_file_storage:
            full_url = image.url  # Cloudinary full URL
        else:
            full_url = image.name if add else image.url  # Local storage

        return full_url  # Store full URL in the database

    def pre_save(self, model_instance, add):
        """Override pre_save to store the full URL in the database."""
        new_image = super().pre_save(model_instance, add)

        if not new_image:
            return None  # No image uploaded

        """Delete the old image when replacing it."""
        if not add and new_image:  # If the instance already exists and has a new image
            old_image = getattr(
                model_instance.__class__.objects.filter(pk=model_instance.pk).first(),
                self.attname,
                None,
            )
            new_image.name = self.get_full_image_url(new_image, add=True)

            if old_image and old_image.name != new_image.name:
                self.delete_old_image(old_image)

        return new_image

    def value_from_object(self, instance):
        """Override default behavior to prevent MEDIA_URL from being added incorrectly."""
        image = super().value_from_object(instance)

        if not image:
            return None  # No image uploaded

        if getattr(image, "name") and not image.name.startswith("http"):
            image.name = self.get_full_image_url(image)

        image.preview_url = self.add_preview_url(image.name) or getattr(image, "name")
        return image

    @staticmethod
    def get_cloudinary_public_id(url) -> str | None:
        try:
            path_parsed = urlparse(url)
            if path_parsed.scheme.startswith("http"):
                if "cloudinary.com" in path_parsed.hostname:
                    url_path = path_parsed.path.split("/")
                    public_id = "/".join(url_path[5:])
                    return public_id
        except Exception:
            ...

    def delete_old_image(self, old_image):
        """Delete the old image from the correct storage backend."""
        if not old_image:
            return

        old_image_path = old_image.name  # Path stored in DB

        if public_id := self.get_cloudinary_public_id(old_image_path):
            # Cloudinary delete logic
            print(f"Deleting image from Cloudinary: {str(default_storage)}")
            if "cloudinary" in str(default_storage):
                cloudinary.uploader.destroy(public_id)
        else:
            # Delete from S3 or local storage
            try:
                if default_storage.exists(old_image_path):
                    default_storage.delete(old_image_path)
            except Exception as e:
                print(f"Error deleting image {old_image_path}: {e}")  # Log error


class MultiBackendImageWidget(forms.ClearableFileInput):
    """Custom Widget to display images correctly in Django Admin."""

    def render(self, name, value, attrs=None, renderer=None):
        # Check if the value (image) has a URL
        image_html = ""
        if value and getattr(value, "preview_url"):
            # Create the HTML for the image preview with a custom style
            image_html = format_html(
                '<img src="{}" style="max-height: 150px; max-width: 150px; padding: 5px" /><br>',
                value.preview_url,
            )

            # Call the parent class's render method but we will modify the output to remove the duplicate <a> tag
            file_input_html = super().render(name, value, attrs, renderer)

            # Remove any <a> link if it is already included in the file input HTML to avoid duplication
            if getattr(value, "url"):
                quoted_url = value.url.replace("&", "&amp;")
                file_input_html = file_input_html.replace(
                    f'href="{quoted_url}"', f'href="{value.name}"'
                )

            # Return the image preview HTML + the modified file input HTML (without duplicate link)
            return format_html(f"<div>{image_html}</div><div>{file_input_html}</div>")
            # return file_input_html

        # Return the standard render for non-image fields
        return super().render(name, value, attrs, renderer)


class MultiBackendImageFormField(forms.ImageField):
    """Custom Form Field to use the custom widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = MultiBackendImageWidget()


class UniversalImageMixin(models.Model):
    """Mixin that automatically converts ImageField values to full URLs after saving."""

    class Meta:
        abstract = True  # Prevents Django from creating a separate table for the mixin.

    def get_full_image_url(self, image_field):
        """Returns the full URL of the given ImageField."""

        if not image_field or not image_field.name:
            return None  # Return None instead of MEDIA_URL + empty path

        image_name = image_field.name  # Get the stored path/filename
        default_file_storage = settings.STORAGES["default"]["BACKEND"]

        if default_file_storage == "storages.backends.s3boto3.S3Boto3Storage":
            return f"{settings.AWS_S3_ENDPOINT_URL}/{image_name}"
        elif "cloudinary" in default_file_storage:
            return image_field.url  # Cloudinary automatically provides a full URL
        else:
            return f"{settings.MEDIA_URL}{image_name}"

    def save(self, *args, **kwargs):
        """Override save() to update all ImageField URLs."""
        super().save(*args, **kwargs)

        update_fields = {}
        for field in self._meta.fields:
            if isinstance(field, models.ImageField):
                image = getattr(self, field.name)  # Get field value
                if image:
                    update_fields[field.name] = self.get_full_image_url(image)

        if update_fields:
            self.__class__.objects.filter(pk=self.pk).update(**update_fields)
