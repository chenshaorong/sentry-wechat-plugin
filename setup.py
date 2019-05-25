# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry-wechat-plugin",
    version='1.3',
    author='shaorong.chen',
    author_email='shaorong.chen@aliyun.com',
    url='https://github.com/chenshaorong/sentry-wechat-plugin',
    description='A Sentry extension which send errors stats to WeChat.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry wechat',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'sentry>=9.0.0',
        'requests',
        'pytz',
        'django',
    ],
    entry_points={
        'sentry.plugins': [
            'wechat = wechat.plugin:WeChatPlugin'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ]
)
