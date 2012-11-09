import unittest
from yay import parser

class TestParser(unittest.TestCase):
    
    def _parse(self, value):
        p = parser.Parser()
        p.input(value)
        d = p.parse()
        return d
    
    def _resolve(self, value):
        return self._parse(value).resolve()
    
    def test_emptydict(self):
        self.assertEqual(self._resolve("""
        a: {}
        """), {'a': {}})
        
    def test_emptylist(self):
        self.assertEqual(self._resolve("""
        a: []
        """), {'a': []})
    
    def test_simple_dict(self):
        self.assertEqual(self._resolve("""
        a: b
        """), {'a': 'b'})
        
        
    def test_two_item_dict(self):
        self.assertEqual(self._resolve("""
        a: b
        c: d
        """), {'a': 'b', 'c': 'd'})
        
    def test_nested_dict(self):
        self.assertEqual(self._resolve("""
        a:
         b: c
        """), {'a': {'b': 'c'}})
    
    def test_sample1(self):
        self.assertEqual(self._resolve("""
        key1: value1
        
        key2: value2
        
        key3: 
          - item1
          - item2
          - item3
          
        key4:
            key5:
                key6: key7
        """), {
            'key1': 'value1',
            'key2': 'value2',
            'key3': ['item1', 'item2', 'item3'],
            'key4': {
                'key5': {
                    'key6': 'key7'
                    }
                }
            })

    def test_sample2(self):
        self.assertEqual(self._resolve("""
        key1:
            key2:
                - a
                - b
            key3: c
            key4:
                key5: d
        """), {
            'key1': {
                'key2': ['a', 'b'],
                'key3': 'c',
                'key4': {
                    'key5': 'd'
                    }
                }
            })
    
    def test_list_of_dicts(self):
        self.assertEqual(self._resolve("""
            a: 
              - b
              - c: d
              - e
              """), {
                'a': [
                'b',
                {'c': 'd'},
                'e',
                ]})

    def test_list_of_multikey_dicts(self):
        self.assertEqual(self._resolve("""
            a: 
              - b
              - c: d
                e: f
              - g
              """), {
                'a': [
                'b',
                {'c': 'd', 'e': 'f'},
                'g',
                ]})

    def test_list_of_dicts_with_lists_in(self):
        self.assertEqual(self._resolve("""
            a:
             - b: c
               d:
                 - e
                 - f
                 - g
              """), {'a': [{'b': 'c', 'd': ['e', 'f', 'g']}]})

    def test_simple_overlay(self):
        self.assertEqual(self._resolve("""
        foo: 
          a: b
          
        foo:
          c: d
        """), {
               'foo': {
                   'a': 'b',
                   'c': 'd',
                   }
               })
        