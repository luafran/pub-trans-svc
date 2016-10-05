import os
import setuptools
from pip.download import PipSession
from pip.req import parse_requirements

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))

# parse_requirements() returns generator of pip.req.InstallRequirement objects
PACKAGE_REQS = parse_requirements("requirements.txt", session=PipSession())

# reqs is a list of requirement
# e.g. ['tornado==3.2.2', '...']
REQS = [str(ir.req) for ir in PACKAGE_REQS]

if __name__ == "__main__":
    setuptools.setup(
        name="pubtrans",
        version="0.0.1",
        description="Media Location Information Service",
        author="Luciano Afranllie",
        namespace_packages=['pubtrans'],
        packages=setuptools.find_packages(PACKAGE_PATH, exclude=["*.test",
                                                                 "*.test.*",
                                                                 "test.*",
                                                                 "test"]),
        keywords="pubtrans",
        install_requires=REQS,
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'pubtrans-runservice = pubtrans.common.runservice:main'
            ],
            'pubtrans.services': [
                'service1 = '
                    'pubtrans.service1_command:Service1Command',
            ],
            'pubtrans.health.plugins': [
            ],
        },
    )
