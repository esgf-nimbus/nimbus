.DEFAULT_GOAL = build

VERSION = 0.1.0

build: ARGS = --build-arg TAG=$(shell tbump -C ../minimal-notebook current-version)

include ../Makefile
