# Test Do It!
![PlsNoSueLookAtFileName](https://github.com/edolfo/TestDoIt/blob/master/obvSatire.png)

### Abstract
Test Do It is a simple library to easily add and maintain unit tests,
right inside the source file.  The aim is to incentivise engineers to
add more test coverage, *with minimal additional effort* on their part.

### Motivation

My own development workflow (after design) goes something like this:

1. Start writing functionality
2. Refine function, start testing
3. Iterate on function to fix bugs, add more needed functionality, and,
if the function is large enough, some small refactorings for ease of 
readability.
4. Think through the sorts of inputs to my function, and the structure
and contents of the function's output.
5. GOTO 3 until satisfied
6. Succumb to deadline pressure/lack of motivation/tiredness, and skip
writing the tests

Through conversations with others, I know that I'm not so special that
this workflow is unique to myself - in fact, most other engineers report
something similar, if not downright exact.  Furthermore, we all generally
agree that this is a Bad Way of doing things!  The tests are never
written, and although the software works when we wrote it,
it may end up breaking later.  Ok, who am I kidding?  It almost certainly
ends up breaking later, either through increased scope of requirements,
or unexpected edge cases.

This library is an attempt to get the tests written during step (4) of
the above development process.

### Installation
No wheel/egg/rpm/binary/toaster firmware/etc. yet, so it's assumed that you Know What You're Doing.

### Quickstart

Here's a stupid function, meant only for illustrative purposes:

```python
def adder(a, b):
    return a + b
```

OK, easy enough.  When writing this, as a first pass I might have
thought that I want this to work on numbers: negative numbers,
zero, and floating point numbers.  But I'm too lazy/unmotivated/etc.
to write out these test cases.  So I might try testing it in the REPL,
and then on success, be done with it.

Here's how I might use Test Do It:

```python
# main.py
from testdoit import testdoit

inputs = [
    [0, 0],
    [1, 1],
    [-1, 2]
]
expected_outputs = [0, 2, 1]


@testdoit(inputs, expected_outputs)
def adder(a, b):
    return a + b


if __name__ == '__main__':
    answer = adder(1, 1)
    print(f'One plus one equals {answer}')
```

Here the parameters to the decorator are written above the decorator, but 
we could have just as well written them inline:

```python
# ...
@testdoit([[0, 0],[1, 1],[-1, 2]], [0, 2, 1])
def adder(a, b):
    return a + b
# ...
```

Now when we run our script `main.py`, Test Do It will generate three
unit tests (for each of our three input/output pairs) and write to a
file.  Here's an excerpt of some generated  output:

```python
# ...
    def test_adder_0(self):
        self.assertEqual(main.adder(0,0), 0)



    def test_adder_1(self):
        self.assertEqual(main.adder(1,1), 2)



    def test_adder_2(self):
        self.assertEqual(main.adder(-1,2), 1)
# ...
```

Running the generated file yields the following:

```fish
'->$ python3 test_main_adder.py
...
----------------------------------------------------------------------
Ran 3 tests in 0.014s

OK
```
Hooray!  We now have some automatically generated tests, with very
minimal effort on our part.  If we ever need to update the tests in
any way (add/remove/modify), we need only update the inputs and outputs
in the decorator right above the function definition and re-run our
script.

### Slowstart

OK, maybe a bit of a misnomer, but consider this some more detailled
documentation of Test Do It.

Test Do It is designed with the following goals in mind:
* Ease of adoption (i.e. low barrier to usage)
* Ease of maintenance
* Ease of integration with existing toolchains
* Improved test coverage

(Not necessarily in that order)

To that end, Test Do It only requires a function to decorate (the function you want to test),
a set of inputs, and a set of expected outputs.  These sets of inputs and outputs can be
lists or tuples - in the future, dictionaries will be used to specify named parameters.  

##### Inputs and outputs
The sets can be of size `[1, n]`, and only require that they can be string-serializable 
and of the same size, e.g. `len(inputs) == len(expected_outputs)`.  If you don't know what it means
to be string-serializable, you probably don't need to worry about it.

Test Do It will generate as many test cases as there are input/output pairs.

##### Detailed examples
We'll walk through a few detailed examples, and provide some commentary on them.

```python
@testdoit([], [])
def side_effect():
    a = 'a'
    GLOBAL_VAR = True
    return
```

Since we aren't passing any inputs or expecting any outputs, Test Do It won't write any tests here,
even though the function itself is setting a local variable and a global variable.

```python
@testdoit(1, None)
def no_op(a):
    return
```

Here we have a function that receives one input, does nothing, and returns nothing.  In this 
trivial case, Test Do It will test that the function indeed returns nothing.  Note that Test Do It
requires at least one parameter to generate tests, as it is assumed that functions returning
something are either always returning the same thing (and therefore an automatic test generator
is not required), or are using variables that Test Do It cannot easily access.

```python
@testdoit([(1, 2), (-1, 1), [5, 0]], (3, 0, 5))
def adder(a, b):
    return a + b
```

Here we have a function that takes in more than one input, does some work, and returns a single output.
You'll notice the mixture of tuples and lists - if you have multiple arguments to pass, the only
requirement is that the arguments come in an iterable form.  In general, Test Do It should *just work*.


Next, we have three variations on what is essentially the same function:
```python
@testdoit([[1, 2]], [(2, 1)])
def reverser_1(a, b):
    return (b, a)
    
@testdoit([[1, 2]], [(2, 1)])
def reverser_2(a, b):
    return b, a  # Still a tuple
    
@testdoit([[1, 2]], [[2, 1]])
def reverser_3(a, b):
    return [b, a]
```
In all three cases, we are returning both `b` and `a`, but in various forms,  In both `reverser_1` and
`reverser_2` our function returns a single tuple, and in `reverser_3`, our function retuns a single
list.  Our expected output argument to Test Do It reflects this tuple/list duality, and in fact if
we tell it that we expect a tuple when we get back a list, the test will fail - as it should!


#### Generated files
Because the interface for Test Do It is a decorator, test files will only get generated if your
decorated function is run.  Files get output into the directory from which your main program was
invoked.  As an example, here's some shell output:


**Running within the same directory as `main.py`**
```fish
.-[edolfo@Edolfos-MacBook-Pro:~/personal/TestDoIt]-[21:03:21]
'->$ ls
README.md        __pycache__      main.py          requirements.txt testdoit.py      tests.py
.-[edolfo@Edolfos-MacBook-Pro:~/personal/TestDoIt]-[21:03:22]
'->$ python3 main.py
[2, 1]
.-[edolfo@Edolfos-MacBook-Pro:~/personal/TestDoIt]-[21:03:26]
'->$ ls
README.md             main.py               test_main_reverser.py tests.py
__pycache__           requirements.txt      testdoit.py
.-[edolfo@Edolfos-MacBook-Pro:~/personal/TestDoIt]-[21:03:27]
'->$
```

**Running outside of the `main.py` directory**
```fish
.-[edolfo@Edolfos-MacBook-Pro:~/personal]-[21:05:18]
'->$ ls TestDoIt/
README.md        __pycache__      main.py          requirements.txt testdoit.py      tests.py
.-[edolfo@Edolfos-MacBook-Pro:~/personal]-[21:05:20]
'->$ python3 TestDoIt/main.py
[2, 1]
.-[edolfo@Edolfos-MacBook-Pro:~/personal]-[21:05:25]
'->$ ls
chome-extensions            fallout_4_classical.mp3     split-transients.py
test_main_reverser.py       TestDoIt
.-[edolfo@Edolfos-MacBook-Pro:~/personal]-[21:05:27]
```

OK, I may (or may not) have selectively censored the items I don't want you to see, and purposely 
left in the items I want you to see.  My trickery for personal optics is beside the point - the 
point is to illustrate where the generated file is saved!


#### Generated naming
Generated files are named according to the file name and function they are testing, in the format of
`test_<module_name>_<function_name>.py`

##### Errors
Any errors that Test Do It produces will get printed to `stdout`, and are always prefixed with
`testdoit.ERROR_PREFIX`, which, as of this writing, is set to `ERROR_TESTDOIT ::'`.

##### Production
Test Do It will exit early (pass-through) if the `PRODUCTION` environment variable is set to 
a truthy value, thus ensuring that your code won't get weighed down unnecessarily when you don't
care about test generation. 

### Known (assumed?) limitations

If there's a limitation here that doesn't actually exist, let me know and I'll take it off the list.
The points here may simply be present because I haven't personally verified their non-working status.

* Currently Test Do It only supports one file per function
* Only supports functions outside of classes
* No support for named parameters (e.g. `f(arg1='hi', arg2=True)`)
* No support for functions that take no parameters
* No support for functions that throw errors
* Partial pep8 support for generated files

### Roadmap

Yes, this is basically addressing all of the known limitations above

* One generated test file for many tested functions
* Configurable output location
* Support for testing class methods, properties, and objects
* Support for named parameters
* Support for assertions other than `assertEqual()`
* Support for functions that throw errors (e.g. check that a `FileNotFound` error is thrown if the file
cannot be found )
* Full pep8 support for generated files
* Tests.  I know, it's crazy to release a test generator without tests.  However, I am the intended
audience, and as the intended audience, I can verify that the initial release constitutes an MVP.
Take that, imaginary, non-existent, and made-up detractors!
