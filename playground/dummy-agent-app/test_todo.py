import argparse
import io
import unittest
from unittest.mock import patch
from todo import cmd_add, cmd_list, cmd_done, load_items, save_items


class TestTodoCLI(unittest.TestCase):
    @patch('todo.load_items')
    @patch('todo.save_items')
    def test_add(self, mock_save, mock_load):
        mock_load.return_value = []
        cmd_add(argparse.Namespace(title="Buy groceries"))
        mock_save.assert_called_once_with([{'title': 'Buy groceries', 'done': False}])

    @patch('todo.load_items')
    def test_list(self, mock_load):
        mock_load.return_value = [{'title': 'Buy groceries', 'done': False}]
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            cmd_list(argparse.Namespace())
            self.assertIn('1. [ ] Buy groceries', mock_stdout.getvalue())

    @patch('todo.load_items')
    @patch('todo.save_items')
    def test_done(self, mock_save, mock_load):
        mock_load.return_value = [{'title': 'Buy groceries', 'done': False}]
        cmd_done(argparse.Namespace(index=1))
        mock_save.assert_called_once_with([{'title': 'Buy groceries', 'done': True}])

if __name__ == '__main__':
    unittest.main()
