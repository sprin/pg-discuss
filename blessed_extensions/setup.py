from setuptools import setup, find_packages

requires = [
    'Flask-Admin>=1.3.0',
    'Flask-Mail>=0.9.1',
]

if __name__ == '__main__':
    setup(
        name='pg-discuss-blessed-extensions',
        version='1.0',

        description='Blessed extensions for pg-discuss',
        license='MIT',

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
                'blessed_csrf_token = blessed_extensions.csrf_token:CsrfTokenExt',
                'blessed_csrf_header = blessed_extensions.csrf_header:CsrfHeaderExt',
                'blessed_route_list = blessed_extensions.route_list:RouteListExt',
                'blessed_archive_comment_versions = blessed_extensions.archive_comment_versions:ArchiveCommentVersionsExt',
                'blessed_validate_comment_len = blessed_extensions.validate_comment_len:ValidateCommentLen',
                'blessed_unix_time_json_encoder = blessed_extensions.unix_time_json_encoder:UnixTimeJSONEncoder',
                'blessed_isso_client_shim = blessed_extensions.isso_client_shim:IssoClientShim',
                'blessed_cors = blessed_extensions.cors:CorsExt',
                'blessed_capture_author = blessed_extensions.capture_author:CaptureAuthor',
                'blessed_capture_website = blessed_extensions.capture_website:CaptureWebsite',
                'blessed_capture_email = blessed_extensions.capture_email:CaptureEmail',
                'blessed_capture_remote_addr = blessed_extensions.capture_remote_addr:CaptureRemoteAddr',
                'blessed_auth_tkt_identity_policy = blessed_extensions.auth_tkt_identity_policy:AuthTktIdentityPolicy',
                'blessed_persist_comment_info_on_id = blessed_extensions.auth_tkt_identity_policy:PersistCommentInfoOnIdentity',
                'blessed_markdown_renderer = blessed_extensions.markdown_renderer:MarkdownRenderer',
                'blessed_voting = blessed_extensions.voting:Voting',
                'blessed_admin = blessed_extensions.admin:AdminExt',
                'blessed_moderation = blessed_extensions.moderation:ModerationExt',
                'blessed_mod_email = blessed_extensions.mod_email:ModerationEmail',
                'blessed_profiler = blessed_extensions.profiler:ProfilerExt',
            ],
        },

        zip_safe=False,

        install_requires=requires,
    )
