import os
import sys
from setuptools import setup, find_packages
import versioneer

# vagrant doesn't appreciate hard-linking
if os.environ.get('USER') == 'vagrant' or os.path.isdir('/vagrant'):
    del os.link

# https://www.pydanny.com/python-dot-py-tricks.html
if sys.argv[-1] == 'test':
    test_requirements = [
        'pytest',
        'coverage',
        'pytest_cov',
    ]
    try:
        modules = map(__import__, test_requirements)
    except ImportError as e:
        err_msg = e.message.replace("No module named ", "")
        msg = "%s is not installed. Install your test requirements." % err_msg
        raise ImportError(msg)
    r = os.system('py.test test -v --cov=cifsdk --cov-fail-under=65')
    if r == 0:
        sys.exit()
    else:
        raise RuntimeError('tests failed')

setup(
    name="cifsdk",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="CIFv3 SDK",
    long_description="Software Development Kit for CIFv3",
    url="https://github.com/csirtgadgets/bearded-avenger-sdk-py",
    license='MPLv2',
    classifiers=[
               "Topic :: System :: Networking",
               "Environment :: Other Environment",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
               "Programming Language :: Python",
               ],
    keywords=['security'],
    author="Wes Young",
    author_email="wes@csirtgadgets.org",
    packages=find_packages(),
    install_requires=[
        'PyYAML>=3.11',
        'prettytable>=0.7.2',
        'pyaml>=15.03.1',
        'pyzmq>=16.0',
        'requests>=2.6.0',
        'urllib3>=1.10.2',
        'csirtg_indicator>=1.0.0,<2.0',
        'msgpack-python>=0.4.8,<0.5.0',
        'ujson'
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
            'cif=cifsdk.client:main',
            'cif-tokens=cifsdk.client.tokens:main',
            'cif-tail=cifsdk.ztail:main'
        ]
    },
)
