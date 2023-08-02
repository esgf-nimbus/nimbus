#!/bin/bash

jupyter nbconvert --execute --to notebook --stdout /notebooks/intro.ipynb.tpl > /notebooks/intro.ipynb
