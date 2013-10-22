Duncan - Blind SQL injector skeleton
====================================

```
"I may be blind, but there are some things I still see."
```

This is a skeleton to implement custom blind SQL injection exploits. It implements binary search and supports multi-threading.

You should implement Duncan.decide() for yourself in accordance with the provided comments. In a typical HTTP(S) scenario I prefer [Requests](http://www.python-requests.org/en/latest/), but you can implement your exploit over arbitrary protocol, Duncan only provides some platform (protocol, DBMS, OS ...) independent boiler plate.

Command Line Examples
---------------------

### Basic usage

```
duncan.py --query "select version()"
```

### Streching the window

By default we look for the first 5 characters of the result. You can expand this:

```
duncan.py --query "select version()" --pos-end 10
```

Or you can look up specific parts of the output:

```
duncan.py --query "select version()" --pos-begin 10 --pos-end 20
```

Duncan starts an individual thread for each tested character position, so large windows can result in high load at server side.

### Strictly typed database backends

Like MSSQL:

```
duncan.py --query "select cast(123 as char)"
```

### Limited charset

```
duncan.py --query "SELECT some_hex_value FROM t" --charset 0123456789abcdef
```

Charset characters can be duplicated and be provided in arbitrary order. 

### Custom charset

Only test uppercase letters:

```
duncan.py --query "SELECT some_hex_value FROM t" --ascii-start 64 -ascii-end 91
```

### Further info

```
duncan.py -h
```

```
cat duncan.py
```