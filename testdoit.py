from functools import wraps
import inspect
import os
import uuid

RUN_HASH = uuid.uuid4().hex
ERROR_PREFIX = 'ERROR_TESTDOIT ::'

TEMPLATE_END = """
if __name__ == '__main__':
    unittest.main()
"""


def __gen_fname__(module_name, func_name):
    return f'test_{module_name}_{func_name}.py'


def __gen_start__(cls: str, module: str):
    return f"""#!/usr/bin/env python3
# RUN_HASH={RUN_HASH}
import unittest
import {module}


class {cls}(unittest.TestCase):
"""


def __gen_func__(title: str,
                 modulename: str,
                 funcname: str,
                 iter_num: int,
                 inputs,
                 outputs):
    try:
        iter(inputs)
    except TypeError:
        input_str = str(inputs)
    else:
        input_str = ','.join(map(str, inputs))

    try:
        iter(outputs)
    except TypeError:
        output_str = str(outputs)
    else:
        if isinstance(outputs, list):
            output_str = '['
            output_str += ','.join(map(str, outputs))
            output_str += ']'
        elif isinstance(outputs, tuple):
            output_str = '('
            output_str += ','.join(map(str, outputs))
            output_str += ')'
        else:
            print(f'{ERROR_PREFIX} Unknown iterable type')

    return f"""

    def test_{title}_{iter_num}(self):
        self.assertEqual({modulename}.{funcname}({input_str}), {output_str})

    """


def __is_production__():
    if 'PRODUCTION' in os.environ:
        if os.environ['PRODUCTION']:
            return True
    return False


def __is_testing__():
    for item in inspect.stack():
        if 'unittest' in item.filename:
            return True
    return False


def __get_outfile__(fname):
    f = open(fname, 'r')
    f.readline()  # Ignore /usr/bin/env python3 line
    prev_hash = f.readline().split('=')[1].strip()
    if prev_hash == RUN_HASH:
        return open(fname, 'a')
    return open(fname, 'w')


def __sanitise_args__(args):
    try:
        iter(args)
    except TypeError:
        # Recieved a single input, e.g. 'a'
        return [args]
    else:
        return args


def testdoit(ins, outs):
    # TODO: deal with len(inputs) != len(expected_outputs)
    def _mydecorator(func):

        argspec = inspect.getfullargspec(func)
        parent_args_def = argspec.args

        @wraps(func)
        def __mydecorator(*args, **kwargs):
            # Early exit if we're in production
            if __is_production__():
                return func(*args, **kwargs)

            # Don't generate the tests if we're running tests
            if __is_testing__():
                return func(*args, **kwargs)

            # first item on the stack is this decorator
            # Second item on the stack is the decorated function
            module_name = inspect.getmodulename(inspect.stack()[1].filename)
            func_name = func.__name__
            generated_file_name = __gen_fname__(module_name, func_name)
            outfile = open(generated_file_name, 'w')
            cls = 'test_class'
            template = __gen_start__(cls, module_name)  # TODO: Only add start if it's the first function
            inputs = __sanitise_args__(ins)
            expected_outputs = __sanitise_args__(outs)
            if len(inputs) != len(expected_outputs):
                print(f'{ERROR_PREFIX} len(inputs) != len(expected_outputs) for {module_name}.{func_name}')
                return func(*args, **kwargs)
            for i in range(len(inputs)):
                this_input = inputs[i]
                this_expected_output = expected_outputs[i]
                # Check that the number of inputs given matches the function's signature
                try:
                    iter(this_input)
                except TypeError:
                    if len(parent_args_def) != 1:
                        print(f'{ERROR_PREFIX}: 1 input argument received ({this_input}), {len(parent_args_def)} arguments expected ({parent_args_def})')
                        return
                else:
                    # iterable
                    if len(this_input) != len(parent_args_def):
                        print(f'{ERROR_PREFIX}: {len(this_input)} input arguments received ({this_input}), {len(parent_args_def)} arguments expected ({parent_args_def})')
                        return
                func_str = __gen_func__(title=func_name,
                                        modulename=module_name,
                                        funcname=func_name,
                                        iter_num=i,
                                        inputs=this_input,
                                        outputs=this_expected_output)
                template = f'{template}{func_str}'
            template += TEMPLATE_END  # TODO: Only add end if it's the last function
            outfile.write(template)
            outfile.close()
            res = func(*args, **kwargs)
            return res
        return __mydecorator
    return _mydecorator
