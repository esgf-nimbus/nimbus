{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "5136743c-1bc2-4ded-afbd-c632c1e5ecc4",
   "metadata": {},
   "source": [
    "# Nimbus\n",
    "\n",
    "[Getting Started](https://nimbus6.llnl.gov/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fesgf-nimbus%2Fnimbus-cookbook&urlpath=lab%2Ftree%2Fnimbus-cookbook%2Fnotebooks%2Fintro.ipynb)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "9a032db2-466c-4436-8116-074a754e0544",
   "metadata": {
    "jupyter": {
     "source_hidden": true
    },
    "tags": []
   },
   "outputs": [
    {
     "data": {
      "text/markdown": [
       "# Changelog\n",
       "- Bump minimal-notebook to 0.1.14\n",
       "  - Udpates tbump and adds automation for version bumping\n",
       "  - Updates tbump to bump version in dependent dockerfiles\n",
       "- Revert \"Bump to 0.1.14\"\n",
       "- Bump to 0.1.14\n",
       "  - Adds script to index directories for intake_es\n",
       "  - Updates intake_es\n",
       "- Bump to 0.1.13\n",
       "  - Fixes intake_es catalog\n",
       "  - Fixes logging\n",
       "- Bumps to 0.1.11\n",
       "  - Fixes intake_es and exports base env before intake_es\n",
       "- Bump to 0.1.10\n",
       "  - Adds packages and removes dask-gateway env\n",
       "  - Adds cmip5 catalog\n",
       "  - Fixes es query\n",
       "  - Adds intake_es documentation\n",
       "- Bump to 0.1.9\n",
       "  - Updates minimal-notebook and adds intake_es package\n",
       "- Bump to 0.1.8\n",
       "  - Adds dask-gateway and changelog\n",
       "- Bump to 0.1.7\n",
       "  - Updates dockerfile\n",
       "- Bump to 0.1.6\n",
       "  - Fixes installing kernelspec\n",
       "- Bump to 0.1.5\n",
       "  - Updates tbump\n",
       "  - Updates containers\n",
       "- Bump to 0.1.4\n",
       "  - Removes version\n",
       "  - Updates intro notebook\n",
       "- Bump to 0.1.3\n",
       "  - Adds nbgitpuller\n",
       "  - Updates makefiles\n",
       "- Bump to 0.1.2\n",
       "  - Adds additional programs\n",
       "  - Updates version environment variable\n",
       "- Bump to 0.1.1\n",
       "  - Adds container versioning\n",
       "  - Adds intro.ipynb\n",
       "  - Adds minimal-notebook dockerfile\n",
       "\n"
      ],
      "text/plain": [
       "<IPython.core.display.Markdown object>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from IPython.display import display, Markdown\n",
    "\n",
    "display(Markdown(open('/changelog.md').read()))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "300abd8d-1384-465d-8e8b-43bf166f5171",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
