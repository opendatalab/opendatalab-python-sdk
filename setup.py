import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opendatalab-python-sdk",
    version="0.0.1",
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
    install_requires=["requests", "oss2"],
)
