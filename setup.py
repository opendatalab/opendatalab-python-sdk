import os
import setuptools

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(
    os.path.join(here, "opendatalab", "__version__.py"), "r", encoding="utf-8"
) as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=about["__name__"],
    version=about["__version__"],
    author="Zhang Chaobin",
    author_email="zhangchaobin@sensetime.com",
    description="Python SDK for reading dataset files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.bj.sensetime.com/zhangchaobin/opendatalab-python-sdk",
    project_urls={
        "Bug Tracker": "https://gitlab.bj.sensetime.com/zhangchaobin/opendatalab-python-sdk/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["opendatalab"],
    python_requires=">=3.6",
    install_requires=["requests", "oss2", "Click", "tqdm"],
)
