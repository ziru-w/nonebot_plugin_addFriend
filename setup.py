from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nonebot_plugin_addFriend",
    version="2.0.0",
    author="wk",
    description="A plugin based on nonebot2, which is used to process requests to add QQ friends and QQ requests.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ziru-w/nonebot_plugin_addFriend",
    project_urls={
        "Bug Tracker": "https://github.com/ziru-w/nonebot_plugin_addFriend/issues",
    },
    install_requires=['requests==2.27.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["nonebot_plugin_addFriend"],
    python_requires=">=3.7",
    install_requires = [
        'nonebot2>=2.0.0b1'
    ]
)
