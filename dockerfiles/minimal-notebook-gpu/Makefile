.DEFAULT_GOAL = build

VERSION = 0.1.2

build: ARGS = --build-arg TAG=$(shell tbump -C ../minimal-notebook current-version)

run: ARGS = -p 8888:8888

include ../Makefile
