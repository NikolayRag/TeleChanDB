from setuptools import setup, find_packages

setup(
    name='TeleChanDB',
    version='0.1a',
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI>=4.0.0',
    ],
    author='Nikolay Ragozin',
    author_email='thenickra@gmail.com',
    description='A basic Database over Telegram channel',
    url='https://github.com/nikolayrag/TeleChanDB',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
