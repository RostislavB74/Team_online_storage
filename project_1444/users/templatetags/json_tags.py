from django import template
import json

register = template.Library()

@register.filter
def jsonify(value):
    return json.dumps(value, ensure_ascii=False)