"""Figure document element."""

from .element import CaptionedElement


class Figure(CaptionedElement):
    def __init__(self, caption, label=None, links=None, **kwargs):
        super().__init__(caption=caption, label=label, **kwargs)
        self.links = list(links or [])

    def serialize(self):
        data = super().serialize()
        data["links"] = self.links
        return data
