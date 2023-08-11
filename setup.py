import os

import setuptools

about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))
with open(
    os.path.join(here, "opendatalab", "__version__.py"), "r", encoding="utf-8"
) as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    version=about["__version__"],
    project_urls={
        "Bug Tracker": "https://github.com/opendatalab/opendatalab-python-sdk/issues",
    },
)
