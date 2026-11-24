class DataMixin:
    title_page = None
    paginate_by = 5
    extra_context = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_context = dict(self.extra_context)
        if self.title_page:
            self.extra_context["title"] = self.title_page

    def get_mixin_context(self, context, **kwargs):
        if self.title_page:
            context["title"] = self.title_page
        context.update(kwargs)
        return context
