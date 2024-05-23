from django import template
import json

register = template.Library()

@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)

@register.simple_tag
def call_method_json(obj, method_name, json_str):
    method = getattr(obj, method_name)
    return method(**json.loads(json_str))