#! /usr/bin/env python3
from invoke import Program


def main():
    program = Program(version="0.2.0", name="do")
    program.run()
