"""Compatibility entry point for the consolidated welcome plugin.

The maintained implementation lives in ``src.plugins.welcome``.  This
wrapper keeps the cloned plugin directory loadable without registering a
second notice handler or using the obsolete D:\\HongXingBot image path.
"""

from src.plugins.welcome import handle_member_notice, member_handler

__all__ = ["handle_member_notice", "member_handler"]
