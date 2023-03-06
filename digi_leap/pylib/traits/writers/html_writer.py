from dataclasses import dataclass

from plants.pylib.writers.html_writer import HtmlWriter as BaseWriter
from plants.pylib.writers.html_writer import HtmlWriterRow as BaseWriterRow

from ... import consts


@dataclass
class HtmlWriterRow(BaseWriterRow):
    label_id: int


class HtmlWriter(BaseWriter):
    def __init__(self, out_html):
        super().__init__(
            template_dir=f"{consts.ROOT_DIR}/digi_leap/pylib/traits/writers/templates",
            out_html=out_html,
        )

    def write(self, labels, in_file_name=""):
        for lb in labels:
            text = self.format_text(lb)
            traits = self.format_traits(lb)
            self.formatted.append(
                HtmlWriterRow(
                    label_id=lb.label_id,
                    formatted_text=text,
                    formatted_traits=traits,
                )
            )

        self.write_template(in_file_name)
