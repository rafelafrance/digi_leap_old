import base64
import io
import warnings
from dataclasses import dataclass

from PIL import Image
from plants.pylib.writers.html_writer import HtmlWriter as BaseWriter
from plants.pylib.writers.html_writer import HtmlWriterRow as BaseWriterRow
from tqdm import tqdm

from ... import const

BASE_HEIGHT = 600.0  # pixels


@dataclass(kw_only=True)
class HtmlWriterRow(BaseWriterRow):
    label_id: int = 0
    label_image: str = ""


class HtmlWriter(BaseWriter):
    def __init__(self, out_html):
        super().__init__(
            template_dir=f"{const.ROOT_DIR}/digi_leap/pylib/traits/writers/templates",
            out_html=out_html,
        )

    def write(self, labels, in_file_name=""):
        for lb in tqdm(sorted(labels, key=lambda label: label.label_id), desc="write"):
            self.formatted.append(
                HtmlWriterRow(
                    label_id=lb.label_id,
                    formatted_text=self.format_text(lb),
                    formatted_traits=self.format_traits(lb),
                    label_image=self.get_label_image(lb),
                )
            )

        self.write_template(in_file_name)

    @staticmethod
    def get_label_image(label) -> str:
        label = label.data
        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            path = const.ROOT_DIR / label["path"]
            sheet = Image.open(path)

        image = sheet.crop(
            (
                label["label_left"],
                label["label_top"],
                label["label_right"],
                label["label_bottom"],
            )
        )

        width = round(BASE_HEIGHT / image.size[1] * image.size[0])
        image = image.resize((width, int(BASE_HEIGHT)))

        memory = io.BytesIO()
        image.save(memory, format="JPEG")
        image_bytes = memory.getvalue()

        string = base64.b64encode(image_bytes).decode()
        return string
