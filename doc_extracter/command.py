# -*- encoding: utf-8 -*-

# @File        :   command.py
# @Time        :   2021/04/16 10:35:15
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   https://stackoverflow.com/questions/46440950/require-and-option-only-if-a-choice-is-made-when-using-click

import click


class OptionRequiredIf(click.Option):
    """
    Option is required if the context has `option` set to `value`
    """

    def __init__(self, *a, **k):
        try:
            option = k.pop('option')
            value  = k.pop('value')
        except KeyError:
            raise(KeyError("OptionRequiredIf needs the option and value "
                           "keywords arguments"))

        click.Option.__init__(self, *a, **k)
        self._option = option
        self._value = value.split(",")

    def full_process_value(self, ctx, value):
        value = super(OptionRequiredIf, self).full_process_value(ctx, value)
        if value is None and ctx.params[self._option] in self._value:
            msg = 'Required if --{}={}'.format(self._option, self._value)
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value
