import django
import collections
from copy import copy

if django.VERSION >= (3, 1):
    from django.db.models import JSONField
else:
    from django.contrib.postgres.fields import JSONField

from django.core import exceptions
from django.utils.translation import gettext_lazy as _

from attributesjsonfield.forms import fields as form_fields


class AttributesJSONField(JSONField):
    description = _("Attribute management for JsonField")

    def __init__(
        self,
        attributes=None,
        **kwargs,
    ):
        self.attributes = attributes
        assert (
            self.attributes is not None
        ), "You must provide an attributes kwarg for this field"
        assert type(self.attributes) == list, "You have to pass a list as attributes"

        # All required attributes start with !, for example: !name, !area, !code
        required_attributes = []
        for attr in self.attributes:
            if type(attr) == dict:
                assert (
                    "field" in attr
                ), "If you are passing an attribute as dict you have to pass a 'field' key with the name definition"
                field = attr["field"]
            else:
                field = attr

            if str.startswith(field, "!"):
                required_attributes.append(field.replace("!", ""))

        self.required_attributes = required_attributes
        self._check_attribute_validators()
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        self.field_name = name
        if self.attributes is not None:
            kwargs["attributes"] = self.attributes

        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs["attributes"] = self.attributes
        return super().formfield(
            **{
                "form_class": form_fields.AttributesJSONField,
                **kwargs,
            }
        )

    def _check_attribute_validators(self):
        attributes = self.attributes
        errors = []
        for attr in attributes:
            if type(attr) == dict:
                validators = attr.get("validators", None)
                if validators:
                    for i, validator in enumerate(validators):
                        if not callable(validator):
                            errors.append(
                                "All 'validators' of the attribute '{attr}' of {obj} must be callable. validators[{i}] "
                                "({repr}) isn't a function or instance of a validator class.".format(
                                    attr=self.get_clean_attribute(attr),
                                    obj=self,
                                    i=i,
                                    repr=repr(validator),
                                )
                            )
        if errors:
            raise exceptions.ValidationError(errors)

    def _get_clean_attributes(self):
        attributes = []
        for attr in self.attributes:
            attributes.append(self.get_clean_attribute(attr))
        return attributes

    @classmethod
    def get_clean_attribute(cls, attribute):
        return (
            attribute["field"].replace("!", "")
            if type(attribute) == dict
            else attribute.replace("!", "")
        )

    @classmethod
    def _is_valid_option_of_the_choices(cls, option, choices):
        options = [option[0] for option in choices]
        try:
            options.index(option)
        except ValueError:
            return False
        return True

    def get_attributes(self):
        attributes = []
        for attr in self.attributes:
            attributes.append(attr["field"] if type(attr) == dict else attr)
        return attributes

    def get_full_attributes(self):
        attributes = copy(self.attributes)
        return attributes

    def get_attribute_choices(self, attribute):
        for attr in self.attributes:
            clean_attribute = self.get_clean_attribute(attr)
            if type(attr) == dict and clean_attribute == attribute:
                return attr.get("choices", None)
        return None

    def get_attribute_verbose_name(self, attribute):
        attributes = self.get_full_attributes()
        for attr in attributes:
            clean_attribute = self.get_clean_attribute(attr)
            if type(attr) == dict and clean_attribute == attribute:
                return attr.get("verbose_name", attribute)
        return attribute

    def get_attribute_validators(self, attribute):
        for attr in self.attributes:
            clean_attribute = self.get_clean_attribute(attr)
            if type(attr) == dict and clean_attribute == attribute:
                return attr.get("validators", None)
        return None

    def get_attribute_default(self, attribute):
        for attr in self.attributes:
            if (
                type(attr) == dict
                and self.get_clean_attribute(attr["field"]) == attribute
            ):
                return attr.get("default", None)
        return None

    def validate_field_structure(self, value):
        # Check that value is present in the JSON
        defined_attributes = self.get_attributes()
        keys = list(value or [])

        # Check that provided attributes are not repeated
        repeated_attributes = [
            attr for attr, count in collections.Counter(keys).items() if count > 1
        ]
        if repeated_attributes:
            raise exceptions.ValidationError(
                f"{repeated_attributes} are repeated attributes for {self.name}"
            )

        # Check that no extra field other than the ones defined in self.attributes are stored in the field
        defined_cleaned_attributes = {
            attr.replace("!", "") for attr in defined_attributes
        }
        unsupported_attributes = set(keys) - set(defined_cleaned_attributes)
        if unsupported_attributes:
            raise exceptions.ValidationError(
                f"{unsupported_attributes} are unsupported attributes for {self.name}"
            )

        # Check that all required fields are passed in
        if self.required_attributes not in keys:
            missing_required_fields = set(self.required_attributes) - set(keys)
            if missing_required_fields:
                raise exceptions.ValidationError(
                    f"{missing_required_fields} are required fields for {self.name}"
                )

    def _run_attribute_validators(self, value, validators):
        if value in self.empty_values:
            return

        errors = []
        for v in validators:
            try:
                v(value)
            except exceptions.ValidationError as e:
                if hasattr(e, "code") and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)

    def _validate_field_value(self, value):
        keys = list(value)
        attributes_to_validate = [key for key in keys]
        for attr in attributes_to_validate:
            attr_value = value[attr]
            attr_default = self.get_attribute_default(attr)

            if attr_default:
                attr_value = attr_value or attr_default

            # Check attr validators
            attr_validators = self.get_attribute_validators(attr)
            if attr_validators:
                self._run_attribute_validators(attr_value, attr_validators)

            # Check that all sent fields have the proper option if they have choices in the definition
            attr_choices = self.get_attribute_choices(attr)
            if attr_choices and not self._is_valid_option_of_the_choices(
                attr_value, attr_choices
            ):
                raise exceptions.ValidationError(
                    f"{attr_value} is not a valid option for {attr}, choices are {attr_choices}"
                )

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        self.validate_field_structure(value)
        self._validate_field_value(value)
