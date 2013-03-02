import unittest
from yay import parser
from yay.ast import *

import os

def parse(value):
    return parser.parse(value, debug=0) 

class TestParser(unittest.TestCase):
    
    def test_include(self):
        res = parse("""
        % include 'foo.yay'
        """)
        self.assertEqual(res, Include(Literal('foo.yay')))
    
    def test_set_integer_literal(self):
        res = parse("""
        % set a = 2
        """)
        self.assertEqual(res, Set('a', Literal(2)))
        
    def test_set_string_literal(self):
        res = parse("""
        % set a = 'foo'
        """)
        self.assertEqual(res, Set('a', Literal("foo")))
        
    def test_set_string_arithmetic(self):
        res = parse("""
        % set a = 'foo ' + 'bar'
        """)
        self.assertEqual(res, Set('a', Expr(Literal('foo '), Literal('bar'), '+')))
                
    def test_set_float_literal(self):
        res = parse("""
        % set a = 2.4
        """)
        self.assertEqual(res, Set('a', Literal(2.4)))
        
    def test_set_identifier(self):
        res = parse("""
        % set a = b
        """)
        self.assertEqual(res, Set('a', Identifier('b')))
    
    def test_set_addition(self):
        res = parse("""
        % set a = 2+2
        """)
        self.assertEqual(res, Set('a', Expr(Literal(2), Literal(2), '+')))
        
    def test_set_complex_expr(self):
        res = parse("""
        % set a = (2+2)*5/12.0
        """)
        self.assertEqual(res, Set('a', 
            Expr(
                Expr(
                    ParentForm(
                            Expr(Literal(2), Literal(2), '+'),
                        ),
                    Literal(5),
                    '*'),
                Literal(12.0),
                '/')
            ))
        
    def test_set_list(self):
        res = parse("""
        % set a = [1,2,3,4]
        """)
        self.assertEqual(res, Set('a', ListDisplay(ExpressionList(*map(Literal, [1,2,3,4])))))
    
    def test_set_dict(self):
        res = parse("""
        % set a = {'b': 4, 'c': 5}
        """)
        self.assertEqual(res, Set('a', DictDisplay(
            KeyDatumList(
                KeyDatum(Literal('b'),
                         Literal(4)),
                KeyDatum(Literal('c'),
                         Literal(5))
                )
            )))
        
    def test_set_attributeref(self):
        res = parse("""
        % set a = b.c
        """)
        self.assertEqual(res, Set('a', 
                                  AttributeRef(
                                      Identifier('b'), 
                                      Identifier('c'))))
        
    def test_set_subscription(self):
        res = parse("""
        % set a = b[1]
        """)
        self.assertEqual(res, Set('a', 
                                  Subscription(
                                      Identifier('b'), 
                                          Literal(1)
                                          )))
    
    def test_set_slice(self):
        res = parse("""
        % set a = b[1:2]
        """)
        self.assertEqual(res, Set('a', 
                                  SimpleSlicing(
                                      Identifier('b'), 
                                      Slice(
                                          Literal(1),
                                          Literal(2),
                                          ))))
                                      
    def test_set_extended_slice(self):
        res = parse("""
        % set a = b[1:2:3]
        """)
        self.assertEqual(res, Set('a', 
                                  ExtendedSlicing(
                                      Identifier('b'), 
                                      SliceList(
                                      Slice(
                                          Literal(1),
                                          Literal(2),
                                          Literal(3),
                                          )))))
        
    def test_set_call(self):
        res = parse("""
        % set a = func()
        """)
        self.assertEqual(res, Set('a',
            Call(Identifier('func'))))
        
    def test_set_parentheses(self):
        res = parse("""
        % set a = (1,2,3)
        """)
        self.assertEqual(res, Set('a',
            ParentForm(ExpressionList(Literal(1), Literal(2), Literal(3)))))
        
    def test_set_parentheses_empty(self):
        res = parse("""
        % set a = ()
        """)
        self.assertEqual(res, Set('a', ParentForm()))
        
    def test_set_not(self):
        res = parse("""
        % set a = not b
        """)
        self.assertEqual(res, Set('a', Not(Identifier('b'))))
        
    def test_for(self):
        res = parse("""
        % for a in b
             - x
        """)
        self.assertEqual(res, For('a', Identifier('b'), YayList(YayScalar('x'))))
        
    def test_set_call_args_simple(self):
        res = parse("""
        % set a = func(4)
        """)
        self.assertEqual(res, Set('a',
            Call(Identifier('func'), 
                 ArgumentList(PositionalArguments(Literal(4))))))
        
    def test_set_call_args_many(self):
        res = parse("""
        % set a = func(4, a, foo='bar', baz='quux')
        """)
        self.assertEqual(res, Set('a',
            Call(Identifier('func'), 
                 ArgumentList(
                     PositionalArguments(
                         Literal(4),
                         Identifier('a'),
                         ),
                     KeywordArguments(
                         KeywordItem('foo', Literal('bar')),
                         KeywordItem('baz', Literal('quux')),
                         ),
                     ))))
       
    def test_emptydict(self):
        res = parse("""
            a: {}
        """)
        self.assertEqual(res, YayDict([('a', YayDict())]))
        
    def test_emptylist(self):
        res = parse("""
            a: []
        """)
        self.assertEqual(res, YayDict([('a', YayList())]))
        
    def test_simple_dict(self):
        res = parse("""
            a: b
        """)
        self.assertEqual(res, YayDict([('a', YayScalar('b'))]))
        
    def test_two_item_dict(self):
        res = parse("""
        a: b
        c: d
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', YayScalar('d')),
        ]))
    
    def test_command_and_dict(self):
        res = parse("""
        % include 'foo.yay'
        
        a: b
        """)
        self.assertEqual(res, Stanzas(
            Include(Literal('foo.yay')), 
            YayDict([('a', YayScalar('b'))])))
        
    def test_nested_dict(self):
        res = parse("""
        a:
            b: c
        """)
        self.assertEqual(res, YayDict([
            ('a', YayDict([
                ('b', YayScalar('c'))
            ]))
        ]))
    
    def test_sample1(self):
        res = parse("""
        key1: value1
        
        key2: value2
        
        key3: 
          - item1
          - item2
          - item3
          
        key4:
            key5:
                key6: key7
        """)
        self.assertEqual(res, YayDict([
            ('key1', YayScalar('value1')),
            ('key2', YayScalar('value2')),
            ('key3', YayList(YayScalar('item1'), YayScalar('item2'), YayScalar('item3'))),
            ('key4', YayDict([
                ('key5', YayDict([
                    ('key6', YayScalar('key7')),
                ]))
            ])),
            ]))
        print res

    def test_list_of_dicts(self):
        res = parse("""
            a: 
              - b
              - c: d
              - e
              """)
        self.assertEqual(res, YayDict([
            ('a', YayList(YayScalar('b'), 
                          YayDict([
                              ('c', YayScalar('d'))
                              ]), 
                          YayScalar('e')
                          ))
            ]))

    def test_template_1(self):
        res = parse("""
        a: b
        c: {{a}}
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', Template(Identifier('a'))),
        ]))
        
    def test_template_2(self):
        res = parse("""
        a: b
        c: hello {{a}}
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', YayMerged(YayScalar('hello '), Template(Identifier('a')))),
        ]))

    def test_template_3(self):
        res = parse("""
        a:b
        c: {{a}} hello
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', YayMerged(Template(Identifier('a')), YayScalar(' hello'))),
        ]))
        
    def test_template_4(self):
        res = parse("""
        a:b
        c: woo {{a}} hello
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', YayMerged(YayScalar('woo '), Template(Identifier('a')), YayScalar(' hello'))),
        ]))
        
    def test_template_5(self):
        res = parse("""
        a:b
        c: {{"this " + a + " that"}}
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', Template(Expr(Expr(Literal('this '), Identifier('a'), '+'), Literal(" that"), "+")))
        ]))
        
    def test_template_6(self):
        res = parse("""
        a:b
        c: {{1.0 + 2}}
        """)
        self.assertEqual(res, YayDict([
            ('a', YayScalar('b')),
            ('c', Template(Expr(Literal(1.0), Literal(2), "+")))
        ]))
    
    def test_list_of_complex_dicts(self):
        res = parse("""
            a:
              - b
              - c:
                - e
                - f
            """)
        self.assertEqual(res, YayDict([
            ('a', YayList(
                YayScalar('b'), 
                YayDict([('c', YayList(
                    YayScalar('e'), 
                    YayScalar('f')
                ))])))]))
        self.assertEqual(res.resolve(), {
            'a': [
                'b',
                {'c': ['e', 'f']},
                ]
            })
        
    def test_list_of_multikey_dicts(self):
        res = parse("""
            a: 
              - b
              - c: d
                e: f
              - g
              """)
        self.assertEqual(res, YayDict([
            ('a', YayList(YayScalar('b'), YayDict([
                ('c', YayScalar('d')), 
                ('e', YayScalar('f'))
                ]), YayScalar('g')))
        ]))

    def test_list_of_dicts_with_lists_in(self):
        res = parse("""
            a:
             - b: c
               d:
                 - e
                 - f
                 - g
              """)
        self.assertEqual(res, YayDict([
            ('a', YayList(YayDict([
                ('b', YayScalar('c')), 
                ('d', YayList(YayScalar('e'), YayScalar('f'), YayScalar('g')))
            ])))
            ]))
        self.assertEqual(res.resolve(), {'a': [
            {'b': 'c',
             'd': ['e', 'f', 'g'],
             }]})

    def test_simple_overlay(self):
        res = parse("""
        foo: 
          a: b
          
        foo:
          c: d
        """)
        self.assertEqual(res, YayDict([
            ('foo', YayDict([('a', YayScalar('b'))])),
            ('foo', YayDict([('c', YayScalar('d'))])),
            ]))
        self.assertEqual(res.resolve(), {
            'foo': {
                'c': 'd',
                }})

    def test_mix(self):
        res = parse("""
        % include 'foo.yay'
        
        bar:
            % set a = 2
            % for x in range(a)
                - {{x}}

        quux:
            - a
            - b
        """)
        self.assertEqual(res, Stanzas(
            Include(Literal('foo.yay')),
            YayDict([
                ('bar', Directives(
                Set('a', Literal(2)),
                For('x', Call(Identifier('range'), ArgumentList(
                    PositionalArguments(Identifier('a')))
                              ), YayList(Template(Identifier('x'))))
                )),
                ('quux', YayList(YayScalar('a'), YayScalar('b')))
                ]),
        ))
        