"""Label."""

from types import new_class
from typing import List, Optional

import numpy as np


class LabelType(object):
    """Label Type."""

    pass

    def assert_valid(self, value) -> None:
        """Check if label type is valid."""
        raise NotImplementedError()


class Classification(LabelType):
    """Classification label."""

    def __init__(self, n_classes: int, class_names: List[str] = None) -> None:
        """Initialize new instance of classification label.

        Args:
            n_classes: number of classes
            class_names: number of classes
        """
        super().__init__()
        self.n_classes = n_classes
        if class_names is not None:
            assert len(class_names) == n_classes, f"{len(class_names)} vs {n_classes}"
        self._class_names = class_names

    @property
    def class_names(self) -> Optional[List[str]]:
        """Return class names."""
        if hasattr(self, "_class_names"):
            return self._class_names
        elif hasattr(self, "class_name"):
            return self.class_name  # for backward compatibility with saved pickles with a typo
        else:
            return None

    def assert_valid(self, value) -> None:
        """Check if classification label is valid.

        Args:
            value to check
        """
        assert isinstance(value, int)
        assert value >= 0, f"{value} is smaller than 0."
        assert value < self.n_classes, f"{value} is >= to {self.n_classes}."

    def __repr__(self) -> str:
        """Return representation of classification label.

        Returns:
            string representation
        """
        if self.class_names is not None:
            if self.n_classes > 3:
                names = ", ".join(self.class_names[:3]) + "..."
            else:
                names = ", ".join(self.class_names) + "."
        else:
            names = "missing class names"
        return f"{self.n_classes}-classification ({names})"

    def label_stats(self, value):
        """Create label stats."""
        one_hot = np.zeros((self.n_classes,))
        one_hot[value] = 1
        return one_hot

    def value_to_str(self, value):
        """Convert numeric class label to name."""
        if self.class_names is None:
            return str(value)
        return self.class_names[value]


class SemanticSegmentation(Classification):
    """Semantic Segmentation label."""

    def assert_valid(self, value) -> None:
        """Check if a semantic segmentation label is valid.

        Args:
            value: value to be checked
        """
        assert isinstance(value, np.ndarray)
        assert len(value.shape) == 2
        assert (value >= 0).all(), f"{value} is smaller than 0."
        assert (value < self.n_classes).all(), f"{value} is >= to {self.n_classes}."


class Regression(LabelType):
    """Regression label."""

    def __init__(self, min_val=None, max_val=None) -> None:
        """Initialize new instance of regression label.

        Args:
            min_val: minimum value of regression targets
            max_val: maximum value of regression targets
        """
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val

    def assert_valid(self, value):
        """Check if a regression label is valid.

        Args:
            value: value to be checked
        """
        assert isinstance(value, float)
        if self.min_val is not None:
            assert value >= self.min_val
        if self.max_val is not None:
            assert value <= self.max_val


class Detection(LabelType):
    """Detection label."""

    def assert_valid(self, value: List[dict]) -> None:
        """Check if a semantic segmentation label is valid.

        Args:
            value: list of dictionary containing boxes and label
        """
        assert isinstance(value, (list, tuple))
        for box in value:
            assert isinstance(box, dict)
            assert len(box) == 4
            for key in ("xmin", "ymin", "xmax", "ymax"):
                assert key in box
                assert box[key] >= 0
            assert box["xmin"] < box["xmax"]
            assert box["ymin"] < box["ymax"]


class PointAnnotation(LabelType):
    """Point annotation label."""

    def assert_valid(self, value: List[dict]) -> None:
        """Check if a semantic segmentation label is valid.

        Args:
            value: list of dictionary containing boxes and label
        """
        assert isinstance(value, (list, tuple))
        for point in value:
            assert isinstance(point, (list, tuple))
            assert len(point) == 2
            assert tuple(point) >= (0, 0)


class MultiLabelClassification(LabelType):
    """Multi-label classification label."""

    def __init__(self, n_classes, class_names=None) -> None:
        """Initialize new instance of classification label.

        Args:
            n_classes: number of classes
            class_names: number of classes
        """
        super().__init__()
        self.n_classes = n_classes
        if class_names is not None:
            assert len(class_names) == n_classes, f"{len(class_names)} vs {n_classes}"
        self.class_name = class_names

    def assert_valid(self, value) -> None:
        """Check if a semantic segmentation label is valid.

        Args:
            value: list of dictionary containing boxes and label
        """
        assert isinstance(value, np.ndarray)
        assert len(value) == self.n_classes
        assert all(np.unique(value) == [0, 1])

    def label_stats(self, value):
        """Return label stats."""
        return value

    def value_to_str(self, value):
        """Convert numeric class label to name."""
        if self.class_name is None:
            return str(value)
        names = []
        for i, active in enumerate(value):
            if active == 1:
                names.append(self.class_name[i])
        return "\n".join(names)
