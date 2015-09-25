import sys
import unittest

sys.path.insert(0, ".")
from coalib.results.result_actions.ShowPatchAction import ShowPatchAction
from coalib.misc.ContextManagers import retrieve_stdout
from coalib.settings.Section import Section
from coalib.results.Result import Result
from coalib.results.Diff import Diff


class ShowPatchActionTest(unittest.TestCase):
    def setUp(self):
        self.uut = ShowPatchAction()
        diff_dict = {"a": Diff(), "b": Diff()}
        diff_dict["a"].add_lines(1, ["test\n"])
        diff_dict["a"].delete_line(3)
        diff_dict["b"].add_lines(0, ["first\n"])

        self.file_dict = {"a": ["a\n", "b\n", "c\n"], "b": ["old_first\n"]}
        self.test_result = Result("origin", "message", diffs=diff_dict)

    def test_is_applicable(self):
        self.assertFalse(self.uut.is_applicable(1))
        self.assertFalse(self.uut.is_applicable(Result("o", "m")))
        self.assertTrue(self.uut.is_applicable(self.test_result))

    def test_apply(self):
        with retrieve_stdout() as stdout:
            self.assertEqual(self.uut.apply_from_section(self.test_result,
                                                         self.file_dict,
                                                         {},
                                                         Section("name")),
                             {})
            self.assertEqual(stdout.getvalue(),
                             "|    |    | --- a\n"
                             "|    |    | +++ a\n"
                             "|   1|   1| a\n"
                             "|    |   2|+test\n"
                             "|   2|   3| b\n"
                             "|   3|    |-c\n"
                             "|    |    | --- b\n"
                             "|    |    | +++ b\n"
                             "|    |   1|+first\n"
                             "|   1|   2| old_first\n")

    def test_apply_with_previous_patches(self):
        with retrieve_stdout() as stdout:
            previous_diffs = {"a": Diff()}
            previous_diffs["a"].change_line(2, "b\n", "b_changed\n")
            self.assertEqual(self.uut.apply_from_section(self.test_result,
                                                         self.file_dict,
                                                         previous_diffs,
                                                         Section("name")),
                             previous_diffs)
            self.assertEqual(stdout.getvalue(),
                             "|    |    | --- a\n"
                             "|    |    | +++ a\n"
                             "|   1|   1| a\n"
                             "|    |   2|+test\n"
                             "|   2|   3| b_changed\n"
                             "|   3|    |-c\n"
                             "|    |    | --- b\n"
                             "|    |    | +++ b\n"
                             "|    |   1|+first\n"
                             "|   1|   2| old_first\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)
