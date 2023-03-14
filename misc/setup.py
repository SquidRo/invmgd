import os, subprocess
from setuptools import setup, find_packages

here = os.path.dirname(os.path.realpath(__file__))
wdir = here #os.path.join(here, 'my_gnmi_server')
desc_str=''
if os.path.exists(wdir):
    git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=wdir)

    # use the git hash in the setup
    desc_str = 'git hash [ %s ]' % git_hash.strip()

dependencies = [
]

app_name = 'invmgd'

setup(
    name=app_name,
    install_requires=dependencies,
    version='0.1',
    description=desc_str,
    packages=find_packages(),
    license='Apache 2.0',
    author='',
    author_email='',
    entry_points={
        'console_scripts': [
            '{} = {}.{}:main'.format(app_name, app_name, app_name)
        ]
    },
    data_files = [
        ('/etc/systemd/system/', [app_name + '.service']),
        ('/etc/' + app_name + '/', ['config.ini'])
    ],
    maintainer='',
    maintainer_email='',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Linux',
        'Programming Language :: Python',
    ],

)
