# Dummy Agent App

This is a tiny test project for the local agent dev stack.

Current scope:

- a small todo CLI
- file-backed task storage
- tests for add, list, and done flows

## Running the CLI

To add an item:

```sh
python todo.py add "Buy groceries"
```

To list items:

```sh
python todo.py list
```

To mark an item complete:

```sh
python todo.py done 1
```

For more information on available commands, use:

```sh
python todo.py --help
```

## Running Tests

To run the tests, execute the following command in the project root:

```sh
python3 -m unittest -v
```
