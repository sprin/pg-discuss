from pg_discuss import ext

class NullIdentityPolicy(ext.IdentityPolicy):
    """An `IdentityPolicy` that never returns an identity."""
    def remember(self, request, identity_id, **extras):
        pass

    def get_identity(self, request, **extras):
        return None

    def forget(self, request, **extras):
        pass
