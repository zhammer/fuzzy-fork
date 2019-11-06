# coding: utf-8

from __future__ import unicode_literals

import ctypes
import string

import pytest
from hypothesis import given, note
from hypothesis import strategies as st
from hypothesis import settings

import fuzzy


class PythonSoundex(object):
    # from sglib 5.0.0 https://github.com/seatgeek/sglib-py/commit/a8fddacb09c8a3edfada667f4244521d1dc68f69
    def __init__(self, size):
        self.size = size
        self.map = "01230120022455012623010202"

        self.memoized_outputs = {}

    def __call__(self, s):
        if s in self.memoized_outputs:
            return self.memoized_outputs[s]

        written = 0

        ords = [ord(i) for i in s]
        out = []
        ls = len(s)
        for i in range(0, ls):
            c = ords[i]
            if c >= 97 and c <= 122:
                c = c - 32
            if c >= 65 and c <= 90:
                if written == 0:
                    out.append(chr(c))
                    written = written + 1
                elif self.map[c - 65] != '0' and (written == 1 or
                                                 out[written - 1] != self.map[c - 65]):
                    out.append(self.map[c - 65])
                    written = written + 1
            if written == self.size:
                break

        for i in range(written, self.size):
            out.append('0')

        ret = ''.join(out)
        self.memoized_outputs[s] = ret
        return ret


cython_input_strategy = st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=30)


@given(cython_input_strategy, st.integers(1, 10))
def test_soundex(text, size):
    # copy over original text to make sure soundex doesn't mutate text
    original_text = text[:]

    cython_out = fuzzy.Soundex(size)(text)

    assert text == original_text
    assert cython_out == PythonSoundex(size)(text)


@given(st.lists(cython_input_strategy, min_size=100, max_size=200, unique=True), st.integers(1, 10))
def test_soundex_repeated_uses(texts, size):
    cython_soundex = fuzzy.Soundex(size)
    python_soundex = PythonSoundex(size)

    for text in texts:
        print(text)
        original_text = text[:]

        cython_out = cython_soundex(text)
        assert original_text == text
        assert cython_out == python_soundex(text)

