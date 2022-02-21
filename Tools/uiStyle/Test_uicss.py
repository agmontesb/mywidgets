
import pytest

from . import uicss


class TestSelector:

    def test_compiled_patterns(self):
        pass

    def test_invalid_selector_str(self):
        def helper_f(selector_str):
            sel = uicss.Selector(selector_str)
            assert not sel.is_valid
            assert sel.pattern.startswith('SelectorStrError')
            return sel

        selector_str = '(?#<nav'
        selector = helper_f(selector_str)

        selector_str = 'p, span, dos'
        selector = helper_f(selector_str)

    def test_specifity(self):
        # elemento
        selector_str = 'h1'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 0, 0, 1)

        # seudo elemento
        selector_str = '::after'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 0, 0, 1)

        # class
        selector_str = '.clase'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 0, 1, 0)

        # attribute
        selector_str = '[class]'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 0, 1, 0)

        # pseudo class
        selector_str = ':disabled'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 0, 1, 0)

        # id
        selector_str = '#identifier'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 1, 0, 0)

        # names can contain -
        selector_str = 'h1 + p::first-letter'
        selector = uicss.Selector(selector_str)
        assert selector.specificity == (0, 0, 0, 3)

        #TODO: Investigar porque el ] desaparece en el split innicial
        # selector_str = 'li > a[href*="en-US"] > .inline-warning'
        # selector = uicss.Selector(selector_str)
        # assert selector.specificity == (0, 0, 2, 2)

