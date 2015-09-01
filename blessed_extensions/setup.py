from setuptools import setup, find_packages

setup(
    name='pg-discuss-blessed-extensions',
    version='1.0',

    description='Blessed extensions for pg-discuss',

    author='Steffen Prince',
    author_email='steffen@sprin.io',

    url='https://sprin.io',
    download_url='https://github.com/sprin/pg-discuss',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Intended Audience :: Developers',
                 'Environment :: Web Environment',
                 'Framework :: Flask',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=['pg_discuss.ext',
              ],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'pg_discuss.ext': [
            'blessed_edit_view = blessed_extensions.edit_view:EditViewExt',
            'blessed_delete_view = blessed_extensions.delete_view:DeleteViewExt',
            'blessed_csrf_token = blessed_extensions.csrf_token:CsrfTokenExt',
            'blessed_csrf_header = blessed_extensions.csrf_header:CsrfHeaderExt',
            'blessed_json_mimetype = blessed_extensions.json_mimetype:JsonMimetypeExt',
            'blessed_route_list = blessed_extensions.route_list:RouteListExt',
            'blessed_archive_updates = blessed_extensions.archive_updates:ArchiveUpdatesExt',
            'blessed_validate_comment_len = blessed_extensions.validate_comment_len:ValidateCommentLen',
            'blessed_unix_time_json_encoder = blessed_extensions.json_encoder:UnixTimeJSONEncoder',
            'blessed_iso_date_json_encoder = blessed_extensions.json_encoder:IsoDateJSONEncoder',
            'blessed_smart_unix_time_json_encoder = blessed_extensions.json_encoder:SmartUnixTimeJSONEncoder',
            'blessed_smart_iso_date_json_encoder = blessed_extensions.json_encoder:SmartIsoDateJSONEncoder',
            'blessed_isso_client_shim = blessed_extensions.isso_client_shim:IssoClientShim',
            'blessed_cors = blessed_extensions.cors:CorsExt',
        ],
    },

    zip_safe=False,
)
