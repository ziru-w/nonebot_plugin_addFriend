from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nonebot_plugin_addFriend",
    version="1.0.0",
    author="wk",
    description="A plugin based on NoneBot2 to process QQ friends and QQ group join requests.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ziru-w/nonebot_plugin_addFriend",
    project_urls={
        "Bug Tracker": "https://github.com/ziru-w/nonebot_plugin_addFriend/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["nonebot_plugin_addFriend"],
    python_requires=">=3.7",
)
