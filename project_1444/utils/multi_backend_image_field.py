from django.conf import settings

from django import forms
from django.utils.html import format_html
from django.db import models


class MultiBackendImageField(models.ImageField):
    """Custom ImageField that correctly generates URLs based on storage backend."""

    @staticmethod
    def add_preview_url(url: str, transform: str = None) -> str:
        if r".cloudinary.com/" in url:
            transform = transform or "c_thumb,g_face,h_150,w_150"
            return url.replace("/image/upload/", f"/image/upload/{transform}/")
        return url

    def formfield(self, **kwargs):
        """Use custom form field with an image preview in Django Admin."""
        kwargs["form_class"] = MultiBackendImageFormField
        return super().formfield(**kwargs)

    def get_full_image_url(self, image):
        if not image:
            return None  # No image uploaded

        image_name = image.name  # File path stored in DB
        if image_name and image_name.startswith("http"):
            return image_name

        default_file_storage = settings.STORAGES["default"]["BACKEND"]

        # Generate full URL based on storage backend
        if default_file_storage == "storages.backends.s3boto3.S3Boto3Storage":
            full_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{image_name}"
        elif "cloudinary" in default_file_storage:
            full_url = image.url  # Cloudinary full URL
        else:
            full_url = f"{settings.MEDIA_URL}{image_name}"  # Local storage

        return full_url  # Store full URL in the database

    def pre_save(self, model_instance, add):
        """Override pre_save to store the full URL in the database."""
        image = super().pre_save(model_instance, add)

        if not image:
            return None  # No image uploaded
        image.name = self.get_full_image_url(image)

        return image

    def value_from_object(self, instance):
        """Override default behavior to prevent MEDIA_URL from being added incorrectly."""
        image = super().value_from_object(instance)

        if not image:
            return None  # No image uploaded

        if image.name and not image.name.startswith("http"):
            image.name = self.get_full_image_url(image)
        image.preview_url = self.add_preview_url(image.name)
        return image


class MultiBackendImageWidget(forms.ClearableFileInput):
    """Custom Widget to display images correctly in Django Admin."""

    def render(self, name, value, attrs=None, renderer=None):
        # Check if the value (image) has a URL
        image_html = ""
        if value and hasattr(value, "preview_url"):
            # Create the HTML for the image preview with a custom style
            image_html = format_html(
                '<img src="{}" style="max-height: 150px; max-width: 150px; padding: 5px" /><br>',
                value.preview_url,
            )

            # Call the parent class's render method but we will modify the output to remove the duplicate <a> tag
            file_input_html = super().render(name, value, attrs, renderer)

            # Remove any <a> link if it is already included in the file input HTML to avoid duplication
            file_input_html = file_input_html.replace(
                f'href="{value.url}"', f'href="{value.name}"'
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
