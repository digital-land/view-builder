from setuptools import setup, find_packages

setup(
    name="view_builder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Click",
        "tqdm",
    ],
    entry_points="""
        [console_scripts]
        view_builder=view_builder.cli:cli
    """,
)
