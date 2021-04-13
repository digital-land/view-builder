from setuptools import setup

setup(
    name="view_builder",
    version="0.1",
    packages=["view_builder"],
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        view_builder=view_builder.cli:cli
    """,
)
