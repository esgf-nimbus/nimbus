#!/bin/bash

cp /notebooks/*.ipynb ${HOME}

tini -g -- /usr/local/bin/start-notebook.sh
