# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


# NOTE: This class should not be instantiated and its
# ``traverse_and_document_shape`` method called directly. It should be
# inherited from a Documenter class with the appropriate methods
# and attributes.
class ShapeDocumenter(object):
    EVENT_NAME = ''

    def __init__(self, service_name, operation_name, event_emitter):
        self._service_name = service_name
        self._operation_name = operation_name
        self._event_emitter = event_emitter

    def traverse_and_document_shape(self, section, shape, history,
                                    include=None, exclude=None, name=None,
                                    is_required=False):
        """Traverses and documents a shape

        Will take a self class and call its appropriate methods as a shape
        is traversed.

        :param section: The section to document.

        :param history: A list of the names of the shapes that have been
            traversed.

        :type include: Dictionary where keys are parameter names and
            values are the shapes of the parameter names.
        :param include: The parameter shapes to include in the documentation.

        :type exclude: List of the names of the parameters to exclude.
        :param exclude: The names of the parameters to exclude from
            documentation.

        :param name: The name of the shape.

        :param is_required: If the shape is a required member.
        """
        param_type = shape.type_name
        if shape.name in history:
            self.document_recursive_shape(section, shape, name=name)
        else:
            history.append(shape.name)
            is_top_level_param = (len(history) == 2)
            getattr(self, 'document_shape_type_%s' % param_type,
                    self.document_shape_default)(
                        section, shape, history=history, name=name,
                        include=include, exclude=exclude,
                        is_top_level_param=is_top_level_param,
                        is_required=is_required)
            if is_top_level_param:
                self._event_emitter.emit(
                    'docs.%s.%s.%s.%s' % (self.EVENT_NAME,
                                          self._service_name,
                                          self._operation_name,
                                          name),
                    section=section)
            at_overlying_method_section = (len(history) == 1)
            if at_overlying_method_section:
                self._event_emitter.emit(
                    'docs.%s.%s.%s.complete-section' % (self.EVENT_NAME,
                                                        self._service_name,
                                                        self._operation_name),
                    section=section)
            history.pop()
