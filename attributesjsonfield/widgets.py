from django.forms import (
    MultiWidget,
    TextInput,
    DateInput,
    Select,
    NumberInput,
    DateTimeInput,
)


class AttributesJSONWidget(MultiWidget):
    """ """

    template_name = "attributesjsonfield/widgets/attributesjsonwidget.html"

    def __init__(self, attributes_json=None, attrs=None):
        self.attributes = attributes_json
        widgets = []
        for attribute in self.attributes:
            name = attribute["name"]
            data_type = attribute.get("data_type")
            new_attributes = attrs or {}
            new_attributes.update({"label": attribute["label"]})
            new_attributes.update({"placeholder": attribute["label"]})
            if attribute.get("default"):
                new_attributes.update({"value": attribute.get("default")})
            choices = attribute.get("choices")
            if choices:
                widget = Select(attrs=new_attributes, choices=choices)
            elif attribute.get("data_type"):
                if data_type == "date":
                    widget = DateInput(attrs=new_attributes)
                if data_type == "int":
                    widget = NumberInput(attrs=new_attributes)
                if data_type == "datetime":
                    widget = DateTimeInput(attrs=new_attributes)
            else:
                widget = TextInput(attrs=new_attributes)
            widget.name = name
            widgets.append(widget)
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.get(widget.name) for widget in self.widgets]
        else:
            return [None for _ in self.attributes]

    def get_context(self, name, value, attrs):
        context = super(MultiWidget, self).get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

        # value is a list of values, each one corresponding to a widget in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context["widget"]["attrs"]
        input_type = final_attrs.pop("type", None)
        id_ = final_attrs.get("id")
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            attribute = self.attributes[i]
            attr_name = attribute["name"]
            if input_type is not None:
                widget.input_type = input_type
            widget_name = "%s_%s" % (name, attr_name)
            try:
                individual_value = value[i]
                if isinstance(individual_value, list):
                    widget_value = ", ".join(individual_value)
                else:
                    widget_value = individual_value
            except IndexError:
                widget_value = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs["id"] = "%s_%s" % (id_, attr_name)
            else:
                widget_attrs = final_attrs
            widget_attrs.update({"required": attribute["required"]})
            subwidgets.append(
                widget.get_context(widget_name, widget_value, widget_attrs)["widget"]
            )
        context["widget"]["subwidgets"] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        return [
            widget.value_from_datadict(
                data, files, name + "_%s" % self.attributes[i]["name"]
            )
            for i, widget in enumerate(self.widgets)
        ]

    def value_omitted_from_data(self, data, files, name):
        return all(
            widget.value_omitted_from_data(
                data, files, name + "_%s" % self.attributes[i]["name"]
            )
            for i, widget in enumerate(self.widgets)
        )
