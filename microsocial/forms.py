# coding=utf-8
from __future__ import absolute_import
from django import forms


class BootstrapFormMixin(object):
    def __init__(self):
        for field_name, field in self.fields.iteritems():
            if not isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.FileInput)):
                continue
            attrs = field.widget.attrs
        if 'class' in attrs:
            if attrs['class']:
                attrs['class'] += ' '
        else:
            attrs['class'] = ''
        attrs['class'] += 'form-control'