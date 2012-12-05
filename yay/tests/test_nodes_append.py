# Copyright 2012 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .base import TestCase

class TestAppend(TestCase):

    def test_append_list(self):
        source = """
            foo:
              - 1
              - 9
            foo extend:
              - 8
              - 5
            """
        expected = {
            "foo": [1, 9, 8, 5],
            }

        self.assertResolves(source, expected)

    def test_append_no_predecessor(self):
        source = """
            foo extend:
              - 1
              - 2
              - 3
            """
        self.assertResolves(source, {"foo": [1,2,3]})
