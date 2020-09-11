from setuptools import setup

setup(
    name='shikyou',
    url='https://github.com/shunjuu/Shikyou',
    author='Kyrielight',
    packages=['shikyou'],
    install_requires=[
        "ayumi @ git+https://github.com/shunjuu/Ayumi",
        "metsuke @ git+https://github.com/shunjuu/Metsuke",
    ],
    version='0.1',
    license='MIT',
    description='Specialized rclone instruciton caller.'
)