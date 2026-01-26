# coding=utf-8

import unittest
import os
from subprocess import Popen, PIPE


class TestPep8(unittest.TestCase):
    def test_pep8(self):
        """Test if the code is PEP8 compliant."""

        if not os.environ.get("RUN_PEP8"):
            self.skipTest("PEP8 check disabled (set RUN_PEP8=1 to enable)")

        test_dir = os.path.dirname(os.path.abspath(__file__))
        root = os.path.abspath(os.path.join(test_dir, os.pardir, os.pardir))

        command = ["make", "pep8"]
        output = Popen(command, stdout=PIPE, cwd=root).communicate()[0]

        # make pep8 produces some extra lines by default.
        default_number_lines = 5
        lines = len(output.splitlines()) - default_number_lines

        message = "Hey mate, go back to your keyboard :)"
        self.assertEqual(lines, 0, message)
