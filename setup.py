import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

tests_require = [
    'coverage',
    'pytest-cov',
    'pytest-flakes',
    'pytest-pep8',
    'pytest-asyncio',
    'pytest',
    'sanic',
    'codecov',
]

extras_require = {
    'docs': ['Sphinx'],
    # 'sphinx_rtd_theme',
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = ['pytest-runner']

install_requires = []

about = {'version': '0.4.0', 'description': ''}

with open(
    os.path.join(here, 'sanic_toolbox', '__init__.py'), 'r', encoding='utf-8'
) as f:
    for line in f:
        if line.startswith('__version__'):
            about['version'] = line.strip().split('=')[1].strip(' \'"')
        if line.startswith('__description__'):
            about['description'] = line.strip().split('=')[1].strip(' \'"')

setup(
    name='sanic-toolbox',
    version=about['version'],
    description=about['description'],
    url='https://github.com/vltr/sanic-toolbox',
    download_url='https://github.com/vltr/sanic-toolbox/archive/master.zip',
    author='Richard Kuesters',
    author_email='rkuesters@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='sanic toolbox utils lazy-evaluation productivity',
    packages=find_packages(exclude=['example', 'tests']),
    install_requires=install_requires,
    extras_require=extras_require,
    setup_requires=setup_requires,
    tests_require=tests_require,
    package_data={},
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/vltr/sanic-toolbox/issues',
        'Source': 'https://github.com/vltr/sanic-toolbox',
    },
)
