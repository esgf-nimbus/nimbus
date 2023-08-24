#!/bin/bash

jupyter nbconvert --execute --to notebook --stdout /notebooks/changelog.ipynb.tpl > /notebooks/changelog.ipynb
