import os
import unittest
from pathlib import Path
from unittest.mock import patch

from config import parse_image_paths, parse_probability


class TestWelcomeConfig(unittest.TestCase):
    def test_image_paths_are_explicit_and_machine_independent(self) -> None:
        self.assertEqual(
            parse_image_paths(" ./welcome.jpg, /tmp/other.png "),
            [Path("welcome.jpg"), Path("/tmp/other.png")],
        )
        self.assertEqual(parse_image_paths(""), [])

    def test_probability_is_bounded_and_invalid_values_fall_back(self) -> None:
        self.assertEqual(parse_probability("2"), 1.0)
        self.assertEqual(parse_probability("-1"), 0.0)
        self.assertEqual(parse_probability("not-a-number", default=0.25), 0.25)

    def test_environment_configuration_is_read_only(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AMIA_WELCOME_IMAGES": "data/a.jpg,data/b.jpg",
                "AMIA_WELCOME_IMAGE_PROBABILITY": "0.5",
            },
            clear=False,
        ):
            self.assertEqual(
                parse_image_paths(None),
                [Path("data/a.jpg"), Path("data/b.jpg")],
            )
            self.assertEqual(parse_probability(None), 0.5)


if __name__ == "__main__":
    unittest.main()
