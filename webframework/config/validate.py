# _*_coding:utf_8 _*_

from schema import Schema, Use, And, Or, Optional, SchemaUnexpectedTypeError, SchemaError
import os.path
import inspect
import pwd

schema = Schema({
    # TODO: validate rules
    },
    ignore_extra_keys=True
)

