import setuptools

setuptools.setup(
    name="django-attributesjsonfield",
    url="https://github.com/JhonFrederick/django-attributesjsonfield",
    download_url="https://github.com/JhonFrederick/django-attributesjsonfield",
    license="MIT",
    author="",
    author_email="",
    keywords="Django JsonField AttributesJSONField",
    description="Additional features for Django JSONField",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=["django>=2.2"],
)
