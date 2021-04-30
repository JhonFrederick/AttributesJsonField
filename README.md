# Django AttributesJsonField
[![Any color you like](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Django package that extends the **JsonField** limiting possible keys of the Json.

## Requirements
Python 3.7 or newer with Django >= 2.2 or newer.

## Installation
1. Install using pip.
``` sh 
pip intall git+https://github.com/JhonFrederick/django-attributesjsonfield.git 
```
2. Add `attributesjsonfield` to `settings.INSTALLED_APPS`.

``` python 
INSTALLED_APPS = (
    # ...
    "attributesjsonfield",
    # ...
)
```

## Usage

#### Models
Just add AttributesJSONField to your models like this:

Simple attribute 
``` python
from django.db import models
from attributesjsonfield.models.fields import AttributesJSONField
class MyModel(models.Model):
    simple_attribute_field = AttributesJSONField(
            "format",
            "value",
        ],
    )
```
Complex attribute 
``` python
class MyModel(models.Model):
    complex_attribute_field = AttributesJSONField(
        attributes=[
            {
                "field": "format",
                "required": False,
                "choices": (("pdf", "PDF"), ("word", "word")),
                "verbose_name": "format type", 
            }
        ],
    )
```

For complex attributes, the following keys are accepted:
- "field": Attribute name
- "required": True or False, default is True
- "choices": Limits the input to the particular values specified
- "verbose_name": Human-readable name for the field

## License

Released under [MIT License](LICENSE).