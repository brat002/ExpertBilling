# -*- coding: utf-8 -*-


class UserKwargModelFormMixin(object):
    """
    Generic model form mixin for popping user out of the kwargs and
    attaching it to the instance.
    This mixin must precede forms.ModelForm/forms.Form. The form is not
    expecting these kwargs to be passed in, so they must be popped off before
    anything else is done.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserKwargModelFormMixin, self).__init__(*args, **kwargs)
