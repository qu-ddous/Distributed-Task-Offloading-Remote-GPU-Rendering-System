"""
Server Documentation & User Guide View.
Re-uses the rich bilingual DocsView tailored for Server Node.
"""
from client.ui.views.docs_view import DocsView

class ServerDocsView(DocsView):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, is_server=True)

