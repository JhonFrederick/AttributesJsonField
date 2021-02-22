import django
from django.forms import MultiValueField, CharField


from attributesjsonfield.widgets import AttributesJSONWidget


class AttributesJSONField(MultiValueField):
    """ """

    widget = AttributesJSONWidget

    def __init__(self, *args, attributes=None, require_all_fields=False, **kwargs):
        self.attributes = attributes

        self.clean_attributes = []
        if self.attributes:
            for attr in self.attributes:
                is_dict = type(attr) == dict
                field = attr["field"] if is_dict else attr
                if is_dict:
                    label = attr.get("verbose_name", field)
                    required = attr.get("required", True)
                else:
                    label = field
                    required = True
                self.clean_attributes.append(
                    {
                        "field": field,
                        "label": label,
                        "name": field,
                        "choices": attr.get("choices") if is_dict else None,
                        "required": required,
                        "default": attr.get("default") if is_dict else None,
                        "data_type": attr.get("data_type") if is_dict else None,
                    }
                )
        else:
            self.clean_attributes = None
        fields = [
            CharField(
                label=attr["label"],
                initial=attr.get("default"),
                required=attr["required"],
            )
            for attr in self.clean_attributes
        ]
        self.widget = AttributesJSONWidget(attributes_json=self.clean_attributes)
        if django.VERSION >= (3, 1):
            # MultiValueField does not receive as kwargs the encoder or decoder
            kwargs.pop("encoder")
            kwargs.pop("decoder")
        super().__init__(fields=fields, require_all_fields=require_all_fields, **kwargs)

    def compress(self, data_list):
        if data_list:
            data = {}
            for i, attribute in enumerate(self.clean_attributes):
                data[attribute["name"]] = data_list[i]
            return data
        return None
