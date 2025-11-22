import numpy as np
import pytest

from doxy2mdx import cat


def test_cat():
    assert np.equal([1, 2, 3, 4], cat([1, 2], [3, 4])).all()

