#!/usr/bin/env python3

import argparse
import os

from argparse_completion import argparse_completion

def get_completion(argument_parser:argparse.ArgumentParser, completion_shell:str):
    os.environ['_ARGPARSE_COMPLETE'] = completion_shell
    return argparse_completion.get_completion(argument_parser)
