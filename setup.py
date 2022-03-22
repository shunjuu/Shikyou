from setuptools import setup

setup(
    name='shikyou',
    url='https://github.com/shunjuu/Shikyou',
    author='Kyrielight',
    packages=['shikyou'],
    install_requires=[
        "ayumi @ git+https://github.com/shunjuu/Ayumi@master#egg=ayumi",
        "metsuke @ git+https://github.com/shunjuu/Metsuke@master#egg=metsuke",
    ],
    version='0.2',
    license='MIT',
    description='Specialized rclone instruction caller.'
)
