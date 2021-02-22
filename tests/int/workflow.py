"""
A test use only library that makes some functional programming techniques much
easier via composition, currying, and more. It was primarily created to
allow easier file and IO process creation from smaller building blocks, and to
quickly iterate on these.
"""


def partial(f):
    """
    Create a function that can be partially applied similar to currying.

    Note that different from currying, this function object must be partially
    applied exactly once, even if all the arguments are given, or it has no
    arguments at all.

    This can be used as a decorator as well.

    Args:
        f: The function to transform into a partially applied function object.

    Returns:
        The transformed function which must be partially applied at least once.
    """
    def c(*args, **kwargs):
        def inner(*other_args, **other_kwargs):
            return f(*args, *other_args, **kwargs, **other_kwargs)

        return inner

    return c


def sink():
    """
    Returns a function that does not do or return anything.

    Returns:
        The empty function object.
    """
    def f():
        pass

    return f


def value(v):
    """
    Creates a function that returns the given value, and takes no args.

    Args:
        v: The value to return.

    Returns:
        The function that returns the provided value.
    """
    return lambda: v


def conditional(cond, t, f):
    """
    Creates a function that will conditionally run and return the second
    parameter, and otherwise run the third parameter.

    Args:
        cond: The function that needs to be evaluated.
        t: The function which is run and whose result is returned on True.
        f: The function which is run and whose result is returned on False.

    Returns:
        The result of running the provided functions conditioned on the result
        of cond.
    """
    def func():
        if cond():
            return t()
        else:
            return f()

    return func


def sequence(*args):
    """
    A sequence of functions that are called in order, with the last function
    result being returned.

    Args:
        args: A sequence of the functions to call in order.

    Returns:
        A function that calls the provided functions in order.
    """
    def func():
        for arg in args[:-1]:
            arg()

        return args[-1]()

    return func


def pipe(*args):
    """
    Creates a function where the results of one function are given to the next.

    Args:
        args: A sequence of the functions, whose results will be the parameters
            to the next.

    Returns:
        A function that returns the result of composition between the provided
        functions in order.
    """
    def func():
        r = None
        if len(args) > 0:
            r = args[0]()

        for arg in args[1:]:
            r = arg(r)

        return r

    return func


def fail(s):
    """
    A function that should fail out of the execution with a RuntimeError and the
    provided message.

    Args:
        s: The message to put into the error.

    Returns:
        A function object that throws an error when run.
    """
    def func():
        raise RuntimeError(s)

    return func
