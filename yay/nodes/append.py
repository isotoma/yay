# Copyright 2010-2011 Isotoma Limited
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

from yay.nodes import Node, Boxed, Sequence

class Append(Node):

    def get(self, idx, default=None):
        return Boxed(self.resolve()[int(idx)])

    def semi_resolve(self):
        if not self.chain:
            return self.value
        return Sequence(list(iter(self.chain.semi_resolve())) + list(iter(self.value.semi_resolve())))

    def resolve(self):
        return self.semi_resolve().resolve()

    def walk(self):
        yield self.chain
        yield self.value

    def clone(self):
        a = Append(self.value.clone())
        a.chain = self.chain.clone() if self.chain else None
        return a

